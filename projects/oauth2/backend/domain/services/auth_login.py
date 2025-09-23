
from typing import Optional

from .user_service import UserService

from ...impl.auth import (
    AuthorizationCodeClient,
    AuthorizationCodeClientConfig,
    Token,
    MissingTokenError,
    TokenExpiredError,
    InvalidTokenError,
    UnsupportedTokenTypeError,
    MismatchingStateError,
)

from ...impl.session_manager import Session, SessionManager


class OAuthLoginServiceConfig(AuthorizationCodeClientConfig):
    provider: str


class OAuthLoginService:
    # oauth2 auth code login flow
    def __init__(
        self,
        cfg: OAuthLoginServiceConfig,
        client: AuthorizationCodeClient,
        session_manager: SessionManager,
        user_service: UserService,
    ):
        self.cfg = cfg
        self.auth_provider = cfg.provider
        self.client = client
        self.session_manager = session_manager
        self.user_service = user_service

    async def login(self, return_to: Optional[str] = None) -> str:
        """生成 OAuth2 授权 URL"""
        uri, state = self.client.create_authorization_url()
        await self.session_manager.set_state(state)
        return uri

    async def callback(self, code: str, state: str) -> Session:
        """处理 OAuth2 回调"""
        # 1. 验证 state 参数
        state_data = await self.session_manager.get_state(state)
        if not state_data:
            raise MismatchingStateError()
        # 2. 获取 token
        token = await self.client.get_token(code)
        # 3. 获取用户信息
        user_info = await self.client.get_user_info(token.access_token)
        # 4. 获取或创建用户
        user = await self.user_service.get_or_create_user(
            self.auth_provider,
            user_info.id,
            username=user_info.username,
            user_info=user_info.model_dump(),
            token=token.model_dump(),
        )
        # 5. 存储令牌和用户信息到会话
        session = await self.session_manager.new_session(str(user.uuid))
        return session
