from contextlib import asynccontextmanager
from fastapi import FastAPI

import redis.asyncio as redis

# In a file like `app/context.py`
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from .db import ASYNC_DATABASE_URL
from .cache import cache
from .redis_config import get_redis_url_for_environment, redis_config

class AppContext:
    redis_client: Redis | None = None
    db_session_factory: async_sessionmaker[AsyncSession] | None = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    
    ctx = AppContext()
    # Redis with configurable URL based on environment
    redis_url = get_redis_url_for_environment()
    print(f"Connecting to Redis: {redis_url.replace(':redis_password', ':***')}")  # Hide password in logs
    
    redis_pool = redis.ConnectionPool.from_url(
        redis_url,
        **redis_config.get_connection_kwargs()
    )
    ctx.redis_client = redis.Redis(connection_pool=redis_pool)
    
    # Test Redis connection with better error handling
    try:
        await ctx.redis_client.ping()
        print("✅ Redis 连接池已初始化。")
    except redis.AuthenticationError:
        print("❌ Redis 认证失败，请检查密码配置")
        raise
    except redis.ConnectionError:
        print("❌ Redis 连接失败，请检查 Redis 服务是否运行")
        raise
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        raise

    cache.setup(ctx.redis_client)

    # db
    async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
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
