"""Secrets backend — file (dev) or HashiCorp Vault KV v2 (production)."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path

import httpx

from app.core.config import settings


class SecretsProvider(ABC):
    @abstractmethod
    async def get_secret(self, key: str) -> str | None:
        pass

    async def materialize_pem(self, vault_key: str, target_path: str) -> bool:
        content = await self.get_secret(vault_key)
        if not content:
            return False
        path = Path(target_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        os.chmod(path, 0o600)
        return True


class FileSecretsProvider(SecretsProvider):
    """Reads secrets from mounted files (development / CI)."""

    async def get_secret(self, key: str) -> str | None:
        mapping = {
            "jwt_private_key": settings.JWT_PRIVATE_KEY_PATH,
            "jwt_public_key": settings.JWT_PUBLIC_KEY_PATH,
        }
        path = mapping.get(key)
        if not path or not Path(path).exists():
            return None
        return Path(path).read_text(encoding="utf-8")


class VaultSecretsProvider(SecretsProvider):
    """HashiCorp Vault KV v2 read-only client."""

    def __init__(self, addr: str, token: str, mount: str, prefix: str) -> None:
        self.addr = addr.rstrip("/")
        self.token = token
        self.mount = mount
        self.prefix = prefix.strip("/")

    def _url(self, key: str) -> str:
        return f"{self.addr}/v1/{self.mount}/data/{self.prefix}/{key}"

    async def get_secret(self, key: str) -> str | None:
        headers = {"X-Vault-Token": self.token}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self._url(key), headers=headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json().get("data", {}).get("data", {})
            return data.get("value")


def get_secrets_provider() -> SecretsProvider:
    if settings.SECRETS_BACKEND == "vault" and settings.VAULT_ADDR and settings.VAULT_TOKEN:
        return VaultSecretsProvider(
            addr=settings.VAULT_ADDR,
            token=settings.VAULT_TOKEN,
            mount=settings.VAULT_MOUNT,
            prefix=settings.VAULT_SECRET_PREFIX,
        )
    return FileSecretsProvider()


async def bootstrap_secrets() -> None:
    """Fetch secrets from Vault and materialize JWT PEM files before app serves traffic."""
    if settings.SECRETS_BACKEND != "vault":
        return

    provider = get_secrets_provider()
    if not isinstance(provider, VaultSecretsProvider):
        return

    private_ok = await provider.materialize_pem("jwt_private_key", settings.JWT_PRIVATE_KEY_PATH)
    public_ok = await provider.materialize_pem("jwt_public_key", settings.JWT_PUBLIC_KEY_PATH)
    if settings.ENVIRONMENT == "production" and (not private_ok or not public_ok):
        raise RuntimeError("Vault JWT keys not found — cannot start in production")
