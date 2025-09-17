from fastapi import APIRouter, Request, HTTPException

from typing import Optional, Dict, Any

import httpx


router = APIRouter()

# RESOURCE_SERVER_BASE_URL = config.RESOURCE_SERVER_BASE_URL



@router.get("/api/user-info")
async def api_user_info(request: Request):
    """Call the user info API."""
    session_data = get_current_session(request)
    if not session_data or "access_token" not in session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await call_protected_api("/user/info", session_data["access_token"])
    return result

@router.get("/api/admin-info")
async def api_admin_info(request: Request):
    """Call the admin info API."""
    session_data = get_current_session(request)
    if not session_data or "access_token" not in session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await call_protected_api("/admin/info", session_data["access_token"])
    return result

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
