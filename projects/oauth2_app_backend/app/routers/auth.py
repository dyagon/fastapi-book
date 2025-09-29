from urllib.parse import urlencode, quote
from dependency_injector.wiring import Provide, inject
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi import APIRouter, Depends, Query, Request

from typing import Optional

from ..templates import templates

from ...impl.auth import Token
from ...impl.session_manager import SessionManager

from ...context.app_container import (
    Container,
    ClientCredentialsClient,
)

router = APIRouter()


@router.get("/fetch_token", response_model=Token)
async def fetch_token():
    cc_client = Container.cc_client()
    return await cc_client.get_token()


@router.get("/get_client_info")
async def get_client_info():
    cc_client = Container.cc_client()
    return await cc_client.get_client_info()


@router.get("/login")
async def login():
    auth_login_service = Container.auth_login_service()
    auth_url = await auth_login_service.login()
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/callback")
async def callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """Handle OAuth2 callback."""
    if error:
        error_msg = f"{error}: {error_description or 'Unknown error'}"
        return RedirectResponse(url=f"/?error={quote(error_msg)}", status_code=302)

    if not code:
        return RedirectResponse(
            url="/?error=No authorization code received", status_code=302
        )

    auth_login_service = Container.auth_login_service()
    session = await auth_login_service.callback(code, state)
    request.session.update(session.model_dump())

    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    session_data = request.session
    if not session_data or not session_data.get("session_id"):
        return RedirectResponse(url="/", status_code=302)
    session_manager = Container.session_manager()
    await session_manager.delete_session(session_data.get("session_id"))
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, error: Optional[str] = Query(None)):
    session_service = Container.session_service()
    try:
        session = await session_service.check_session(request.session)
        request.session.update(session.model_dump())
        user_service = Container.user_service()
        user, auths = await user_service.get_user_and_auths(session.user_id)
        if user:
            context = {
                        "request": request,
                        "user": user,
                        "session": session,
                        "auths": auths,
                        "error": error,
                    }
            return templates.TemplateResponse("user.html", context)
    except Exception as e:
        print(e)
        context = {
            "request": request,
            "error": error,
        }
        return templates.TemplateResponse("index.html", context)
