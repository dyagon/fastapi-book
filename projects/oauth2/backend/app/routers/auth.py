from urllib.parse import urlencode, quote
from fastapi.responses import RedirectResponse

from fastapi import APIRouter, Depends, Query, Request

from typing import Optional

from ...domain.services.auth_login import OAuthLoginService

from ..depends import (
    get_auth_login_service,
    get_auth_service,
    OAuth2ClientCredentialsService,
)

router = APIRouter()


@router.get("/fetch_token")
async def fetch_token(
    auth_service: OAuth2ClientCredentialsService = Depends(get_auth_service),
):
    return await auth_service.get_token()


@router.get("/get_client_info")
async def get_client_info(
    auth_service: OAuth2ClientCredentialsService = Depends(get_auth_service),
):
    return await auth_service.get_client_info()


@router.get("/login")
async def login(
    auth_login_service: OAuthLoginService = Depends(get_auth_login_service),
):
    auth_url = await auth_login_service.login()
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/callback")
async def callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    auth_login_service: OAuthLoginService = Depends(get_auth_login_service),
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
        return RedirectResponse(
            url="/?error=No authorization code received", status_code=302
        )

    result = await auth_login_service.callback(code, state)
    return RedirectResponse(url="/", status_code=302)
