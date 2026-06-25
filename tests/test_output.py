from __future__ import annotations

import unittest
from types import SimpleNamespace

from helpbot.output import detect_intent


class FakeMessages:
    def __init__(self, text: str) -> None:
        self.text = text

    def create(self, **kwargs):
        return SimpleNamespace(content=[SimpleNamespace(text=self.text)])


class FakeClient:
    def __init__(self, text: str) -> None:
        self.messages = FakeMessages(text)


class DetectIntentTests(unittest.TestCase):
    def test_detect_intent_returns_valid_intent(self) -> None:
        settings = SimpleNamespace(model="test-model")

        intent = detect_intent(
            "Where is my order?",
            settings,
            FakeClient('{"intent": "order_status"}'),
        )

        self.assertEqual(intent, "order_status")

    def test_detect_intent_falls_back_on_malformed_json(self) -> None:
        settings = SimpleNamespace(model="test-model")

        intent = detect_intent(
            "Where is my order?",
            settings,
            FakeClient('{"intent": "order_status"'),
        )

        self.assertEqual(intent, "general_enquiry")


if __name__ == "__main__":
    unittest.main()
