
# from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator


# metadata = MetaData()
class Base(DeclarativeBase):
    pass


from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # SALCHEMY CONFIG
    ASYNC_DATABASE_URI: str
    DB_DEBUG_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    # REDIS CONFIG
    REDIS_URL: str
    # TOKEN CONFIG
    TOKEN_SIGN_SECRET: str
    TOKEN_SIGN_ALGORITHM: str = "HS256"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=settings.DB_DEBUG_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# 创建异步的会话管理对象
SessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


from .utils import register_custom_docs