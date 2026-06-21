from pydantic import BaseModel
from typing import Literal

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class Conversation(BaseModel):
    messages: list[Message] = []

    def add_user(self, text: str) -> None:
        self.messages.append(Message(role="user", content=text))

    def add_assistant(self, text: str) -> None:
        self.messages.append(Message(role="assistant", content=text))

    def clear(self) -> None:
        self.messages.clear()

    def to_api_format(self) -> list[dict]:
        return [m.model_dump() for m in self.messages]
