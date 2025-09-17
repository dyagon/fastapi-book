from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

from enum import StrEnum


from .token import TokenRequest, TokenResponse
from .client import Client


class GrantType(StrEnum):
    CLIENT_CREDENTIALS = "client_credentials"
    AUTHORIZATION_CODE = "authorization_code"
    AUTHORIZATION_CODE_PKCE = "authorization_code_pkce"
    REFRESH_TOKEN = "refresh_token"

class AuthorizationCode(BaseModel):
    code: str
    redirect_uri: str
    client_id: str
    client_secret: str
    scope: Optional[str] = None
    model_config = { "from_attributes": True }

class RefreshToken(BaseModel):
    refresh_token: str
    client_id: str
    client_secret: str
    scope: Optional[str] = None
    model_config = { "from_attributes": True }

class AuthorizationCodePKCE(BaseModel):
    code: str
    redirect_uri: str
    client_id: str
    scope: Optional[str] = None
    code_challenge: str
    code_challenge_method: str
    model_config = { "from_attributes": True }



