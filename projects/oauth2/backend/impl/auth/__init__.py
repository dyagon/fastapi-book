import httpx
import time

from typing import Optional
import asyncio

from .oauth2.client_credentials import (
    OAuth2ClientCredentialsConfig,
    OAuth2ClientCredentialsClient,
)

from .oauth2.auth_code import (
    OAuth2AuthorizationCodeConfig,
    OAuth2AuthorizationCodeClient,
)

from .auth_strategy import AuthStrategy, ApiKeyAuth, OAuth2ClientCredentialsAuth

from .auth_client import AuthClient

from ...infra.security import generate_token


class ClientCredentialsClientConfig(OAuth2ClientCredentialsConfig):
    base_url: str


class ClientCredentialsClient:

    def __init__(self, client: httpx.AsyncClient, cfg: ClientCredentialsClientConfig):
        self._client = client
        self._oauth2_client = OAuth2ClientCredentialsClient(client, cfg)
        self._base_url = cfg.base_url
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()

    @property
    def _is_expired(self) -> bool:
        return time.time() > self._expires_at - 60  # add 60 seconds buffer

    async def get_token(self) -> str:
        async with self._lock:
            if self._access_token is None or self._is_expired:
                token_data = await self._oauth2_client.fetch_token()
                self._access_token = token_data["access_token"]
                self._expires_at = time.time() + token_data["expires_in"]
        return self._access_token

    async def get_client_info(self) -> dict:
        url = f"{self._base_url}/client"
        response = await self._client.get(
            url, headers={"Authorization": f"Bearer {await self.get_token()}"}
        )
        return response.json()


class AuthorizationCodeClientConfig(OAuth2AuthorizationCodeConfig):
    base_url: str
    

class AuthorizationCodeClient:
    def __init__(self, client: httpx.AsyncClient, cfg: AuthorizationCodeClientConfig):
        self._client = client
        self._oauth2_client = OAuth2AuthorizationCodeClient(client, cfg)
        self._base_url = cfg.base_url

    def create_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        if not state:
            state = generate_token()
        return self._oauth2_client.make_auth_url(state), state

    async def get_token(self, code: str) -> str:
        return await self._oauth2_client.exchange_code_for_tokens(code)

    async def refresh_token(self, refresh_token: str) -> str:
        return await self._oauth2_client.refresh_token(refresh_token)

    async def get_user_info(self) -> dict:
        url = f"{self._base_url}/userinfo"
        response = await self._client.get(
            url, headers={"Authorization": f"Bearer {await self.get_token()}"}
        )
        return response.json()
