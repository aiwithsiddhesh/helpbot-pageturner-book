from __future__ import annotations

import json
from typing import Callable
import anthropic

from helpbot.config import Settings


# ---------------------------------------------------------------------------
# Core extraction primitive — prefill + stop sequence pattern
# ---------------------------------------------------------------------------

def _extract(prompt: str, settings: Settings) -> dict:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.model,
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "```json"},
        ],
        stop_sequences=["```"],
    )
    raw = "```json" + response.content[0].text
    json_str = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(json_str)


# ---------------------------------------------------------------------------
# Intent classification
# ---------------------------------------------------------------------------

_INTENTS = [
    "order_status", "order_cancellation", "order_wrong_item", "order_missing_item",
    "return_request", "refund_status", "account_login_issue", "account_update",
    "book_recommendation", "book_availability", "complaint", "general_enquiry",
]


def detect_intent(customer_message: str, settings: Settings) -> str:
    """Classifies the message into one of the supported intents. Falls back to general_enquiry."""
    prompt = (
        "Classify the customer support message below into exactly one intent.\n\n"
        f"Allowed intents: {', '.join(_INTENTS)}\n\n"
        "Return ONLY a JSON object with a single field: intent\n\n"
        f"Customer message: {customer_message}"
    )
    result = _extract(prompt, settings)
    return result.get("intent", "general_enquiry")


# ---------------------------------------------------------------------------
# Extractor registry
# To add a new intent: one entry in _EXTRACTOR_SPECS. Nothing else changes.
# Each entry: intent key -> (description, fields specification)
# ---------------------------------------------------------------------------

_EXTRACTOR_SPECS: dict[str, tuple[str, str]] = {
    "order_status": (
        "an order status enquiry",
        "order_id (string or null), query_type (location/eta/delivered)",
    ),
    "order_cancellation": (
        "an order cancellation request",
        "order_id (string or null), reason (string)",
    ),
    "order_wrong_item": (
        "a wrong item complaint",
        "order_id (string or null), received_item (string), expected_item (string or null)",
    ),
    "order_missing_item": (
        "a missing item complaint",
        "order_id (string or null), missing_item (string)",
    ),
    "return_request": (
        "a return request",
        "order_id (string or null), reason (string), urgency (low/medium/high)",
    ),
    "refund_status": (
        "a refund status enquiry",
        "order_id (string or null), return_date (string or null)",
    ),
    "account_login_issue": (
        "an account login issue",
        "email (string or null), issue_type (forgot_password/locked/other)",
    ),
    "account_update": (
        "an account update request",
        "update_type (email/address/payment), new_value (string or null)",
    ),
    "book_recommendation": (
        "a book recommendation request",
        "genre (string or null), author_preference (string or null), format (ebook/paperback/hardcover/any), mood (string or null)",
    ),
    "book_availability": (
        "a book availability enquiry",
        "title (string or null), author (string or null)",
    ),
    "complaint": (
        "a customer complaint",
        "complaint_type (shipping/product_quality/wrong_item/service/other), order_id (string or null), severity (low/medium/high)",
    ),
}


def _make_extractor(description: str, fields: str) -> Callable[[str, Settings], dict]:
    """Factory — returns an extractor closed over the given description and fields."""
    def extractor(customer_message: str, settings: Settings) -> dict:
        prompt = (
            f"Extract {description} from this customer message.\n"
            f"Return ONLY a JSON object with: {fields}.\n\n"
            f"Customer message: {customer_message}"
        )
        return _extract(prompt, settings)
    extractor.__doc__ = f"Fields: {fields}"
    return extractor


# Dict comprehension — clean, no loop side-effects, no globals() injection
# main.py looks up the right extractor via INTENT_EXTRACTOR_MAP.get(intent)
INTENT_EXTRACTOR_MAP: dict[str, Callable[[str, Settings], dict]] = {
    intent: _make_extractor(desc, fields)
    for intent, (desc, fields) in _EXTRACTOR_SPECS.items()
}
