from pydantic import Field, field_validator, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", frozen=True)

    anthropic_api_key: str
    model: str = "claude-haiku-4-5"
    max_tokens: int = Field(default=1000, gt=0)
    brevo_api_key: str = ""
    sender_email: EmailStr = ""

    @field_validator("model")
    @classmethod
    def must_be_claude(cls, v: str) -> str:
        if not v.startswith("claude-"):
            raise ValueError(f"model must be a Claude model ID (got {v!r})")
        return v
