# infra/redis_mixin.py
from pydantic import BaseModel
from redis.asyncio import Redis, ConnectionPool

from fastapi_book import BaseInfra

class RedisConfig(BaseModel):
    url: str

class RedisInfra(BaseInfra):
    def __init__(self, cfg: RedisConfig):
        self._cfg = cfg
        self._redis_pool: ConnectionPool | None = None
        self._redis_client: Redis | None = None

    async def setup(self):
        """初始化 Redis 连接。"""
        print("Initializing Redis...")
        pool = ConnectionPool.from_url(
            self._cfg.url, decode_responses=True
        )
        self._redis_client = Redis(connection_pool=pool)
        # 简单地 Ping 一下，确保连接成功
        await self._redis_client.ping()
        print("Redis connection established.")

    async def shutdown(self):
        """关闭 Redis 连接。"""
        if self._redis_client:
            print("Closing Redis connection...")
            await self._redis_client.close()
            print("Redis connection closed.")

    def get_redis(self) -> Redis:
        """获取 Redis 客户端实例。"""
        if not self._redis_client:
            raise Exception("Redis client not initialized. Call init_redis() first.")
        return self._redis_client
