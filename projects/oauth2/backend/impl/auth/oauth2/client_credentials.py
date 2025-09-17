import time
import asyncio
import base64
import httpx

from typing import Optional
from pydantic import BaseModel


class OAuth2ClientCredentialsConfig(BaseModel):
    token_url: str
    client_id: str
    client_secret: str


class OAuth2ClientCredentialsClient:

    def __init__(
        self, client: httpx.AsyncClient, config: OAuth2ClientCredentialsConfig
    ):
        self._client = client
        self._token_url = config.token_url
        self._client_id = config.client_id
        self._client_secret = config.client_secret
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()

    @property
    def _basic_auth_header(self) -> str:
        credentials = f"{self._client_id}:{self._client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    @property
    def _is_expired(self) -> bool:
        return time.time() > self._expires_at - 60  # add 60 seconds buffer

    async def get_token(self) -> str:
        async with self._lock:
            if self._access_token is None or self._is_expired:
                await self._fetch_new_token()
        return self._access_token

    async def _fetch_new_token(self):
        data = {"grant_type": "client_credentials", "scope": "get_client_info"}
        headers = {
            "Authorization": self._basic_auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            # Get access token using client credentials
            response = await self._client.post(
                self._token_url, data=data, headers=headers
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
