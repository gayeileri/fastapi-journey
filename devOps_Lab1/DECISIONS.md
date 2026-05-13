# DECISIONS.md — DevOps Lab 1: OpenAI API in Python

## 1. Why use `python-dotenv` instead of hardcoding the API key?

Hardcoding secrets in source code is a critical security anti-pattern. If the repository is pushed to GitHub (even privately), the API key can be scraped by automated bots and abused within minutes.

Using `python-dotenv` solves this by:

- **Separation of concerns**: configuration lives outside of code
- **Environment parity**: the same code runs on a developer laptop, CI/CD pipeline, or production server by simply swapping the `.env` file (or injecting environment variables)
- **`.gitignore` enforcement**: `.env` is excluded from version control while `.env.example` documents the required keys for new contributors

The `OpenAI()` constructor automatically reads `OPENAI_API_KEY` from the environment, so no additional wiring is needed.

---

## 2. Why use the `client.chat.completions.create()` syntax instead of `openai.ChatCompletion.create()`?

The legacy `openai.ChatCompletion.create()` pattern was deprecated in **openai >= 1.0.0** (released November 2023). The new syntax:

```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(...)
```

...introduces an **instantiated client object** rather than calling module-level functions. Benefits:

| Legacy (< 1.0) | Current (>= 1.0) |
|---|---|
| Module-level global state | Explicit client instance |
| Hard to test / mock | Easy to inject and mock in tests |
| No support for multiple API keys | Multiple clients with different keys |
| Deprecated — no new features | Actively maintained |

This project targets `openai >= 1.0.0` as required by the lab specification.

---

## 3. What does `temperature` actually control?

Temperature scales the **logit distribution** before the model samples the next token. In plain terms:

- **temperature = 0**: The model always picks the single highest-probability token → fully deterministic, repetitive output.
- **temperature = 0.7** (default): Balanced randomness — the model explores plausible alternatives, producing natural-sounding text.
- **temperature ≥ 1.5**: The distribution flattens dramatically → highly creative but potentially incoherent output.

**Why this matters for DevOps use cases:**

| Use Case | Recommended Temperature |
|---|---|
| Code generation | 0 – 0.3 (deterministic) |
| Summarisation | 0.3 – 0.7 |
| Brainstorming / creative prompts | 0.8 – 1.2 |

---

## 4. What does `max_tokens` control and why is it important?

`max_tokens` sets a hard ceiling on the number of tokens **in the response** (not including the prompt). One token ≈ 4 characters in English.

**Why cap it?**

- **Cost control**: OpenAI charges per token. A runaway prompt with no limit can exhaust a billing quota.
- **Latency**: Shorter responses return faster — critical for interactive applications.
- **Predictable output**: For structured outputs (JSON, code), a known maximum prevents truncated, invalid responses.

This project defaults to `max_tokens=256` for demos and `max_tokens=150` during temperature comparisons to keep output scannable.

---

## 5. Why structure the code with separate functions (`get_response`, `compare_temperatures`, `interactive_chat`)?

Following the **Single Responsibility Principle (SRP)**:

- `get_response()` — pure API call, reusable in any context (scripts, notebooks, tests)
- `compare_temperatures()` — isolated demo logic, can be called independently
- `interactive_chat()` — UI / REPL layer, separated from business logic

This makes the project easy to extend: adding logging, retry logic, or streaming only requires touching `get_response()`, not the entire script.

---

## Technical Stack

| Component | Choice | Reason |
|---|---|---|
| Language | Python 3.10+ | Async support, type hints, f-strings |
| LLM Client | `openai >= 1.0.0` | Required by lab; current stable API |
| Secrets | `python-dotenv` | Industry-standard `.env` pattern |
| Model | `gpt-3.5-turbo` | Cost-efficient; sufficient for demos |
| Runtime | Any Python IDE or Jupyter | No server needed |
