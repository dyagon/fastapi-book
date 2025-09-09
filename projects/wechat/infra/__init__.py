import logging
from fastapi_book import Base, get_settings, SessionLocal

from .config import config


from redis.asyncio import ConnectionPool, Redis

# redis
redis_pool = ConnectionPool.from_url(
        get_settings().REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,  # 5 seconds timeout for connection
        socket_timeout=5,  # 5 seconds timeout for operations
    )

redis_client = Redis(connection_pool=redis_pool)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)