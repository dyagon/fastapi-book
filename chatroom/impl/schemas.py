from dataclasses import dataclass

from pydantic import BaseModel
from starlette.websockets import WebSocket

@dataclass
class UserInfo:
    phone_number: str
    username: str

@dataclass
class UserConnection(UserInfo):
    websocket: WebSocket

class RedisMessage(BaseModel):
    user: UserInfo
    message: str | None = None

class EventType:
    USER_LOGIN = "login"
    USER_LOGOUT = "logout"
    USER_MESSAGE = "chat"