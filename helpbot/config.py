from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", frozen=True)

    anthropic_api_key: str
    model: str = "claude-haiku-4-5"
    max_tokens: int = Field(default=1000, gt=0)
