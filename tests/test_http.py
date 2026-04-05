"""Tests for HTTP transport status mapping and network errors."""

from __future__ import annotations

import httpx
import pytest

from ainrve._exceptions import APIConnectionError, AuthError, ProviderError, RateLimitError
from ainrve._http import HttpTransport


def _response(status_code: int, text: str = "") -> httpx.Response:
    """Build an HTTP response with an attached request for tests."""
    req = httpx.Request("POST", "http://localhost:8080/v1/chat/completions")
    return httpx.Response(status_code=status_code, text=text, request=req)


def test_raise_for_status_maps_401_to_auth_error() -> None:
    """HTTP 401 should map to AuthError."""
    transport = HttpTransport("http://localhost:8080", "test-key", 30.0)
    try:
        with pytest.raises(AuthError) as exc_info:
            transport._raise_for_status(_response(401, "unauthorized"))
        assert exc_info.value.status_code == 401
    finally:
        transport.close()


def test_raise_for_status_maps_429_to_rate_limit_error() -> None:
    """HTTP 429 should map to RateLimitError."""
    transport = HttpTransport("http://localhost:8080", "test-key", 30.0)
    try:
        with pytest.raises(RateLimitError) as exc_info:
            transport._raise_for_status(_response(429, "rate limited"))
        assert exc_info.value.status_code == 429
    finally:
        transport.close()


def test_raise_for_status_maps_503_to_provider_error() -> None:
    """HTTP 503 should map to ProviderError."""
    transport = HttpTransport("http://localhost:8080", "test-key", 30.0)
    try:
        with pytest.raises(ProviderError) as exc_info:
            transport._raise_for_status(_response(503, "provider down"))
        assert exc_info.value.status_code == 503
    finally:
        transport.close()


def test_post_maps_connection_error_to_api_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Connection failures should raise APIConnectionError."""
    transport = HttpTransport("http://localhost:8080", "test-key", 30.0)
    try:
        request = httpx.Request("POST", "http://localhost:8080/v1/chat/completions")

        def _raise_connect_error(*args: object, **kwargs: object) -> httpx.Response:
            raise httpx.ConnectError("connect failed", request=request)

        monkeypatch.setattr(transport._client, "post", _raise_connect_error)

        with pytest.raises(APIConnectionError) as exc_info:
            transport.post("/v1/chat/completions", json={"model": "x", "messages": []})

        assert "Cannot connect to aiNrve proxy" in str(exc_info.value)
    finally:
        transport.close()
