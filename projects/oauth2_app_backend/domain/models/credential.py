

from pydantic import BaseModel

from ...impl.auth import Token, UserInfoDto

from .user import User


class LocalOAuthInfo(BaseModel):
    user: User
    token: Token
    user_info: UserInfoDto

    model_config = {"from_attributes": True}