from typing import Dict
from pydantic import BaseModel
from ...impl.auth import (
    OAuth2ClientCredentialsClient,
    OAuth2ClientCredentialsAuth,
    AuthClient,
    OAuth2ClientCredentialsConfig,
)


class OAuth2ClientCredentialsServiceConfig(OAuth2ClientCredentialsConfig):
    base_url: str


class OAuth2ClientCredentialsService:

    def __init__(self, base_url: str, auth_client: AuthClient):
        self.base_url = base_url
        self.auth_client = auth_client

    async def get_token(self) -> Dict[str, str]:
        return await self.auth_client._auth.get_auth_headers()

    async def get_client_info(self) -> dict:
        url = f"{self.base_url}/client"
        response = await self.auth_client.get(url)
        return response.json()
