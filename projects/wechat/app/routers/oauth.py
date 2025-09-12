"""OAuth2 路由"""
import pathlib
import secrets
from urllib.parse import urlencode, parse_qs
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..dependencies import get_db, get_oauth_service, OAuthService
from ..dto import (
    OAuthAuthorizeRequest,
    OAuthCallbackRequest,
    AccessTokenResponse,
    UserInfoResponse,
    ErrorResponse,
)

router = APIRouter(tags=["OAuth2"])

# 创建模板实例
templates = Jinja2Templates(directory="templates")


class TokenRequest(BaseModel):
    """令牌交换请求"""
    code: str
    state: str = None



@router.post("/oauth/token")
async def exchange_token(
    request: TokenRequest,
    db: Session = Depends(get_db),
):
    """使用授权码交换访问令牌"""
    oauth_service = OAuthService(db)
    
    try:
        # 使用授权码换取访问令牌
        token_response = await oauth_service.exchange_code_for_token(request.code)
        
        return {
            "access_token": token_response.access_token,
            "expires_in": token_response.expires_in,
            "scope": token_response.scope,
            "openid": token_response.openid,
            "token_type": "Bearer",
            "message": "令牌获取成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/userinfo")
async def get_user_info_with_token(
    authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_db),
):
    """使用Bearer token获取用户信息"""
    # 解析Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的授权头格式")
    
    access_token = authorization[7:]  # 移除"Bearer "前缀
    
    oauth_service = OAuthService(db)
    
    # 验证访问令牌
    token_record = oauth_service.validate_access_token(access_token)
    if not token_record:
        raise HTTPException(status_code=401, detail="无效的访问令牌")
    
    try:
        user_info = await oauth_service.get_user_info(access_token, token_record.openid)
        return user_info
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Query(..., description="刷新令牌"),
    db: Session = Depends(get_db),
):
    """刷新访问令牌"""
    oauth_service = OAuthService(db)

    try:
        new_token = oauth_service.refresh_access_token(refresh_token)
        if not new_token:
            raise HTTPException(status_code=401, detail="无效的刷新令牌")

        return new_token

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
