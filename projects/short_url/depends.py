
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends

from .db import SessionLocal

from .service import UserService, ShortService

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_user_service(db: AsyncSession = Depends(get_db_session)):
    yield UserService(db)

async def get_short_service(db: AsyncSession = Depends(get_db_session)):
    yield ShortService(db)