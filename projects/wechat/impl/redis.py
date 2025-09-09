from redis.asyncio import Redis

from typing import Any

from ..infra import redis_client

class CacheManager:

    def __init__(self, redis_client: Redis, prefix: str = "wechat"):
        self.redis_client = redis_client

    def _get_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    def put(self, key: str, value: Any, expire: int = 3600):
        self.redis_client.set(self._get_key(key), value, ex=expire)

    def get(self, key: str) -> Any:
        return self.redis_client.get(self._get_key(key))

    def delete(self, key: str):
        self.redis_client.delete(self._get_key(key))

    def exists(self, key: str) -> bool:
        return self.redis_client.exists(self._get_key(key))



cache = CacheManager(redis_client)