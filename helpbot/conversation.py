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

    def add_tool_result(self, tool_use_id: str, content: str, is_error: bool = False) -> None:
        """Appends a user-role tool_result message back to Claude."""
        self.messages.append(Message(
            role="user",
            content=[{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": content,
                "is_error": is_error,
            }]
        ))

    def clear(self) -> None:
        self.messages.clear()

    def to_api_format(self) -> list[dict]:
        return [m.model_dump() for m in self.messages]
