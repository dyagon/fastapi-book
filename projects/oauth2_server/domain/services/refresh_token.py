

from datetime import timedelta
from pydantic import ValidationError

from .oauth2_service import OAuth2Service
from .token_service import TokenService
from ...impl.repo import ClientRepo
from ..models.token import TokenRequest, TokenResponse, RefreshToken
from ..exception import InvalidRequestException, UnauthorizedClientException



class RefreshTokenFlowService(OAuth2Service):

    async def handle_token_request(self, token_request: TokenRequest) -> TokenResponse:
        # 1. check paramters
        try:
            rt = RefreshToken.model_validate(token_request)
        except ValidationError as e:
            raise InvalidRequestException()

        # 2. validate client
        client = await self.get_client(rt.client_id)
        rt.validate_client(client)

        # 3. generate token
        token_data = rt.token_data()
        access_token = self.token_service.jwt_token(token_data, timedelta(minutes=15))
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=15 * 60,
            scope=rt.scope,
        )