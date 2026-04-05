"""Public chat completion response types."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatCompletionMessage(BaseModel):
	"""Assistant message payload for a completion choice."""

	role: str
	content: str | None = None

	model_config = ConfigDict(extra="allow")


class Choice(BaseModel):
	"""A single completion choice."""

	index: int
	message: ChatCompletionMessage
	finish_reason: str | None = None

	model_config = ConfigDict(extra="allow")


class Usage(BaseModel):
	"""Token accounting details for a completion."""

	prompt_tokens: int = 0
	completion_tokens: int = 0
	total_tokens: int = 0

	model_config = ConfigDict(extra="allow")


class ChatCompletion(BaseModel):
	"""Top-level response model for chat completions."""

	id: str
	object: str = "chat.completion"
	created: int
	model: str
	choices: list[Choice]
	usage: Usage = Field(default_factory=Usage)
	provider: str | None = None

	model_config = ConfigDict(extra="allow")

