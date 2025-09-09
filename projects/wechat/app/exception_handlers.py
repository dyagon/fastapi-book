from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..infra import logger

from ..domain.exceptions import WeChatAPIException, PaymentException


async def wechat_api_exception_handler(request: Request, exc: WeChatAPIException):
    """微信API异常处理器"""
    logger.error(f"微信API异常: {exc.error_code} - {exc.error_message}")

    return JSONResponse(
        status_code=400,
        content={"error": exc.error_code, "error_description": exc.error_message},
    )


async def payment_exception_handler(request: Request, exc: PaymentException):
    """支付异常处理器"""
    logger.error(f"支付异常: {exc.error_code} - {exc.error_message}")

    return JSONResponse(
        status_code=400,
        content={"error": exc.error_code, "error_description": exc.error_message},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.error(f"请求验证失败: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "error_description": "请求参数验证失败",
            "details": exc.errors(),
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "error_description": exc.detail},
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {type(exc).__name__} - {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "error_description": "服务器内部错误",
        },
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(WeChatAPIException, wechat_api_exception_handler)
    app.add_exception_handler(PaymentException, payment_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
