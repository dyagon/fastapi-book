from ...impl.repo.user import UserRepo
from ...impl.dto import UserInfoDto
from ...domain.models.user import User

class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def get_user_by_uuid(self, uuid: str) -> User | None:
        return self.user_repo.get_user_by_uuid(uuid)


    def get_or_create_user(self, provider: str, user_info: UserInfoDto) -> User:
        provider_id = user_info.id
        auth = self.user_repo.get_auth_by_provider_and_provider_id(provider, provider_id)
        user = self.user_repo.get_user_by_provider_and_provider_id(provider, provider_id)



    def create_user(self, nickname: str, avatar_url: str) -> User:
        return self.user_repo.create_user(nickname, avatar_url)

    def update_user(self, uuid: str, nickname: str, avatar_url: str) -> User | None:
        return self.user_repo.update_user(uuid, nickname, avatar_url)

    def delete_user(self, uuid: str) -> bool:
        return self.user_repo.delete_user(uuid)
