from typing import Optional
from pydantic import BaseModel


class AuthorizationCodeResponse(BaseModel):
    code: str
    state: Optional[str] = None
    scope: Optional[str] = None



class UserInfoDto(BaseModel):
    id: str
    username: str
    email: Optional[str]
    full_name: Optional[str]