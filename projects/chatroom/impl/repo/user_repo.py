from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_by_phone(self, phone_number: str):
        result = await self.db_session.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalars().first()
    
    async def get_user(self, user_id: int):
        result = await self.db_session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()
    
    async def get_users(self):
        result = await self.db_session.execute(select(User))
        return result.scalars().all()
    
    async def create_user(self, phone_number: str, username: str, password: str):
        new_user = User(
            phone_number=phone_number,
            username=username,
            password=password
        )
        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)
        return new_user
    
    async def update_user(self, user_id: int, **kwargs):
        await self.db_session.execute(
            update(User).where(User.id == user_id).values(**kwargs)
        )
        await self.db_session.commit()
        return await self.get_user(user_id)
    
    async def delete_user(self, user_id: int):
        await self.db_session.execute(
            delete(User).where(User.id == user_id)
        )
        await self.db_session.commit()