from fastapi import Request

from fastapi.responses import JSONResponse, RedirectResponse
from ..domain.exceptions import (
    SessionException,
    NotAuthenticatedException,
    SessionExpiredException,
    InvalidCredentialsException,
    MissingSessionTokenException,
    PermissionDeniedException,
)


async def session_exception_handler(request: Request, exc: SessionException):
    status_code = 400

    if isinstance(
        exc,
        (
            NotAuthenticatedException,
            InvalidCredentialsException,
            MissingSessionTokenException,
        ),
    ):
        status_code = 401
    elif isinstance(exc, PermissionDeniedException):
        status_code = 403
    elif isinstance(exc, SessionExpiredException):
        return RedirectResponse(url="/", status_code=302)

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.detail},
    )


from ..impl.auth.exceptions import OAuthError

async def oauth_exception_handler(request: Request, exc: OAuthError):
    return JSONResponse(
        status_code=400,
        content={"error": exc.error, "error_description": exc.error_description},
    )
