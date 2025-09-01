from fastapi import Depends

from .user_repo import UserRepository
from .redis.cache import cache

class UserService:
    def __init__(self, user_repo: UserRepository = Depends(UserRepository)):
        self.user_repo = user_repo

    @cache.cacheable(cache_name="users", key="user:{user_id}", expire=300)
    async def get_user_by_id(self, user_id: int):
        return await self.user_repo.get_user_by_id(user_id)
    
    @cache.cache_put(cache_name="users", key="user:{result.id}", expire=300)
    async def create_user(self, username: str, email: str, hashed_password: str):
        user = await self.user_repo.create_user(username, email, hashed_password)
        return user
    