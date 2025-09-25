from datetime import timedelta, datetime, timezone
from urllib.parse import urlencode

from pydantic import BaseModel

from .models.user import UserInDB
from ..impl.token_manager import TokenManager

from .models import Client, TokenRequest, TokenResponse
from .models.token import AuthorizationCode, ClientCredentials, TokenIssuer
from .models.auth import AuthorizeRequestQuery, AuthorizeRequestForm
from ..impl.repo import ClientRepo, UserRepo
from .exception import UnauthorizedClientException, InvalidGrantException


class AuthCodeData(BaseModel):
    user_id: str
    client_id: str
    redirect_uri: str
    scope: str
    code_challenge: str
    code_challenge_method: str


class OAuth2Service:

    def __init__(
        self, client_repo: ClientRepo, user_repo: UserRepo, token_manager: TokenManager
    ):
        self.client_repo = client_repo
        self.user_repo = user_repo
        self.token_manager = token_manager

    async def get_client(self, client_id: str) -> Client:
        client = await self.client_repo.get_client(client_id)
        if not client:
            raise UnauthorizedClientException(f"Client {client_id} not found")
        return client

    async def handle_token_request(self, token_request: TokenRequest) -> TokenResponse:
        if token_request.grant_type == "client_credentials":
            client_credentials = ClientCredentials.model_validate(token_request)
            return await self.handle_client_credentials(client_credentials)
        elif token_request.grant_type == "authorization_code":
            authorization_code = AuthorizationCode.model_validate(token_request)
            return await self.handle_authorization_code(authorization_code)
        elif token_request.grant_type == "refresh_token":
            refresh_token = RefreshToken.model_validate(token_request)
            return await self.handle_refresh_token(refresh_token)
        else:
            raise UnauthorizedClientException(
                f"Unsupported grant type: {token_request.grant_type}"
            )

    async def handle_client_credentials(
        self, client_credentials: ClientCredentials
    ) -> TokenResponse:
        client = await self.get_client(client_credentials.client_id)
        client_credentials.validate_client(client)
        token_data = client_credentials.token_data()
        access_token = self.token_manager.jwt_token(token_data, timedelta(minutes=15))
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=15 * 60,
            scope=client_credentials.scope,
        )

    async def handle_authorization_code(
        self, authorization_code: AuthorizationCode
    ) -> TokenResponse:
        client = await self.get_client(authorization_code.client_id)
        authorization_code.validate_client(client)

        data = await self.token_manager.get_code(authorization_code.code)
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

        access_token = self.token_manager.jwt_token(token_data, timedelta(minutes=15))
        refresh_token_data = {
            "user_id": user_id,
            "client_id": auth_code_data.client_id,
            "scope": auth_code_data.scope,
            "issue_at": datetime.now(timezone.utc).isoformat(),
        }
        refresh_token = await self.token_manager.opaque_token(
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
        """验证授权请求，支持AuthorizeRequestQuery和AuthorizeFormRequest"""

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
        auth_code = await self.token_manager.generate_code(data, timedelta(minutes=5))

        # 构建成功重定向URL
        success_params = {"code": auth_code}
        if auth_request.state:
            success_params["state"] = auth_request.state

        redirect_url = f"{auth_request.redirect_uri}?{urlencode(success_params)}"
        return redirect_url
