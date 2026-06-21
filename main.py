import sys
from helpbot import Settings, HelpBot
from pydantic import ValidationError


def main() -> None:
    try:
        settings = Settings()
    except ValidationError:
        sys.exit("Error: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
    
    bot = HelpBot(settings = settings)
    print("Welcome to HelpBot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            print("Please enter a valid question.")
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        result = bot.chat(user_input)
        print(f"HelpBot: {result.text}")
        print(f"(Input Tokens: {result.input_tokens}, Output Tokens: {result.output_tokens}, Total Tokens: {result.total_tokens})\n")



if __name__ == "__main__":
    main()
