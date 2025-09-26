from datetime import timedelta
from pydantic import ValidationError

from .token_service import TokenService
from .oauth2_service import OAuth2Service
from ...impl.repo import ClientRepo
from ..models.token import TokenRequest, TokenResponse, ClientCredentials
from ..exception import InvalidRequestException, UnauthorizedClientException


class ClientCredentialsFlowService(OAuth2Service):

    def __init__(self, client_repo: ClientRepo, token_service: TokenService):
        super().__init__(client_repo, token_service)

    async def handle_token_request(self, token_request: TokenRequest) -> TokenResponse:
        # 1. check paramters
        try:
            cc = ClientCredentials.model_validate(token_request)
        except ValidationError as e:
            raise InvalidRequestException()

        # 2. validate client
        client = await self.get_client(cc.client_id)
        cc.validate_client(client)

        # 3. generate token
        token_data = cc.token_data()
        access_token = self.token_service.jwt_token(token_data, timedelta(minutes=15))
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=15 * 60,
            scope=cc.scope,
        )
