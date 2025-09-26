import os
from redis.asyncio import ConnectionPool, Redis

REDIS_URL = os.environ["REDIS_URL"]

redis_pool = ConnectionPool.from_url(
    REDIS_URL, decode_responses=True, socket_connect_timeout=5, socket_timeout=5
)

redis_client = Redis(connection_pool=redis_pool)
