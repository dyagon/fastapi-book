"""OAuth2 路由"""
import pathlib
import secrets
from urllib.parse import urlencode, parse_qs
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

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


@router.get("/authorize", response_class=HTMLResponse)
async def authorize(
    request: Request,
    redirect_uri: str = Query(..., description="回调地址"),
    scope: str = Query(default="snsapi_userinfo", description="授权范围"),
    state: str = Query(None, description="状态参数"),
    db: Session = Depends(get_db),
):
    """OAuth2 授权页面"""
    # 验证redirect_uri
    if not redirect_uri:
        raise HTTPException(status_code=400, detail="缺少redirect_uri参数")
    
    return templates.TemplateResponse("oauth_authorize.html", {
        "request": request,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "app_name": "微信模拟授权服务"
    })


@router.post("/authorize")
async def authorize_submit(
    request: Request,
    redirect_uri: str = Query(..., description="回调地址"),
    scope: str = Query(default="snsapi_userinfo", description="授权范围"),
    state: str = Query(None, description="状态参数"),
    db: Session = Depends(get_db),
):
    """处理授权提交"""
    # 生成授权码
    auth_code = f"auth_code_{secrets.token_hex(16)}"
    
    # 构建回调URL
    callback_params = {
        "code": auth_code,
        "state": state
    }
    
    # 添加redirect_uri参数
    callback_url = f"{redirect_uri}?{urlencode(callback_params)}"
    
    # 重定向到回调URL
    return RedirectResponse(url=callback_url, status_code=302)


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="授权码"),
    state: str = Query(None, description="状态参数"),
    db: Session = Depends(get_db),
):
    """OAuth2 回调端点"""
    oauth_service = OAuthService(db)

    try:
        # 使用授权码换取访问令牌
        token_response = await oauth_service.exchange_code_for_token(code)

        return {
            "access_token": token_response.access_token,
            "expires_in": token_response.expires_in,
            "scope": token_response.scope,
            "openid": token_response.openid,
            "message": "授权成功",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/userinfo")
async def get_user_info(
    access_token: str = Query(..., description="访问令牌"),
    openid: str = Query(..., description="用户openid"),
    db: Session = Depends(get_db),
):
    """获取用户信息"""
    oauth_service = OAuthService(db)

    # 验证访问令牌
    token_record = oauth_service.validate_access_token(access_token)
    if not token_record:
        raise HTTPException(status_code=401, detail="无效的访问令牌")

    try:
        user_info = await oauth_service.get_user_info(access_token, openid)
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


@router.get("/demo", response_class=HTMLResponse)
async def oauth_demo(request: Request):
    """OAuth2 流程演示页面"""
    return templates.TemplateResponse("oauth_demo.html", {
        "request": request
    })


@router.get("/test")
async def test_oauth_flow(db: Session = Depends(get_db)):
    """测试OAuth流程（模拟环境专用）"""
    oauth_service = OAuthService(db)

    # 模拟完整的OAuth流程
    try:
        # 1. 生成授权URL
        authorize_url = oauth_service.generate_authorize_url(
            redirect_uri="http://localhost:8000/wechat/oauth/callback",
            scope="snsapi_userinfo",
        )

        # 2. 模拟授权码换取令牌
        mock_code = "auth_code_mock_test_123"
        token_response = await oauth_service.exchange_code_for_token(mock_code)

        # 3. 获取用户信息
        user_info = await oauth_service.get_user_info(
            token_response.access_token, token_response.openid
        )

        return {
            "authorize_url": authorize_url,
            "token_response": token_response,
            "user_info": user_info,
            "message": "OAuth流程测试完成",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
