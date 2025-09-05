from typing import Dict, Optional

from redis.asyncio import Redis

from redis.asyncio.client import PubSub
import asyncio
from typing import List
from fastapi import WebSocket
from typing import Any

from .schemas import UserInfo, RedisMessage, EventType, UserConnection


class RoomManager:

    def __init__(self, redis: Redis):
        self.redis = redis
        self.rooms: Dict[str, Room] = {}

    async def get_room(self, room_name: str) -> "Room":
        room: Optional[Room] = self.rooms.get(room_name)
        if not room:
            room = Room(self, room_name)
            self.rooms[room_name] = room
            await room.setup()
        return room

    async def close_room(self, room_name: str):
        room = self.rooms.pop(room_name, None)
        if room:
            await room.destroy()
            print(f"Room {room_name} closed and cleaned up.")


class Room:

    def __init__(self, room_manager: "RoomManager", room_name: str):
        self.room_name: str = room_name
        self.room_manager: RoomManager = room_manager
        self.redis: Redis = room_manager.redis
        self.pubsub: Optional[PubSub] = None
        self._users: Dict[str, UserConnection] = {}
        self._listen_task: Optional[asyncio.Task] = None

    @property
    def event_channel(self) -> str:
        return f"chat:room:{self.room_name}:event"

    @property
    def chat_channel(self) -> str:
        return f"chat:room:{self.room_name}:msg"

    @property
    def active_connections(self) -> List[WebSocket]:
        return [user.websocket for user in self._users.values()]

    async def setup(self):
        print(f"Setting up room: {self.room_name}")
        self.destroy()
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(self.chat_channel, self.event_channel)

        async def listen(pubsub: PubSub):
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message:
                    await self._handle_message(message)
                await asyncio.sleep(0.01)  # Prevent busy-waiting

        self._listen_task = asyncio.create_task(listen(self.pubsub))

    def destroy(self):
        if self._listen_task:
            self._listen_task.cancel()
            self._listen_task = None
        if self.pubsub:
            self.pubsub.unsubscribe(self.chat_channel, self.event_channel)
            self.pubsub.close()

    async def _handle_message(self, message: Any):
        print(f"Received message: {message}")
        if not message or message["type"] != "message":
            return
        data = message["data"]
        channel = message["channel"]

        # Convert bytes to string if necessary
        if isinstance(channel, bytes):
            channel = channel.decode("utf-8")
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        print(f"Processing channel: {channel}, data: {data}")

        try:
            msg = RedisMessage.model_validate_json(data)
            if channel == self.chat_channel:
                await self._broadcast_user_message(msg.user, msg.message)
            elif channel == self.event_channel:
                await self._broadcast_user_event(msg.user, msg.message)
            else:
                print(f"Unknown channel: {channel}")
        except Exception as e:
            print(f"Error processing message: {e}")

    async def _broadcast_user_message(self, user: UserInfo, message: str):
        for connection in self.active_connections:
            await connection.send_json(
                {
                    "type": "message",
                    "user": {
                        "phone_number": user.phone_number,
                        "username": user.username,
                    },
                    "message": message,
                }
            )

    async def _broadcast_user_event(self, user: UserInfo, event: str):
        if event == EventType.USER_LOGIN:
            message = f"{user.username} has joined the room."
        elif event == EventType.USER_LOGOUT:
            message = f"{user.username} has left the room."
        else:
            message = f"Unknown event {event} for user {user.username}."
        for connection in self.active_connections:
            await connection.send_json(
                {
                    "type": event,
                    "user": {
                        "phone_number": user.phone_number,
                        "username": user.username,
                    },
                    "message": message,
                }
            )

    async def login(self, user: UserInfo, websocket: WebSocket) -> bool:
        if user.phone_number in self._users:
            return False
        self._users[user.phone_number] = UserConnection(
            phone_number=user.phone_number, username=user.username, websocket=websocket
        )
        await self._pubs_user_event(
            UserInfo(phone_number=user.phone_number, username=user.username),
            EventType.USER_LOGIN,
        )
        return True

    async def logout(self, user: UserInfo):
        if user.phone_number in self._users:
            await self._pubs_user_event(
                UserInfo(phone_number=user.phone_number, username=user.username),
                EventType.USER_LOGOUT,
            )
            del self._users[user.phone_number]

    async def send_message(self, user: UserInfo, message: str):
        connection = self._users.get(user.phone_number)
        if connection:
            await self._pub_user_message(connection, message)

    async def _pub_message(self, channel: str, user: UserInfo, message: str):
        if self.redis:
            event = RedisMessage(user=user, message=message)
            await self.redis.publish(channel, event.model_dump_json())

    async def _pub_user_message(self, user: UserInfo, message: str):
        await self._pub_message(self.chat_channel, user, message)

    async def _pubs_user_event(self, user: UserInfo, event: str):
        await self._pub_message(self.event_channel, user, event)
