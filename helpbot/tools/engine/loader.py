from __future__ import annotations

import importlib
import json
from datetime import datetime
from pathlib import Path

from helpbot.tools.engine.base import Tool
from helpbot.tools.engine.session import Session

_REGISTRY: dict[str, Tool] = {}
_LOADED = False

_PROTECTED_TOOLS = {
    "check_order_status", "cancel_order", "check_return_eligibility",
    "get_refund_status", "get_account_status", "get_loyalty_status",
    "get_digital_purchase", "resend_download_link",
}
_AUDIT_LOG = Path(__file__).parent.parent.parent.parent / "audit.log"


def _audit(tool_name: str, input: dict, session_email: str | None, outcome: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    identity = session_email or "guest"
    line = f"[{timestamp}] {identity} | {tool_name} | {json.dumps(input)} | {outcome}\n"
    with open(_AUDIT_LOG, "a") as f:
        f.write(line)


def _load_all() -> None:
    global _LOADED
    if _LOADED:
        return
    catalog_dir = Path(__file__).parent.parent / "tools_catalog"
    for path in catalog_dir.glob("*.py"):
        if path.stem == "__init__":
            continue
        importlib.import_module(f"helpbot.tools.tools_catalog.{path.stem}")
    for cls in _all_subclasses(Tool):
        instance = cls()
        _REGISTRY[instance.schema["name"]] = instance
    _LOADED = True


def _all_subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _all_subclasses(sub)


def load_schemas(tool_names: list[str]) -> list[dict]:
    _load_all()
    missing = [n for n in tool_names if n not in _REGISTRY]
    if missing:
        raise ValueError(f"Unknown tool(s) referenced in registry.toml: {missing}. Check tools_catalog/ for missing implementations.")
    return [_REGISTRY[name].schema for name in tool_names]


def run_tool(name: str, input: dict, session: Session) -> tuple[str, bool]:
    _load_all()

    is_protected = name in _PROTECTED_TOOLS

    if is_protected:
        if not session.is_valid():
            session.expire()
            _audit(name, input, None, "needs_identity")
            return json.dumps({"needs_identity": True, "message": "Please verify your identity before I can access your account details."}), False

        if session.rate_limit_reached():
            _audit(name, input, session.email, "rate_limited")
            return json.dumps({"error": True, "message": "Too many requests in this session. Please contact support."}), True

        session.increment_rate()

    try:
        tool = _REGISTRY[name]
        result = tool.run(**input, session_email=session.email)
        if name == "set_customer_identity" and result.get("success") and result.get("_email"):
            session.set(result["_email"], verified=False)
        outcome = "denied" if result.get("access_denied") else "granted"
        _audit(name, input, session.email, outcome)
        print(f"[Tool called: {name}({input})]")
        return json.dumps(result), False
    except KeyError:
        return f"Tool '{name}' not found.", True
    except Exception as e:
        return f"Tool '{name}' error: {e}", True
