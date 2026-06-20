import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://localhost/sportmeet"
    WHATSAPP_VERIFY_TOKEN: str = "sportmeet_token_123"
    WHATSAPP_API_TOKEN: str = "fake_token_for_now"
    WHATSAPP_PHONE_NUMBER_ID: str = "fake_phone_number_id"
    WHATSAPP_VERSION: str = "v19.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
