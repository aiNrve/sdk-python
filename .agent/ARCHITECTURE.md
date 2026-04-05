# aiNrve/sdk-python — Architecture

## What this is
A Python package that wraps the aiNrve proxy HTTP API and exposes
an interface identical to the openai Python library. Developers 
swap one import, nothing else changes.

## The one-line migration
BEFORE:
  import openai
  client = openai.OpenAI(api_key="sk-openai-key")

AFTER:
  import ainrve
  client = ainrve.Client(
      api_key="ainrve-key",         # your ainrve proxy key
      base_url="http://localhost:8080"  # your proxy URL
  )

Everything else — client.chat.completions.create(), streaming,
async, response objects — stays identical.

## Package structure
ainrve/
  __init__.py          → exports Client, AsyncClient, version
  _client.py           → Client (sync) and AsyncClient classes
  _http.py             → HTTP transport layer (httpx wrapper)
  _streaming.py        → SSE streaming response handler
  _models.py           → Pydantic request/response types
  _exceptions.py       → AiNrveError, APIError, AuthError,
                          RateLimitError, ProviderError
  _version.py          → __version__ = "0.1.0"
  resources/
    __init__.py
    chat/
      __init__.py
      completions.py   → ChatCompletions resource (sync + async)
  types/
    __init__.py
    chat_completion.py → ChatCompletion, Choice, Message, Usage
    stream.py          → ChatCompletionChunk, ChoiceDelta

tests/
  conftest.py          → pytest fixtures, mock proxy server
  test_client.py       → Client init, base_url resolution
  test_chat.py         → chat.completions.create() sync + async
  test_streaming.py    → streaming response parsing
  test_exceptions.py   → error mapping from proxy HTTP codes
  test_migration.py    → proves one-line migration works

## Request flow
1. Developer calls client.chat.completions.create(...)
2. ChatCompletions.create() validates args with pydantic
3. Adds X-AiNrve-Task header if task= kwarg provided
4. Adds X-AiNrve-Provider header if provider= kwarg provided
5. POST to {base_url}/v1/chat/completions
6. Response parsed into ChatCompletion pydantic model
7. Returned to developer — identical shape to openai response

## Extra kwargs (ainrve-specific, ignored by openai)
These are ainrve extensions that pass as headers to the proxy:
  task="code"        → X-AiNrve-Task: code
  task="classify"    → X-AiNrve-Task: classify
  task="summarize"   → X-AiNrve-Task: summarize
  task="reasoning"   → X-AiNrve-Task: reasoning
  task="rag"         → X-AiNrve-Task: rag
  provider="groq"    → X-AiNrve-Provider: groq  (force provider)

These kwargs are popped before building the request body so
the proxy receives a clean OpenAI-format body.

## Streaming
stream=True returns a Stream object (sync) or AsyncStream (async).
Both are iterables yielding ChatCompletionChunk objects.
SSE parsing: read lines, skip empty, skip "data: [DONE]",
parse "data: {json}" → ChatCompletionChunk pydantic model.

## Error mapping
Proxy HTTP status → Python exception:
  401 → AuthError("Invalid aiNrve API key")
  429 → RateLimitError("Rate limit exceeded")
  502/503 → ProviderError("Upstream provider unavailable")
  5xx → APIError("Proxy error: {status} {body}")
  Network error → APIConnectionError("Cannot reach proxy")
