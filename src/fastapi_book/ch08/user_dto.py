from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreateDTO(BaseModel):
    username: str
    email: str
    password: str

class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
