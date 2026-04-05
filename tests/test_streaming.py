"""Tests for sync and async SSE streaming parsers."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest

from ainrve._streaming import AsyncStream, Stream


def _chunk_payload(content: str, *, created: int = 1) -> str:
    """Return a valid chat.completion.chunk JSON payload string."""
    return (
        "{"
        '"id":"chunk-1",'
        '"object":"chat.completion.chunk",'
        f'"created":{created},'
        '"model":"gpt-4o-mini",'
        '"choices":[{"index":0,"delta":{"content":"'
        f"{content}"
        '"},"finish_reason":null}]'
        "}"
    )


class _FakeSyncResponseCM:
    """Minimal sync context manager exposing iter_lines()."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    def __enter__(self) -> _FakeSyncResponseCM:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def iter_lines(self) -> Iterator[str]:
        for line in self._lines:
            yield line


class _FakeAsyncResponse:
    """Minimal async response exposing aiter_lines()."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    async def aiter_lines(self) -> AsyncIterator[str]:
        for line in self._lines:
            yield line


class _FakeAsyncResponseCM:
    """Minimal async context manager returning an async response."""

    def __init__(self, lines: list[str]) -> None:
        self._response = _FakeAsyncResponse(lines)

    async def __aenter__(self) -> _FakeAsyncResponse:
        return self._response

    async def __aexit__(self, *args: object) -> None:
        return None


def test_stream_parses_multiple_sse_chunks_correctly() -> None:
    """Stream should parse each valid SSE data chunk into typed models."""
    lines = [
        f"data: {_chunk_payload('Hello', created=1)}",
        "",
        f"data: {_chunk_payload(' world', created=2)}",
        "data: [DONE]",
    ]

    stream = Stream(_FakeSyncResponseCM(lines))
    chunks = list(stream)

    assert len(chunks) == 2
    assert chunks[0].choices[0].delta.content == "Hello"
    assert chunks[1].choices[0].delta.content == " world"


def test_stream_stops_at_done() -> None:
    """Stream should stop consuming lines immediately after [DONE]."""
    lines = [
        f"data: {_chunk_payload('Only this')}",
        "data: [DONE]",
        f"data: {_chunk_payload('Ignored')}",
    ]

    chunks = list(Stream(_FakeSyncResponseCM(lines)))

    assert len(chunks) == 1
    assert chunks[0].choices[0].delta.content == "Only this"


def test_stream_skips_malformed_chunks_without_raising() -> None:
    """Malformed JSON chunks should be ignored instead of raising."""
    lines = [
        f"data: {_chunk_payload('ok')}",
        "data: {not-valid-json}",
        "data: [DONE]",
    ]

    chunks = list(Stream(_FakeSyncResponseCM(lines)))

    assert len(chunks) == 1
    assert chunks[0].choices[0].delta.content == "ok"


@pytest.mark.asyncio
async def test_async_stream_iteration_works() -> None:
    """AsyncStream should parse valid chunks via async iteration."""
    lines = [
        f"data: {_chunk_payload('Hello', created=1)}",
        f"data: {_chunk_payload(' async', created=2)}",
        "data: [DONE]",
    ]

    stream = AsyncStream(_FakeAsyncResponseCM(lines))

    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0].choices[0].delta.content == "Hello"
    assert chunks[1].choices[0].delta.content == " async"
