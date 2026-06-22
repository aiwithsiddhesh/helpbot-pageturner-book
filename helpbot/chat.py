from pydantic import BaseModel
import anthropic
from helpbot.config import Settings, SYSTEM_PROMPT
from helpbot.conversation import Conversation


class ChatResult(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class HelpBot:
    def __init__(self, settings: Settings, client: anthropic.Anthropic):
        self._client = client
        self._settings = settings
    
    def chat(self, conversation: Conversation, temperature: float = 0.1) -> ChatResult:
        # Blocking call — waits for the full response before returning.
        # Not used by main.py after Module 3 (chat_streaming() takes over),
        # but kept here deliberately for two learning reasons:
        #   1. Shows the before/after contrast — you can call both and compare behaviour.
        #   2. In real projects, blocking calls are still useful for things like
        #      automated tests, batch processing, or any context where you don't
        #      need live output and just want the result as a value.
        # ChatResult and chat() together are the simplest possible API call pattern.
        # chat_streaming() is the production UX pattern. Both are worth knowing.
        response = self._client.messages.create(
            model=self._settings.model,
            messages=conversation.to_api_format(),
            max_tokens=self._settings.max_tokens,
            system=SYSTEM_PROMPT,
            temperature=temperature,
        )
        return ChatResult(
            text=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens
        )
    
    def chat_streaming(self, conversation: Conversation, opener: str = "", temperature: float = 0.1) -> ChatResult:
      messages = conversation.to_api_format()
      if opener:
          messages.append({"role": "assistant", "content": opener})

      with self._client.messages.stream(
          model=self._settings.model,
          messages=messages,
          max_tokens=self._settings.max_tokens,
          system=SYSTEM_PROMPT,
          temperature=temperature,
      ) as stream:
          if opener:
              print(opener, end="", flush=True)  # print opener before chunks arrive
          for chunk in stream.text_stream:
              print(chunk, end="", flush=True)
          print()
          final = stream.get_final_message()

      full_text = opener + final.content[0].text
      conversation.add_assistant(full_text)
      return ChatResult(
          text=full_text,
          input_tokens=final.usage.input_tokens,
          output_tokens=final.usage.output_tokens,
          total_tokens=final.usage.input_tokens + final.usage.output_tokens,
      )
