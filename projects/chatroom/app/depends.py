
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from ..infra import SessionLocal
from ..impl import UserRepository
from ..impl.room_manager import RoomManager

from ..domain.service.user_service import UserService

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db_session = None
    try:
        db_session = SessionLocal()
        yield db_session
    finally:
        await db_session.close()

async def get_user_repo(db: AsyncSession = Depends(get_db_session)):
    yield UserRepository(db)

async def get_user_service(user_repo: UserRepository = Depends(get_user_repo)):
    yield UserService(user_repo)
