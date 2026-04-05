# Testing Strategy

## Tools
- pytest >= 7.0
- respx — mock httpx calls (NOT responses, NOT httpretty)
- pytest-asyncio — async test support
- pytest-cov — coverage

## Mock strategy
Use respx.mock as a context manager or decorator to intercept
httpx calls. Do NOT spin up a real server in unit tests.
Shared fixtures for test payloads and defaults live in
tests/conftest.py.

## Transport coverage
Include explicit tests for HTTP status-to-exception mapping in
tests/test_http.py (401/429/502/503 and connection failures).

## Chat resource coverage
tests/test_chat.py validates sync + async create(), stream object
returns, chunk yielding, header injection for task/provider, response
provider extraction, and request-body field serialization behavior.

## Stream lifecycle coverage
tests/test_streaming.py includes a regression test ensuring sync
stream iteration (`for chunk in stream`) opens/closes the response
context internally without requiring caller-managed context blocks.

Example mock pattern:
  import respx
  import httpx

  @respx.mock
  def test_complete():
      respx.post("http://localhost:8080/v1/chat/completions").mock(
          return_value=httpx.Response(200, json={
              "id": "chatcmpl-123",
              "object": "chat.completion",
              "created": 1234567890,
              "model": "gpt-4o-mini",
              "choices": [{
                  "index": 0,
                  "message": {"role": "assistant", "content": "Hello!"},
                  "finish_reason": "stop"
              }],
              "usage": {
                  "prompt_tokens": 10,
                  "completion_tokens": 5,
                  "total_tokens": 15
              }
          })
      )
      client = ainrve.Client(api_key="test-key")
      response = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[{"role": "user", "content": "Hi"}]
      )
      assert response.choices[0].message.content == "Hello!"

## SSE mock pattern for streaming tests
  SSE_BODY = (
      'data: {"id":"1","object":"chat.completion.chunk","created":1,'
      '"model":"gpt-4o-mini","choices":[{"index":0,"delta":'
      '{"role":"assistant","content":"Hello"},"finish_reason":null}]}\n\n'
      'data: {"id":"1","object":"chat.completion.chunk","created":1,'
      '"model":"gpt-4o-mini","choices":[{"index":0,"delta":'
      '{"content":" world"},"finish_reason":null}]}\n\n'
      'data: [DONE]\n\n'
  )
  respx.post(...).mock(return_value=httpx.Response(
      200,
      content=SSE_BODY.encode(),
      headers={"content-type": "text/event-stream"}
  ))

## test_migration.py — the most important test
This test proves the one-line migration claim:

  def test_openai_code_works_with_ainrve_client():
      """
      This is verbatim code a developer would write using openai library.
      It must work with ainrve.Client with no other changes.
      """
      import ainrve as openai  # ← the ONE line change

      client = openai.Client(api_key="test-key")  # was openai.OpenAI(...)

      with respx.mock:
          respx.post(...).mock(return_value=httpx.Response(200, json={...}))
          response = client.chat.completions.create(
              model="gpt-4o-mini",
              messages=[
                  {"role": "system", "content": "You are helpful"},
                  {"role": "user", "content": "Hello"},
              ],
              temperature=0.7,
              max_tokens=100,
          )
          assert response.choices[0].message.content is not None
          assert response.usage.total_tokens > 0
