
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

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    root_path = request.scope.get("root_path", "")
    return get_swagger_ui_html(
        openapi_url=f"{root_path}/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=f"{root_path}/docs/oauth2-redirect",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/redoc", include_in_schema=False)
async def redoc_html(request: Request):
    root_path = request.scope.get("root_path", "")
    return get_redoc_html(
        openapi_url=f"{root_path}/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
    )


@app.get("/ml-models", tags=["default"])
async def get_ml_models():
    return {"loaded_models": list(ml_models.keys())}