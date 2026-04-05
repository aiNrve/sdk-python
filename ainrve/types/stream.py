"""Public streaming chunk response types."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ChoiceDelta(BaseModel):
	"""Delta payload for streaming chat tokens."""

	role: str | None = None
	content: str | None = None

	model_config = ConfigDict(extra="allow")


class StreamChoice(BaseModel):
	"""A streaming completion choice."""

	index: int
	delta: ChoiceDelta
	finish_reason: str | None = None

	model_config = ConfigDict(extra="allow")


class ChatCompletionChunk(BaseModel):
	"""Top-level SSE chunk model for chat completions."""

	id: str
	object: str = "chat.completion.chunk"
	created: int
	model: str
	choices: list[StreamChoice]

	model_config = ConfigDict(extra="allow")

