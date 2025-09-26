from abc import ABC, abstractmethod
from datetime import timedelta, datetime, timezone

from pydantic import BaseModel

from .token_service import TokenService
from ...impl.repo import ClientRepo
from ..models.client import Client
from ..models.token import TokenRequest, TokenResponse, AuthorizationCode
from ..exception import UnauthorizedClientException


class OAuth2Service(ABC):

    def __init__(
        self, client_repo: ClientRepo, token_service: TokenService
    ):
        self.client_repo = client_repo
        self.token_service = token_service

    async def get_client(self, client_id: str) -> Client:
        client = await self.client_repo.get_client(client_id)
        if not client:
            raise UnauthorizedClientException(f"Client {client_id} not found")
        return client

    @abstractmethod
    async def handle_token_request(self, token_request: TokenRequest) -> TokenResponse:
        raise NotImplementedError


