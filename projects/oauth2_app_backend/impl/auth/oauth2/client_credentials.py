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
    scope: Optional[str] = None


class OAuth2ClientCredentialsClient:

    def __init__(
        self, client: httpx.AsyncClient, config: OAuth2ClientCredentialsConfig
    ):
        self._client = client
        self._token_url = config.token_url
        self._client_id = config.client_id
        self._client_secret = config.client_secret
        self._scope = config.scope

    @property
    def _basic_auth_header(self) -> str:
        credentials = f"{self._client_id}:{self._client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    async def fetch_token(self) -> dict:
        data = {"grant_type": "client_credentials"}
        if self._scope:
            data["scope"] = self._scope
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
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch new token: {e.response.text}")
            self._access_token = None
            self._expires_at = 0.0
            raise e
