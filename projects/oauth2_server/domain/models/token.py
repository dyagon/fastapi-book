from typing import Optional, Literal
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from .client import Client
from ..exception import UnauthorizedClientException

class TokenRequest(BaseModel):
    grant_type: Literal["authorization_code", "client_credentials", "refresh_token"]
    client_id: str
    client_secret: Optional[str] = None # PKCE 流程中不需要 client_secret
    scope: Optional[str] = None
    redirect_uri: Optional[str] = None
    code: Optional[str] = None
    refresh_token: Optional[str] = None
    code_verifier: Optional[str] = None

class TokenResponse(BaseModel):
    """
    成功的令牌响应模型, 符合 RFC 6749, Section 5.1
    """
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: Optional[str] = None # 例如 "read write"
    refresh_token: Optional[str] = None # 在授权码流程中可以颁发刷新令牌

class TokenIssuer(BaseModel):
    client_id: str
    scope: Optional[str] = None

    model_config = { "from_attributes": True }

    def validate_client(self, client: Client):
        raise NotImplementedError

class ClientCredentials(TokenIssuer):
    client_secret: str

    def validate_client(self, client: Client):
        if client is None:
            raise UnauthorizedClientException(f"Client {self.client_id} not found")
            
        if client.is_public_client():
            raise UnauthorizedClientException(f"Client {self.client_id} is a public client")

        if client.client_secret != self.client_secret:
            raise UnauthorizedClientException(f"Client {self.client_id} has invalid credentials")

        if self.scope and self.scope not in client.scopes:
            raise UnauthorizedClientException(f"Client {self.client_id} has invalid scope")

    def token_data(self) -> dict:
        return {
            "sub": self.client_id,
            "scopes": self.scope,
            "client_id": self.client_id,
        }
    
class AuthorizationCode(TokenIssuer):
    code: str
    redirect_uri: str

    def validate_client(self, client: Client):
        if client.is_public_client():
            raise UnauthorizedClientException(f"Client {self.client_id} is a public client")

    def token_data(self) -> dict:
        return {
            "sub": self.client_id,
            "scope": self.scope
        }

class RefreshToken(TokenIssuer):
    refresh_token: str

    def validate_client(self, client: Client):
        if client.is_public_client():
            raise UnauthorizedClientException(f"Client {self.client_id} is a public client")

    def token_data(self) -> dict:
        return {
            "sub": self.client_id,
            "scope": self.scope
        }