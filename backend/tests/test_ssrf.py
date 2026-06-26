import pytest

from app.integrations.http_client import SSRFError, validate_external_url


def test_blocks_localhost():
    with pytest.raises(SSRFError):
        validate_external_url("https://localhost/api")


def test_blocks_http_scheme():
    with pytest.raises(SSRFError):
        validate_external_url("http://example.com/api")


def test_allows_public_https(monkeypatch):
    import socket

    def fake_getaddrinfo(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    assert validate_external_url("https://example.com/path") == "https://example.com/path"
