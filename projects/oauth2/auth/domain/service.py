
import secrets
from urllib.parse import urlencode

from projects.oauth2.auth.domain.models.user import UserInDB

from .models import Client, TokenRequest, TokenResponse
from .models.client_credentials import ClientCredentials
from .models.auth import AuthorizeRequestQuery, AuthorizeRequestForm
from .repo import ClientRepo, UserRepo
from .exception import UnauthorizedClientException, InvalidGrantException



class OAuth2Service:

    def __init__(self, client_repo: ClientRepo, user_repo: UserRepo):
        self.client_repo = client_repo
        self.user_repo = user_repo

    def get_client(self, client_id: str) -> Client:
        client = self.client_repo.get_client(client_id)
        if not client:
            raise UnauthorizedClientException(f"Client {client_id} not found")
        return client

    def handle_token_request(self, token_request: TokenRequest) -> TokenResponse:
        if token_request.grant_type == "client_credentials":
            client_credentials = ClientCredentials.model_validate(token_request)
        else:
            raise UnauthorizedClientException(f"Unsupported grant type: {token_request.grant_type}")
        
        client = self.get_client(client_credentials.client_id)
        client_credentials.validate_client(client)
        return client_credentials.issue_token(client)

    def validate_authorize_request(self, auth_request: AuthorizeRequestQuery):
        """验证授权请求，支持AuthorizeRequestQuery和AuthorizeFormRequest"""
        if not auth_request.scope:
            raise UnauthorizedClientException(f"scope must be provided")

        client = self.get_client(auth_request.client_id)

        invalid_scopes = auth_request.invalid_scopes(client.scopes)
        if invalid_scopes:
            raise UnauthorizedClientException(f"Invalid scope: {invalid_scopes}")

        if client.is_public_client():
            if not auth_request.code_challenge:
                raise UnauthorizedClientException(f"Invalid code_challenge: {auth_request.code_challenge}")
            if auth_request.code_challenge_method not in ["plain", "S256"]:
                raise UnauthorizedClientException(f"Invalid code_challenge_method: {auth_request.code_challenge_method}")

    def validate_authorize_form_request(self, auth_request: AuthorizeRequestForm):
        """验证授权请求，支持AuthorizeFormRequest"""
        if not auth_request.scope:
            raise UnauthorizedClientException(f"scope must be provided")
        
        client = self.get_client(auth_request.client_id)
        invalid_scopes = auth_request.invalid_scopes(client.scopes)
        if invalid_scopes:
            raise UnauthorizedClientException(f"Invalid scope: {invalid_scopes}")
        
        if client.is_public_client():
            if not auth_request.code_challenge:
                raise UnauthorizedClientException(f"Invalid code_challenge: {auth_request.code_challenge}")
            if auth_request.code_challenge_method not in ["plain", "S256"]:
                raise UnauthorizedClientException(f"Invalid code_challenge_method: {auth_request.code_challenge_method}")


    def authenticate_user(self, username: str, password: str) -> UserInDB:
        user = self.user_repo.get_user(username)
        if user.verify_password(password):
            return user
        raise UnauthorizedClientException("Invalid username or password")

    def generate_authorization_code(self, auth_request: AuthorizeRequestForm) -> str:
        """生成授权码并处理用户授权决定"""
        # 验证用户凭据
        user = self.authenticate_user(auth_request.username, auth_request.password)
        
        # 检查用户是否同意授权
        if not auth_request.consent:
            # 用户拒绝授权，重定向到错误页面
            error_params = {
                "error": "access_denied",
                "error_description": "用户拒绝了授权请求"
            }
            if auth_request.state:
                error_params["state"] = auth_request.state
            
            redirect_url = f"{auth_request.redirect_uri}?{urlencode(error_params)}"
            return redirect_url
        
        # 生成授权码
        auth_code = secrets.token_urlsafe(32)
        
        # 这里应该将授权码存储到数据库或缓存中，关联用户和客户端信息
        # 为了简化，这里直接返回带授权码的重定向URL
        
        # 构建成功重定向URL
        success_params = {
            "code": auth_code
        }
        if auth_request.state:
            success_params["state"] = auth_request.state
        
        redirect_url = f"{auth_request.redirect_uri}?{urlencode(success_params)}"
        return redirect_url
