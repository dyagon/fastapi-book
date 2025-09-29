import uuid
import json
import time
from secrets import token_urlsafe
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ValidationError
from redis.asyncio import Redis
from jose import jwt, JWTError

from ..exception import UnauthorizedClientException

from ...impl.token_manager import TokenManager


class TokenInfo(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    scope: str
    jti: str | None = None


class RefreshTokenInfo(BaseModel):
    user_id: str
    client_id: str
    scopes: str
    expires_at: int
    created_at: int
    revoke_at: int | None = None

    def is_expired(self) -> bool:
        return int(time.time()) > self.expires_at


class TokenService:

    def __init__(
        self,
        token_manager: TokenManager,
        secret_key: str,
        algorithm: str,
        iss: str,
        aud: str,
    ):
        self.token_manager = token_manager
        self.prefix = "oauth2:token:"
        self.code_prefix = "oauth2:code:"
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.iss = iss
        self.aud = aud
        self.code_ttl = 5 * 60  # 5 minutes
        self.access_token_ttl = 15 * 60  # 15 minutes
        self.refresh_token_ttl = 7 * 24 * 60 * 60  # 7 days

    def _access_token(self, sub: str, scope: str) -> str:
        token = {
            "sub": sub,
            "scope": scope,
            "iat": int(time.time()),
            "exp": int(time.time()) + self.access_token_ttl,
        }
        return jwt.encode(token, self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError | ValidationError:
            raise UnauthorizedClientException("Invalid token")

    async def _refresh_token(self, sub: str, scope: str, client_id: str) -> str:
        token = {
            "user_id": sub,
            "client_id": client_id,
            "scopes": scope,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + self.refresh_token_ttl,
        }
        return await self.token_manager.generate_opaque_token(token)

    async def generate_token(
        self, sub: str, scope: str, client_id: str | None = None
    ) -> dict:
        token = {
            "access_token": self._access_token(sub, scope),
            "expires_in": self.access_token_ttl,
            "token_type": "Bearer",
            "scope": scope,
        }
        if client_id:
            token["refresh_token"] = await self._refresh_token(sub, scope, client_id)
        return token

    async def refresh_token(self, refresh_token: str) -> dict:
        token_info = await self.token_manager.get_opaque_token(refresh_token)
        print("refresh token info", token_info)
        if not token_info:
            raise UnauthorizedClientException("Invalid refresh token")
        token_info = RefreshTokenInfo.model_validate(token_info)
        if token_info.is_expired():
            raise UnauthorizedClientException("Refresh token expired")
        if token_info.revoke_at:
            raise UnauthorizedClientException("Refresh token revoked")
        await self.token_manager.revoke_opaque_token(refresh_token)

        token = {
            "access_token": self._access_token(token_info.user_id, token_info.scopes),
            "expires_in": self.access_token_ttl,
            "token_type": "Bearer",
            "scope": token_info.scopes,
        }
        if token_info.client_id:
            token["refresh_token"] = await self._refresh_token(
                token_info.user_id, token_info.scopes, token_info.client_id
            )
        return token

    async def generate_code(self, data: dict) -> str:
        return await self.token_manager.generate_code(data, self.code_ttl)

    async def get_code(self, code: str) -> dict:
        return await self.token_manager.get_code(code)

    async def delete_code(self, code: str):
        await self.token_manager.delete_code(code)
