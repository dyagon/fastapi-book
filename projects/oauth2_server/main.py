from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .context import infra

from fastapi_book.utils import register_custom_docs

# 全局资源本身是在这里创建和管理的
async def lifespan(app: FastAPI):
    print("🚀 App startup: Creating DB connection pool.")
    await infra.setup_all()
    app.state.infra = infra
    yield
    print("👋 App shutdown: Closing DB connection pool.")

    await infra.shutdown_all()
    print("    -> DB connection pool closed.")


app = FastAPI(
    title="OAuth2 Authorization Code Example",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

register_custom_docs(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8002", "http://127.0.0.1:8002"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

from .app.exception_handler import oauth2_exception_handler
from .domain.exception import OAuth2Exception

app.add_exception_handler(OAuth2Exception, oauth2_exception_handler)
from .app.routers.oauth import router as oauth_router
from .app.routers.resource import router as resource_router

app.include_router(oauth_router, prefix="/oauth2")

app.include_router(resource_router, prefix="/api")
