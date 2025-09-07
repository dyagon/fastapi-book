# 导入异步引擎的模块
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from redis.asyncio import ConnectionPool, Redis


from .utils import AuthToeknHelper

from fastapi_book import Base, get_settings

# 创建异步引擎对象
async_engine = create_async_engine(get_settings().ASYNC_DATABASE_URI, echo=False)
# 创建异步的会话管理对象
SessionLocal = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)


# redis
redis_pool = ConnectionPool.from_url(
        get_settings().REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,  # 5 seconds timeout for connection
        socket_timeout=5,  # 5 seconds timeout for operations
    )

print(redis_pool)
redis_client = Redis(connection_pool=redis_pool)
print(redis_client)

all = ["Base", "AuthToeknHelper", "SessionLocal", "get_settings", "redis_client"]