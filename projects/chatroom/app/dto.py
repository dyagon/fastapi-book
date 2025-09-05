from pydantic import BaseModel


class RegisterAaction(BaseModel):
    phone_number: str
    username: str
    password: str

class LoginAaction(BaseModel):
    phone_number: str
    password: str

