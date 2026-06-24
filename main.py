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


def _handle_command(user_input: str, temperature: float) -> tuple[float | None, bool]:
    if not user_input:
        print("Please enter a valid question.")
        return temperature, False
    if user_input.lower() == "exit":
        print("Goodbye!")
        return temperature, True
    if user_input.startswith("/temp "):
        try:
            new_temp = float(user_input.split()[1])
            if not 0.0 <= new_temp <= 1.0:
                raise ValueError
            print(f"[Temperature set to {new_temp}]\n")
            return new_temp, False
        except (ValueError, IndexError):
            print("[Valid Usage: /temp 0.0 to 1.0]\n")
        return temperature, False
    return None, False


def _handle_message(
    user_input: str,
    bot: HelpBot,
    conversation: Conversation,
    temperature: float,
) -> None:
    intent = detect_intent(user_input, bot.settings, bot.client)
    tool_names = INTENT_REGISTRY[intent].get("tools", [])
    tools = load_schemas(tool_names) if tool_names else None
    conversation.add_user(user_input)
    print("HelpBot: ", end="", flush=True)
    opener = _INTENT_OPENERS.get(intent, "")
    result = bot.chat_streaming(conversation, opener=opener, temperature=temperature, tools=tools)
    total_calls = result.api_calls + 1  # +1 for detect_intent()
    print(f"(API Calls: {total_calls} | Input Tokens: {result.input_tokens}, Output Tokens: {result.output_tokens}, Total Tokens: {result.total_tokens})\n")


def main() -> None:
    bot, conversation = _bootstrap()
    temperature: float = 0.1

    print("Welcome to HelpBot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()

        new_temp, should_exit = _handle_command(user_input, temperature)
        if should_exit:
            break
        if new_temp is not None:
            temperature = new_temp
            continue

        _handle_message(user_input, bot, conversation, temperature)


if __name__ == "__main__":
    main()
