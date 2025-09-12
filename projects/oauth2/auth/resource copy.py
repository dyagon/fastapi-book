from fastapi import FastAPI, HTTPException, Request
from fastapi import Depends
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from pydantic import ValidationError


from jose import jwt, JWTError
from starlette.status import HTTP_401_UNAUTHORIZED

app = FastAPI(
    title="Protected Resource Server for OAuth2",
    description="An example of OAuth2 Resource Server protecting APIs",
    version="0.1.0",
)

SECRET_KEY = "0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
ALGORITHM = "HS256"
CREDENTIALS_EXCEPTION_DETAIL = "Could not validate credentials"



# endpoints for user info


# Protected resource endpoints
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail=CREDENTIALS_EXCEPTION_DETAIL,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Check if this is a client credentials token
        grant_type = payload.get("grant_type")
        if grant_type == "client_credentials":
            # For client credentials, the subject is the client_id
            # Return a special user representation for the client
            return User(
                username=f"client:{username}",
                email=None,
                full_name=f"Client Application ({username})",
                disabled=False,
            )

        token_data = TokenData(username=username, scopes=payload.get("scopes", []))
    except JWTError:
        raise credentials_exception

    user_data = fake_users_db.get(token_data.username)
    if user_data is None:
        raise credentials_exception

    return User(**user_data)


@app.get("/user/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@app.get("/user/info")
async def get_user_info(
    current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)
):
    """Get user info - requires get_user_info scope."""
    # Decode token to check scopes
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        scopes = payload.get("scopes", [])

        if "get_user_info" not in scopes:
            raise HTTPException(status_code=403, detail="Insufficient scope")

        return {
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
        }
    except JWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=CREDENTIALS_EXCEPTION_DETAIL
        )


@app.get("/admin/info")
async def get_admin_info(
    current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)
):
    """Get admin info - requires get_admin_info scope."""
    # Decode token to check scopes
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        scopes = payload.get("scopes", [])

        if "get_admin_info" not in scopes:
            raise HTTPException(status_code=403, detail="Insufficient scope")

        return {
            "message": "Admin information",
            "user": current_user.username,
            "admin_level": "super",
        }
    except JWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=CREDENTIALS_EXCEPTION_DETAIL
        )
