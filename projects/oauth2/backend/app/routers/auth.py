from urllib.parse import urlencode, quote
from fastapi.responses import RedirectResponse

from fastapi import APIRouter, Depends, Query, Request
from redis.asyncio import Redis

from typing import Optional

from ...config import config
from ..depends import get_redis_client, get_oauth_client, OAuthClient

router = APIRouter()


@router.get("/fetch_token")
async def fetch_token(oauth_client: OAuthClient = Depends(get_oauth_client)):
    return await oauth_client.get_token()


@router.get("/get_client_info")
async def get_client_info(oauth_client: OAuthClient = Depends(get_oauth_client)):
    return await oauth_client.call("/client")


@router.get("/login")
async def login(redis: Redis = Depends(get_redis_client)):

    auth_params = {
        "response_type": "code",
        "client_id": config.AUTH_CODE_CLIENT_ID,
        "redirect_uri": config.REDIRECT_URI,
        "scope": "get_user_info get_admin_info",
        "state": "1234",
    }
    auth_url = (
        f"{config.AUTH_SERVER_BASE_URL}/oauth2/authorize?{urlencode(auth_params)}"
    )
    return RedirectResponse(url=auth_url, status_code=302)



@router.get("/callback")
async def callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    """Handle OAuth2 callback."""
    # session_id = request.cookies.get("session_id")
    # if not session_id or session_id not in sessions:
    #     return RedirectResponse(url="/?error=Invalid session", status_code=302)
    
    # session_data = sessions[session_id]
    
    # Handle error response
    if error:
        error_msg = f"{error}: {error_description or 'Unknown error'}"
        return RedirectResponse(url=f"/?error={quote(error_msg)}", status_code=302)
    
    # # Validate state parameter
    # if not state or state != session_data.get("oauth_state"):
    #     return RedirectResponse(url="/?error=Invalid state parameter", status_code=302)
    
    # Validate authorization code
    if not code:
        return RedirectResponse(url="/?error=No authorization code received", status_code=302)
    
    # # Exchange code for tokens
    # token_response = await exchange_code_for_tokens(code)
    # if not token_response:
    #     return RedirectResponse(url="/?error=Failed to exchange code for tokens", status_code=302)
    
    # # Get user information
    # user_info = await get_user_info_from_token(token_response.access_token)
    # if not user_info:
    #     return RedirectResponse(url="/?error=Failed to get user information", status_code=302)
    
    # # Store tokens and user info in session
    # session_data.update({
    #     "access_token": token_response.access_token,
    #     "refresh_token": token_response.refresh_token,
    #     "token_type": token_response.token_type,
    #     "expires_in": token_response.expires_in,
    #     "scopes": token_response.scope.split() if token_response.scope else [],
    #     "user": user_info.dict(),
    #     "login_time": datetime.now(timezone.utc).isoformat()
    # })
    
    # # Clean up OAuth state
    # session_data.pop("oauth_state", None)
    
    return RedirectResponse(url="/", status_code=302)