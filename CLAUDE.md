# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HelpBot is a CLI chatbot for PageTurner Books (a fictional bookstore) built as a progressive learning project using the Anthropic Python SDK. Each git commit corresponds to a numbered module/task, adding one new Claude API concept.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
```

## Running

```bash
python main.py          # run the chatbot
python eval_intent.py   # run intent classification eval (makes ~37 API calls)
```

Runtime commands in the chat loop:
- `exit` — quit (prints session token summary on exit)

OTP identity flow runs at startup: if `BREVO_API_KEY` and `SENDER_EMAIL` are set in `.env`, the user can verify their email before chatting. Skip by pressing Enter — the session continues as guest.

## Architecture

### Entry points

All Claude API calls flow through two entry points:

1. **`helpbot/output.py` — `detect_intent()`**: Classifies each user message into one of 15 intents via a single API call. Uses the prefill + stop sequence pattern — the static classification prompt is cached via `cache_control: ephemeral`; only the dynamic customer message is sent uncached each time.

2. **`helpbot/chat.py` — `HelpBot.chat_streaming()`**: Production streaming path. Accepts an `opener` string injected as an assistant prefill for tone steering. Runs a tool-use loop — keeps calling `_call()` and appending tool results to the conversation until `stop_reason != "tool_use"`. System prompt and tool schemas are cached via `cache_control: ephemeral` on every call.

### Intent and tool dispatch

The system is driven by **`helpbot/registry.toml`** — a TOML file where each `[intent]` section declares an optional `opener` string, a `tools` list, and a `temperature` value tuned for that intent type. `registry.py` loads this once into `INTENT_REGISTRY`.

Request lifecycle in `_handle_message()`:
1. `detect_intent()` — one cached API call, returns a key from `INTENT_REGISTRY`
2. `INTENT_REGISTRY[intent]["temperature"]` — per-intent temperature (factual intents low, empathy/creative intents higher)
3. `INTENT_REGISTRY[intent]["tools"]` — resolves to a list of tool names
4. `load_schemas(tool_names)` — fetches Anthropic tool schemas from the tool engine
5. `bot.chat_streaming(..., tools=tools)` — streams the response, running tool calls if needed

**To add a new intent:** add a `[new_intent]` block to `registry.toml` with `tools = [...]`, `temperature = X`, and an optional `opener`. No Python changes needed unless you also need a new tool.

### Prompt caching

Three layers of caching are active on every request:
- **System prompt** — passed as a typed block with `cache_control: ephemeral` in `_call()`
- **Tool schemas** — `cache_control` appended to the last tool schema before the API call (copy, never mutate `_REGISTRY`)
- **Conversation prefix** — `to_api_format()` marks the second-to-last message with `cache_control: ephemeral` so the stable history prefix is cached each turn
- **Intent classification prompt** — the static prefix of the `detect_intent()` prompt is cached; only the customer message is dynamic

Cache stats (`cache_creation_tokens`, `cache_read_tokens`) are tracked in `ChatResult` and shown in the per-turn stats line and the session summary.

### Tool engine

`helpbot/tools/engine/base.py` — `Tool` (ABC):
- Subclasses declare `properties: dict[str, str]` (field → description) as a class attribute
- `schema` property auto-generates the Anthropic tool schema; tool `name` is derived from the class name via `_to_snake_case()`
- `run(**kwargs) -> dict` is the implementation

`helpbot/tools/engine/loader.py`:
- On first call, auto-discovers all `Tool` subclasses by importing every module in `tools_catalog/`
- `load_schemas(tool_names)` returns schemas; `run_tool(name, input)` executes a tool by name

**To add a new tool:** create a class in `helpbot/tools/tools_catalog/` that inherits `Tool`, set `properties`, write `run()`. It is discovered automatically — no registration step.

**`session_email` parameter contract:** Every `Tool.run()` receives `session_email: str | None` as a keyword argument (injected by `run_tool()`). Protected tools (those in `_PROTECTED_TOOLS` in `loader.py`) are gated: `run_tool()` rejects calls with no valid session before `run()` is ever invoked.

**Security layer in `loader.py`:** `_PROTECTED_TOOLS` lists the tool names that require a verified identity. `run_tool()` checks session validity and rate-limits (5 calls per session) before dispatching. Every call is appended to `audit.log` with timestamp, identity, tool name, inputs, and outcome.

### Database layer

`helpbot/db/__init__.py` — `get_connection()` returns a `sqlite3.Connection` (with `row_factory = sqlite3.Row`). The DB is initialised from `schema.sql` and `seed.sql` on first use.

Tables: `orders`, `return_eligibility`, `refunds`, `books`, `accounts`, `promo_codes`, `loyalty`, `digital_purchases`, `gift_orders`.

### Data model

- `Settings` (`config.py`, pydantic-settings): loads `ANTHROPIC_API_KEY`, `model`, `max_tokens` from `.env`. Frozen.
- `Conversation` (`conversation.py`): typed message history. `to_api_format()` serialises to the API format and attaches `cache_control` to the second-to-last message. `add_assistant_raw()` accepts raw content blocks for tool-use turns.
- `ChatResult` (`chat.py`): return value of `chat_streaming()` — includes `input_tokens`, `output_tokens`, `total_tokens`, `api_calls`, `cache_creation_tokens`, `cache_read_tokens`.
- `SessionStats` (`main.py`): accumulates `ChatResult` values across the session; prints a summary on exit.

### Intent eval harness

`eval_intent.py` — 37 labelled test cases covering all 15 intents plus edge cases. Run after any change to the classification prompt or `SYSTEM_PROMPT` to get an objective accuracy score. Exits with code 1 if accuracy drops below 80%. Record the baseline score in the file docstring after the first run.

## Key Patterns to Preserve

- **Prefill / stop-sequence JSON extraction** (`_extract()`): The ` ```json ` prefill and ` ``` ` stop sequence are load-bearing — do not alter them.
- **Tool-use loop** (`chat_streaming`): The `while True` loop handles multi-turn tool calls. The loop breaks only when `stop_reason != "tool_use"`. `MAX_TOOL_ROUNDS = 10` guards against infinite loops — raises `RuntimeError` if exceeded.
- **Registry-driven dispatch** (`registry.toml`): Intent→tools→temperature mapping lives in TOML, not Python. Keep new intents there.
- **Auto-discovery** (`loader.py`): `Tool` subclasses self-register via `_all_subclasses()`. Do not maintain a manual list.
- **Cache safety** (`_call()`): Tool schemas are copied before attaching `cache_control` — never mutate the shared `_REGISTRY` dicts directly.
- **Conversation cache pointer** (`to_api_format()`): Marks `serialised[-2]`, not the live turn. Handles both `str` and `list` content shapes correctly.

## Dependencies

| Package | Purpose |
|---|---|
| `anthropic` | Claude API client |
| `pydantic` / `pydantic-settings` | Settings validation and typed models |
| `python-dotenv` | `.env` loading (via `pydantic-settings`) |
| `sib-api-v3-sdk` | Brevo transactional email (OTP delivery) |

`utils._with_retry()` wraps any callable with up to 3 attempts and exponential backoff on `RateLimitError` / `APIStatusError`. Used in both `_call()` and `detect_intent()`.

Default model: `claude-haiku-4-5` (fast, cheap — appropriate for a learning project).
