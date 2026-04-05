"""Chat completion resources for sync and async aiNrve clients."""

from __future__ import annotations

from typing import Any

from ainrve._http import AsyncHttpTransport, HttpTransport
from ainrve._models import ChatCompletionRequest, ChatMessage
from ainrve._streaming import AsyncStream, Stream
from ainrve.types.chat_completion import ChatCompletion


class ChatCompletions:
	"""Sync chat completions resource."""

	def __init__(self, transport: HttpTransport) -> None:
		"""Initialize sync chat completions resource.

		Args:
			transport: Sync HTTP transport instance.
		"""
		self._transport = transport

	def create(
		self,
		*,
		model: str,
		messages: list[dict[str, Any]],
		stream: bool = False,
		max_tokens: int | None = None,
		temperature: float | None = None,
		top_p: float | None = None,
		frequency_penalty: float | None = None,
		presence_penalty: float | None = None,
		stop: str | list[str] | None = None,
		n: int | None = None,
		task: str | None = None,
		provider: str | None = None,
		**kwargs: Any,
	) -> ChatCompletion | Stream:
		"""Create a chat completion.

		This method is a drop-in replacement for
		``openai.chat.completions.create()`` and supports the aiNrve
		routing extensions ``task`` and ``provider``.

		Args:
			model: Target model identifier.
			messages: OpenAI-format chat messages.
			stream: Whether to return a streaming response iterator.
			max_tokens: Maximum completion tokens.
			temperature: Sampling temperature.
			top_p: Nucleus sampling probability.
			frequency_penalty: Frequency penalty parameter.
			presence_penalty: Presence penalty parameter.
			stop: Optional stop sequence(s).
			n: Number of choices to generate.
			task: Optional aiNrve task hint.
			provider: Optional aiNrve provider override.
			**kwargs: Additional OpenAI-compatible request fields.

		Returns:
			A typed ``ChatCompletion`` response for non-streaming calls, or a
			``Stream`` iterator when ``stream=True``.
		"""
		extra_headers: dict[str, str] = {}
		if task:
			extra_headers["X-AiNrve-Task"] = task
		if provider:
			extra_headers["X-AiNrve-Provider"] = provider

		body = ChatCompletionRequest(
			model=model,
			messages=[ChatMessage(**message) for message in messages],
			stream=stream,
			max_tokens=max_tokens,
			temperature=temperature,
			top_p=top_p,
			frequency_penalty=frequency_penalty,
			presence_penalty=presence_penalty,
			stop=stop,
			n=n,
			**kwargs,
		).model_dump(exclude_none=True)

		if stream:
			stream_ctx = self._transport.post(
				"/v1/chat/completions",
				json=body,
				extra_headers=extra_headers,
				stream=True,
			)
			return Stream(stream_ctx)

		resp = self._transport.post(
			"/v1/chat/completions",
			json=body,
			extra_headers=extra_headers,
		)
		data = resp.json()
		data["provider"] = resp.headers.get("X-AiNrve-Provider")
		return ChatCompletion.model_validate(data)


class AsyncChatCompletions:
	"""Async chat completions resource."""

	def __init__(self, transport: AsyncHttpTransport) -> None:
		"""Initialize async chat completions resource.

		Args:
			transport: Async HTTP transport instance.
		"""
		self._transport = transport

	async def create(
		self,
		*,
		model: str,
		messages: list[dict[str, Any]],
		stream: bool = False,
		max_tokens: int | None = None,
		temperature: float | None = None,
		top_p: float | None = None,
		frequency_penalty: float | None = None,
		presence_penalty: float | None = None,
		stop: str | list[str] | None = None,
		n: int | None = None,
		task: str | None = None,
		provider: str | None = None,
		**kwargs: Any,
	) -> ChatCompletion | AsyncStream:
		"""Create an async chat completion.

		This method mirrors ``openai.AsyncOpenAI().chat.completions.create()``
		while supporting aiNrve routing hints.

		Args:
			model: Target model identifier.
			messages: OpenAI-format chat messages.
			stream: Whether to return a streaming response iterator.
			max_tokens: Maximum completion tokens.
			temperature: Sampling temperature.
			top_p: Nucleus sampling probability.
			frequency_penalty: Frequency penalty parameter.
			presence_penalty: Presence penalty parameter.
			stop: Optional stop sequence(s).
			n: Number of choices to generate.
			task: Optional aiNrve task hint.
			provider: Optional aiNrve provider override.
			**kwargs: Additional OpenAI-compatible request fields.

		Returns:
			A typed ``ChatCompletion`` response for non-streaming calls, or an
			``AsyncStream`` iterator when ``stream=True``.
		"""
		extra_headers: dict[str, str] = {}
		if task:
			extra_headers["X-AiNrve-Task"] = task
		if provider:
			extra_headers["X-AiNrve-Provider"] = provider

		body = ChatCompletionRequest(
			model=model,
			messages=[ChatMessage(**message) for message in messages],
			stream=stream,
			max_tokens=max_tokens,
			temperature=temperature,
			top_p=top_p,
			frequency_penalty=frequency_penalty,
			presence_penalty=presence_penalty,
			stop=stop,
			n=n,
			**kwargs,
		).model_dump(exclude_none=True)

		if stream:
			stream_ctx = await self._transport.post(
				"/v1/chat/completions",
				json=body,
				extra_headers=extra_headers,
				stream=True,
			)
			return AsyncStream(stream_ctx)

		resp = await self._transport.post(
			"/v1/chat/completions",
			json=body,
			extra_headers=extra_headers,
		)
		data = resp.json()
		data["provider"] = resp.headers.get("X-AiNrve-Provider")
		return ChatCompletion.model_validate(data)

