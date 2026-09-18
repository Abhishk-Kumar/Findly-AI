from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Findly AI Research Engine"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API Keys
    GROQ_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./findly_research.db"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    # Pipeline Defaults
    DEFAULT_QUALITY_BAR: int = 7
    MAX_REVISION_CYCLES: int = 3
    MAX_SEARCH_RESULTS: int = 6
    MAX_SOURCES_TO_SCRAPE: int = 3
    SCRAPE_TIMEOUT_SECONDS: int = 12


@lru_cache()
def get_settings() -> Settings:
    return Settings()
