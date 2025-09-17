from pydantic import BaseModel


class User(BaseModel):
    nickname: str
    avatar_url: str

    model_config = {"from_attributes": True}



class Authentication(BaseModel):
    user_id: str
    provider: str
    provider_id: str
    credentials: dict

    model_config = {"from_attributes": True}


