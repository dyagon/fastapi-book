from fastapi import Depends

from .user_repo import UserRepository
from ..cache import cache

class UserService:
    def __init__(self, user_repo: UserRepository = Depends(UserRepository)):
        self.user_repo = user_repo

    @cache(ttl=60)
    async def get_user_by_id(self, user_id: int):
        return await self.user_repo.get_user_by_id(user_id)
    
    async def create_user(self, username: str, email: str, hashed_password: str):
        user = await self.user_repo.create_user(username, email, hashed_password)
        return user
    