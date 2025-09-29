from typing import Optional
import time
from ...impl.session_manager import SessionManager, Session

from ..exceptions import (
    SessionException,
    SessionExpiredException,
    NotAuthenticatedException,
)


class SessionService:

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def check_session(self, session_data: dict) -> Session:
        if not session_data or not session_data.get("session_id"):
            raise NotAuthenticatedException()
        session_id = session_data.get("session_id")
        session = await self.session_manager.check_and_refresh_session(session_id)
        if not session:
            raise SessionExpiredException()
        return session
        
    async def new_session(self, user_id: str) -> Session:
        return await self.session_manager.new_session(user_id)
    
    async def get_state(self, state: str) -> Optional[str]:
        return await self.session_manager.get_state(state)
    
    async def set_state(self, state: str) -> None:
        await self.session_manager.set_state(state)

    async def delete_state(self, state: str) -> None:
        await self.session_manager.delete_state(state)