import httpx
import base64
import random
from typing import Optional
from urllib.parse import urlencode

from pydantic import BaseModel


class OAuth2AuthorizationCodeConfig(BaseModel):
    auth_url: str
    token_url: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str


class OAuth2AuthorizationCodeClient:
    def __init__(
        self, client: httpx.AsyncClient, config: OAuth2AuthorizationCodeConfig
    ):
        self._client = client
        self._client_id = config.client_id
        self._client_secret = config.client_secret
        self._token_url = config.token_url
        self._auth_url = config.auth_url
        self._redirect_uri = config.redirect_uri
        self._scope = config.scope

    @property
    def _basic_auth_header(self) -> str:
        credentials = f"{self._client_id}:{self._client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

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
            "Authorization": self._basic_auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = await self._client.post(self._token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    async def refresh_token(self, refresh_token: str):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self._client_id,
        }
        headers = {
            "Authorization": self._basic_auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await self._client.post(self._token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
