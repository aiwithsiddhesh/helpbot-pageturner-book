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
python main.py
```

Runtime commands in the chat loop:
- `exit` — quit

## Architecture

### Entry points

All Claude API calls flow through two entry points:

1. **`helpbot/output.py` — `_extract()`**: Low-level primitive for structured extraction. Pre-fills the assistant turn with ` ```json ` and uses ` ``` ` as a stop sequence to force valid JSON output without preamble. Powers `detect_intent()`.

2. **`helpbot/chat.py` — `HelpBot.chat_streaming()`**: Production streaming path. Accepts an `opener` string injected as an assistant prefill for tone steering. Runs a tool-use loop — keeps calling `_call()` and appending tool results to the conversation until `stop_reason != "tool_use"`.

### Intent and tool dispatch

The system is driven by **`helpbot/registry.toml`** — a TOML file where each `[intent]` section declares an optional `opener` string and a `tools` list. `registry.py` loads this once into `INTENT_REGISTRY`.

Request lifecycle in `_handle_message()`:
1. `detect_intent()` — one API call, returns a key from `INTENT_REGISTRY`
2. `INTENT_REGISTRY[intent]["tools"]` — resolves to a list of tool names
3. `load_schemas(tool_names)` — fetches Anthropic tool schemas from the tool engine
4. `bot.chat_streaming(..., tools=tools)` — streams the response, running tool calls if needed

**To add a new intent:** add a `[new_intent]` block to `registry.toml` with `tools = [...]` and an optional `opener`. No Python changes needed unless you also need a new tool.

### Tool engine

`helpbot/tools/engine/base.py` — `Tool` (ABC):
- Subclasses declare `properties: dict[str, str]` (field → description) as a class attribute
- `schema` property auto-generates the Anthropic tool schema; tool `name` is derived from the class name via `_to_snake_case()`
- `run(**kwargs) -> dict` is the implementation

`helpbot/tools/engine/loader.py`:
- On first call, auto-discovers all `Tool` subclasses by importing every module in `tools_catalog/`
- `load_schemas(tool_names)` returns schemas; `run_tool(name, input)` executes a tool by name

**To add a new tool:** create a class in `helpbot/tools/tools_catalog/` that inherits `Tool`, set `properties`, write `run()`. It is discovered automatically — no registration step.

### Database layer

`helpbot/db/__init__.py` — `get_connection()` returns a `sqlite3.Connection` (with `row_factory = sqlite3.Row`). The DB is initialised from `schema.sql` and `seed.sql` on first use.

Tables: `orders`, `return_eligibility`, `refunds`, `books`, `accounts`, `promo_codes`, `loyalty`, `digital_purchases`, `gift_orders`.

### Data model

- `Settings` (`config.py`, pydantic-settings): loads `ANTHROPIC_API_KEY`, `model`, `max_tokens` from `.env`. Frozen. `temperature` is runtime state — a plain `float` in `main()`, not in Settings.
- `Conversation` (`conversation.py`): typed message history. `to_api_format()` serialises to `[{"role": ..., "content": ...}]`. `add_assistant_raw()` accepts raw content blocks for tool-use turns.
- `ChatResult` (`chat.py`): return value of `chat_streaming()` — includes `api_calls` count (just the streaming turns; `detect_intent()` adds 1 more in `main.py`).

## Key Patterns to Preserve

- **Prefill / stop-sequence JSON extraction** (`_extract()`): The ` ```json ` prefill and ` ``` ` stop sequence are load-bearing — do not alter them.
- **Tool-use loop** (`chat_streaming`): The `while True` loop in `chat_streaming()` handles multi-turn tool calls. The loop breaks only when `stop_reason != "tool_use"`.
- **Registry-driven dispatch** (`registry.toml`): Intent→tools mapping lives in TOML, not Python. Keep new intents there.
- **Auto-discovery** (`loader.py`): `Tool` subclasses self-register via `_all_subclasses()`. Do not maintain a manual list.

## Dependencies

| Package | Purpose |
|---|---|
| `anthropic` | Claude API client |
| `pydantic` / `pydantic-settings` | Settings validation and typed models |
| `python-dotenv` | `.env` loading (via `pydantic-settings`) |

Default model: `claude-haiku-4-5` (fast, cheap — appropriate for a learning project).
