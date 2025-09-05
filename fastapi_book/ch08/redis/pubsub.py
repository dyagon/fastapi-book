# pubsub_manager.py
import asyncio
import redis.asyncio as redis
from typing import AsyncGenerator

class PubSubManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def publish(self, channel: str, message: str):
        """
        向指定频道发布一条消息。
        """
        print(f"--- [PubSub] Publishing to channel '{channel}': {message} ---")
        await self.redis_client.publish(channel, message)

    async def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        """
        订阅一个频道并作为一个异步生成器返回消息。
        这是一个长期运行的方法。
        """
        # 1. 创建一个 PubSub 对象
        pubsub_client = self.redis_client.pubsub()

        # 2. 订阅频道
        await pubsub_client.subscribe(channel)
        print(f"--- [PubSub] Subscribed to channel '{channel}' ---")

        # 3. 无限循环监听消息
        async for message in pubsub_client.listen():
            # 忽略订阅成功时的确认消息
            if message["type"] == "subscribe":
                continue
            print(message)

            # 检查消息数据是否存在
            if "data" in message:
                # pubsub 返回的数据是 bytes，需要解码
                yield message["data"]


if __name__ == "__main__":
    
    from redis.asyncio import Redis
    from fastapi_book.config import get_settings
    settings = get_settings()
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    pubsub_manager = PubSubManager(redis_client)

    async def main():
        # 启动订阅任务
        async def subscriber():
            async for msg in pubsub_manager.subscribe("my_channel"):
                print(f"Received message: {msg}")

        # 启动发布任务
        async def publisher():
            for i in range(5):
                await asyncio.sleep(2)
                await pubsub_manager.publish("my_channel", f"Hello {i}")
        await asyncio.gather(subscriber(), publisher())
    asyncio.run(main())