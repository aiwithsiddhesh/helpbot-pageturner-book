from __future__ import annotations

import importlib
from pathlib import Path

_TOOLS_DIR = Path(__file__).parent
_cache: dict[str, object] = {}


def _get_module(name: str):
    if name not in _cache:
        py_path = _TOOLS_DIR / f"{name}.py"
        if not py_path.exists():
            raise FileNotFoundError(f"No tool file found for '{name}'")
        _cache[name] = importlib.import_module(f"helpbot.tools.{name}")
    return _cache[name]


def load_schemas(tool_names: list[str]) -> list[dict]:
    return [getattr(_get_module(name), "SCHEMA") for name in tool_names]


def run_tool(name: str, input: dict) -> tuple[str, bool]:
    try:
        module = _get_module(name)
        fn = getattr(module, name)
        result = fn(**input)
        print(f"[Tool called: {name}({input})]")
        return str(result), False
    except Exception as e:
        return f"Tool '{name}' error: {e}", True
