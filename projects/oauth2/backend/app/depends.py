from fastapi import Depends, Cookie, Request

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra import AppInfra, OAuthClient, DatabaseInfra, RedisInfra


async def get_infra(request: Request):
    return request.app.state.infra

async def get_oauth_client(infra: AppInfra = Depends(get_infra)) -> OAuthClient:
    return infra.oauth_client

async def get_async_db(infra: AppInfra = Depends(get_infra)) -> AsyncSession:
    async with infra.db.db_sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()
    
async def get_redis_client(infra: AppInfra = Depends(get_infra)) -> Redis:
    return infra.redis.get_redis()