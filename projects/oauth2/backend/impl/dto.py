from pydantic import BaseModel
from typing import Optional


class UserInfoDto(BaseModel):
    id: str
    username: str
    email: Optional[str]
    full_name: Optional[str]