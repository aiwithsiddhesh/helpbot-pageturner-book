import inspect
import re
from abc import ABC, abstractmethod


def _to_snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Tool(ABC):
    properties: dict[str, str | dict]  # field: description or descriptor dict

    @property
    def schema(self) -> dict:
        props = getattr(self, "properties", {})
        sig = inspect.signature(self.run)
        required = [
            name for name, param in sig.parameters.items()
            if name not in ("self", "session_email")
            and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            and param.default is inspect.Parameter.empty
        ]
        prop_schemas = {}
        for field, desc in props.items():
            if isinstance(desc, dict):
                prop_schemas[field] = {"type": "string", **desc}
            else:
                prop_schemas[field] = {"type": "string", "description": desc}
        return {
            "name": _to_snake_case(type(self).__name__),
            "description": (type(self).__doc__ or "").strip(),
            "input_schema": {
                "type": "object",
                "properties": prop_schemas,
                "required": required,
            },
        }

    @abstractmethod
    def run(self, *args, session_email: str | None = None, **kwargs) -> dict:
        ...
