# SDK Public API

## Sync client

  import ainrve

  client = ainrve.Client(
      api_key="your-ainrve-key",          # required
      base_url="http://localhost:8080",   # optional, env AINRVE_BASE_URL
      timeout=30.0,                       # optional, default 30s
  )

  # Standard completion (identical to openai)
  response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": "Hello"}],
  )
  print(response.choices[0].message.content)

  # With task hint (ainrve extension)
  response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": "Write a sort function"}],
      task="code",          # hints router: use fast code model
  )

  # Force a specific provider (ainrve extension)
  response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[...],
      provider="groq",      # bypass routing, use groq directly
  )

  # Streaming (identical to openai)
  stream = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": "Tell me a story"}],
      stream=True,
  )
  for chunk in stream:
      print(chunk.choices[0].delta.content or "", end="", flush=True)

## Async client

  import ainrve
  import asyncio

  async def main():
      client = ainrve.AsyncClient(
          api_key="your-ainrve-key",
          base_url="http://localhost:8080",
      )
      response = await client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[{"role": "user", "content": "Hello"}],
      )
      print(response.choices[0].message.content)

      # Async streaming
      stream = await client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[...],
          stream=True,
      )
      async for chunk in stream:
          print(chunk.choices[0].delta.content or "", end="", flush=True)

  asyncio.run(main())

## Environment variables
  AINRVE_API_KEY      — default api_key if not passed to constructor
  AINRVE_BASE_URL     — default base_url (default: http://localhost:8080)
  AINRVE_TIMEOUT      — default timeout in seconds (default: 30)

## Response object shape (identical to openai)
  response.id                              # str
  response.object                          # "chat.completion"
  response.created                         # int (unix timestamp)
  response.model                           # str (model used)
  response.choices[0].message.role         # "assistant"
  response.choices[0].message.content      # str
  response.choices[0].finish_reason        # "stop" | "length"
  response.usage.prompt_tokens             # int
  response.usage.completion_tokens         # int
  response.usage.total_tokens              # int
  response.provider                        # ainrve extension: which
                                           # provider actually handled it
                                           # (from X-AiNrve-Provider header)
