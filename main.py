import sys
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


def main() -> None:
    try:
        settings = Settings()
    except ValidationError:
        sys.exit("Error: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
    
    bot = HelpBot(settings = settings)
    conversation = Conversation()

    print("Welcome to HelpBot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()

        if not user_input:
            print("Please enter a valid question.")
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        if user_input.startswith("/temp "):
            try:
                new_temp = float(user_input.split()[1])
                settings = Settings(
                    anthropic_api_key=settings.anthropic_api_key,
                    model=settings.model,
                    max_tokens=settings.max_tokens,
                    temperature=new_temp
                )
                bot = HelpBot(settings)
                print(f"[Temperature set to {new_temp}]\n")
            except (ValueError, IndexError):
                print("[Valid Usage: /temp 0.0 to 1.0]\n")
            continue

        # Detect intent and extract structured fields before responding
        intent = detect_intent(user_input, settings)
        extractor = INTENT_EXTRACTOR_MAP.get(intent)
        if extractor:
            extracted = extractor(user_input, settings)
            print(f"[Intent: {intent}] {extracted}")
        
        conversation.add_user(user_input)
        print("HelpBot: ", end="", flush=True)
        opener = _INTENT_OPENERS.get(intent, "")
        result = bot.chat_streaming(conversation, opener=opener)
        print(f"(Input Tokens: {result.input_tokens}, Output Tokens: {result.output_tokens}, Total Tokens: {result.total_tokens})\n")


if __name__ == "__main__":
    main()
