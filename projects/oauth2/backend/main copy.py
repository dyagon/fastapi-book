from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os
import httpx
import secrets
import urllib.parse
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import base64

# Client configuration
CLIENT_ID = "auth-code-client"
CLIENT_SECRET = "auth-code-secret-123"
AUTH_SERVER_BASE_URL = "http://localhost:8000"  # Auth server runs on port 8000
RESOURCE_SERVER_BASE_URL = "http://localhost:8000/api"  # Resource server runs on port 8000
CLIENT_BASE_URL = "http://localhost:8001"       # Client runs on port 8001
REDIRECT_URI = f"{CLIENT_BASE_URL}/callback"

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}

app = FastAPI(
    title="OAuth2 Client Application",
    version="0.1.0",
    description="A sample client application that uses OAuth2 Authorization Code flow"
)

# Initialize templates
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)

# Models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str

class UserInfo(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# Security
security = HTTPBearer(auto_error=False)

def generate_state() -> str:
    """Generate a secure random state parameter."""
    return secrets.token_urlsafe(32)

async def exchange_code_for_tokens(code: str) -> Optional[TokenResponse]:
    """Exchange authorization code for access tokens."""
    token_url = f"{AUTH_SERVER_BASE_URL}/oauth2/token"
    
    # Prepare token request
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
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
            return TokenResponse(**token_data)
        except httpx.HTTPStatusError as e:
            print(f"Token exchange failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Token exchange error: {e}")
            return None

async def get_user_info_from_token(access_token: str) -> Optional[UserInfo]:
    """Get user information using access token."""
    user_url = f"{RESOURCE_SERVER_BASE_URL}/user/me"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(user_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()
            return UserInfo(**user_data)
        except Exception as e:
            print(f"Failed to get user info: {e}")
            return None

def get_session_id(request: Request) -> str:
    """Get or create session ID from cookies."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = secrets.token_urlsafe(32)
    return session_id

def get_current_session(request: Request) -> Optional[Dict[str, Any]]:
    """Get current session data."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    return sessions.get(session_id)

@app.get("/login")
async def login(request: Request):
    """Initiate OAuth2 login flow."""
    # Generate state parameter for CSRF protection
    state = generate_state()
    session_id = get_session_id(request)
    
    # Store state in session
    if session_id not in sessions:
        sessions[session_id] = {}
    sessions[session_id]["oauth_state"] = state
    
    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "get_user_info get_admin_info get_user_role",
        "state": state
    }
    
    auth_url = f"{AUTH_SERVER_BASE_URL}/oauth2/authorize?{urllib.parse.urlencode(auth_params)}"
    
    # Redirect to authorization server
    response = RedirectResponse(url=auth_url, status_code=302)
    response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=3600)
    return response

@app.get("/callback")
async def callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    """Handle OAuth2 callback."""
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/?error=Invalid session", status_code=302)
    
    session_data = sessions[session_id]
    
    # Handle error response
    if error:
        error_msg = f"{error}: {error_description or 'Unknown error'}"
        return RedirectResponse(url=f"/?error={urllib.parse.quote(error_msg)}", status_code=302)
    
    # Validate state parameter
    if not state or state != session_data.get("oauth_state"):
        return RedirectResponse(url="/?error=Invalid state parameter", status_code=302)
    
    # Validate authorization code
    if not code:
        return RedirectResponse(url="/?error=No authorization code received", status_code=302)
    
    # Exchange code for tokens
    token_response = await exchange_code_for_tokens(code)
    if not token_response:
        return RedirectResponse(url="/?error=Failed to exchange code for tokens", status_code=302)
    
    # Get user information
    user_info = await get_user_info_from_token(token_response.access_token)
    if not user_info:
        return RedirectResponse(url="/?error=Failed to get user information", status_code=302)
    
    # Store tokens and user info in session
    session_data.update({
        "access_token": token_response.access_token,
        "refresh_token": token_response.refresh_token,
        "token_type": token_response.token_type,
        "expires_in": token_response.expires_in,
        "scopes": token_response.scope.split() if token_response.scope else [],
        "user": user_info.dict(),
        "login_time": datetime.now(timezone.utc).isoformat()
    })
    
    # Clean up OAuth state
    session_data.pop("oauth_state", None)
    
    return RedirectResponse(url="/", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    """Logout user."""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="session_id")
    return response

@app.get("/status")
async def status(request: Request):
    """Show current authentication status."""
    session_data = get_current_session(request)
    
    if not session_data:
        return {"authenticated": False, "message": "No active session"}
    
    return {
        "authenticated": "access_token" in session_data,
        "user": session_data.get("user"),
        "scopes": session_data.get("scopes", []),
        "login_time": session_data.get("login_time"),
        "has_refresh_token": "refresh_token" in session_data
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "oauth2-client"}


@app.get("/test-client-credentials")
async def test_client_credentials(
    client_id: str = Query("client-credentials-client"),
    client_secret: str = Query("client-credentials-secret-456")
):
    """Test Client Credentials flow to get client info."""
    token_url = f"{AUTH_SERVER_BASE_URL}/oauth2/token"
    
    data = {
        "grant_type": "client_credentials",
        "scope": "get_client_info"
    }
    headers = {
        "Authorization": create_basic_auth_header(client_id, client_secret),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Get access token using client credentials
            response = await client.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"Obtained access token: {access_token}")
            
            # Call protected client info endpoint
            client_info_url = f"{RESOURCE_SERVER_BASE_URL}/client"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            response = await client.get(client_info_url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"Client credentials flow failed: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Client credentials flow failed: {str(e)}")