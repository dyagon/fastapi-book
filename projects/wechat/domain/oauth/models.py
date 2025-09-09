
from datetime import datetime

from pydantic import BaseModel


class Apps(BaseModel):
    app_id: str
    app_secret: str
    owner_developer_id: str
    authorized_redirect_uris: list[str]

class Users(BaseModel):
    internal_user_id: str
    nickname: str
    avatar_url: str

class UserIdentities(BaseModel):
    app_id: str   # 应用ID
    internal_user_id: str   # 微信内部用户 id
    open_id: str   # 用户在应用内的唯一 id
    union_id: str   # 在同一个开发者账号下的唯一 id

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



