# src/fastapi_book/context.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis, ConnectionPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from .config import get_settings
from .redis.cache import cache
from .redis.lock import lock_manager


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

