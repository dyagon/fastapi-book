from typing import Optional


from ..models.user import User
from ...impl.repo.user import UserRepo
from ...impl.auth import UserInfoDto


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def get_user_by_uuid(self, uuid: str) -> User | None:
        return await self.user_repo.get_user_by_uuid(uuid)

    async def get_or_create_user(self, provider: str, provider_id: str, **kwargs) -> User:
        username = kwargs.get("username") or f"{provider}_{provider_id}"
        avatar_url = kwargs.get("avatar_url") or f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
        auth = await self.user_repo.get_auth(provider, provider_id)
        if not auth:
            user = await self.user_repo.create_user(username, avatar_url)
            auth = await self.user_repo.create_authentication(
                user.uuid, provider, provider_id, kwargs
            )
            
        return await self.user_repo.get_user_by_uuid(auth.user_uuid)
