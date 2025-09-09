"""微信模拟应用主入口"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi_book.utils import register_custom_docs
from .infra import config, logger
from .app.middleware import LoggingMiddleware, CORSMiddleware
from .app.exception_handlers import register_exception_handlers
from .app.routers.login import router as login_router
# from .app.routers import oauth, payment, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("微信模拟应用启动中...")
    # task = asyncio.create_task(cleanup_expired_sessions())
    yield
    # 关闭时执行
    logger.info("微信模拟应用关闭")
    # task.cancel()


# 创建FastAPI应用
app = FastAPI(
    title="微信模拟应用",
    description="模拟微信OAuth2和支付功能的FastAPI应用",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

# 添加中间件
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware)

# 注册异常处理器
register_exception_handlers(app)

# 注册路由
# app.include_router(oauth.router)
# app.include_router(payment.router)
# app.include_router(user.router)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "app_name": config.app_name, "version": "1.0.0"}


register_custom_docs(app)

app.include_router(login_router)

