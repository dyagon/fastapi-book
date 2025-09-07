from pydantic_settings import BaseSettings

from functools import lru_cache

class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./short.db"
    TOKEN_SIGN_SECRET: str = "abc123!@#"

@lru_cache
def get_settings() -> Settings:
    return Settings()



from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


async_engine = create_async_engine(get_settings().ASYNC_DATABASE_URL, echo=False)


SessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

from fastapi_book import Base

all = ["Base", "SessionLocal", "get_settings", "async_engine"]