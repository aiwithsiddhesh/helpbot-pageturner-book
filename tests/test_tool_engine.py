from __future__ import annotations

import json
import unittest

import helpbot.tools.engine.loader as loader_module
from helpbot.tools.engine.loader import load_schemas, run_tool, set_session_email


def _reset_loader():
    loader_module._REGISTRY.clear()
    loader_module._LOADED = False
    loader_module._SESSION_EMAIL = None
    loader_module._SESSION_TIMESTAMP = None
    loader_module._RATE_COUNTER = 0


class LoadSchemasTests(unittest.TestCase):
    def setUp(self):
        _reset_loader()

    def test_load_known_tool(self) -> None:
        schemas = load_schemas(["check_order_status"])
        self.assertEqual(len(schemas), 1)
        self.assertEqual(schemas[0]["name"], "check_order_status")
        self.assertIn("input_schema", schemas[0])

    def test_load_multiple_tools(self) -> None:
        schemas = load_schemas(["check_order_status", "validate_promo_code"])
        names = [s["name"] for s in schemas]
        self.assertIn("check_order_status", names)
        self.assertIn("validate_promo_code", names)

    def test_unknown_tool_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            load_schemas(["nonexistent_tool"])
        self.assertIn("nonexistent_tool", str(ctx.exception))

    def test_all_registry_tools_resolve(self) -> None:
        from helpbot.registry import INTENT_REGISTRY
        all_tool_names = {
            name
            for cfg in INTENT_REGISTRY.values()
            for name in cfg.get("tools", [])
        }
        schemas = load_schemas(list(all_tool_names))
        resolved_names = {s["name"] for s in schemas}
        self.assertEqual(all_tool_names, resolved_names)


class RunToolSecurityTests(unittest.TestCase):
    def setUp(self):
        _reset_loader()
        load_schemas(["check_order_status"])  # trigger load

    def test_protected_tool_blocked_without_session(self) -> None:
        result_json, is_error = run_tool("check_order_status", {"order_id": "PT-1001"})
        result = json.loads(result_json)
        self.assertTrue(result.get("needs_identity"))
        self.assertFalse(is_error)

    def test_protected_tool_allowed_with_session(self) -> None:
        set_session_email("john.doe@example.com")
        result_json, is_error = run_tool("check_order_status", {"order_id": "PT-1001"})
        result = json.loads(result_json)
        self.assertNotIn("needs_identity", result)

    def test_rate_limit_enforced(self) -> None:
        set_session_email("john.doe@example.com")
        for _ in range(loader_module._RATE_LIMIT):
            run_tool("check_order_status", {"order_id": "PT-1001"})
        result_json, is_error = run_tool("check_order_status", {"order_id": "PT-1001"})
        result = json.loads(result_json)
        self.assertTrue(result.get("error"))
        self.assertTrue(is_error)

    def test_unprotected_tool_runs_without_session(self) -> None:
        result_json, is_error = run_tool("validate_promo_code", {"code": "SUMMER20"})
        result = json.loads(result_json)
        self.assertTrue(result.get("found"))
        self.assertFalse(is_error)


if __name__ == "__main__":
    unittest.main()
