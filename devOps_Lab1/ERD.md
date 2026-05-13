# ERD — DevOps Lab 1: OpenAI API in Python

> **Note:** This project does not use a database. The "data model" here describes the
> **in-memory data structures** that flow between the script, the user, and the OpenAI API.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py (Runtime)                        │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────────────────────────┐  │
│  │  .env file   │───▶│  os.environ["OPENAI_API_KEY"]        │  │
│  └──────────────┘    └──────────────────────────────────────┘  │
│                                          │                      │
│                                          ▼                      │
│  ┌──────────────┐    ┌──────────────────────────────────────┐  │
│  │  UserInput   │───▶│        get_response()                │  │
│  │  (stdin)     │    │  - message: str                      │  │
│  └──────────────┘    │  - temperature: float                │  │
│                       │  - max_tokens: int                   │  │
│                       └──────────────────┬───────────────────┘  │
│                                          │                      │
└──────────────────────────────────────────┼──────────────────────┘
                                           │ HTTPS POST
                                           ▼
                         ┌─────────────────────────────┐
                         │   OpenAI API (External)     │
                         │  POST /v1/chat/completions  │
                         └──────────────┬──────────────┘
                                        │ JSON Response
                                        ▼
                         ┌─────────────────────────────┐
                         │      CompletionResponse     │
                         │  choices[0].message.content │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                               Print to stdout
```

---

## Entity Definitions

### Entity 1: `ChatMessage`
Represents a single message in the conversation thread.

| Field | Type | Values | Description |
|---|---|---|---|
| `role` | `string` | `system`, `user`, `assistant` | Who authored the message |
| `content` | `string` | any text | The message body |

---

### Entity 2: `ChatRequest`
The payload sent to the OpenAI API.

| Field | Type | Example | Description |
|---|---|---|---|
| `model` | `string` | `"gpt-3.5-turbo"` | Model identifier |
| `messages` | `ChatMessage[]` | `[system_msg, user_msg]` | Conversation history |
| `temperature` | `float` | `0.7` | Sampling temperature |
| `max_tokens` | `int` | `256` | Response token limit |

---

### Entity 3: `ChatResponse`
The payload returned by the OpenAI API.

| Field | Type | Example | Description |
|---|---|---|---|
| `id` | `string` | `"chatcmpl-abc123"` | Unique completion ID |
| `choices` | `Choice[]` | see below | Array of candidate responses |
| `usage.prompt_tokens` | `int` | `42` | Tokens in the prompt |
| `usage.completion_tokens` | `int` | `85` | Tokens in the response |
| `usage.total_tokens` | `int` | `127` | Sum of both |

---

### Entity 4: `Choice`
A single candidate response inside `ChatResponse.choices`.

| Field | Type | Example | Description |
|---|---|---|---|
| `index` | `int` | `0` | Position in choices array |
| `message` | `ChatMessage` | `{role: assistant, ...}` | The model's reply |
| `finish_reason` | `string` | `"stop"` / `"length"` | Why generation stopped |

---

## Entity Relationship (Conceptual)

```
ChatRequest  1 ──── N  ChatMessage
     │
     │ (sent to API)
     ▼
ChatResponse 1 ──── N  Choice
                          │
                          └──── 1  ChatMessage  (the reply)
```

---

## Environment Variable Entity

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ Yes | Secret key for authenticating with OpenAI |

Loaded from `.env` via `python-dotenv` at runtime. Never stored in code or version control.
