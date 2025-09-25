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
    session_manager = Container.session_manager()
    session = await session_manager.get_session(request.session)
    print(session)
    if not session:
        raise NotAuthenticatedException()
    async with Container.auth_login_service() as auth_login_service:
        auth_info = await auth_login_service.get_oauth_info(session)
    # if not auth_info:
    #     raise NotAuthenticatedException()
    # ac_client = Container.ac_client()
    # user_info = await ac_client.get_user_info(auth_info.token.access_token)
    return { "auth_info": auth_info }

@router.get("/api/admin-info")
async def api_admin_info(request: Request):
    session_data = request.session
    user, auth_info = await get_local_oauth_info(session_data, "local-oauth")
    if not user or not auth_info:
        raise HTTPException(status_code=401, detail="Not authenticated")
    ac_client = Container.ac_client()
    user_info = await ac_client.get_user_info(auth_info.access_token)
    return { "user": user, "auth": auth_info, "user_info": user_info }

@router.get("/api/refresh")
async def api_refresh_token(request: Request):
    """Refresh access token."""
    session_data = get_current_session(request)
    if not session_data or "refresh_token" not in session_data:
        raise HTTPException(status_code=400, detail="No refresh token available")
    
    token_url = f"{AUTH_SERVER_BASE_URL}/oauth2/token"
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": session_data["refresh_token"]
    }
    
    headers = {
        "Authorization": create_basic_auth_header(CLIENT_ID, CLIENT_SECRET),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            
            # Update session with new tokens
            session_data.update({
                "access_token": token_data["access_token"],
                "expires_in": token_data["expires_in"],
                "scopes": token_data["scope"].split() if token_data.get("scope") else session_data.get("scopes", [])
            })
            
            return {"message": "Token refreshed successfully", "expires_in": token_data["expires_in"]}
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"Token refresh failed: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")
