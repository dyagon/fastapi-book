from fastapi import FastAPI, HTTPException, Request, Form, Depends, Query
from fastapi.security import OAuth2AuthorizationCodeBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional, Dict, Any

from datetime import datetime, timedelta, timezone
import secrets
import urllib.parse
import os
import hashlib
import base64

from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

from jose import jwt, JWTError

from .config import pwd_context
from repo import fake_users_db, fake_client_db
from .models import UserInDB, Client, Token, OAuth2AuthorizationRequest
from .resource import app as resource_app
from .dto import AuthorizeRequestQuery, AuthorizeFormRequest, TokenRequest, TokenResponse
# Constants
CREDENTIALS_EXCEPTION_DETAIL = "Could not validate credentials"
SECRET_KEY = "0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 70

# Initialize templates
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)

# In-memory storage for authorization codes and tokens
authorization_codes: Dict[str, Dict[str, Any]] = {}
tokens: Dict[str, Dict[str, Any]] = {}

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/oauth2/authorize",
    tokenUrl="/oauth2/token",
    refreshUrl="/oauth2/refresh",
    scopes={
        "get_admin_info": "获取管理员信息",
        "get_user_info": "获取用户信息",
        "get_user_role": "获取用户角色",
    },
)

# HTTP Basic Auth for client authentication
security = HTTPBasic(auto_error=False)



# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user with username and password."""
    user_data = fake_users_db.get(username)
    if not user_data:
        return None
    if not verify_password(password, user_data["password"]):
        return None
    return UserInDB(**user_data, hashed_password=user_data["password"])

def get_client(client_id: str) -> Optional[Client]:
    """Get client by client_id."""
    client_data = fake_client_db.get(client_id)
    if not client_data:
        return None
    return Client(**client_data)

def verify_client_credentials(client_id: str, client_secret: Optional[str]) -> bool:
    """Verify client credentials."""
    client = get_client(client_id)
    if not client:
        return False
    
    # For public clients, no secret is required
    if is_public_client(client):
        return client_secret is None or client_secret == ""
    
    # For confidential clients, secret is required
    return client.client_secret == client_secret

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_authorization_code() -> str:
    """Generate a secure random authorization code."""
    return secrets.token_urlsafe(32)

def verify_code_challenge(code_verifier: str, code_challenge: str, code_challenge_method: str) -> bool:
    """Verify PKCE code challenge."""
    if code_challenge_method == "plain":
        return code_verifier == code_challenge
    elif code_challenge_method == "S256":
        # Create SHA256 hash of code_verifier and base64url encode it
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        encoded = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
        return encoded == code_challenge
    else:
        return False

def is_public_client(client: Client) -> bool:
    """Check if client is a public client."""
    return client.client_type == "public"

def get_client_credentials(credentials: Optional[HTTPBasicCredentials], 
                          client_id: Optional[str], 
                          client_secret: Optional[str]) -> tuple[str, Optional[str]]:
    """Extract client credentials from Basic Auth or form parameters."""
    if credentials and credentials.username:
        return credentials.username, credentials.password
    elif client_id:
        return client_id, client_secret
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Client identification required"
        )

def validate_client_authentication(client_id: str, client_secret: Optional[str]) -> Client:
    """Validate client credentials and return client object."""
    client = get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid client"
        )
    
    if not verify_client_credentials(client_id, client_secret):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials"
        )
    
    return client

def handle_authorization_code_grant(
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: Optional[str],
    code_verifier: Optional[str]
) -> Token:
    """Handle authorization code grant type."""
    # Get client info
    client = get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid client"
        )
    
    # Verify client credentials based on client type
    if is_public_client(client):
        # For public clients, don't require secret but verify code_verifier
        if not code_verifier:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="code_verifier is required for public clients"
            )
    else:
        # For confidential clients, verify credentials
        if not verify_client_credentials(client_id, client_secret):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials"
            )
    
    # Get and validate authorization code
    auth_code_data = authorization_codes.get(code)
    print("Auth code data:", auth_code_data)
    if not auth_code_data:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code"
        )
    
    # Check if code has expired
    if datetime.now(timezone.utc) > auth_code_data["expires_at"]:
        del authorization_codes[code]
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Authorization code expired"
        )
    
    # Validate client_id and redirect_uri match
    if auth_code_data["client_id"] != client_id:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Client ID mismatch"
        )
    
    if auth_code_data["redirect_uri"] != redirect_uri:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Redirect URI mismatch"
        )
    
    # PKCE verification for public clients
    if is_public_client(client):
        code_challenge = auth_code_data.get("code_challenge")
        code_challenge_method = auth_code_data.get("code_challenge_method", "S256")
        
        if not code_challenge or not code_verifier:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="PKCE verification failed: missing challenge or verifier"
            )
        
        if not verify_code_challenge(code_verifier, code_challenge, code_challenge_method):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="PKCE verification failed"
            )
    
    # Generate tokens
    token_data = {
        "sub": auth_code_data["username"],
        "scopes": auth_code_data["scopes"],
        "client_id": client_id
    }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    refresh_token_str = create_refresh_token(
        data=token_data, expires_delta=refresh_token_expires
    )
    
    # Remove used authorization code
    del authorization_codes[code]
    
    # Store refresh token
    tokens[refresh_token_str] = {
        "username": auth_code_data["username"],
        "client_id": client_id,
        "scopes": auth_code_data["scopes"]
    }
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token_str,
        scope=" ".join(auth_code_data["scopes"])
    )

