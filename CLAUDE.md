# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HelpBot is a CLI chatbot for PageTurner Books (a fictional bookstore) built as a progressive learning project using the Anthropic Python SDK. Each git commit corresponds to a numbered module/task, adding one new Claude API concept.

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Running

```bash
python main.py
```

Runtime commands available in the chat loop:
- `/temp 0.7` — change temperature on the fly (0.0–1.0); updates a local float, no object reconstruction
- `exit` — quit

## Architecture

All Claude API calls flow through two entry points:

1. **`helpbot/output.py` — `_extract()`**: A low-level primitive used for structured extraction. It uses the prefill + stop sequence pattern: pre-fills the assistant turn with ` ```json ` and uses ` ``` ` as a stop sequence to force valid JSON output. This powers both `detect_intent()` and all `INTENT_EXTRACTOR_MAP` extractors.

2. **`helpbot/chat.py` — `HelpBot`**: Wraps the Anthropic client. `chat()` is the blocking pattern (kept for reference); `chat_streaming()` is the production path — it streams chunks to stdout, supports tone prefilling via an `opener` parameter injected as an assistant turn prefill, then appends the final response to the `Conversation`.

**`main.py` structure:**
- `_bootstrap()` — loads `Settings`, creates the single `anthropic.Anthropic` client, `HelpBot`, and `Conversation`. The client is created once and shared for the entire session.
- `_handle_command()` — routes `/temp`, `exit`, and empty input. Returns `(new_temperature | None, should_exit)`. `None` temperature signals "not a command, proceed to chat".
- `_handle_message()` — runs the full intent pipeline and streams the response.
- `main()` — the `while` loop; just calls the above three.

**Request lifecycle (`_handle_message`):**
1. `detect_intent()` classifies the message (one extra API call)
2. `INTENT_EXTRACTOR_MAP.get(intent)` optionally extracts structured fields (another API call)
3. `_INTENT_OPENERS` maps the intent to a prefill string (tone steering)
4. `bot.chat_streaming(conversation, opener=opener, temperature=temperature)` generates and streams the response

**Data model:**
- `Settings` (pydantic-settings, `config.py`): loads `ANTHROPIC_API_KEY`, `model`, `max_tokens` from `.env`. Frozen. `temperature` is intentionally excluded — it is runtime state, not config.
- `temperature` — plain `float` local in `main()`, defaulting to `0.1`. `/temp` reassigns it directly; no object reconstruction needed.
- `Conversation` (pydantic, `conversation.py`): typed message history; `to_api_format()` serialises to the `[{"role": ..., "content": ...}]` shape the API expects.
- `ChatResult` (pydantic, `chat.py`): return value of both `chat()` and `chat_streaming()` — includes token counts.

## Key Patterns to Preserve

- **Extractor registry** (`output.py`): Adding a new intent only requires one entry in `_EXTRACTOR_SPECS`; `INTENT_EXTRACTOR_MAP` is built via dict comprehension. Don't break this pattern.
- **Prefill / stop-sequence JSON extraction** (`_extract()`): The `"```json"` assistant prefill and `"```"` stop sequence are load-bearing — they force the model to emit parseable JSON without preamble.
- **Tone prefilling** (`chat_streaming` + `opener`): The opener is appended as an assistant turn in the messages list before streaming, causing the model to continue from that tone. The opener is also printed before streaming begins so output is contiguous.

## Dependencies

| Package | Purpose |
|---|---|
| `anthropic` | Claude API client |
| `pydantic` / `pydantic-settings` | Settings validation and typed models |
| `python-dotenv` | `.env` loading (handled via `pydantic-settings`) |

Default model: `claude-haiku-4-5` (fast, cheap — appropriate for a learning project).
