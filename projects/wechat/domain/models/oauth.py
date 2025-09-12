

from datetime import datetime

from pydantic import BaseModel



class AuthCodes(BaseModel):
    internal_user_id: str
    app_id: str
    scope: str
    is_used: bool = False
    expires_at: int # 时间戳


class AccessTokens(BaseModel):
    union_id: str
    open_id: str
    scope: str
    expires_at: int