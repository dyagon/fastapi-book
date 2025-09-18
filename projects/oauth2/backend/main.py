
import os
from telnetlib import theNULL
import threading
from typing import Optional, Dict, Any


from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# from .context import infra


# # 全局资源本身是在这里创建和管理的
# async def lifespan(app: FastAPI):
#     print("🚀 App startup: Creating DB connection pool.")
#     await infra.setup()
#     app.state.infra = infra
#     yield
#     print("👋 App shutdown: Closing DB connection pool.")

#     await infra.shutdown()
#     print("    -> DB connection pool closed.")


from .context.app_container import Container


async def lifespan(app: FastAPI):
    app_container = Container()
    app_container.wire(modules=[".app.routers.auth"])
    print(threading.current_thread().name)
    app_container.init_resources()
    print("🚀 App startup")
    app.state.app_container = app_container
    yield
    print("👋 App shutdown")


app = FastAPI(
    title="OAuth2 Client Application",
    version="0.1.0",
    description="A sample client application that uses OAuth2 Authorization Code flow",
    lifespan=lifespan,
)

from .app.routers.auth import router as auth_router
from .app.routers.api import router as api_router

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


def get_current_session(request: Request) -> Optional[Dict[str, Any]]:
    """Get current session data."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    return sessions.get(session_id)


# Initialize templates
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, error: Optional[str] = Query(None)):
    """Home page."""
    session_data = get_current_session(request)

    context = {
        "request": request,
        "user": session_data.get("user") if session_data else None,
        "scopes": session_data.get("scopes", []) if session_data else [],
        "error": error,
    }

    return templates.TemplateResponse("index.html", context)


app.include_router(auth_router)
app.include_router(api_router)
