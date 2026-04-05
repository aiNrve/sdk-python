"""Internal request models for aiNrve resources."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ChatMessage(BaseModel):
	"""A chat message in OpenAI-compatible format."""

	role: str
	content: str


class ChatCompletionRequest(BaseModel):
	"""Request payload for chat completion endpoints."""

	model: str
	messages: list[ChatMessage]
	stream: bool = False
	max_tokens: int | None = None
	temperature: float | None = None
	top_p: float | None = None
	frequency_penalty: float | None = None
	presence_penalty: float | None = None
	stop: str | list[str] | None = None
	n: int | None = None

	model_config = ConfigDict(extra="allow")

