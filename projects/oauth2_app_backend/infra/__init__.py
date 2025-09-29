from dotenv import load_dotenv

load_dotenv()


from httpx import AsyncClient
from redis.asyncio import Redis

from .redis import redis_client
from .db import (
    engine,
    transactional_session,
    read_only_session,
    Repository,
)




class AppInfra:
    def __init__(self):
        self.async_client = AsyncClient()
        self.redis_client = redis_client
        self.engine = engine

    def get_async_client(self) -> AsyncClient:
        return self.async_client

    def get_redis_client(self) -> Redis:
        return self.redis_client


    async def dispose(self):
        print("Disposing infra...")
        if self.async_client:
            print("Disposing async client...")
            await self.async_client.aclose()
        if self.redis_client:
            print("Disposing redis client...")
            await self.redis_client.aclose()
        if self.engine:
            print("Disposing engine...")
            await self.engine.dispose()
        print("Infra disposed")

infra = AppInfra()



__all__ = [
    "infra",
    "Repository",
    "transactional_session",
    "read_only_session",
]
