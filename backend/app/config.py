from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Rowing Coach Booking API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./rowing.db"
    directus_url: str = "http://localhost:8055"
    directus_token: str = ""
    ollama_base_url: str = "http://localhost:11434"

    booking_confirmation_timeout_hours: int = 24
    max_training_history: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()