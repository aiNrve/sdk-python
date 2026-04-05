# Architecture Decisions

## ADR-001: Mirror openai library's interface exactly
The primary design constraint is drop-in compatibility.
client.chat.completions.create() must accept exactly the same
arguments as the openai library and return the same shape.
We achieve this via pydantic models that mirror openai's types.

## ADR-002: httpx for HTTP transport
Use httpx (not requests) because it supports both sync and async
with the same API. httpx.Client for sync, httpx.AsyncClient for async.
This avoids maintaining two separate HTTP implementations.

## ADR-003: ainrve-specific kwargs are popped before request body
task= and provider= are not OpenAI fields. They are extracted from
kwargs before building the request body and converted to headers.
This means existing OpenAI code that passes **kwargs through still
works correctly.

## ADR-004: Stream object mirrors openai's Stream
The Stream class is iterable (sync) and the AsyncStream class is
async-iterable. Both yield ChatCompletionChunk objects. This means
code like "for chunk in stream:" works identically regardless of
whether the underlying provider supports SSE.

## ADR-005: pydantic v2 for models
Use pydantic v2. Models use model_validate() not parse_obj().
All response models have model_config = ConfigDict(extra="allow")
so that ainrve extensions (like provider field) don't break parsing.

## ADR-006: api_key falls back to env var
If api_key is not passed to the constructor, read AINRVE_API_KEY
from environment. If neither is set, raise AuthError at call time
(not at construction time — lazy validation).
