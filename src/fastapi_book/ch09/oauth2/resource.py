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


from .db import fake_users_db, fake_client_db
from .models import User, TokenData


class TokenUtils:
    @staticmethod
    def token_encode(data: dict) -> str:
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def token_decode(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


class OAuth2ClientCredentialsBearer(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials={"tokenUrl": tokenUrl, "scopes": scopes}
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            auto_error=auto_error,
            description=description,
        )

    async def __call__(self, request: Request):
        authorization: str | None = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        print(scheme, param)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2ClientCredentialsBearer(tokenUrl="/authorize")


@app.get("/client", summary="Get Client Info, protected endpoint")
async def get_client_info(token: str = Depends(oauth2_scheme)):
    payload = TokenUtils.token_decode(token)
    client_id: str = payload.get("client_id")
    if client_id is None or client_id not in fake_client_db:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    client = fake_client_db.get(client_id)
    return {"client_id": client["client_id"], "scopes": client["scopes"]}


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
                disabled=False
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
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Get user info - requires get_user_info scope."""
    # Decode token to check scopes
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        scopes = payload.get("scopes", [])
        
        if "get_user_info" not in scopes:
            raise HTTPException(
                status_code=403,
                detail="Insufficient scope"
            )
        
        return {
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name
        }
    except JWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=CREDENTIALS_EXCEPTION_DETAIL
        )

@app.get("/admin/info")
async def get_admin_info(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Get admin info - requires get_admin_info scope."""
    # Decode token to check scopes
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        scopes = payload.get("scopes", [])
        
        if "get_admin_info" not in scopes:
            raise HTTPException(
                status_code=403,
                detail="Insufficient scope"
            )
        
        return {
            "message": "Admin information",
            "user": current_user.username,
            "admin_level": "super"
        }
    except JWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=CREDENTIALS_EXCEPTION_DETAIL
        )


