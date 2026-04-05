"""Exception hierarchy for the aiNrve SDK."""

from __future__ import annotations


class AiNrveError(Exception):
	"""Base exception for all aiNrve errors."""

	def __init__(self, message: str, status_code: int | None = None) -> None:
		"""Initialize a typed aiNrve exception.

		Args:
			message: Human-readable error message.
			status_code: Optional HTTP status code associated with the error.
		"""
		self.message = message
		self.status_code = status_code
		super().__init__(message)


class APIError(AiNrveError):
	"""The proxy returned an unexpected error."""


class AuthError(AiNrveError):
	"""Invalid or missing API key."""

	def __init__(self, message: str, status_code: int | None = 401) -> None:
		"""Initialize an authentication error.

		Args:
			message: Human-readable error message.
			status_code: HTTP status code for auth errors.
		"""
		super().__init__(message=message, status_code=status_code)


class RateLimitError(AiNrveError):
	"""Rate limit hit on the proxy."""

	def __init__(self, message: str, status_code: int | None = 429) -> None:
		"""Initialize a rate-limit error.

		Args:
			message: Human-readable error message.
			status_code: HTTP status code for rate-limit errors.
		"""
		super().__init__(message=message, status_code=status_code)


class ProviderError(AiNrveError):
	"""All upstream providers failed or are unavailable."""

	def __init__(self, message: str, status_code: int | None = 503) -> None:
		"""Initialize an upstream provider error.

		Args:
			message: Human-readable error message.
			status_code: HTTP status code for provider errors.
		"""
		super().__init__(message=message, status_code=status_code)


class APIConnectionError(AiNrveError):
	"""Cannot connect to the aiNrve proxy."""

	def __init__(self, message: str, status_code: int | None = None) -> None:
		"""Initialize a network connectivity error.

		Args:
			message: Human-readable error message.
			status_code: Optional status code, usually omitted for network failures.
		"""
		super().__init__(message=message, status_code=status_code)


class APITimeoutError(APIConnectionError):
	"""Request to proxy timed out."""

