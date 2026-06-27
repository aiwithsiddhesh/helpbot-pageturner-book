import sys
import time
from dataclasses import dataclass, field
import anthropic
from pydantic import ValidationError

from helpbot import (
    Settings, HelpBot,
    Conversation,
    detect_intent,
    INTENT_REGISTRY,
)
from helpbot.tools import load_schemas, Session
from helpbot.chat import ChatResult
from helpbot.otp import generate_otp, send_otp


_INTENT_OPENERS: dict[str, str] = {
    intent: cfg["opener"]
    for intent, cfg in INTENT_REGISTRY.items()
    if cfg.get("opener")
}


@dataclass
class SessionStats:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    api_calls: int = 0

    def add(self, result: ChatResult, extra_calls: int = 0) -> None:
        self.input_tokens += result.input_tokens
        self.output_tokens += result.output_tokens
        self.cache_creation_tokens += result.cache_creation_tokens
        self.cache_read_tokens += result.cache_read_tokens
        self.api_calls += result.api_calls + extra_calls

    def print_summary(self) -> None:
        if self.api_calls == 0:
            return
        total = self.input_tokens + self.output_tokens
        print("\n── Session Summary ──────────────────────────────────")
        print(f"  API calls       : {self.api_calls:,}")
        print(f"  Input tokens    : {self.input_tokens:,}  (cache created: {self.cache_creation_tokens:,} | cache read: {self.cache_read_tokens:,})")
        print(f"  Output tokens   : {self.output_tokens:,}")
        print(f"  Total tokens    : {total:,}")
        print("─────────────────────────────────────────────────────")


def _run_otp_flow(settings: Settings, session: Session) -> None:
    email = input("Enter your email to verify identity (or press Enter to skip): ").strip()
    if not email:
        print("Continuing as guest. Some features will require identity verification.")
        return

    otp = generate_otp()
    otp_expiry = time.time() + 300  # 5 minutes

    sent = send_otp(email, otp, settings.brevo_api_key, settings.sender_email)
    if not sent:
        print("Could not send verification email. Continuing as guest.")
        return

    print(f"A verification code has been sent to {email}.")
    for attempt in range(3):
        code = input("Enter the code: ").strip()
        if time.time() > otp_expiry:
            print("Code has expired. Continuing as guest.")
            return
        if code == otp:
            session.set(email, verified=True)
            print("Identity verified.")
            return
        remaining = 2 - attempt
        if remaining > 0:
            print(f"Incorrect code. {remaining} attempt(s) remaining.")

    print("Too many failed attempts. Continuing as guest.")


def _bootstrap() -> tuple[HelpBot, Conversation, Session]:
    try:
        settings = Settings()
    except ValidationError:
        sys.exit("Error: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return HelpBot(settings=settings, client=client), Conversation(), Session()


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
    session: Session,
) -> ChatResult:
    intent = detect_intent(user_input, bot.settings, bot.client)
    temperature = INTENT_REGISTRY[intent].get("temperature", 0.1)
    tool_names = INTENT_REGISTRY[intent].get("tools", [])
    tools = load_schemas(tool_names) if tool_names else None
    conversation.add_user(user_input)
    print("HelpBot: ", end="", flush=True)
    opener = _INTENT_OPENERS.get(intent, "")
    result = bot.chat_streaming(conversation, session, opener=opener, temperature=temperature, tools=tools, intent=intent)
    total_calls = result.api_calls + 1  # +1 for detect_intent()
    cache_info = f", Cache Created: {result.cache_creation_tokens}, Cache Read: {result.cache_read_tokens}" if (result.cache_creation_tokens or result.cache_read_tokens) else ""
    print(f"(API Calls: {total_calls} | Input Tokens: {result.input_tokens}, Output Tokens: {result.output_tokens}, Total Tokens: {result.total_tokens}{cache_info})\n")
    return result


def main() -> None:
    bot, conversation, session = _bootstrap()
    stats = SessionStats()

    print("Welcome to HelpBot! Type 'exit' to quit.")
    _run_otp_flow(bot.settings, session)
    while True:
        user_input = input("You: ").strip()

        if _handle_command(user_input):
            break

        if user_input:
            result = _handle_message(user_input, bot, conversation, session)
            stats.add(result, extra_calls=1)  # +1 for detect_intent()

    stats.print_summary()


if __name__ == "__main__":
    main()
