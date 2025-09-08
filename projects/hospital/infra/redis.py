

from redis.asyncio import ConnectionPool, Redis

from fastapi_book import get_settings

redis_pool = ConnectionPool.from_url(
        get_settings().REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,  # 5 seconds timeout for connection
        socket_timeout=5,  # 5 seconds timeout for operations
    )

redis_client = Redis(connection_pool=redis_pool)