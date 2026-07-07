import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    google_api_key: str = ""
    google_model: str = "gemini-2.5-flash"

    aladhan_base_url: str = "https://api.aladhan.com/v1"

    prayer_window_minutes: int = 20
    milestone_target: int = 50


settings = Settings()

# google-genai (used internally by google-adk) reads GOOGLE_API_KEY straight from
# the process environment rather than from our Settings object, so make sure it's there.
if settings.google_api_key:
    os.environ.setdefault("GOOGLE_API_KEY", settings.google_api_key)
