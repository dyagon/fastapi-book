import time
import base64
import asyncio
import httpx

from typing import Optional, Dict, Any
from urllib.parse import urlencode

from pydantic import BaseModel

from ..infra.web_client import WebClient

from .dto import UserInfoDto


class OAuthClientConfig(BaseModel):
    base_url: str
    token_url: str
    client_id: str
    client_secret: str


class AuthorizationCodeClientConfig(OAuthClientConfig):
    provider: str
    auth_url: str
    redirect_uri: str
    scope: str



class OAuthClient(WebClient):
    def __init__(self, config: OAuthClientConfig):
        self.base_url = config.base_url
        self.token_url = config.token_url
        self._client_id = config.client_id
        self._client_secret = config.client_secret

    @property
    def basic_auth_header(self) -> str:
        credentials = f"{self._client_id}:{self._client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"


class ClientCredentialsClient(OAuthClient):

    def __init__(self, config: OAuthClientConfig):
        super().__init__(config)
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()

    @property
    async def bearer_auth_header(self) -> str:
        return f"Bearer {await self.get_token()}"

    @property
    def is_expired(self) -> bool:
        return time.time() > self._expires_at - 60  # add 60 seconds buffer

    async def get_token(self) -> str:
        async with self._lock:
            if self._access_token is None or self.is_expired:
                await self._fetch_new_token()
        return self._access_token

    async def _fetch_new_token(self):
        data = {"grant_type": "client_credentials", "scope": "get_client_info"}
        headers = {
            "Authorization": self.basic_auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            # Get access token using client credentials
            response = await self._client.post(
                self.token_url, data=data, headers=headers
            )
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._expires_at = time.time() + token_data["expires_in"]
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch new token: {e.response.text}")
            self._access_token = None
            self._expires_at = 0.0
            raise e

    async def call(self, endpoint: str):
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": await self.bearer_auth_header}
        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}",
                "detail": e.response.text,
            }
        except Exception as e:
            return {"error": "Request failed", "detail": str(e)}


class AuthCodeClient(OAuthClient):
    def __init__(self, config: AuthorizationCodeClientConfig):
        super().__init__(config)
        self.provider = config.provider
        self._auth_url = config.auth_url
        self._redirect_uri = config.redirect_uri
        self._scope = config.scope

    def make_auth_url(self, state: Optional[str] = None):
        auth_params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "scope": self._scope,
        }
        if state:
            auth_params["state"] = state
        return f"{self._auth_url}?{urlencode(auth_params)}"

    async def exchange_code_for_tokens(self, code: str):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
        }
        headers = {
            "Authorization": self.basic_auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = await self._client.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    async def refresh_token(self, refresh_token: str):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self._client_id,
        }
        headers = {
            "Authorization": self.basic_auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await self._client.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_user_info(self, access_token: str) -> UserInfoDto:
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        user_info_url = f"{self.base_url}/user/info"
        response = await self._client.get(user_info_url, headers=headers)
        response.raise_for_status()
        return UserInfoDto(**response.json())

