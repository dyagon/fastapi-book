import httpx
import asyncio
import time

from typing import Optional


from .oauth2.client_credentials import (
    OAuth2ClientCredentialsConfig,
    OAuth2ClientCredentialsClient,
)

from .oauth2.auth_code import (
    OAuth2AuthorizationCodeConfig,
    OAuth2AuthorizationCodeClient,
)

from .utils import generate_token

from .exceptions import (
    OAuthError,
    MissingRequestTokenError,
    MissingTokenError,
    TokenExpiredError,
    InvalidTokenError,
    UnsupportedTokenTypeError,
    MismatchingStateError,
)

from .dto import Token, UserInfoDto


class ClientCredentialsClientConfig(OAuth2ClientCredentialsConfig):
    base_url: str


class ClientCredentialsClient:

    def __init__(self, client: httpx.AsyncClient, cfg: ClientCredentialsClientConfig):
        self._client = client
        self._oauth2_client = OAuth2ClientCredentialsClient(client, cfg)
        self._base_url = cfg.base_url
        self._token: Optional[Token] = None
        self._lock = asyncio.Lock()

    async def get_token(self) -> Token:
        try:
            async with self._lock:
                if self._token is None or self._token.is_expired():
                    token_data = await self._oauth2_client.fetch_token()
                    print(token_data)
                    self._token = Token(**token_data)
        except httpx.HTTPStatusError as e:
            raise OAuthError(e.response.text) from e
        return self._token

    async def get_client_info(self) -> dict:
        url = f"{self._base_url}/client"
        try:
            token = await self.get_token()
            if token is None:
                raise MissingTokenError()
            response = await self._client.get(
                url, headers={"Authorization": f"Bearer {token.access_token}"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise MissingTokenError() from e
            raise OAuthError(e.response.text) from e


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

    async def get_token(self, code: str) -> Token:
        try:
            token = await self._oauth2_client.exchange_code_for_tokens(code)
            return Token(**token)
        except httpx.HTTPStatusError as e:
            raise OAuthError(e.response.text) from e

    async def refresh_token(self, refresh_token: str) -> Token:
        try:
            token =  await self._oauth2_client.refresh_token(refresh_token)
            return Token(**token)
        except httpx.HTTPStatusError as e:
            raise OAuthError(e.response.text) from e

    async def get_user_info(self, access_token: str) -> UserInfoDto:
        url = f"{self._base_url}/user/info"
        try:
            response = await self._client.get(
                url, headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return UserInfoDto(**response.json())
        except httpx.HTTPStatusError as e:
            raise OAuthError(e.response.text) from e

    async def get_admin_info(self, access_token: str) -> dict:
        url = f"{self._base_url}/admin/info"
        try:
            response = await self._client.get(
                url, headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise OAuthError(e.response.text) from e
