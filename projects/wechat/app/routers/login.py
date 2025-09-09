import pathlib
import random
import string
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

from ..dependencies import (
    get_login_service,
    WechatLoginService,
    get_current_user,
    UserInfo,
)
from ...domain.models.session import QRCodeStatus, UserInfo

# 初始化模板引擎

templates_dir = pathlib.Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


router = APIRouter(tags=["Login"])


class ScanRequest(BaseModel):
    """扫描请求模型"""

    session_id: str
    user_index: Optional[int] = None  # 指定用户索引，如果不指定则随机选择
    openid: Optional[str] = None  # 指定openid，优先级高于user_index


class ConfirmRequest(BaseModel):
    """确认请求模型"""

    session_id: str


class CancelRequest(BaseModel):
    """取消请求模型"""

    session_id: str


@router.get("/connect/qrconnect", response_class=HTMLResponse)
async def get_qr_connect_page(
    request: Request,
    appid: str,
    redirect_uri: str = "http://127.0.0.1:8000/callback",
    scope: str = "snsapi_login",
    state: str = "",
    login_service: WechatLoginService = Depends(get_login_service),
):
    if scope != "snsapi_login":
        raise HTTPException(status_code=400, detail="Invalid scope for QR connect")

    session = await login_service.create_qr_session(appid, redirect_uri, state)
    # 使用模板渲染页面
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "session_id": session.session_id,
            "redirect_uri": session.redirect_uri,
            "state_param": session.state,
            "app_id": session.app_id,
        },
    )


@router.get("/status")
async def get_status(
    session_id: str, login_service: WechatLoginService = Depends(get_login_service)
):
    """获取会话状态"""
    session = await login_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 检查是否过期
    if session.is_expired() and session.status not in [
        QRCodeStatus.CONFIRMED,
        QRCodeStatus.CANCELLED,
    ]:
        session.mark_expired()
        await login_service.update_session(session)

    return session.to_dict()


@router.post("/simulate/scan")
async def simulate_scan(
    request: ScanRequest,
    user_info: UserInfo = Depends(get_current_user),
    login_service: WechatLoginService = Depends(get_login_service),
):
    """
    模拟用户扫描二维码
    将会话状态从UNSCANNED改为SCANNED
    支持指定用户或随机选择用户
    """
    session = await login_service.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.can_scan():
        raise HTTPException(
            status_code=400,
            detail=f"Session cannot be scanned. Current status: {session.status.value}",
        )

    updated_session = await login_service.mark_scanned(request.session_id, user_info)
    if not updated_session:
        raise HTTPException(status_code=500, detail="Failed to update session")

    print(
        f"Simulated SCAN for session: {request.session_id} with user: {user_info.nickname}"
    )
    return {
        "message": "扫描成功，等待确认",
        "session_id": request.session_id,
        "user_info": user_info.model_dump(),
        "selected_method": (
            "openid"
            if request.openid
            else ("index" if request.user_index is not None else "random")
        ),
    }


@router.post("/simulate/confirm")
async def simulate_confirm(
    request: ConfirmRequest,
    user_info: UserInfo = Depends(get_current_user),
    login_service: WechatLoginService = Depends(get_login_service),
):
    """
    模拟用户确认登录
    将会话状态改为CONFIRMED并生成一次性code
    """
    session = await login_service.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.can_confirm():
        raise HTTPException(
            status_code=400,
            detail=f"Session cannot be confirmed. Current status: {session.status.value}",
        )

    # 使用 WechatLoginService 的 mark_confirmed 方法，它会自动生成 code
    updated_session = await login_service.mark_confirmed(request.session_id)
    if not updated_session:
        raise HTTPException(status_code=500, detail="Failed to update session")

    print(
        f"Simulated CONFIRM for session: {request.session_id}. Generated code: {updated_session.auth_code}"
    )

    # 获取用户信息用于返回
    user_info = updated_session.user_info if updated_session.user_info else None

    return {
        "message": "确认成功，正在重定向...",
        "session_id": request.session_id,
        "code": updated_session.auth_code,
        "user_info": user_info.model_dump() if user_info else None,
        "redirect_url": f"{updated_session.redirect_uri}?code={updated_session.auth_code}&state={updated_session.state}",
    }


@router.post("/simulate/cancel")
async def simulate_cancel(
    request: CancelRequest,
    login_service: WechatLoginService = Depends(get_login_service),
):
    """
    模拟用户取消登录
    将会话状态改为CANCELLED
    """
    session = await login_service.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.can_cancel():
        raise HTTPException(
            status_code=400,
            detail=f"Session cannot be cancelled. Current status: {session.status.value}",
        )

    updated_session = await login_service.mark_cancelled(request.session_id)
    if not updated_session:
        raise HTTPException(status_code=500, detail="Failed to update session")

    print(f"Simulated CANCEL for session: {request.session_id}")
    return {"message": "登录已取消", "session_id": request.session_id}


@router.get("/callback")
async def callback_page(request: Request, code: str, state: str):
    """回调页面，显示登录结果"""
    return templates.TemplateResponse(
        "callback.html",
        {
            "request": request,
            "code": code,
            "state": state,
        },
    )
