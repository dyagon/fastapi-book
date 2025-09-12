# infra/db_mixin.py
from pydantic import BaseModel

from fastapi_book import BaseInfra

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

class DatabaseConfig(BaseModel):
    uri: str
    debug_echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class DatabaseInfra(BaseInfra):
    def __init__(self, db_cfg: DatabaseConfig):
        self._db_cfg = db_cfg
        self._db_engine: AsyncEngine | None = None
        self._db_sessionmaker: async_sessionmaker[AsyncSession] | None = None

    async def setup(self):
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

    async def shutdown(self):
        """关闭数据库引擎。"""
        if self._db_engine:
            print("Closing Database engine...")
            await self._db_engine.dispose()
            print("Database engine closed.")

    @property
    def db_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        """获取 SQLAlchemy 的 session 工厂。"""
        if not self._db_sessionmaker:
            raise Exception("DB sessionmaker not initialized. Call init_db() first.")
        return self._db_sessionmaker