import sys
import anthropic
from pydantic import ValidationError

from helpbot import (
    Settings, HelpBot,
    Conversation,
    detect_intent,
    INTENT_REGISTRY,
)
from helpbot.tools import load_schemas


_INTENT_OPENERS: dict[str, str] = {
    intent: cfg["opener"]
    for intent, cfg in INTENT_REGISTRY.items()
    if cfg["opener"]
}


def _bootstrap() -> tuple[HelpBot, Conversation]:
    try:
        settings = Settings()
    except ValidationError:
        sys.exit("Error: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return HelpBot(settings=settings, client=client), Conversation()


def _handle_command(user_input: str) -> bool:
    if not user_input:
        print("Please enter a valid question.")
        return False
    if user_input.lower() == "exit":
        print("Goodbye!")
        return True
    return False


def _handle_message(
    user_input: str,
    bot: HelpBot,
    conversation: Conversation,
) -> None:
    intent = detect_intent(user_input, bot.settings, bot.client)
    temperature = INTENT_REGISTRY[intent].get("temperature", 0.1)
    tool_names = INTENT_REGISTRY[intent].get("tools", [])
    tools = load_schemas(tool_names) if tool_names else None
    conversation.add_user(user_input)
    print("HelpBot: ", end="", flush=True)
    opener = _INTENT_OPENERS.get(intent, "")
    result = bot.chat_streaming(conversation, opener=opener, temperature=temperature, tools=tools)
    total_calls = result.api_calls + 1  # +1 for detect_intent()
    cache_info = f", Cache Created: {result.cache_creation_tokens}, Cache Read: {result.cache_read_tokens}" if (result.cache_creation_tokens or result.cache_read_tokens) else ""
    print(f"(API Calls: {total_calls} | Input Tokens: {result.input_tokens}, Output Tokens: {result.output_tokens}, Total Tokens: {result.total_tokens}{cache_info})\n")


def main() -> None:
    bot, conversation = _bootstrap()

    print("Welcome to HelpBot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()

        if _handle_command(user_input):
            break

        if user_input:
            _handle_message(user_input, bot, conversation)


if __name__ == "__main__":
    main()
