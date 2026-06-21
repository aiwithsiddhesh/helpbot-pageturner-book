from pydantic import BaseModel
import anthropic
from helpbot import Settings

class ChatResult(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int

class HelpBot:
    def __init__(self, settings: Settings):
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._settings = settings
    
    def chat(self, user_input: str) -> ChatResult:
        response = self._client.messages.create(
            model=self._settings.model,
            messages=[{"role": "user", "content": user_input}],
            max_tokens=self._settings.max_tokens
        )
        return ChatResult(
            text=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens
        )
