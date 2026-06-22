import sys
import anthropic
from pydantic import ValidationError

from helpbot import Settings, HelpBot, Conversation, detect_intent, INTENT_EXTRACTOR_MAP


_INTENT_OPENERS: dict[str, str] = {
    "return_request":      "I'm sorry to hear that. Let me help you sort this out!",
    "complaint":           "I sincerely apologise for the trouble you've experienced.",
    "order_wrong_item":    "I'm sorry you received the wrong item — let's fix that right away.",
    "order_missing_item":  "I apologise that part of your order is missing.",
    "refund_status":       "I understand waiting for a refund is frustrating.",
    "account_login_issue": "I'm sorry you're having trouble accessing your account.",
}


def _bootstrap() -> tuple[anthropic.Anthropic, HelpBot, Conversation, Settings]:
    try:
        settings = Settings()
    except ValidationError:
        sys.exit("Error: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    bot = HelpBot(settings=settings, client=client)
    return client, bot, Conversation(), settings


def _handle_command(user_input: str, temperature: float) -> tuple[float | None, bool]:
    """Handle slash commands and control inputs. Returns (new_temperature, should_exit)."""
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
    return None, False  # None signals: not a command, proceed to chat


def _handle_message(
    user_input: str,
    bot: HelpBot,
    conversation: Conversation,
    settings: Settings,
    client: anthropic.Anthropic,
    temperature: float,
) -> None:
    intent = detect_intent(user_input, settings, client)
    extractor = INTENT_EXTRACTOR_MAP.get(intent)
    if extractor:
        extracted = extractor(user_input, settings, client)
        print(f"[Intent: {intent}] {extracted}")

    conversation.add_user(user_input)
    print("HelpBot: ", end="", flush=True)
    opener = _INTENT_OPENERS.get(intent, "")
    result = bot.chat_streaming(conversation, opener=opener, temperature=temperature)
    print(f"(Input Tokens: {result.input_tokens}, Output Tokens: {result.output_tokens}, Total Tokens: {result.total_tokens})\n")


def main() -> None:
    client, bot, conversation, settings = _bootstrap()
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

        _handle_message(user_input, bot, conversation, settings, client, temperature)


if __name__ == "__main__":
    main()
