"""Streaming response handlers for sync and async chat completions."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from contextlib import AbstractAsyncContextManager, AbstractContextManager, ExitStack

import httpx

from ainrve.types.stream import ChatCompletionChunk


class _DoneSentinel:
	"""Marker type used to indicate stream completion."""


DONE = _DoneSentinel()


def _parse_sse_line(line: str) -> ChatCompletionChunk | _DoneSentinel | None:
	"""Parse a single SSE line into a typed chunk.

	Args:
		line: Single line from the SSE stream.

	Returns:
		Parsed chunk, a done sentinel for stream completion, or None for
		ignorable/malformed lines.
	"""
	cleaned = line.strip()
	if not cleaned:
		return None
	if cleaned == "data: [DONE]":
		return DONE
	if not cleaned.startswith("data: "):
		return None
	data = cleaned[6:]
	try:
		return ChatCompletionChunk.model_validate_json(data)
	except Exception:
		return None


class Stream:
	"""Sync iterator over SSE stream from proxy."""

	def __init__(
		self,
		response: httpx.Response | AbstractContextManager[httpx.Response],
	) -> None:
		"""Create a sync stream wrapper.

		Args:
			response: Streaming response object or context manager.
		"""
		self._response = response

	def __iter__(self) -> Iterator[ChatCompletionChunk]:
		"""Yield completion chunks parsed from SSE lines."""
		with ExitStack() as stack:
			if isinstance(self._response, httpx.Response):
				resp = self._response
				stack.callback(resp.close)
			else:
				resp = stack.enter_context(self._response)

			for line in resp.iter_lines():
				parsed = _parse_sse_line(line)
				if parsed is None:
					continue
				if parsed is DONE:
					break
				yield parsed

	def __enter__(self) -> Stream:
		"""Enter context manager scope for sync stream."""
		return self

	def __exit__(self, *args: object) -> None:
		"""Exit context manager scope for sync stream."""


class AsyncStream:
	"""Async iterator over SSE stream from proxy."""

	def __init__(
		self,
		response_cm: AbstractAsyncContextManager[httpx.Response],
	) -> None:
		"""Create an async stream wrapper.

		Args:
			response_cm: Async context manager returning a streaming response.
		"""
		self._response_cm = response_cm
		self._response: httpx.Response | None = None
		self._line_iterator: AsyncIterator[str] | None = None
		self._closed = False

	def __aiter__(self) -> AsyncStream:
		"""Return async iterator for stream consumption."""
		return self

	async def __anext__(self) -> ChatCompletionChunk:
		"""Return the next parsed chunk from the async SSE stream."""
		if self._closed:
			raise StopAsyncIteration

		if self._line_iterator is None:
			self._response = await self._response_cm.__aenter__()
			self._line_iterator = self._response.aiter_lines()

		while True:
			assert self._line_iterator is not None
			try:
				line = await self._line_iterator.__anext__()
			except StopAsyncIteration:
				await self.aclose()
				raise

			parsed = _parse_sse_line(line)
			if parsed is None:
				continue
			if parsed is DONE:
				await self.aclose()
				raise StopAsyncIteration
			return parsed

	async def aclose(self) -> None:
		"""Close the underlying async streaming response context."""
		if self._closed:
			return
		self._closed = True
		await self._response_cm.__aexit__(None, None, None)

	async def __aenter__(self) -> AsyncStream:
		"""Enter async context manager scope for stream."""
		return self

	async def __aexit__(self, *args: object) -> None:
		"""Exit async context manager scope and close stream resources."""
		await self.aclose()

