# src/fastapi_book/context.py
import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Depends, Request
from redis.asyncio import Redis, ConnectionPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from .config import get_settings
from .ch08.redis.cache import cache
from .ch08.redis.lock import lock_manager


class AppContext:
    redis_client: Redis | None = None
    db_session_factory: async_sessionmaker[AsyncSession] | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    ctx = AppContext()
    settings = get_settings()
    # Redis with configurable URL based on environment
    redis_url = settings.REDIS_URL
    redis_pool = ConnectionPool.from_url(
        redis_url,
        decode_responses=True,
        max_connections=20,
        socket_connect_timeout=5,  # 5 seconds timeout for connection
        socket_timeout=5,  # 5 seconds timeout for operations
    )
    ctx.redis_client = Redis(connection_pool=redis_pool)

    # Test Redis connection with better error handling
    try:
        await ctx.redis_client.ping()
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        raise

    cache.setup(ctx.redis_client, prefix="cache")
    lock_manager.setup(ctx.redis_client, prefix="dist-lock")

    # db
    async_engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)
    ctx.db_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

    app.state.app_context = ctx

    yield

    # 应用关闭时执行
    print("应用关闭，正在清理资源...")
    if ctx.redis_client:
        await ctx.redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()
    print("资源清理完成。")


async def get_app_context(request: Request) -> AppContext:
    print(
        "depends on get_app_context() called",
        threading.current_thread().name,
        threading.get_ident(),
    )
    return request.app.state.app_context


async def get_redis_client(ctx: AppContext = Depends(get_app_context)) -> Redis:
    print(
        "depends on get_redis_client() called",
        threading.current_thread().name,
        threading.get_ident(),
    )
    return ctx.redis_client


async def get_async_db(
    ctx: AppContext = Depends(get_app_context),
) -> AsyncGenerator[AsyncSession, None]:
    print(
        "depends on get_async_db() called",
        threading.current_thread().name,
        threading.get_ident(),
    )
    if not ctx.db_session_factory:
        raise RuntimeError("数据库 Session 工厂未初始化！")
    async with ctx.db_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
