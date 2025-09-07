# 导入异步引擎的模块
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from contextlib import asynccontextmanager


# URL地址格式
from .config import get_settings

# 创建异步引擎对象
settings = get_settings()
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=settings.DB_DEBUG_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# 创建异步的会话管理对象
SessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


# 需要使用这个来装饰一下，才可以使用with
@asynccontextmanager
async def async_context_get_db() -> AsyncGenerator:
    """
        async def init() -> None:
        pass
        async with get_db() as session:
            result = await session.execute(select(Hospital))
            listsd = result.scalars().fetchall()
            print([itm.name for itm in listsd])
            # import asyncio
            # # asyncio.run(init())
            # loop = asyncio.get_event_loop()
            # loop.run_until_complete(init())
    :return:
    """
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as ex:
        await session.rollback()
        raise ex
    finally:
        await session.close()
