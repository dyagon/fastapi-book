import asyncio

from ..models.user import Authentication, User
from ...impl.repo.user import UserRepo
from ...impl.auth import UserInfoDto
from ...impl.session_manager import SessionManager
from ...infra import transactional_session, read_only_session


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    @read_only_session
    async def get_user_by_uuid(self, uuid: str) -> User | None:
        return await self.user_repo.get_user_by_uuid(uuid)

    @read_only_session
    async def get_user_and_auths(
        self, uuid: str
    ) -> tuple[User | None, list[Authentication] | None]:
        user = await self.user_repo.get_user_by_uuid(uuid)
        if not user:
            return None, None
        auths = await self.user_repo.get_user_authentications(uuid)
        return user, auths

    @read_only_session
    async def get_user_and_auth(
        self, uuid: str, provider: str
    ) -> tuple[User | None, Authentication | None]:
        return await self.user_repo.get_user_and_auth(uuid, provider)

    async def get_user_and_auth_for_update(
        self, uuid: str, provider: str
    ) -> tuple[User | None, Authentication | None]:
        return await self.user_repo.get_user_and_auth_for_update(uuid, provider)

    @transactional_session
    async def get_or_create_user(
        self, provider: str, provider_id: str, credential: dict, user_info: dict
    ) -> User:
        username = user_info.get("username") or f"{provider}_{provider_id}"
        avatar_url = (
            user_info.get("avatar_url")
            or f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
        )
        auth = await self.user_repo.get_auth(provider, provider_id)
        if not auth:
            user = await self.user_repo.create_user(username, avatar_url)
            auth = await self.user_repo.create_authentication(
                user.uuid, provider, provider_id, credential, user_info
            )

        return await self.user_repo.get_user_by_uuid(auth.user_uuid)


