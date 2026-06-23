from __future__ import annotations

import json
from typing import Callable
import anthropic

from helpbot.config import Settings
from helpbot.registry import INTENT_REGISTRY


# ---------------------------------------------------------------------------
# Core extraction primitive — prefill + stop sequence pattern
# ---------------------------------------------------------------------------

def _extract(prompt: str, settings: Settings, client: anthropic.Anthropic) -> dict:
    response = client.messages.create(
        model=settings.model,
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "```json"},
        ],
        stop_sequences=["```"],
    )
    return json.loads(response.content[0].text.strip())


# ---------------------------------------------------------------------------
# Intent classification
# ---------------------------------------------------------------------------

_INTENTS = list(INTENT_REGISTRY.keys())


def detect_intent(customer_message: str, settings: Settings, client: anthropic.Anthropic) -> str:
    """Classifies the message into one of the supported intents. Falls back to general_enquiry."""
    prompt = (
        "Classify the customer support message below into exactly one intent.\n\n"
        f"Allowed intents: {', '.join(_INTENTS)}\n\n"
        "Return ONLY a JSON object with a single field: intent\n\n"
        f"Customer message: {customer_message}"
    )
    result = _extract(prompt, settings, client)
    return result.get("intent", "general_enquiry")
