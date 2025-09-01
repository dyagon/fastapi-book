
import time
from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)


def take_up_time(func):
    def wrapper(*args, **kwargs):
        print("开始执行--->")
        now = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"执行时间：{end - now}秒")
        return result
    return wrapper


def register_custom_docs(app: FastAPI):
    """
    注册自定义的文档路由，使用 CDN 版本的 Swagger UI 和 ReDoc。
    
    :param app: FastAPI 应用实例
    """
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