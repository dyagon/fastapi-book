from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):

    ASYNC_DATABASE_URI: str
    DB_DEBUG_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    REDIS_URL: str

    TOKEN_SIGN_SECRET: str
    TOKEN_SIGN_ALGORITHM: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()
