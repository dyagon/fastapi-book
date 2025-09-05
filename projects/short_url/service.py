
from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, ShortUrl

import threading

class UserService:

    def __init__(self, db: AsyncSession):
        print(f"UserService, {threading.current_thread().name}")
        self.db = db

    async def get_user(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    
    async def get_user_by_name(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def get_users(self) -> list[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()
    
    async def create_user(self, username: str, password: str) -> User:
        new_user = User(
            username=username,
            password=password
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
    
    async def update_user(self, user_id: int, username: str | None, email: str | None, hashed_password: str | None) -> User | None:
        stmt = update(User).where(User.id == user_id)
        if username:
            stmt = stmt.values(username=username)
        if email:
            stmt = stmt.values(email=email)
        if hashed_password:
            stmt = stmt.values(hashed_password=hashed_password)
        
        result = await self.db.execute(stmt.returning(User))
        await self.db.commit()
        return result.scalars().first()
    
    async def delete_user(self, user_id: int) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    

class ShortService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_short_url(self, short_tag: str):
        result = await self.db.execute(select(ShortUrl).where(ShortUrl.short_tag == short_tag))
        return result.scalars().first()
    
    async def create_short_url(self, **kwargs):
        new_short_url = ShortUrl(
            **kwargs
        )
        self.db.add(new_short_url)
        await self.db.commit()
        await self.db.refresh(new_short_url)
        return new_short_url
    
    async def update_short_url(self, short_url_id: int, **kwargs):
        stmt = update(ShortUrl).where(ShortUrl.id == short_url_id)
        stmt = stmt.values(**kwargs)
        result = await self.db.execute(stmt.returning(ShortUrl))
        await self.db.commit()
        return result.scalars().first()

    async def delete_short_url(self, short_url_id: int):
        stmt = delete(ShortUrl).where(ShortUrl.id == short_url_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def create_batch_short_urls(self, short_urls: list[dict]):
        new_short_urls = [ShortUrl(**data) for data in short_urls]
        self.db.add_all(new_short_urls)
        await self.db.commit()
        for short_url in new_short_urls:
            await self.db.refresh(short_url)
        return new_short_urls
    