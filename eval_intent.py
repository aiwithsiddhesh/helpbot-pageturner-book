"""
Intent classification eval harness.

Run with: python eval_intent.py

Each test case is (customer_message, expected_intent). The script calls
detect_intent() for every case, compares against the expected label, and
prints per-intent accuracy plus an overall score.

Baseline (recorded after #22 system prompt rewrite): TBD — run once to establish.
Fail threshold: overall accuracy must be >= 80% or the script exits with code 1.
"""

import sys
import anthropic
from pydantic import ValidationError

from helpbot import Settings
from helpbot.output import detect_intent

PASS_THRESHOLD = 0.80

TEST_CASES: list[tuple[str, str]] = [
    # order_status (3)
    ("Where is my order PT-1001?", "order_status"),
    ("Has my order shipped yet?", "order_status"),
    ("What's the status of my delivery?", "order_status"),

    # order_cancellation (3)
    ("I want to cancel my order.", "order_cancellation"),
    ("Please cancel order PT-1003 immediately.", "order_cancellation"),
    ("Can I still cancel? I just placed it.", "order_cancellation"),

    # order_wrong_item (2)
    ("I received the wrong book — this isn't what I ordered.", "order_wrong_item"),
    ("You sent me the wrong item entirely.", "order_wrong_item"),

    # order_missing_item (2)
    ("Part of my order is missing.", "order_missing_item"),
    ("I only received one book but I ordered two.", "order_missing_item"),

    # return_request (3)
    ("I want to return this book.", "return_request"),
    ("How do I send a book back for a return?", "return_request"),
    ("I'd like to initiate a return for order PT-1002.", "return_request"),

    # refund_status (2)
    ("When will my refund arrive?", "refund_status"),
    ("I returned my order two weeks ago — where's my money?", "refund_status"),

    # account_login_issue (2)
    ("I can't log into my account.", "account_login_issue"),
    ("My password isn't working and I'm locked out.", "account_login_issue"),

    # account_update (2)
    ("I need to update my email address.", "account_update"),
    ("Can I change the delivery address on my account?", "account_update"),

    # book_recommendation (3)
    ("Can you recommend a good thriller?", "book_recommendation"),
    ("What should I read if I loved The Alchemist?", "book_recommendation"),
    ("I'm looking for a gift book for someone who likes history.", "book_recommendation"),

    # book_availability (3)
    ("Is Dune in stock?", "book_availability"),
    ("Do you have Atomic Habits available?", "book_availability"),
    ("When will Project Hail Mary be back in stock?", "book_availability"),

    # complaint (3)
    ("This is absolutely terrible service — I'm very unhappy.", "complaint"),
    ("My parcel arrived completely damaged and I'm furious.", "complaint"),
    ("I've been waiting three weeks and nobody has helped me.", "complaint"),

    # promo_enquiry (2)
    ("Do you have a discount code I can use?", "promo_enquiry"),
    ("Is the promo code SUMMER20 still valid?", "promo_enquiry"),

    # loyalty_enquiry (2)
    ("How many loyalty points do I have?", "loyalty_enquiry"),
    ("What tier am I on in the rewards programme?", "loyalty_enquiry"),

    # digital_access_issue (2)
    ("I can't download my ebook.", "digital_access_issue"),
    ("My download link for Sapiens has expired — can you resend it?", "digital_access_issue"),

    # gift_order_enquiry (2)
    ("I sent a gift order — has it arrived yet?", "gift_order_enquiry"),
    ("Can you check on a gift I ordered for my friend Emma?", "gift_order_enquiry"),

    # general_enquiry (2)
    ("Hi, I have a question.", "general_enquiry"),
    ("Do you sell gift cards?", "general_enquiry"),

    # Edge cases
    ("Hi", "general_enquiry"),
    ("???", "general_enquiry"),
    # Ambiguous — damaged item could be complaint or return; complaint is more direct fit
    ("My book arrived damaged and I want my money back.", "complaint"),
    # Polite wrapper around a clear intent
    ("I was just wondering if maybe you could tell me where my order is?", "order_status"),
    # Multi-intent — order status is the primary ask
    ("Can you check my order status and also tell me about your return policy?", "order_status"),
]


def _bootstrap() -> tuple[Settings, anthropic.Anthropic]:
    try:
        settings = Settings()
    except ValidationError:
        sys.exit("Error: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
    return settings, anthropic.Anthropic(api_key=settings.anthropic_api_key)


def run_eval() -> None:
    settings, client = _bootstrap()

    all_intents = sorted({expected for _, expected in TEST_CASES})
    per_intent: dict[str, list[bool]] = {intent: [] for intent in all_intents}

    total = len(TEST_CASES)
    correct = 0

    print(f"Running {total} test cases...\n")

    for i, (message, expected) in enumerate(TEST_CASES, 1):
        predicted = detect_intent(message, settings, client)
        passed = predicted == expected
        per_intent[expected].append(passed)
        if passed:
            correct += 1
        status = "PASS" if passed else "FAIL"
        label = f"[{status}]"
        print(f"  {i:02d}. {label} expected={expected!r:30s} got={predicted!r}")

    overall = correct / total

    print(f"\n{'─' * 60}")
    print("Per-intent results:")
    for intent in all_intents:
        results = per_intent[intent]
        intent_correct = sum(results)
        intent_total = len(results)
        bar = "✓" * intent_correct + "✗" * (intent_total - intent_correct)
        print(f"  {intent:30s} {intent_correct}/{intent_total}  {bar}")

    print(f"\n{'─' * 60}")
    print(f"Overall: {correct}/{total} correct — {overall:.1%}")
    print(f"Threshold: {PASS_THRESHOLD:.0%}")

    if overall < PASS_THRESHOLD:
        print(f"\nFAIL — accuracy below {PASS_THRESHOLD:.0%} threshold.")
        sys.exit(1)
    else:
        print("\nPASS")


if __name__ == "__main__":
    run_eval()
