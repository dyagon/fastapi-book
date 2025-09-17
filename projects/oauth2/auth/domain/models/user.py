from pydantic import BaseModel
from typing import Optional

from passlib.context import CryptContext

# Initialize password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    model_config = {"from_attributes": True}


class UserInDB(User):
    password: str

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)
