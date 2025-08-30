from fastapi import Depends


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi_book.db import get_async_db
from fastapi_book.ch08.user_model import User



class UserService:
    def __init__(self, db: AsyncSession = Depends(get_async_db)):
        self.db = db

    async def get_user_by_username(self, username: str):
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()
    
    async def get_user_by_email(self, email: str):
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()
    
    async def create_user(self, username: str, email: str, hashed_password: str):
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
    
    async def get_user_by_id(self, user_id: int):
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()
