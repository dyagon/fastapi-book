from contextlib import asynccontextmanager
from fastapi import FastAPI


from .infra import SessionLocal

from .app.routes.user import router_user
from .app.routes.short import router_short
from .app.lifespan import lifespan

from fastapi_book.utils import register_custom_docs

app = FastAPI(
    title="Chapter 10 - Short Url",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

register_custom_docs(app)

app.include_router(router_user)
app.include_router(router_short)
