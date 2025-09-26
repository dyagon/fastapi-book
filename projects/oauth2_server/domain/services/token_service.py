import uuid
import json
from secrets import token_urlsafe
from datetime import datetime, timedelta, timezone

from redis.asyncio import Redis
from jose import jwt, JWTError

from ..exception import UnauthorizedClientException


class TokenService:
    def __init__(self, redis_client: Redis, secret_key: str, algorithm: str):
        self.redis_client = redis_client
        self.prefix = "oauth2:token:"
        self.code_prefix = "oauth2:code:"
        self.secret_key = secret_key
        self.algorithm = algorithm

    def jwt_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def jwt_token_decode(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise UnauthorizedClientException("Invalid token")

    async def _set(self, prefix: str, key: str, value: dict, expires_delta: timedelta):
        value = json.dumps(value)
        await self.redis_client.set(prefix + key, value, expires_delta)

    async def _get(self, prefix: str, key: str) -> dict:
        value = await self.redis_client.get(prefix + key)
        if not value:
            return None
        return json.loads(value)

    async def _delete(self, prefix: str, key: str):
        await self.redis_client.delete(prefix + key)

    async def generate_code(self, data: dict, expires_delta: timedelta) -> str:
        code = str(uuid.uuid4())
        await self._set(self.code_prefix, code, data, expires_delta)
        return code

    async def get_code(self, code: str) -> dict:
        return await self._get(self.code_prefix, code)

    async def delete_code(self, code: str):
        await self._delete(self.code_prefix, code)

    async def opaque_token(self, data: dict, expires_delta: timedelta) -> str:
        token = token_urlsafe(32)
        await self._set(self.prefix, token, data, expires_delta)
        return token

    async def opaque_token_decode(self, token: str) -> dict:
        return await self._get(self.prefix, token)

    async def opaque_token_delete(self, token: str):
        await self._delete(self.prefix, token)
