import uuid
import time
from datetime import timedelta, datetime


from redis.asyncio import Redis


class TokenManager:

    def __init__(self, redis: Redis):
        self.redis = redis
        self.prefix = "oauth2:token:"
        self.code_prefix = "oauth2:code:"

    #### code ####
    async def generate_code(self, data: dict, ttl: int) -> str:
        code = str(uuid.uuid4())
        print(code)
        await self.redis.hset(self.code_prefix + code, mapping=data)
        await self.redis.expire(self.code_prefix + code, ttl)
        return code

    async def get_code(self, code: str) -> dict:
        return await self.redis.hgetall(self.code_prefix + code)

    async def delete_code(self, code: str):
        await self.redis.delete(self.code_prefix + code)

    #### opaque token ####
    async def generate_opaque_token(self, data: dict) -> str:
        token = str(uuid.uuid4())
        await self.redis.hset(self.prefix + token, mapping=data)
        return token

    async def get_opaque_token(self, token: str) -> dict:
        return await self.redis.hgetall(self.prefix + token)

    async def revoke_opaque_token(self, token: str):
        await self.redis.hset(self.prefix + token, "revoke_at", time.time())