def handle_refresh_token_grant(
    refresh_token: str,
    client_id: str,
    client_secret: Optional[str]
) -> Token:
    """Handle refresh token grant type."""
    # Get client info
    client = get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid client"
        )
    
    # Verify client credentials for confidential clients
    if not is_public_client(client):
        if not verify_client_credentials(client_id, client_secret):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials"
            )
    
    # Validate refresh token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
        # Get stored token data
        token_data_stored = tokens.get(refresh_token)
        if not token_data_stored or token_data_stored["client_id"] != client_id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
        
    except JWTError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    # Generate new access token
    token_data = {
        "sub": username,
        "scopes": token_data_stored["scopes"],
        "client_id": client_id
    }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(token_data_stored["scopes"])
    )

def handle_client_credentials_grant(
    client_id: str,
    client_secret: Optional[str],
    scope: Optional[str] = None
) -> Token:
    """Handle client credentials grant type."""
    # Validate client credentials
    client = validate_client_authentication(client_id, client_secret)
    
    # Client credentials grant doesn't support public clients
    if is_public_client(client):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Client credentials grant not supported for public clients"
        )
    
    # Parse requested scopes
    requested_scopes = scope.split() if scope else []
    
    # Validate requested scopes against client's allowed scopes
    allowed_scopes = client.scopes
    invalid_scopes = [s for s in requested_scopes if s not in allowed_scopes]
    if invalid_scopes:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Invalid scopes: {', '.join(invalid_scopes)}"
        )
    
    # Use requested scopes or default to all allowed scopes
    final_scopes = requested_scopes if requested_scopes else allowed_scopes
    
    # Generate access token (no user context for client credentials)
    token_data = {
        "sub": client_id,  # Use client_id as subject for client credentials
        "scopes": final_scopes,
        "client_id": client_id,
        "grant_type": "client_credentials"
    }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    # Client credentials flow typically doesn't include refresh tokens
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(final_scopes)
    )

app = FastAPI(
    title="OAuth2 Authorization Code Example",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8002",
        "http://127.0.0.1:8002"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/oauth2/authorize", response_class=HTMLResponse)
async def authorize_get(
    request: Request,
    auth_request: AuthorizeRequestQuery = Depends()
):
    """Authorization endpoint - shows login form."""
    
    # 验证请求参数
    is_valid, error_message = auth_request.validate()
    if not is_valid:
        return RedirectResponse(
            url=auth_request.get_error_redirect_url("invalid_request", error_message),
            status_code=302
        )
    
    # Validate client
    client = get_client(auth_request.client_id)
    if not client:
        return RedirectResponse(
            url=auth_request.get_error_redirect_url("invalid_client", "Invalid client_id"),
            status_code=302
        )
    
    # Validate redirect_uri
    if auth_request.redirect_uri not in client.redirect_uris:
        print("Invalid redirect_uri")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid redirect_uri"
        )
    
    # PKCE validation for public clients
    if is_public_client(client):
        if not auth_request.code_challenge:
            return RedirectResponse(
                url=auth_request.get_error_redirect_url("invalid_request", "code_challenge is required for public clients"),
                status_code=302
            )
        
        if auth_request.code_challenge_method not in ["plain", "S256"]:
            return RedirectResponse(
                url=auth_request.get_error_redirect_url("invalid_request", "Invalid code_challenge_method"),
                status_code=302
            )
    
    # Show login form
    return templates.TemplateResponse("login.html", {
        "request": request,
        "client_id": auth_request.client_id,
        "redirect_uri": auth_request.redirect_uri,
        "response_type": auth_request.response_type,
        "state": auth_request.state or "",
        "scope": auth_request.scope,
        "code_challenge": auth_request.code_challenge or "",
        "code_challenge_method": auth_request.code_challenge_method or ""
    })

# OAuth2 Authorization Endpoint (POST) - Process login
@app.post("/oauth2/authorize", response_class=RedirectResponse)
async def authorize_post(
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    response_type: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    scope: str = Form(""),
    state: Optional[str] = Form(None),
    code_challenge: Optional[str] = Form(None),
    code_challenge_method: Optional[str] = Form(None),
):
    """Process login and generate authorization code."""
    
    # Authenticate user
    user = authenticate_user(username, password)
    if not user:
        # Return to login page with error
        request = Request({"type": "http", "method": "GET"})
        return templates.TemplateResponse("login.html", {
            "request": request,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": response_type,
            "state": state or "",
            "scope": scope,
            "code_challenge": code_challenge or "",
            "code_challenge_method": code_challenge_method or "",
            "error": "Invalid username or password"
        })
    
    # Generate authorization code
    auth_code = generate_authorization_code()
    scopes = scope.split() if scope else []
    
    # Store authorization code with PKCE data
    auth_code_data = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "username": username,
        "scopes": scopes,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
    }
    
    # Add PKCE data if present
    if code_challenge:
        auth_code_data["code_challenge"] = code_challenge
        auth_code_data["code_challenge_method"] = code_challenge_method or "S256"
    
    authorization_codes[auth_code] = auth_code_data
    
    # Redirect back to client with authorization code
    params = {"code": auth_code}
    if state:
        params["state"] = state
    
    return RedirectResponse(
        url=f"{redirect_uri}?{urllib.parse.urlencode(params)}",
        status_code=302
    )


app.mount("/api", resource_app)  # Mount the resource server app