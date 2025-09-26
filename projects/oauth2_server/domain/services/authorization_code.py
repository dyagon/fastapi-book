from datetime import timedelta, datetime, timezone
from pydantic import BaseModel, ValidationError

from urllib.parse import urlencode

from .oauth2_service import OAuth2Service
from .token_service import TokenService
from ...impl.repo import ClientRepo, UserRepo
from ..models.token import TokenRequest, TokenResponse, AuthorizationCode
from ..models.auth import AuthorizeRequestQuery, AuthorizeRequestForm
from ..models.user import UserInDB
from ..exception import InvalidRequestException, UnauthorizedClientException



class AuthCodeData(BaseModel):
    user_id: str
    client_id: str
    redirect_uri: str
    scope: str
    code_challenge: str
    code_challenge_method: str


class AuthorizationCodeFlowService(OAuth2Service):

    def __init__(
        self, client_repo: ClientRepo, user_repo: UserRepo, token_service: TokenService
    ):
        super().__init__(client_repo, token_service)
        self.user_repo = user_repo

    async def handle_token_request(self, token_request: TokenRequest) -> TokenResponse:
        # 1. check paramters
        try:
            authorization_code = AuthorizationCode.model_validate(token_request)
        except ValidationError as e:
            raise InvalidRequestException()

        client = await self.get_client(authorization_code.client_id)
        authorization_code.validate_client(client)

        data = await self.token_service.get_code(authorization_code.code)
        if not data:
            raise UnauthorizedClientException(
                f"Invalid code: {authorization_code.code}"
            )

        auth_code_data = AuthCodeData.model_validate(data)

        user_id = auth_code_data.user_id

        token_data = {
            "sub": user_id,
            "scope": auth_code_data.scope,
            "client_id": auth_code_data.client_id,
        }

        access_token = self.token_service.jwt_token(token_data, timedelta(minutes=15))
        refresh_token_data = {
            "user_id": user_id,
            "client_id": auth_code_data.client_id,
            "scope": auth_code_data.scope,
            "issue_at": datetime.now(timezone.utc).isoformat(),
        }
        refresh_token = await self.token_service.opaque_token(
            refresh_token_data, timedelta(days=7)
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=15 * 60,
            scope=auth_code_data.scope,
        )

    async def validate_authorize_request(self, auth_request: AuthorizeRequestQuery):

        client = await self.get_client(auth_request.client_id)

        invalid_scopes = auth_request.invalid_scopes(client.scopes)
        if invalid_scopes:
            raise UnauthorizedClientException(f"Invalid scope: {invalid_scopes}")

        if not auth_request.scope:
            auth_request.scope = " ".join(client.scopes)

        if client.is_public_client():
            if not auth_request.code_challenge:
                raise UnauthorizedClientException(
                    f"Invalid code_challenge: {auth_request.code_challenge}"
                )
            if auth_request.code_challenge_method not in ["plain", "S256"]:
                raise UnauthorizedClientException(
                    f"Invalid code_challenge_method: {auth_request.code_challenge_method}"
                )

    async def validate_authorize_form_request(self, auth_request: AuthorizeRequestForm):
        """验证授权请求，支持AuthorizeFormRequest"""
        if not auth_request.scope:
            raise UnauthorizedClientException(f"scope must be provided")

        client = await self.get_client(auth_request.client_id)
        invalid_scopes = auth_request.invalid_scopes(client.scopes)
        if invalid_scopes:
            raise UnauthorizedClientException(f"Invalid scope: {invalid_scopes}")

        if client.is_public_client():
            if not auth_request.code_challenge:
                raise UnauthorizedClientException(
                    f"Invalid code_challenge: {auth_request.code_challenge}"
                )
            if auth_request.code_challenge_method not in ["plain", "S256"]:
                raise UnauthorizedClientException(
                    f"Invalid code_challenge_method: {auth_request.code_challenge_method}"
                )

    async def authenticate_user(self, username: str, password: str) -> UserInDB:
        user = await self.user_repo.get_user(username)
        if user.verify_password(password):
            return user
        raise UnauthorizedClientException("Invalid username or password")

    async def generate_authorization_code(
        self, auth_request: AuthorizeRequestForm
    ) -> str:
        # 验证用户凭据
        user = await self.authenticate_user(
            auth_request.username, auth_request.password
        )

        # 检查用户是否同意授权
        if not auth_request.consent:
            # 用户拒绝授权，重定向到错误页面
            error_params = {
                "error": "access_denied",
                "error_description": "用户拒绝了授权请求",
            }
            if auth_request.state:
                error_params["state"] = auth_request.state

            redirect_url = f"{auth_request.redirect_uri}?{urlencode(error_params)}"
            return redirect_url

        # 生成授权码

        auth_code_data = AuthCodeData(
            user_id=user.id,
            client_id=auth_request.client_id,
            redirect_uri=auth_request.redirect_uri,
            scope=auth_request.scope,
            code_challenge=auth_request.code_challenge,
            code_challenge_method=auth_request.code_challenge_method,
        )
        data = auth_code_data.model_dump()
        auth_code = await self.token_service.generate_code(data, timedelta(minutes=5))

        # 构建成功重定向URL
        success_params = {"code": auth_code}
        if auth_request.state:
            success_params["state"] = auth_request.state

        redirect_url = f"{auth_request.redirect_uri}?{urlencode(success_params)}"
        return redirect_url
