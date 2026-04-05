"""Tests for aiNrve SDK exceptions."""

from __future__ import annotations

import pytest

from ainrve._exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AiNrveError,
    AuthError,
    ProviderError,
    RateLimitError,
)


@pytest.mark.parametrize(
    "exc_type",
    [
        APIError,
        AuthError,
        RateLimitError,
        ProviderError,
        APIConnectionError,
        APITimeoutError,
    ],
)
def test_all_exceptions_subclass_ainrve_error(exc_type: type[AiNrveError]) -> None:
    """Every SDK exception should inherit from AiNrveError."""
    assert issubclass(exc_type, AiNrveError)


@pytest.mark.parametrize(
    "exc, expected_message, expected_status",
    [
        (AiNrveError("base", 500), "base", 500),
        (APIError("api", 500), "api", 500),
        (AuthError("auth"), "auth", 401),
        (RateLimitError("rate"), "rate", 429),
        (ProviderError("provider", 502), "provider", 502),
        (APIConnectionError("conn"), "conn", None),
        (APITimeoutError("timeout"), "timeout", None),
    ],
)
def test_exception_attributes(
    exc: AiNrveError,
    expected_message: str,
    expected_status: int | None,
) -> None:
    """Exceptions should expose message and status_code attributes."""
    assert exc.message == expected_message
    assert exc.status_code == expected_status
    assert str(exc) == expected_message
