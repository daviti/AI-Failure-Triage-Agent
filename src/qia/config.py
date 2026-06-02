from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str
    model: str = "claude-opus-4-8"
    max_tokens: int = 8192
    effort: str = "high"


settings = Settings()  # type: ignore[call-arg]
