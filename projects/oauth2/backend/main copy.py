from fastapi import FastAPI, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer

import os
import httpx
import secrets
import urllib.parse
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

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
