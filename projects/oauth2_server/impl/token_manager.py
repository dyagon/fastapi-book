import uuid
import json
from secrets import token_urlsafe
from datetime import datetime, timedelta, timezone

from redis.asyncio import Redis
from jose import jwt, JWTError
from ..domain.exception import UnauthorizedClientException


SECRET_KEY = "0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
ALGORITHM = "HS256"


class TokenManager:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.prefix = "oauth2:token:"
        self.code_prefix = "oauth2:code:"

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

    
    def jwt_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def jwt_token_decode(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise UnauthorizedClientException("Invalid token")

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
