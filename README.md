# HelpBot

AI-powered customer support chatbot for PageTurner Books, built progressively across modules using the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python).

Each git commit introduces one new Claude API concept — streaming, tool use, structured extraction, tone prefilling, prompt caching, and more.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -e .

cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=your-key-here
# Optional: set BREVO_API_KEY and SENDER_EMAIL to enable OTP identity verification
```

## Running

```bash
python main.py          # run the chatbot
python eval_intent.py   # run intent classification eval (~37 API calls)
```

**Runtime commands:**
- `exit` — quit (prints a session token + cache summary on exit)

At startup, the bot prompts for email-based OTP verification (requires Brevo credentials). Press Enter to skip and continue as a guest — account-specific tools will prompt for identity when needed.

## How It Works

Every message goes through a three-step pipeline:

1. **Intent classification** — a cached API call classifies the message into one of 15 intents (order status, returns, book availability, complaints, etc.)
2. **Tool dispatch** — the intent maps to a set of tools and a temperature (both defined in `helpbot/registry.toml`); the model calls tools against a local SQLite database
3. **Streamed response** — the reply streams to the terminal with optional tone prefilling for empathy-sensitive intents

Per-turn stats (API calls, tokens, cache hits/misses) are printed after each response. A full session summary prints on exit.

## Security

Account-sensitive tools (`check_order_status`, `cancel_order`, `get_refund_status`, etc.) are protected — they require a verified session before the model can call them. The loader enforces this before dispatching to any tool, and rate-limits each session to 5 protected-tool calls. Every tool call is appended to `audit.log` (gitignored) with timestamp, identity, tool name, inputs, and outcome.

## Prompt Caching

Four layers of caching reduce latency and token costs across a session:

| What is cached | Where |
|---|---|
| System prompt | `chat.py` — passed as a typed block with `cache_control` |
| Tool schemas | `chat.py` — `cache_control` appended to the last tool before each call |
| Conversation prefix | `conversation.py` — second-to-last message marked each turn |
| Intent classification prompt | `output.py` — static prefix cached; only the customer message is dynamic |

## Project Structure

```
helpbot/
├── config.py           # Settings (pydantic-settings) + system prompt
├── conversation.py     # Typed message history + conversation prefix caching
├── chat.py             # HelpBot class — streaming + tool-use loop + cache stats
├── output.py           # detect_intent() — cached intent classification
├── registry.py         # Loads registry.toml → INTENT_REGISTRY
├── registry.toml       # Intent → tools + opener + temperature (add intents here)
├── otp.py              # OTP generation + Brevo email delivery
├── utils.py            # _with_retry() — exponential backoff on rate limit errors
├── db/
│   ├── schema.sql      # SQLite schema
│   ├── seed.sql        # Sample data
│   └── __init__.py     # get_connection() — lazy DB init, commit/rollback context manager
└── tools/
    ├── engine/
    │   ├── base.py     # Tool ABC — define properties + run()
    │   └── loader.py   # Auto-discovery, session/rate-limit guard, audit logging
    └── tools_catalog/  # One file per domain (books, orders, returns, …)
eval_intent.py          # Intent classification eval harness (80% pass threshold)
```

## Adding a New Intent

1. Add a block to `helpbot/registry.toml`:
   ```toml
   [my_new_intent]
   opener = "Optional empathy opener string."
   tools  = ["my_tool_name"]
   temperature = 0.3
   ```
2. If you need a new tool, create a class in `helpbot/tools/tools_catalog/`:
   ```python
   from helpbot.tools.engine.base import Tool

   class MyToolName(Tool):
       """One-sentence description used as the tool description."""
       properties = {"param": "What this parameter means."}

       def run(self, param: str, session_email: str | None = None) -> dict:
           return {"result": ...}
   ```
   The class name becomes the tool name (`MyToolName` → `my_tool_name`). No registration needed — tools are auto-discovered. Always accept `session_email` as a keyword argument; the loader injects it on every call.

3. If the tool should require identity verification, add its name to `_PROTECTED_TOOLS` in `helpbot/tools/engine/loader.py`.

## Dependencies

| Package | Purpose |
|---|---|
| `anthropic` | Claude API client |
| `pydantic` / `pydantic-settings` | Config validation and typed models |
| `python-dotenv` | `.env` loading |
| `sib-api-v3-sdk` | Brevo transactional email (OTP delivery) |

Default model: `claude-haiku-4-5`
