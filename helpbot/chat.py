from pydantic import BaseModel
import anthropic
from helpbot.config import Settings, SYSTEM_PROMPT
from helpbot.conversation import Conversation
from helpbot.tools import run_tool
from helpbot.utils import _with_retry


class ChatResult(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    api_calls: int
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0


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
        cached_system = [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}]

        cached_tools = None
        if tools:
            cached_tools = tools[:-1] + [{**tools[-1], "cache_control": {"type": "ephemeral"}}]

        def _do_call():
            with self._client.messages.stream(
                model=self._settings.model,
                max_tokens=self._settings.max_tokens,
                system=cached_system,
                temperature=temperature,
                messages=messages,
                **({"tools": cached_tools} if cached_tools else {}),
            ) as stream:
                for chunk in stream.text_stream:
                    print(chunk, end="", flush=True)
                print()
                return stream.get_final_message()

        return _with_retry(_do_call)

    def chat_streaming(
        self,
        conversation: Conversation,
        opener: str = "",
        temperature: float = 0.1,
        tools: list[dict] | None = None,
    ) -> ChatResult:
        MAX_TOOL_ROUNDS = 10
        total_input = total_output = api_calls = rounds = 0
        total_cache_creation = total_cache_read = 0
        while True:
            if rounds >= MAX_TOOL_ROUNDS:
                raise RuntimeError(f"Tool-use loop exceeded {MAX_TOOL_ROUNDS} rounds — possible model loop.")
            rounds += 1
            final = self._call(conversation.to_api_format(), temperature, tools)
            total_input += final.usage.input_tokens
            total_output += final.usage.output_tokens
            total_cache_creation += getattr(final.usage, "cache_creation_input_tokens", 0) or 0
            total_cache_read += getattr(final.usage, "cache_read_input_tokens", 0) or 0
            api_calls += 1

            if final.stop_reason == "tool_use":
                conversation.add_assistant_raw([b.model_dump() for b in final.content])
                [conversation.add_tool_result(b.id, *run_tool(b.name, b.input)) for b in final.content if b.type == "tool_use"]
            else:
                text = " ".join(b.text for b in final.content if b.type == "text")
                if final.stop_reason == "max_tokens":
                    text += "\n\n*(Response was cut off — please ask me to continue.)*"
                if opener:
                    text = opener + " " + text
                conversation.add_assistant(text)
                break

        return ChatResult(
            text=text,
            input_tokens=total_input,
            output_tokens=total_output,
            total_tokens=total_input + total_output,
            api_calls=api_calls,
            cache_creation_tokens=total_cache_creation,
            cache_read_tokens=total_cache_read,
        )
