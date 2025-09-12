
from ..config import clients, users

fake_users_db = users
fake_client_db = clients


from .models import Client, UserInDB
from .exception import UnauthorizedClientException

class UserRepo:
    def __init__(self):
        self.users = fake_users_db

    def get_user(self, username: str) -> UserInDB:
        user = self.users.get(username)
        if not user:
            raise UnauthorizedClientException(f"User {username} not found")
        return UserInDB(**user)


class ClientRepo:
    def __init__(self):
        self.clients = fake_client_db

    def get_client(self, client_id: str) -> Client:
        client = self.clients.get(client_id)
        if not client:
            raise UnauthorizedClientException(f"Client {client_id} not found")
        return Client(**client)
