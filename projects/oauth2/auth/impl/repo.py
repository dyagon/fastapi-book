
from ..config import clients, users

fake_users_db = users
fake_client_db = clients

from ..domain.models.client import Client
from ..domain.models.user import UserInDB
from ..domain.exception import UnauthorizedClientException

class UserRepo:
    def __init__(self):
        self.users = fake_users_db

    async def get_user(self, username: str) -> UserInDB:
        user = self.users.get(username)
        if not user:
            raise UnauthorizedClientException(f"User {username} not found")
        return UserInDB(**user)
    
    async def get_user_by_id(self, user_id: str) -> UserInDB:
        """通过用户ID获取用户信息"""
        for username, user_data in self.users.items():
            if user_data.get("id") == user_id:
                return UserInDB(**user_data)
        raise UnauthorizedClientException(f"User with ID {user_id} not found")


class ClientRepo:
    def __init__(self):
        self.clients = fake_client_db

    async def get_client(self, client_id: str) -> Client:
        client = self.clients.get(client_id)
        if not client:
            raise UnauthorizedClientException(f"Client {client_id} not found")
        return Client(**client)
