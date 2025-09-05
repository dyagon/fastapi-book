import pathlib
from fastapi import APIRouter, Depends
from starlette.endpoints import WebSocketEndpoint
from typing import Optional

from starlette.responses import FileResponse

from ...infra import AuthToeknHelper
from fastapi import WebSocket, status

from ...impl import room_manager, UserInfo, Room


router_chat = APIRouter(tags=["聊天室"])


templates_dir = pathlib.Path(__file__).parent.parent / "templates"

@router_chat.get("/api/v1/room/online")
def index():
    return FileResponse(templates_dir / "room.html")


@router_chat.websocket_route("/api/v1/room/socketws")
@router_chat.websocket_route("/api/v1/room/socketws/")
class ChatRoomWebSocket(WebSocketEndpoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.curr_user: Optional[UserInfo] = None
        self.room: Optional[Room] = None

    async def get_user(self, websocket: WebSocket) -> Optional[UserInfo]:
        token = websocket.query_params.get("token")
        if not token:
            raise ValueError("Missing token in query parameters")        
        if not self.curr_user:
            AuthToeknHelper.token_decode(token)
            payload = AuthToeknHelper.token_decode(token=token)
            # 解析token信息
            phone_number = payload.get("phone_number")
            username = payload.get("username")
            # 初始化当前连接用户信息
            self.curr_user = UserInfo(phone_number=phone_number, username=username)
        return self.curr_user
        

    async def close_clean_user_websocket(self, code: int, websocket: WebSocket):
        if self.curr_user and self.room:
            await self.room.logout(self.curr_user)
        await websocket.close(code=code)

    async def on_connect(self, _websocket: WebSocket):
        try:
            # 确认链接
            await _websocket.accept()
            # 初始化当前用户信息
            self.curr_user = await self.get_user(_websocket)
            self.room = await room_manager.get_room("default")
            await self.room.login(self.curr_user, _websocket)
        except Exception as e:
            print("连接异常:", e)
            await self.close_clean_user_websocket(
                code=status.WS_1011_INTERNAL_ERROR, websocket=_websocket
            )

    async def on_receive(self, _websocket: WebSocket, msg: str):
        if self.curr_user is None:
            await self.close_clean_user_websocket(
                code=status.WS_1008_POLICY_VIOLATION, websocket=_websocket
            )

        await self.room.send_message(self.curr_user, message=msg)

    async def on_disconnect(self, _websocket: WebSocket, _close_code: int):
        await self.close_clean_user_websocket(
            code=status.WS_1000_NORMAL_CLOSURE, websocket=_websocket
        )
        del self.curr_user
