"""Tests for sync and async client initialization behavior."""

from __future__ import annotations

import pytest

from ainrve._client import AsyncClient, Client
from ainrve.resources.chat.completions import AsyncChatCompletions


def test_client_uses_env_var_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Client should read api_key from AINRVE_API_KEY when omitted."""
    monkeypatch.setenv("AINRVE_API_KEY", "env-key")
    client = Client(base_url="http://localhost:8080")
    try:
        assert client._transport.api_key == "env-key"
    finally:
        client.close()


def test_client_uses_env_var_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Client should read base_url from AINRVE_BASE_URL when omitted."""
    monkeypatch.setenv("AINRVE_BASE_URL", "http://env-proxy:9000")
    client = Client(api_key="test-key")
    try:
        assert client._transport.base_url == "http://env-proxy:9000"
    finally:
        client.close()


def test_client_constructor_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Explicit constructor values should override environment variables."""
    monkeypatch.setenv("AINRVE_API_KEY", "env-key")
    monkeypatch.setenv("AINRVE_BASE_URL", "http://env-proxy:9000")

    client = Client(api_key="arg-key", base_url="http://arg-proxy:8081")
    try:
        assert client._transport.api_key == "arg-key"
        assert client._transport.base_url == "http://arg-proxy:8081"
    finally:
        client.close()


def test_client_default_base_url_is_localhost(monkeypatch: pytest.MonkeyPatch) -> None:
    """Client should default base_url to local proxy when env is unset."""
    monkeypatch.delenv("AINRVE_BASE_URL", raising=False)
    client = Client(api_key="test-key")
    try:
        assert client._transport.base_url == "http://localhost:8080"
    finally:
        client.close()


def test_client_uses_env_var_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Client should read timeout from AINRVE_TIMEOUT when omitted."""
    monkeypatch.setenv("AINRVE_TIMEOUT", "12.5")
    client = Client(api_key="test-key")
    try:
        assert client._transport.timeout == 12.5
    finally:
        client.close()


def test_client_invalid_env_timeout_falls_back_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid AINRVE_TIMEOUT values should fall back to 30s."""
    monkeypatch.setenv("AINRVE_TIMEOUT", "not-a-number")
    client = Client(api_key="test-key")
    try:
        assert client._transport.timeout == 30.0
    finally:
        client.close()


def test_client_context_manager_closes_transport() -> None:
    """Sync client context manager should close the underlying transport."""
    client = Client(api_key="test-key")
    assert client._transport._client.is_closed is False

    with client:
        assert client._transport._client.is_closed is False

    assert client._transport._client.is_closed is True


@pytest.mark.asyncio
async def test_async_client_init() -> None:
    """AsyncClient should initialize async chat resources and transport."""
    client = AsyncClient(api_key="test-key")
    try:
        assert client._transport.api_key == "test-key"
        assert client._transport.base_url == "http://localhost:8080"
        assert isinstance(client.chat.completions, AsyncChatCompletions)
    finally:
        await client.aclose()
