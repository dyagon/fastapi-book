from typing import Optional, Literal
from pydantic import BaseModel


class TokenRequest(BaseModel):
    grant_type: Literal["authorization_code", "client_credentials"]
    client_id: str
    client_secret: Optional[str] = None # PKCE 流程中不需要 client_secret
    scope: Optional[str] = None
    redirect_uri: Optional[str] = None
    code: Optional[str] = None
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
