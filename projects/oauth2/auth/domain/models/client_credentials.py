
from typing import Optional
from datetime import datetime, timezone, timedelta

from pydantic import BaseModel


from .token import TokenResponse
from .client import Client
from ..utils import TokenUtils
from ..exception import UnauthorizedClientException


class ClientCredentials(BaseModel):
    client_id: str
    client_secret: str
    scope: Optional[str] = None
    model_config = { "from_attributes": True }

    def validate_client(self, client: Client):
        if client.is_public_client():
            raise UnauthorizedClientException(f"Client {self.client_id} is a public client")

        if client.client_secret != self.client_secret:
            raise UnauthorizedClientException(f"Client {self.client_id} has invalid credentials")

        if self.scope and self.scope not in client.scopes:
            raise UnauthorizedClientException(f"Client {self.client_id} has invalid scope")

    def jwt_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = TokenUtils.token_encode(to_encode)
        return encoded_jwt

    def create_access_token(self, data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
        return self.jwt_token(data, expires_delta)
        
    def create_refresh_token(self, data: dict, expires_delta: timedelta = timedelta(days=7)) -> str:
        return self.jwt_token(data, expires_delta)

    def issue_token(self, client: Client) -> TokenResponse:

        data = {
            "sub": self.client_id,
            "scopes": self.scope,
            "client_id": self.client_id,
            "grant_type": "client_credentials"
        }

        access_token = self.create_access_token(data, timedelta(minutes=15))
        refresh_token = self.create_refresh_token(data, timedelta(days=7))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=15 * 60,
            scope=self.scope
        )

    
        