from secrets import token_urlsafe
import uuid
from pydantic import BaseModel
from redis.asyncio import Redis
from typing import Optional

from datetime import datetime, timedelta, timezone


class Session(BaseModel):
    user_id: str
    session_id: str
    created_at: datetime
    last_activity_at: datetime


class SessionManager:

    prefix: str = "app:session:"
    ttl: timedelta = timedelta(minutes=20)
    abs_ttl: timedelta = timedelta(days=7)

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def new_session(self, user_id: str) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
        )
        await self.redis_client.hset(
            self.prefix + session_id, mapping=session.model_dump()
        )
        await self.redis_client.expire(self.prefix + session_id, self.ttl)
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        if not await self.redis_client.exists(self.prefix + session_id):
            return None
        
        session_data = await self.redis_client.hgetall(self.prefix + session_id)
        session = Session.model_validate(session_data)

        # check if session is expired
        if session.last_activity_at + self.ttl < datetime.now(timezone.utc):
            await self.redis_client.delete(self.prefix + session_id)
            return None

        if session.created_at + self.abs_ttl < datetime.now(timezone.utc):
            await self.redis_client.delete(self.prefix + session_id)
            return None

        await self.redis_client.expire(self.prefix + session_id, self.ttl)
        return await self.redis_client.hgetall(self.prefix + session_id)

    async def set_session(self, session_id: str, session: Session):
        await self.redis_client.hset(
            self.prefix + session_id, mapping=session.model_dump()
        )
        await self.redis_client.expire(self.prefix + session_id, self.ttl)

    async def update_session_timestamp(self, session_id: str):
        await self.redis_client.hset(
            self.prefix + session_id, "last_activity_at", datetime.now(timezone.utc)
        )
        await self.redis_client.expire(self.prefix + session_id, self.ttl)

    async def delete_session(self, session_id: str):
        await self.redis_client.delete(self.prefix + session_id)

    ## state manage
    async def new_state(self, expires_delta: timedelta = timedelta(minutes=5)) -> str:
        state = token_urlsafe(32)
        await self.redis_client.set(self.prefix + state, state, expires_delta)
        return state

    async def validate_state(self, state: str) -> bool:
        return await self.redis_client.get(self.prefix + state) is not None

    async def get_state(self, state: str) -> Optional[str]:
        return await self.redis_client.get(self.prefix + state)

    async def delete_state(self, state: str):
        await self.redis_client.delete(self.prefix + state)
