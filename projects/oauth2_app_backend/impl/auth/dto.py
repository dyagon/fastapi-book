import time

from pydantic import BaseModel, model_validator
from typing import Optional


class Token(BaseModel):
    access_token: str
    expires_in: int
    expires_at: int
    token_type: str
    scope: str
    refresh_token: Optional[str] = None

    def is_expired(self) -> bool:
        return time.time() > self.expires_at - 60  # add 60 seconds buffer


class UserInfoDto(BaseModel):
    id: str
    username: str
    email: Optional[str]
    full_name: Optional[str]