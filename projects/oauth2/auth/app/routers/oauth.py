import pathlib

from typing import Optional, Literal
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi.security import HTTPBasicCredentials, HTTPBasic

from ...domain.models import TokenRequest, TokenResponse
from ...domain.exception import InvalidRequestException
from ...domain.models.auth import AuthorizeRequestForm, AuthorizeRequestQuery

from ..depends import get_oauth2_service, OAuth2Service


template_dir = pathlib.Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

router = APIRouter(tags=["OAuth2"])

# HTTP Basic Authentication for client credentials
security = HTTPBasic(auto_error=False)


# OAuth2 Token Endpoint
@router.post("/token", response_model=TokenResponse)
async def get_token(
    # 使用 Form 参数接收 OAuth2 token 请求
    grant_type: Literal[
        "authorization_code", "client_credentials", "refresh_token"
    ] = Form(...),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    basic_credentials: Optional[HTTPBasicCredentials] = Depends(security),
    oauth2_service: OAuth2Service = Depends(get_oauth2_service),
):
    # 优先使用 HTTP Basic Auth，如果没有则使用 Form 参数
    if basic_credentials and basic_credentials.username:
        # 从 HTTP Basic Auth 获取客户端凭据
        final_client_id = basic_credentials.username
        final_client_secret = basic_credentials.password
    elif client_id:
        # 从 Form 参数获取客户端凭据
        final_client_id = client_id
        final_client_secret = client_secret
    else:
        # 没有提供客户端认证信息
        raise InvalidRequestException("Client authentication required")

    # 创建 TokenRequest 对象
    token_request = TokenRequest(
        grant_type=grant_type,
        client_id=final_client_id,
        client_secret=final_client_secret,
        scope=scope,
        redirect_uri=redirect_uri,
        code=code,
        code_verifier=code_verifier,
        refresh_token=refresh_token,
    )
    return await oauth2_service.handle_token_request(token_request)


@router.get("/authorize")
async def authorize(
    request: Request,
    auth_request: AuthorizeRequestQuery = Depends(),
    oauth2_service: OAuth2Service = Depends(get_oauth2_service),
):

    await oauth2_service.validate_authorize_request(auth_request)

    # Show login form
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "client_id": auth_request.client_id,
            "redirect_uri": auth_request.redirect_uri,
            "response_type": auth_request.response_type,
            "state": auth_request.state or "",
            "scope": auth_request.scope,
            "code_challenge": auth_request.code_challenge or "",
            "code_challenge_method": auth_request.code_challenge_method or "",
        },
    )


@router.post("/authorize")
async def authorize(
    username: str = Form(...),
    password: str = Form(...),
    consent: bool = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    code_challenge: Optional[str] = Form(None),
    code_challenge_method: Optional[str] = Form(None),
    oauth2_service: OAuth2Service = Depends(get_oauth2_service),
):
    try:
        auth_request = AuthorizeRequestForm(
            username=username,
            password=password,
            consent=consent,
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        # 打印提交的授权信息
        print("=== 授权请求信息 ===")
        print(f"用户名: {auth_request.username}")
        print(f"客户端ID: {auth_request.client_id}")
        print(f"重定向URI: {auth_request.redirect_uri}")
        print(f"权限范围: {auth_request.scope}")
        print(f"用户同意: {auth_request.consent}")
        print(f"状态参数: {auth_request.state}")
        print(f"代码挑战: {auth_request.code_challenge}")
        print(f"代码挑战方法: {auth_request.code_challenge_method}")
        print("==================")

        # 验证授权请求
        await oauth2_service.validate_authorize_form_request(auth_request)

        # 生成授权码并处理用户授权决定
        redirect_url = await oauth2_service.generate_authorization_code(auth_request)

        print(f"重定向URL: {redirect_url}")

        return RedirectResponse(
            url=redirect_url,
            status_code=302,
        )
    except Exception as e:
        print(f"授权处理错误: {e}")
        # 处理错误情况，重定向到错误页面
        error_params = {"error": "server_error", "error_description": str(e)}
        if auth_request.state:
            error_params["state"] = auth_request.state

        from urllib.parse import urlencode

        error_url = f"{auth_request.redirect_uri}?{urlencode(error_params)}"
        return RedirectResponse(
            url=error_url,
            status_code=302,
        )
