from pydantic import BaseModel


class User(BaseModel):
    uuid: str
    username: str
    avatar_url: str

    model_config = {"from_attributes": True}



class Authentication(BaseModel):
    uuid: str
    provider: str
    provider_id: str
    credentials: dict

    model_config = {"from_attributes": True}


