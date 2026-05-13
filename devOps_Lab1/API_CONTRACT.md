# API Contract — DevOps Lab 1: OpenAI API in Python

> **Note:** This project is a **CLI/script application**, not a REST API server.
> The "API contract" here documents the interface between the Python functions in `main.py`
> and the OpenAI Chat Completions API endpoint they call.

---

## Internal Function Interface

### `get_response(user_message, temperature, max_tokens) → str`

| Parameter | Type | Default | Valid Range | Description |
|---|---|---|---|---|
| `user_message` | `str` | *(required)* | Non-empty string | The user's input prompt |
| `temperature` | `float` | `0.7` | `0.0 – 2.0` | Randomness of the output |
| `max_tokens` | `int` | `256` | `1 – 4096` | Max tokens in the response |

**Returns:** `str` — the model's response text

**Raises:**
- `openai.AuthenticationError` — if `OPENAI_API_KEY` is missing or invalid
- `openai.RateLimitError` — if the API quota is exceeded
- `openai.BadRequestError` — if parameters are out of range

---

## OpenAI Chat Completions API — Upstream Contract

**Endpoint:** `POST https://api.openai.com/v1/chat/completions`

**Authentication:** `Authorization: Bearer $OPENAI_API_KEY` (set automatically by the SDK)

### Request Body

```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant specialized in Python and DevOps topics..."
    },
    {
      "role": "user",
      "content": "<user_message>"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 256
}
```

### Response Body (Success — HTTP 200)

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1715000000,
  "model": "gpt-3.5-turbo-0125",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "<model response text>"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 85,
    "total_tokens": 127
  }
}
```

### Fields Used by This Project

| Field | Path | Usage |
|---|---|---|
| Response text | `choices[0].message.content` | Returned to the caller |
| Finish reason | `choices[0].finish_reason` | `"stop"` = complete, `"length"` = truncated by `max_tokens` |
| Token usage | `usage.total_tokens` | Useful for cost monitoring |

### Error Response (HTTP 4xx / 5xx)

```json
{
  "error": {
    "message": "Incorrect API key provided.",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

---

## Message Role Definitions

| Role | Purpose |
|---|---|
| `system` | Configures model persona and constraints (set once per session) |
| `user` | The human's input |
| `assistant` | The model's previous replies (used in multi-turn conversations) |

---

## Parameter Effects Summary

| Parameter | Low Value | High Value |
|---|---|---|
| `temperature` | Predictable, focused | Creative, unpredictable |
| `max_tokens` | Short, possibly truncated | Long, higher cost |
