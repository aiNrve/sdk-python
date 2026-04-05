"""Shared pytest fixtures for aiNrve SDK tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def proxy_base_url() -> str:
    """Default local aiNrve proxy URL used in tests."""
    return "http://localhost:8080"


@pytest.fixture
def test_api_key() -> str:
    """Default API key used in tests."""
    return "test-key"


@pytest.fixture
def mock_chat_completion_response() -> dict:
    """Canonical non-streaming chat completion response payload."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        },
    }


@pytest.fixture
def mock_stream_sse_body() -> str:
    """Canonical SSE payload body used by streaming tests."""
    return (
        'data: {"id":"1","object":"chat.completion.chunk","created":1,'
        '"model":"gpt-4o-mini","choices":[{"index":0,"delta":'
        '{"role":"assistant","content":"Hello"},"finish_reason":null}]}\n\n'
        'data: {"id":"1","object":"chat.completion.chunk","created":1,'
        '"model":"gpt-4o-mini","choices":[{"index":0,"delta":'
        '{"content":" world"},"finish_reason":null}]}\n\n'
        'data: [DONE]\n\n'
    )
