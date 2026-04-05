"""HTTP transport layer for aiNrve sync and async clients."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any

import httpx

from ainrve._exceptions import (
	APIConnectionError,
	APIError,
	APITimeoutError,
	AuthError,
	ProviderError,
	RateLimitError,
)
from ainrve._version import __version__


class HttpTransport:
	"""Sync HTTP transport using httpx.Client."""

	def __init__(self, base_url: str, api_key: str, timeout: float) -> None:
		"""Create a sync transport configured for aiNrve proxy requests.

		Args:
			base_url: aiNrve proxy base URL.
			api_key: Bearer token used for authentication.
			timeout: Request timeout in seconds.
		"""
		self.base_url = base_url.rstrip("/")
		self.api_key = api_key
		self.timeout = timeout
		self._client = httpx.Client(
			base_url=self.base_url,
			headers={
				"Authorization": f"Bearer {api_key}",
				"Content-Type": "application/json",
				"User-Agent": f"ainrve-python/{__version__}",
			},
			timeout=timeout,
		)

	def post(
		self,
		path: str,
		json: dict[str, Any],
		extra_headers: Mapping[str, str] | None = None,
		stream: bool = False,
	) -> httpx.Response | AbstractContextManager[httpx.Response]:
		"""Send a POST request to the proxy.

		Args:
			path: Relative request path.
			json: JSON payload body.
			extra_headers: Additional request headers.
			stream: Whether to return a streaming context manager.

		Returns:
			A response object for non-streaming requests, or a response context
			manager when streaming is enabled.

		Raises:
			APITimeoutError: When the request times out.
			APIConnectionError: When the proxy cannot be reached.
			AuthError: On HTTP 401.
			RateLimitError: On HTTP 429.
			ProviderError: On HTTP 502/503.
			APIError: On HTTP 5xx responses.
		"""
		headers = dict(extra_headers or {})
		try:
			if stream:
				return self._client.stream("POST", path, json=json, headers=headers)
			resp = self._client.post(path, json=json, headers=headers)
			self._raise_for_status(resp)
			return resp
		except httpx.TimeoutException as exc:
			raise APITimeoutError(str(exc)) from exc
		except httpx.ConnectError as exc:
			raise APIConnectionError(
				f"Cannot connect to aiNrve proxy at {self.base_url}"
			) from exc

	def _raise_for_status(self, resp: httpx.Response) -> None:
		"""Map HTTP response status codes to aiNrve exceptions.

		Args:
			resp: HTTP response to validate.

		Raises:
			AuthError: On HTTP 401.
			RateLimitError: On HTTP 429.
			ProviderError: On HTTP 502/503.
			APIError: On HTTP 5xx.
			httpx.HTTPStatusError: For non-mapped 4xx status codes.
		"""
		if resp.status_code == 401:
			raise AuthError("Invalid aiNrve API key", 401)
		if resp.status_code == 429:
			raise RateLimitError("Rate limit exceeded", 429)
		if resp.status_code in (502, 503):
			raise ProviderError("Upstream provider unavailable", resp.status_code)
		if resp.status_code >= 500:
			raise APIError(f"Proxy error: {resp.status_code} {resp.text}", resp.status_code)
		resp.raise_for_status()

	def close(self) -> None:
		"""Close the underlying sync HTTP client."""
		self._client.close()

	def __enter__(self) -> HttpTransport:
		"""Enter context manager scope for sync transport."""
		return self

	def __exit__(self, *args: object) -> None:
		"""Exit context manager scope and close client resources."""
		self.close()


class AsyncHttpTransport:
	"""Async HTTP transport using httpx.AsyncClient."""

	def __init__(self, base_url: str, api_key: str, timeout: float) -> None:
		"""Create an async transport configured for aiNrve proxy requests.

		Args:
			base_url: aiNrve proxy base URL.
			api_key: Bearer token used for authentication.
			timeout: Request timeout in seconds.
		"""
		self.base_url = base_url.rstrip("/")
		self.api_key = api_key
		self.timeout = timeout
		self._client = httpx.AsyncClient(
			base_url=self.base_url,
			headers={
				"Authorization": f"Bearer {api_key}",
				"Content-Type": "application/json",
				"User-Agent": f"ainrve-python/{__version__}",
			},
			timeout=timeout,
		)

	async def post(
		self,
		path: str,
		json: dict[str, Any],
		extra_headers: Mapping[str, str] | None = None,
		stream: bool = False,
	) -> httpx.Response | AbstractAsyncContextManager[httpx.Response]:
		"""Send an async POST request to the proxy.

		Args:
			path: Relative request path.
			json: JSON payload body.
			extra_headers: Additional request headers.
			stream: Whether to return a streaming async context manager.

		Returns:
			A response object for non-streaming requests, or an async response
			context manager when streaming is enabled.

		Raises:
			APITimeoutError: When the request times out.
			APIConnectionError: When the proxy cannot be reached.
			AuthError: On HTTP 401.
			RateLimitError: On HTTP 429.
			ProviderError: On HTTP 502/503.
			APIError: On HTTP 5xx responses.
		"""
		headers = dict(extra_headers or {})
		try:
			if stream:
				return self._client.stream("POST", path, json=json, headers=headers)
			resp = await self._client.post(path, json=json, headers=headers)
			self._raise_for_status(resp)
			return resp
		except httpx.TimeoutException as exc:
			raise APITimeoutError(str(exc)) from exc
		except httpx.ConnectError as exc:
			raise APIConnectionError(
				f"Cannot connect to aiNrve proxy at {self.base_url}"
			) from exc

	def _raise_for_status(self, resp: httpx.Response) -> None:
		"""Map HTTP response status codes to aiNrve exceptions.

		Args:
			resp: HTTP response to validate.

		Raises:
			AuthError: On HTTP 401.
			RateLimitError: On HTTP 429.
			ProviderError: On HTTP 502/503.
			APIError: On HTTP 5xx.
			httpx.HTTPStatusError: For non-mapped 4xx status codes.
		"""
		if resp.status_code == 401:
			raise AuthError("Invalid aiNrve API key", 401)
		if resp.status_code == 429:
			raise RateLimitError("Rate limit exceeded", 429)
		if resp.status_code in (502, 503):
			raise ProviderError("Upstream provider unavailable", resp.status_code)
		if resp.status_code >= 500:
			raise APIError(f"Proxy error: {resp.status_code} {resp.text}", resp.status_code)
		resp.raise_for_status()

	async def aclose(self) -> None:
		"""Close the underlying async HTTP client."""
		await self._client.aclose()

	async def __aenter__(self) -> AsyncHttpTransport:
		"""Enter async context manager scope for async transport."""
		return self

	async def __aexit__(self, *args: object) -> None:
		"""Exit async context manager scope and close client resources."""
		await self.aclose()

