import re
from abc import ABC, abstractmethod


def _to_snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Tool(ABC):
    properties: dict[str, str]  # field: description

    @property
    def schema(self) -> dict:
        props = getattr(self, "properties", {})
        return {
            "name": _to_snake_case(type(self).__name__),
            "description": (type(self).__doc__ or "").strip(),
            "input_schema": {
                "type": "object",
                "properties": {
                    field: {"type": "string", "description": desc}
                    for field, desc in props.items()
                },
                "required": list(props.keys()),
            },
        }

    @abstractmethod
    def run(self, *args, session_email: str | None = None, **kwargs) -> dict:
        ...
