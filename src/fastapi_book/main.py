
from fastapi import FastAPI

from .utils import register_custom_docs
from .ch02.main import app as app_ch02
from .ch03.main import app as app_ch03

app = FastAPI(
    title="FastAPI Book",
    description="This is a book about FastAPI",
    docs_url=None,
    redoc_url=None,
    version="0.1.0")

# 注册自定义文档路由
register_custom_docs(app)

# Mount the sub-applications
app.mount("/ch02", app_ch02, name="ch02")
app.mount("/ch03", app_ch03, name="ch03")
