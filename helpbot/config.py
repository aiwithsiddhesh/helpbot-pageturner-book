import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    model: str = "claude-haiku-4-5"
    max_tokens: int = 1000

    @classmethod
    def from_env(cls) -> 'Settings':
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
        return cls(anthropic_api_key=api_key)
