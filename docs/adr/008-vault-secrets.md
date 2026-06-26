# ADR-008: Production Secrets via HashiCorp Vault

## Status
Accepted (Phase 5)

## Context
JWT signing keys, TOTP encryption keys, and PINFL encryption keys must not live in environment variables or git in production. Phase 0–4 used file-mounted secrets for development.

## Decision
Use **HashiCorp Vault KV v2** as the production secrets backend:

- `SECRETS_BACKEND=vault` in production
- Secrets path: `{VAULT_MOUNT}/data/{VAULT_SECRET_PREFIX}/{key}`
- Keys: `jwt_private_key`, `jwt_public_key` (PEM text in `value` field)
- Application materializes JWT PEMs to `/secrets/` at startup via `bootstrap_secrets()`
- Non-secret config remains in environment variables

## Consequences
- Vault outage blocks new container starts (existing pods keep running with mounted keys)
- Token rotation requires rolling restart after Vault secret update
- Development/CI continue using `SECRETS_BACKEND=file` with generated keys

## Alternatives Considered
- AWS KMS / GCP KMS — deferred; on-prem Uzbekistan deployment favors Vault
- Kubernetes Secrets alone — insufficient audit trail and rotation workflow
