from pydantic import BaseModel

from redis.asyncio import Redis

from fastapi_book import InfraRegistry
from fastapi_book.infra import DatabaseInfra, RedisInfra, RedisConfig


class InfraSettings(BaseModel):
    redis: RedisConfig


class AppInfra(InfraRegistry):

    def __init__(self, settings: InfraSettings):
        super().__init__()
        self.cfg = settings
        self.redis = RedisInfra(self.cfg.redis)
        self.register("redis", self.redis)

    def get_redis(self) -> Redis:
        return self.redis.get_redis()

