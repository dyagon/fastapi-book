from typing import Optional
from pydantic import BaseModel


class AuthorizationCodeResponse(BaseModel):
    code: str
    state: Optional[str] = None
    scope: Optional[str] = None


