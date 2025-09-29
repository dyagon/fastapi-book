import time
from secrets import token_urlsafe
import uuid
from pydantic import BaseModel
from redis.asyncio import Redis
from typing import Optional, List, Dict

from datetime import datetime


class Session(BaseModel):
    user_id: str
    session_id: str
    created_at: float
    last_activity_at: float

    def login_time(self) -> str:
        return datetime.fromtimestamp(self.created_at).strftime("%Y-%m-%d %H:%M:%S")

    def last_activity_time(self) -> str:
        return datetime.fromtimestamp(self.last_activity_at).strftime(
            "%Y-%m-%d %H:%M:%S"
        )


CHECK_AND_REFRESH_SCRIPT = """
if redis.call('EXISTS', KEYS[1]) == 0 then
    return nil
end
local created_at = redis.call('HGET', KEYS[1], 'created_at')
if not created_at then
    redis.call('DEL', KEYS[1])
    return nil
end
local absolute_expiry_time = tonumber(created_at) + tonumber(ARGV[1])
if absolute_expiry_time < tonumber(ARGV[3]) then
    redis.call('DEL', KEYS[1])
    return nil
end
redis.call('HSET', KEYS[1], 'last_activity_at', ARGV[3])
redis.call('EXPIRE', KEYS[1], ARGV[2])
return redis.call('HGETALL', KEYS[1])
"""


class SessionManager:

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.prefix = "app:session:"
        self.state_prefix = "app:state:"
        self.rel_ttl = 20 * 60  # 20 minutes
        self.abs_ttl = 7 * 24 * 60 * 60  # 7 days
        self.check_and_refresh_script = self.redis_client.register_script(
            CHECK_AND_REFRESH_SCRIPT
        )

    def _key(self, session_id: str) -> str:
        return self.prefix + session_id

    def _state_key(self, state: str) -> str:
        return self.state_prefix + state

    async def new_session(self, user_id: str) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(
            user_id=user_id,
            session_id=session_id,
            created_at=time.time(),
            last_activity_at=time.time(),
        )
        await self.redis_client.hset(
            self._key(session_id), mapping=session.model_dump()
        )
        await self.redis_client.expire(self._key(session_id), self.rel_ttl)
        return session

    def _hgetall_to_dict(self, result: List[str]) -> Dict[str, str]:
        """Converts the flat list from HGETALL into a dictionary."""
        if not result:
            return {}
        return dict(zip(result[0::2], result[1::2]))

    async def check_and_refresh_session(self, session_id: str) -> Optional[Session]:
        """
        原子地检查并刷新 session (使用浮点秒数)。
        """
        if not session_id:
            return None
        key = self._key(session_id)
        # EVALSHA 参数对应新的 Lua 脚本
        result = await self.check_and_refresh_script(
            keys=[key],
            args=[self.abs_ttl, self.rel_ttl, time.time()],
        )
        if not result:
            return None
        return Session.model_validate(self._hgetall_to_dict(result))

    async def delete_session(self, session_id: str):
        await self.redis_client.delete(self._key(session_id))

    ## state manage
    async def set_state(self, state: str, expires_delta: int = 5 * 60):
        await self.redis_client.set(self._state_key(state), state, expires_delta)

    async def get_state(self, state: str) -> Optional[str]:
        return await self.redis_client.get(self._state_key(state))

    async def delete_state(self, state: str):
        await self.redis_client.delete(self._state_key(state))
