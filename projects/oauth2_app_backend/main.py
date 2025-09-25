import os
from telnetlib import theNULL
import threading
from typing import Optional, Dict, Any


from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from starlette.middleware.sessions import SessionMiddleware

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


from .context.app_container import Container, infra, app_settings
from .domain.exceptions import SessionException


async def lifespan(app: FastAPI):
    print("🚀 App startup")
    await infra.setup()
    app_container = Container()
    app_container.wire(modules=[".app.routers.auth"])
    print(threading.current_thread().name)
    app.state.app_container = app_container
    yield
    await infra.shutdown()
    print("👋 App shutdown")


app = FastAPI(
    title="OAuth2 Client Application",
    version="0.1.0",
    description="A sample client application that uses OAuth2 Authorization Code flow",
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=app_settings.app.secret_key)

from .app.routers.auth import router as auth_router
from .app.routers.api import router as api_router
from .app.exception_handlers import session_exception_handler

app.add_exception_handler(SessionException, session_exception_handler)

app.include_router(auth_router)
app.include_router(api_router)
