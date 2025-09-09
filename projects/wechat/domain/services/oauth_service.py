"""OAuth2 服务"""
import secrets
import hashlib
import hmac
import time
from typing import Optional, Dict, Any
from urllib.parse import urlencode, parse_qs
import httpx
from sqlalchemy.orm import Session
from ...infra.config import config
from ..models import User, OAuthToken
from app.dto import AccessTokenResponse, UserInfoResponse


class OAuthService:
    """OAuth2 服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config = config

    
    def generate_authorize_url(self, redirect_uri: str, scope: str = "snsapi_userinfo", state: Optional[str] = None) -> str:
        """生成授权URL"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state
        }
        
        # 使用我们自己的授权页面
        base_url = "http://localhost:8000/wechat/oauth/authorize"
        return f"{base_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> AccessTokenResponse:
        """使用授权码换取访问令牌"""
        # 验证授权码格式
        if not code.startswith("auth_code_"):
            raise ValueError("无效的授权码")
        
        # 模拟微信API调用
        async with httpx.AsyncClient() as client:
            params = {
                "appid": self.config.app_id,
                "secret": self.config.app_secret,
                "code": code,
                "grant_type": "authorization_code"
            }
            
            # 模拟API响应 - 使用固定的用户信息
            mock_response = {
                "access_token": f"ACCESS_TOKEN_{secrets.token_hex(16)}",
                "expires_in": 7200,
                "refresh_token": f"REFRESH_TOKEN_{secrets.token_hex(16)}",
                "scope": "snsapi_userinfo",
                "openid": "mock_openid_123456"  # 固定的openid
            }
        
        # 保存令牌到数据库
        token_record = OAuthToken(
            access_token=mock_response["access_token"],
            refresh_token=mock_response["refresh_token"],
            openid=mock_response["openid"],
            scope=mock_response["scope"],
            expires_in=mock_response["expires_in"],
            expires_at=time.time() + mock_response["expires_in"]
        )
        
        self.db.add(token_record)
        self.db.commit()
        
        return AccessTokenResponse(**mock_response)
    
    async def get_user_info(self, access_token: str, openid: str) -> UserInfoResponse:
        """获取用户信息"""
        # 在真实环境中，这里应该调用微信API
        # 这里我们模拟返回固定的用户信息
        
        mock_user_info = {
            "openid": openid,
            "nickname": "微信模拟用户",
            "sex": 1,
            "province": "广东",
            "city": "深圳",
            "country": "中国",
            "headimgurl": "https://via.placeholder.com/100x100?text=微",
            "privilege": [],
            "unionid": "mock_unionid_123456"
        }
        
        # 保存或更新用户信息到数据库
        user = self.db.query(User).filter(User.openid == openid).first()
        if not user:
            user = User(
                openid=openid,
                unionid=mock_user_info.get("unionid"),
                nickname=mock_user_info["nickname"],
                avatar_url=mock_user_info["headimgurl"],
                gender=mock_user_info["sex"],
                city=mock_user_info["city"],
                province=mock_user_info["province"],
                country=mock_user_info["country"]
            )
            self.db.add(user)
        else:
            user.nickname = mock_user_info["nickname"]
            user.avatar_url = mock_user_info["headimgurl"]
            user.gender = mock_user_info["sex"]
            user.city = mock_user_info["city"]
            user.province = mock_user_info["province"]
            user.country = mock_user_info["country"]
            user.unionid = mock_user_info.get("unionid")
        
        self.db.commit()
        
        return UserInfoResponse(**mock_user_info)
    
    def validate_access_token(self, access_token: str) -> Optional[OAuthToken]:
        """验证访问令牌"""
        token_record = self.db.query(OAuthToken).filter(
            OAuthToken.access_token == access_token
        ).first()
        
        if token_record and token_record.expires_at > time.time():
            return token_record
        
        return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[AccessTokenResponse]:
        """刷新访问令牌"""
        # 在真实环境中，这里应该调用微信API
        # 这里我们模拟刷新令牌
        
        token_record = self.db.query(OAuthToken).filter(
            OAuthToken.refresh_token == refresh_token
        ).first()
        
        if not token_record:
            return None
        
        # 生成新的访问令牌
        new_access_token = f"ACCESS_TOKEN_{secrets.token_hex(16)}"
        new_refresh_token = f"REFRESH_TOKEN_{secrets.token_hex(16)}"
        
        # 更新数据库记录
        token_record.access_token = new_access_token
        token_record.refresh_token = new_refresh_token
        token_record.expires_at = time.time() + 7200
        
        self.db.commit()
        
        return AccessTokenResponse(
            access_token=new_access_token,
            expires_in=7200,
            refresh_token=new_refresh_token,
            scope=token_record.scope,
            openid=token_record.openid
        )
