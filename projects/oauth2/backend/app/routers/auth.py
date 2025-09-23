import os
from pathlib import Path

from urllib.parse import urlencode, quote
from dependency_injector.wiring import Provide, inject
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi import APIRouter, Depends, Query, Request

from typing import Optional

from fastapi.templating import Jinja2Templates


from ...impl.auth import Token
from ...impl.session_manager import SessionManager

from ...context.app_container import (
    Container,
    ClientCredentialsClient,
)
from ...domain.services.auth_login import OAuthLoginService
from ...domain.services.user_service import UserService


router = APIRouter()


@router.get("/fetch_token", response_model=Token)
@inject
async def fetch_token(
    cc_client: ClientCredentialsClient = Depends(Provide[Container.cc_client]),
):
    return await cc_client.get_token()


@router.get("/get_client_info")
@inject
async def get_client_info(
    cc_client: ClientCredentialsClient = Depends(Provide[Container.cc_client]),
):
    return await cc_client.get_client_info()


@router.get("/login")
@inject
async def login():
    async with Container.auth_login_service() as auth_login_service:
        auth_url = await auth_login_service.login()
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/callback")
@inject
async def callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
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

    async with Container.auth_login_service() as auth_login_service:
        session = await auth_login_service.callback(code, state)
        request.session.update(session.to_dict())

    return RedirectResponse(url="/", status_code=302)



# Initialize templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

@router.get("/", response_class=HTMLResponse)
@inject
async def home(request: Request, error: Optional[str] = Query(None), session_manager: SessionManager = Depends(Provide[Container.session_manager])):
    """Home page."""
    session_data = request.session
    if session_data:
        session = await session_manager.get_session(session_data.get("session_id"))
        user_id = session.get("user_id")
        async with Container.user_service() as user_service:
            user, auths = await user_service.get_user_and_auth(user_id)
            if user:
                print(user)
                print(auths)
    else:
        session = None
        user = None

    context = {
        "request": request,
        "user": session_data.get("user") if session_data else None,
        "scopes": session_data.get("scopes", []) if session_data else [],
        "error": error,
    }

    return templates.TemplateResponse("index.html", context)