# infra/db_mixin.py
from typing import AsyncGenerator
from pydantic import BaseModel
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from redis.asyncio import Redis, ConnectionPool

from httpx import AsyncClient


class DatabaseConfig(BaseModel):
    uri: str
    debug_echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class Database:
    def __init__(self, db_cfg: DatabaseConfig):
        self._db_cfg = db_cfg
        """初始化数据库引擎和 session 工厂。"""
        print("Initializing Database...")
        self._db_engine = create_async_engine(
            self._db_cfg.uri,
            echo=self._db_cfg.debug_echo,
            pool_size=self._db_cfg.pool_size,
            max_overflow=self._db_cfg.max_overflow,
        )
        self._db_sessionmaker = async_sessionmaker(
            self._db_engine, expire_on_commit=False
        )
        print("Database engine and session factory created.")

    async def close(self):
        """关闭数据库引擎。"""
        if self._db_engine:
            print("Closing Database engine...")
            await self._db_engine.dispose()
            print("Database engine closed.")

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        try:
            session: AsyncSession = self._session_factory()
            print(f"    -> (Factory) New ASYNC session created: {id(session)}")
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            print(f"    <- (Factory) ASYNC Session closed: {id(session)}")


class RedisConfig(BaseModel):
    url: str


async def get_redis_client(cfg: RedisConfig) -> AsyncGenerator[Redis, None]:
    pool = ConnectionPool.from_url(cfg.url, decode_responses=True)
    redis_client = Redis(connection_pool=pool)
    await redis_client.ping()
    print("Redis connection established.")
    yield redis_client
    await redis_client.close(close_connection_pool=True)
    print("Redis connection closed.")


async def get_async_client():
    client = AsyncClient()
    yield client
    await client.aclose()
