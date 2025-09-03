from pydantic_settings import BaseSettings

from functools import lru_cache

class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./short.db"
    TOKEN_SIGN_SECRET: str = "abc123!@#"

@lru_cache
def get_settings() -> Settings:
    return Settings()