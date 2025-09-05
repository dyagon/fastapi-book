
from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from .lifespan import lifespan, ml_models
from .exception import exception_handlers
from .router.user import router as user_router
from .router.test import router as test_router
from .router.files import router as files_router
from .router.resp import router as resp_router
from .router.bgtask import router as bgtask_router

from fastapi_book.utils import register_custom_docs

app = FastAPI(
    title="FastAPI Book Chapter 3",
    description="Chapter 3 Example for FastAPI Book",
    docs_url=None,
    redoc_url=None,
    version="0.1.0",
    lifespan=lifespan,
    exception_handlers=exception_handlers)

app.include_router(user_router, tags=["user"])
app.include_router(test_router, tags=["test"])
app.include_router(files_router, tags=["files"])
app.include_router(resp_router, tags=["response"])
app.include_router(bgtask_router, tags=["bgtask"])


@app.get("/hello", tags=["default"])
async def hello():
    return {"message": "Hello, FastAPI Book Chapter 3!"}


@app.get("/ml-models", tags=["default"])
async def get_ml_models():
    return {"loaded_models": list(ml_models.keys())}


register_custom_docs(app)