from pydantic import BaseModel
import anthropic
from helpbot import Settings, SYSTEM_PROMPT

class ChatResult(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int

class HelpBot:
    def __init__(self, settings: Settings):
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._settings = settings
    
    def chat(self, messages: list) -> ChatResult:
        response = self._client.messages.create(
            model=self._settings.model,
            messages=messages,
            max_tokens=self._settings.max_tokens,
            system=SYSTEM_PROMPT,
            temperature=self._settings.temperature,
        )
        return ChatResult(
            text=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens
        )
