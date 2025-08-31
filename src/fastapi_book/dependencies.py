from typing import AsyncGenerator

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from .context import AppContext


def get_app_context(request: Request) -> AppContext:
    return request.app.state.app_context


def get_redis_client(ctx: AppContext = Depends(get_app_context)) -> Redis:
    return ctx.redis_client


async def get_async_db(
    ctx: AppContext = Depends(get_app_context),
) -> AsyncGenerator[AsyncSession, None]:
    if not ctx.db_session_factory:
        raise RuntimeError("数据库 Session 工厂未初始化！")
    async with ctx.db_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
