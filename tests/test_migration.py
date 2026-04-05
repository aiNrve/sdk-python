"""Migration compatibility tests proving one-line OpenAI replacement."""

from __future__ import annotations

import json

import httpx
import respx

MOCK_RESPONSE = {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "gpt-4o-mini",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "4"},
            "finish_reason": "stop",
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 2,
        "total_tokens": 12,
    },
}

SSE_BODY = (
    'data: {"id":"1","object":"chat.completion.chunk","created":1,'
    '"model":"gpt-4o-mini","choices":[{"index":0,"delta":'
    '{"role":"assistant","content":"Hello"},"finish_reason":null}]}\n\n'
    'data: {"id":"1","object":"chat.completion.chunk","created":1,'
    '"model":"gpt-4o-mini","choices":[{"index":0,"delta":'
    '{"content":" world"},"finish_reason":null}]}\n\n'
    'data: [DONE]\n\n'
)


def test_exact_openai_usage_pattern() -> None:
    """The ONLY change from OpenAI usage is: import ainrve as openai."""
    import ainrve as openai

    client = openai.Client(api_key="test-key")

    try:
        with respx.mock:
            respx.post("http://localhost:8080/v1/chat/completions").mock(
                return_value=httpx.Response(200, json=MOCK_RESPONSE)
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 2+2?"},
                ],
                temperature=0.7,
                max_tokens=100,
            )
            assert isinstance(response.choices, list)
            assert response.choices[0].message.content is not None
            assert response.usage.total_tokens > 0
    finally:
        client.close()


def test_streaming_openai_pattern() -> None:
    """Verbatim OpenAI streaming style should work with ainrve client."""
    import ainrve as openai

    client = openai.Client(api_key="test-key")

    try:
        with respx.mock:
            respx.post("http://localhost:8080/v1/chat/completions").mock(
                return_value=httpx.Response(
                    200,
                    content=SSE_BODY.encode(),
                    headers={"content-type": "text/event-stream"},
                )
            )
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say hello"}],
                stream=True,
            )

            output = ""
            for chunk in stream:
                output += chunk.choices[0].delta.content or ""

            assert output == "Hello world"
    finally:
        client.close()


def test_task_hint_does_not_break_existing_code() -> None:
    """Extra kwargs pass-through still works while task/provider become headers."""
    import ainrve as openai

    client = openai.Client(api_key="test-key")

    try:
        with respx.mock:
            route = respx.post("http://localhost:8080/v1/chat/completions").mock(
                return_value=httpx.Response(200, json=MOCK_RESPONSE)
            )

            dynamic_kwargs = {
                "task": "code",
                "provider": "groq",
                "temperature": 0.5,
            }
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Write a loop"}],
                **dynamic_kwargs,
            )

            assert response.choices[0].message.content is not None
            assert route.calls.last is not None
            request = route.calls.last.request
            body = json.loads(request.content.decode())

            assert request.headers["X-AiNrve-Task"] == "code"
            assert request.headers["X-AiNrve-Provider"] == "groq"
            assert "task" not in body
            assert "provider" not in body
            assert body["temperature"] == 0.5
    finally:
        client.close()
