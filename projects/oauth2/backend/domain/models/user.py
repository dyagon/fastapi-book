import uuid
from pydantic import BaseModel


class User(BaseModel):
    uuid: uuid.UUID
    username: str
    avatar_url: str

    model_config = {"from_attributes": True}



class Authentication(BaseModel):
    user_uuid: uuid.UUID
    provider: str
    provider_id: str
    credentials: dict

    model_config = {"from_attributes": True}


