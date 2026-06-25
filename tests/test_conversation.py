from __future__ import annotations

import unittest

from helpbot.conversation import Conversation


class ToApiFormatTests(unittest.TestCase):
    def test_empty_conversation(self) -> None:
        conv = Conversation()
        self.assertEqual(conv.to_api_format(), [])

    def test_single_message_no_cache_pointer(self) -> None:
        conv = Conversation()
        conv.add_user("Hello")
        result = conv.to_api_format()
        self.assertEqual(len(result), 1)
        # Only one user text message — not enough to place cache pointer
        self.assertIsInstance(result[0]["content"], str)

    def test_cache_pointer_on_second_to_last_user_text(self) -> None:
        conv = Conversation()
        conv.add_user("First message")
        conv.add_assistant("First reply")
        conv.add_user("Second message")
        conv.add_assistant("Second reply")
        conv.add_user("Third message")

        result = conv.to_api_format()
        # Three user text messages — second-to-last is "Second message"
        cached = [m for m in result if isinstance(m["content"], list) and
                  any(isinstance(b, dict) and b.get("cache_control") for b in m["content"])]
        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0]["content"][0]["text"], "Second message")

    def test_cache_pointer_skips_tool_result_messages(self) -> None:
        conv = Conversation()
        conv.add_user("Check my order")
        conv.add_assistant_raw([{"type": "tool_use", "id": "tu_1", "name": "check_order_status", "input": {}}])
        conv.add_tool_results([{"type": "tool_result", "tool_use_id": "tu_1", "content": "{}", "is_error": False}])
        conv.add_user("Thanks")

        result = conv.to_api_format()
        # Two user text messages: "Check my order" and "Thanks"
        # Cache pointer lands on "Check my order" (second-to-last user text)
        # Tool result message (list content) is correctly skipped
        cached = [m for m in result if isinstance(m["content"], list) and
                  any(isinstance(b, dict) and b.get("cache_control") for b in m["content"]
                  if isinstance(b, dict))]
        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0]["content"][0]["text"], "Check my order")

    def test_add_tool_results_single_message(self) -> None:
        conv = Conversation()
        conv.add_user("Query")
        conv.add_tool_results([
            {"type": "tool_result", "tool_use_id": "id1", "content": "{}", "is_error": False},
            {"type": "tool_result", "tool_use_id": "id2", "content": "{}", "is_error": False},
        ])
        result = conv.to_api_format()
        # Both tool results must be in a single user message
        user_messages = [m for m in result if m["role"] == "user"]
        tool_result_messages = [m for m in user_messages if isinstance(m["content"], list)
                                and m["content"] and m["content"][0].get("type") == "tool_result"]
        self.assertEqual(len(tool_result_messages), 1)
        self.assertEqual(len(tool_result_messages[0]["content"]), 2)


if __name__ == "__main__":
    unittest.main()
