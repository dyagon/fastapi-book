# src/fastapi_book/ch09/api_key.py
import os
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

# --- 配置 ---

# 1. 定义 API Key 的名称 (即请求头的名称)
API_KEY_NAME = "X-API-Key"

# 2. 定义安全方案
# auto_error=False 让我们能自定义错误响应，而不是直接抛出 FastAPI 的默认 403 错误。
api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# 3. 存储有效的 API Key
# 在真实应用中，绝不应硬编码！应从环境变量或安全配置/数据库中加载。
# 这里我们为了演示，直接从环境变量读取。如果没有设置，则使用一个默认值。
VALID_API_KEY = os.getenv("API_KEY", "my-secret-api-key-1234")


# --- API Key 验证逻辑 ---
async def get_api_key(api_key_header: str = Security(api_key_header_scheme)):
    """
    依赖函数：从请求头提取 API Key 并验证它。
    """
    if not api_key_header:
        # 如果请求头中根本没有 API Key
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )

    # 使用 secrets.compare_digest 来安全地比较字符串，防止时序攻击
    # if secrets.compare_digest(api_key_header, VALID_API_KEY):
    # 为简单起见，这里我们用直接比较
    if api_key_header == VALID_API_KEY:
        # 如果密钥有效，返回它（或任何你想要的值，比如 True）
        return api_key_header
    else:
        # 如果密钥无效
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )


app = FastAPI(
    title="API Key Auth Example",
    description="An example of how to implement API Key authentication in FastAPI.",
)


@app.get("/secure")
async def read_secure_data(api_key: str = Depends(get_api_key)):
    """
    一个受保护的端点。
    只有当 `get_api_key` 函数成功执行（即 API Key 有效）时，
    这个路径操作函数才会被执行。
    `api_key` 参数会接收到 `get_api_key` 函数返回的值。
    """
    return {
        "message": f"Hello from a secure endpoint! Your API key is '{api_key[-4:]}'.",
    }

