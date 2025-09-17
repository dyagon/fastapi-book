import secrets
import httpx
import json
from urllib.parse import urlencode, quote
from typing import Optional, Dict, Any
from datetime import datetime, timezone

# from ...impl.auth_client import AuthCodeClient
from ...impl.session_manager import SessionManager
from .user_service import UserService


class OAuthLoginService:
    # oauth2 auth code login flow

    def __init__(
        self,
        # auth_code_client: AuthCodeClient,
        session_manager: SessionManager,
        user_service: UserService,
    ):
        self.client = auth_code_client
        self.session_manager = session_manager
        self.user_service = user_service

    async def login(self, return_to: Optional[str] = None) -> str:
        """生成 OAuth2 授权 URL"""
        state = await self.session_manager.new_state()
        return self.client.make_auth_url(state)

    async def callback(self, code: str, state: str) -> Dict[str, Any]:
        """处理 OAuth2 回调"""
        try:
            # 1. 验证 state 参数
            if not await self.session_manager.validate_state(state):
                return {"success": False, "error": "Invalid or expired state parameter"}

            # 2. 使用授权码换取访问令牌
            tokens = await self.client.exchange_code_for_tokens(code)
            if not tokens:
                return {"success": False, "error": "Failed to exchange code for tokens"}
            print(tokens)

            # 3. 使用访问令牌获取用户信息
            user_info = await self.client.get_user_info(tokens["access_token"])
            if not user_info:
                return {"success": False, "error": "Failed to get user information"}

            print(user_info)

            # 4. 获取或创建用户
            self.user_service.create_user
            user = self._get_or_create_user(user_info)

            # 5. 存储令牌和用户信息到会话
            session_id = secrets.token_urlsafe(32)
            self._store_session_data(session_id, tokens, user)

            # 6. 获取重定向 URL 并清理 state
            state_data = self._state_storage.get(state, {})
            return_to = state_data.get("return_to", "/")
            self._cleanup_state(state)

            return {
                "success": True,
                "redirect_url": return_to,
                "user": user,
                "tokens": {
                    "access_token": tokens["access_token"],
                    "token_type": tokens.get("token_type", "Bearer"),
                    "expires_in": tokens.get("expires_in"),
                    "scope": tokens.get("scope"),
                },
            }

        except Exception as e:
            # 清理 state 以防出错
            self._cleanup_state(state)
            return {"success": False, "error": f"Callback processing failed: {str(e)}"}
