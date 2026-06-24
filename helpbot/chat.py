from pydantic import BaseModel
import anthropic
from helpbot.config import Settings, SYSTEM_PROMPT
from helpbot.conversation import Conversation
from helpbot.tools import run_tool


class ChatResult(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class HelpBot:
    def __init__(self, settings: Settings, client: anthropic.Anthropic):
        self._client = client
        self._settings = settings

    @property
    def client(self) -> anthropic.Anthropic:
        return self._client

    @property
    def settings(self) -> Settings:
        return self._settings

    def _call(
        self,
        messages: list[dict],
        temperature: float,
        tools: list[dict] | None,
    ) -> anthropic.types.Message:
        with self._client.messages.stream(
            model=self._settings.model,
            max_tokens=self._settings.max_tokens,
            system=SYSTEM_PROMPT,
            temperature=temperature,
            messages=messages,
            **({"tools": tools} if tools else {}),
        ) as stream:
            for chunk in stream.text_stream:
                print(chunk, end="", flush=True)
            print()
            return stream.get_final_message()

    def chat_streaming(
        self,
        conversation: Conversation,
        opener: str = "",
        temperature: float = 0.1,
        tools: list[dict] | None = None,
    ) -> ChatResult:
        if opener:
            print(opener, end="", flush=True)
            conversation.add_assistant(opener)

        total_input = total_output = 0
        while True:
            final = self._call(conversation.to_api_format(), temperature, tools)
            total_input += final.usage.input_tokens
            total_output += final.usage.output_tokens

            if final.stop_reason == "tool_use":
                conversation.add_assistant_raw([b.model_dump() for b in final.content])
                [conversation.add_tool_result(b.id, *run_tool(b.name, b.input)) for b in final.content if b.type == "tool_use"]
            else:
                text = " ".join(b.text for b in final.content if b.type == "text")
                conversation.add_assistant(text)
                break

        return ChatResult(
            text=text,
            input_tokens=total_input,
            output_tokens=total_output,
            total_tokens=total_input + total_output,
        )
