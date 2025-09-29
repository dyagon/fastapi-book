from fastapi import APIRouter, Request, HTTPException

from typing import Optional, Dict, Any

import httpx

from ..service import get_local_oauth_info
from ...domain.exceptions import NotAuthenticatedException, SessionExpiredException
from ...context import Container

router = APIRouter()

# RESOURCE_SERVER_BASE_URL = config.RESOURCE_SERVER_BASE_URL

@router.get("/api/user-info")
async def api_user_info(request: Request):
    """Call the user info API."""
    session_service = Container.session_service()
    session = await session_service.check_session(request.session)
    if not session:
        raise SessionExpiredException()
    login_service = Container.auth_login_service()
    auth_info = await login_service.get_oauth_info(session)
    if not auth_info:
        raise NotAuthenticatedException()
    ac_client = Container.ac_client()
    user_info = await ac_client.get_user_info(auth_info.token.access_token)
    return { "auth_info": auth_info, "user_info": user_info }

@router.get("/api/admin-info")
async def api_admin_info(request: Request):
    session_service = Container.session_service()
    session = await session_service.check_session(request.session)
    if not session:
        raise SessionExpiredException()
    login_service = Container.auth_login_service()
    auth_info = await login_service.get_oauth_info(session)
    if not auth_info:
        raise NotAuthenticatedException()
    ac_client = Container.ac_client()
    admin_info = await ac_client.get_admin_info(auth_info.token.access_token)
    return {"auth": auth_info, "admin_info": admin_info }

@router.get("/api/refresh")
async def api_refresh_token(request: Request):
    """Refresh access token."""
    session_service = Container.session_service()
    session = await session_service.check_session(request.session)
    if not session:
        raise SessionExpiredException()

    login_service = Container.auth_login_service()
    await login_service.refresh_token(session)

    return "OK"