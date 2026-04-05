# ainrve Python SDK

[![PyPI version](https://img.shields.io/pypi/v/ainrve.svg)](https://pypi.org/project/ainrve/)
[![Python versions](https://img.shields.io/pypi/pyversions/ainrve.svg)](https://pypi.org/project/ainrve/)
[![License](https://img.shields.io/pypi/l/ainrve.svg)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/aiNrve/sdk-python/tests.yml?branch=main&label=tests)](https://github.com/aiNrve/sdk-python/actions)

Drop-in replacement for the OpenAI Python SDK with automatic provider routing, fallback, and cost-aware inference through aiNrve proxy.

## The Migration

### BEFORE (OpenAI)
```python
import openai

client = openai.OpenAI(api_key="sk-openai-key")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.choices[0].message.content)
```

### AFTER (aiNrve)
```python
import ainrve

client = ainrve.Client(
    api_key="ainrve-key",
    base_url="http://localhost:8080",
)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.choices[0].message.content)
```

## Install

```bash
pip install ainrve
```

## Quickstart

```python
import ainrve

client = ainrve.Client(api_key="your-ainrve-key")
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a haiku about latency."}],
)
print(resp.choices[0].message.content)
```

## Task Hints

Use `task=` to help aiNrve route requests to the best model/provider for your workload.

```python
# code generation
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a binary search in Python."}],
    task="code",
)

# summarization
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Summarize this report..."}],
    task="summarize",
)

# force a provider (override routing)
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
    provider="groq",
)
```

Supported task hints include: `code`, `classify`, `summarize`, `reasoning`, `rag`.

## Async Example

```python
import asyncio
import ainrve


async def main() -> None:
    client = ainrve.AsyncClient(api_key="your-ainrve-key")
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello from async"}],
    )
    print(response.choices[0].message.content)
    await client.aclose()


asyncio.run(main())
```

## Streaming Example

```python
import ainrve

client = ainrve.Client(api_key="your-ainrve-key")
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a short story."}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
print()
```

## Full Provider List

See the aiNrve proxy repository for the latest supported providers:
https://github.com/aiNrve/proxy

## Running the Proxy

Start or deploy the proxy before using this SDK:
https://github.com/aiNrve/proxy#quickstart

Default SDK target is `http://localhost:8080` (override with `base_url` or `AINRVE_BASE_URL`).

## License

MIT. See [LICENSE](LICENSE).
