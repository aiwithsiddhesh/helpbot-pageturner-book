from __future__ import annotations

import importlib
import json
from pathlib import Path

from helpbot.tools.engine.base import Tool

_REGISTRY: dict[str, Tool] = {}
_LOADED = False


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


def run_tool(name: str, input: dict) -> tuple[str, bool]:
    _load_all()
    try:
        tool = _REGISTRY[name]
        result = tool.run(**input)
        print(f"[Tool called: {name}({input})]")
        return json.dumps(result), False
    except KeyError:
        return f"Tool '{name}' not found.", True
    except Exception as e:
        return f"Tool '{name}' error: {e}", True
