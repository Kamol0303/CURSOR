"""SSRF-safe HTTP client for external integrations."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

ALLOWED_SCHEMES = {"https"}
MAX_RESPONSE_BYTES = 1_048_576


class SSRFError(ValueError):
    pass


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    return any(ip in network for network in BLOCKED_NETWORKS)


def validate_external_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise SSRFError("Only HTTPS URLs are allowed")
    if not parsed.hostname:
        raise SSRFError("Invalid URL hostname")

    hostname = parsed.hostname.lower()
    if hostname in {"localhost", "metadata.google.internal"}:
        raise SSRFError("Blocked hostname")

    try:
        addr_infos = socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise SSRFError("Unable to resolve hostname") from exc

    for info in addr_infos:
        ip = ipaddress.ip_address(info[4][0])
        if _is_blocked_ip(ip):
            raise SSRFError("Target resolves to a blocked network")

    return url


async def safe_get(url: str, *, timeout: float = 10.0, headers: dict | None = None) -> httpx.Response:
    validated = validate_external_url(url)
    async with httpx.AsyncClient(follow_redirects=False, timeout=timeout) as client:
        response = await client.get(validated, headers=headers)
        if int(response.headers.get("content-length", 0)) > MAX_RESPONSE_BYTES:
            raise SSRFError("Response too large")
        return response
