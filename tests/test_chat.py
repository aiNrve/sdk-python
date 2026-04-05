"""Tests for chat completions resource behavior."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from ainrve._http import AsyncHttpTransport, HttpTransport
from ainrve._streaming import AsyncStream, Stream
from ainrve.resources.chat.completions import AsyncChatCompletions, ChatCompletions

MOCK_RESPONSE = {
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

SSE_BODY = (
    'data: {"id":"1","object":"chat.completion.chunk","created":1,'
    '"model":"gpt-4o-mini","choices":[{"index":0,"delta":'
    '{"role":"assistant","content":"Hello"},"finish_reason":null}]}\n\n'
    'data: {"id":"1","object":"chat.completion.chunk","created":1,'
    '"model":"gpt-4o-mini","choices":[{"index":0,"delta":'
    '{"content":" world"},"finish_reason":null}]}\n\n'
    'data: [DONE]\n\n'
)


def _sync_resource() -> tuple[HttpTransport, ChatCompletions]:
    """Build a sync transport and chat resource for tests."""
    transport = HttpTransport("http://localhost:8080", "test-key", 30.0)
    return transport, ChatCompletions(transport)


def _request_json(route: respx.Route) -> dict:
    """Decode the JSON body from the last recorded route call."""
    assert route.calls.last is not None
    return json.loads(route.calls.last.request.content.decode())


@respx.mock
def test_create_sync_success() -> None:
    """Sync create should return a typed completion response."""
    route = respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    transport, resource = _sync_resource()
    try:
        response = resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert route.called
        assert response.choices[0].message.content == "Hello!"
    finally:
        transport.close()


@respx.mock
def test_create_sync_with_task_header() -> None:
    """task= should be sent as X-AiNrve-Task header."""
    route = respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    transport, resource = _sync_resource()
    try:
        resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "hello"}],
            task="code",
        )
        assert route.calls.last is not None
        assert route.calls.last.request.headers["X-AiNrve-Task"] == "code"
    finally:
        transport.close()


@respx.mock
def test_create_sync_with_provider_override() -> None:
    """provider= should be sent as X-AiNrve-Provider header."""
    route = respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    transport, resource = _sync_resource()
    try:
        resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "hello"}],
            provider="groq",
        )
        assert route.calls.last is not None
        assert route.calls.last.request.headers["X-AiNrve-Provider"] == "groq"
    finally:
        transport.close()


@respx.mock
def test_create_sync_provider_in_response() -> None:
    """Provider should be surfaced from the X-AiNrve-Provider header."""
    route = respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json=MOCK_RESPONSE,
            headers={"X-AiNrve-Provider": "groq"},
        )
    )
    transport, resource = _sync_resource()
    try:
        response = resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "hello"}],
        )
        assert route.called
        assert response.provider == "groq"
    finally:
        transport.close()


@respx.mock
def test_create_stream_returns_stream_object() -> None:
    """stream=True should return a Stream wrapper."""
    respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            content=SSE_BODY.encode(),
            headers={"content-type": "text/event-stream"},
        )
    )
    transport, resource = _sync_resource()
    try:
        stream = resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "hello"}],
            stream=True,
        )
        assert isinstance(stream, Stream)
    finally:
        transport.close()


@respx.mock
def test_create_stream_yields_chunks() -> None:
    """stream=True should yield parsed ChatCompletionChunk objects."""
    respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            content=SSE_BODY.encode(),
            headers={"content-type": "text/event-stream"},
        )
    )
    transport, resource = _sync_resource()
    try:
        stream = resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "hello"}],
            stream=True,
        )
        chunks = list(stream)
        assert len(chunks) == 2
        assert chunks[0].choices[0].delta.content == "Hello"
    finally:
        transport.close()


@respx.mock
@pytest.mark.asyncio
async def test_create_async_success() -> None:
    """Async create should return a typed completion response."""
    route = respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    transport = AsyncHttpTransport("http://localhost:8080", "test-key", 30.0)
    resource = AsyncChatCompletions(transport)

    try:
        response = await resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert route.called
        assert response.choices[0].message.content == "Hello!"
    finally:
        await transport.aclose()


@respx.mock
@pytest.mark.asyncio
async def test_create_async_stream() -> None:
    """Async stream create should return async stream and yield chunks."""
    respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            content=SSE_BODY.encode(),
            headers={"content-type": "text/event-stream"},
        )
    )
    transport = AsyncHttpTransport("http://localhost:8080", "test-key", 30.0)
    resource = AsyncChatCompletions(transport)

    try:
        stream = await resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            stream=True,
        )
        assert isinstance(stream, AsyncStream)

        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[1].choices[0].delta.content == " world"
    finally:
        await transport.aclose()


@respx.mock
def test_create_passes_temperature() -> None:
    """temperature should be serialized into the request body."""
    route = respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    transport, resource = _sync_resource()
    try:
        resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
        )
        body = _request_json(route)
        assert body["temperature"] == 0.7
    finally:
        transport.close()


@respx.mock
def test_create_passes_max_tokens() -> None:
    """max_tokens should be serialized into the request body."""
    route = respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    transport, resource = _sync_resource()
    try:
        resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=100,
        )
        body = _request_json(route)
        assert body["max_tokens"] == 100
    finally:
        transport.close()


@respx.mock
def test_create_excludes_none_fields() -> None:
    """None-valued optional fields should not be present in the payload."""
    route = respx.post("http://localhost:8080/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    transport, resource = _sync_resource()
    try:
        resource.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
        )
        body = _request_json(route)
        assert "max_tokens" not in body
        assert "temperature" not in body
        assert "top_p" not in body
        assert "frequency_penalty" not in body
        assert "presence_penalty" not in body
        assert "stop" not in body
        assert "n" not in body
    finally:
        transport.close()
