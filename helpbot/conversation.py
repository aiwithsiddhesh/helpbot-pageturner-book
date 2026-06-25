from pydantic import BaseModel
from typing import Literal

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str | list

class Conversation(BaseModel):
    messages: list[Message] = []

    def add_user(self, text: str) -> None:
        self.messages.append(Message(role="user", content=text))

    def add_assistant(self, text: str) -> None:
        self.messages.append(Message(role="assistant", content=text))
    
    def add_assistant_raw(self, content: list) -> None:
        """For tool_use turns — content is a list of blocks, not plain text."""
        self.messages.append(Message(role="assistant", content=content))

    def add_tool_results(self, results: list[dict]) -> None:
        """Appends all tool results for one turn as a single user message."""
        self.messages.append(Message(role="user", content=results))

    def clear(self) -> None:
        self.messages.clear()

    def to_api_format(self) -> list[dict]:
        serialised = [m.model_dump() for m in self.messages]
        # Cache the stable conversation prefix on the second-to-last user text message,
        # skipping tool_use and tool_result blocks so the pointer never lands on a tool turn.
        user_text_indices = [
            i for i, m in enumerate(serialised)
            if m["role"] == "user" and isinstance(m["content"], str)
        ]
        if len(user_text_indices) >= 2:
            target = serialised[user_text_indices[-2]]
            target["content"] = [{"type": "text", "text": target["content"], "cache_control": {"type": "ephemeral"}}]
        return serialised
