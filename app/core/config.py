from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    TELEGRAM_TOKEN: str
    CHAT_ID: int

    MIN_MOVE_PERCENT: float = Field(default=8)
    RSI_OVERBOUGHT: int = Field(default=80)
    RSI_OVERSOLD: int = Field(default=20)


settings = Settings()
