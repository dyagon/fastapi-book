import threading

from typing import AsyncGenerator

from fastapi import Request, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from .context import AppContext

async def get_app_context(request: Request) -> AsyncGenerator[AppContext, None]:
    print(
        "depends on get_app_context() called",
        threading.current_thread().name,
        threading.get_ident(),
    )
    yield request.app.state.app_context


async def get_redis_client(ctx: AppContext = Depends(get_app_context)) -> AsyncGenerator[Redis, None]:
    print(
        "depends on get_redis_client() called",
        threading.current_thread().name,
        threading.get_ident(),
    )
    yield ctx.redis_client


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
