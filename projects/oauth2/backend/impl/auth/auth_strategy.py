from abc import ABC, abstractmethod
from typing import Dict

from .oauth2.client_credentials import OAuth2ClientCredentialsClient

class AuthStrategy(ABC):
    @abstractmethod
    async def get_auth_headers(self) -> Dict[str, str]:
        pass


class ApiKeyAuth(AuthStrategy):
    def __init__(self, api_key: str, header_name: str = "x-api-key"):
        self._api_key = api_key
        self._header_name = header_name

    async def get_auth_headers(self) -> Dict[str, str]:
        return {self._header_name: self._api_key}


class OAuth2ClientCredentialsAuth(AuthStrategy):
    def __init__(
        self, client: OAuth2ClientCredentialsClient, header_name: str = "Authorization"
    ):
        self._client = client
        self._header_name = header_name

    async def get_auth_headers(self) -> Dict[str, str]:
        token = await self._client.get_token()
        return {self._header_name: f"Bearer {token}"}
