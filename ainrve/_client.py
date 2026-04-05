"""Public sync and async aiNrve client implementations."""

from __future__ import annotations

import os

from ainrve._http import AsyncHttpTransport, HttpTransport
from ainrve.resources.chat.completions import AsyncChatCompletions, ChatCompletions


class Chat:
	"""Sync chat namespace containing completion resources."""

	def __init__(self, transport: HttpTransport) -> None:
		"""Initialize sync chat resources.

		Args:
			transport: Shared sync HTTP transport.
		"""
		self.completions = ChatCompletions(transport)


class AsyncChat:
	"""Async chat namespace containing completion resources."""

	def __init__(self, transport: AsyncHttpTransport) -> None:
		"""Initialize async chat resources.

		Args:
			transport: Shared async HTTP transport.
		"""
		self.completions = AsyncChatCompletions(transport)


class Client:
	"""Sync aiNrve client.

	Drop-in replacement for ``openai.OpenAI()``.
	"""

	def __init__(
		self,
		api_key: str | None = None,
		base_url: str | None = None,
		timeout: float = 30.0,
	) -> None:
		"""Create a sync aiNrve client.

		Args:
			api_key: aiNrve API key. Falls back to ``AINRVE_API_KEY`` and then
				``local-dev-key``.
			base_url: aiNrve proxy URL. Falls back to ``AINRVE_BASE_URL`` and
				then ``http://localhost:8080``.
			timeout: Request timeout in seconds.
		"""
		resolved_key = api_key or os.environ.get("AINRVE_API_KEY") or "local-dev-key"
		resolved_url = (
			base_url or os.environ.get("AINRVE_BASE_URL") or "http://localhost:8080"
		)
		self._transport = HttpTransport(resolved_url, resolved_key, timeout)
		self.chat = Chat(self._transport)

	def close(self) -> None:
		"""Close the underlying sync transport."""
		self._transport.close()

	def __enter__(self) -> Client:
		"""Enter context manager scope for sync client."""
		return self

	def __exit__(self, *args: object) -> None:
		"""Exit context manager scope and close the sync transport."""
		self.close()


class AsyncClient:
	"""Async aiNrve client.

	Drop-in replacement for ``openai.AsyncOpenAI()``.
	"""

	def __init__(
		self,
		api_key: str | None = None,
		base_url: str | None = None,
		timeout: float = 30.0,
	) -> None:
		"""Create an async aiNrve client.

		Args:
			api_key: aiNrve API key. Falls back to ``AINRVE_API_KEY`` and then
				``local-dev-key``.
			base_url: aiNrve proxy URL. Falls back to ``AINRVE_BASE_URL`` and
				then ``http://localhost:8080``.
			timeout: Request timeout in seconds.
		"""
		resolved_key = api_key or os.environ.get("AINRVE_API_KEY") or "local-dev-key"
		resolved_url = (
			base_url or os.environ.get("AINRVE_BASE_URL") or "http://localhost:8080"
		)
		self._transport = AsyncHttpTransport(resolved_url, resolved_key, timeout)
		self.chat = AsyncChat(self._transport)

	async def aclose(self) -> None:
		"""Close the underlying async transport."""
		await self._transport.aclose()

	async def __aenter__(self) -> AsyncClient:
		"""Enter async context manager scope for async client."""
		return self

	async def __aexit__(self, *args: object) -> None:
		"""Exit async context manager scope and close the async transport."""
		await self.aclose()

