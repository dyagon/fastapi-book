from typing import Optional, Dict, Any
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []


class Client(BaseModel):
    client_id: str
    client_secret: Optional[str]  # None for public clients
    redirect_uris: list[str]
    scopes: list[str]
    client_type: str  # "confidential" or "public"


class UserInDB(User):
    hashed_password: str
    

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str

