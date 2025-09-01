import base64
import hashlib
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

# --- 1. 配置和初始化 ---

# FastAPI 应用和模板
app = FastAPI(title="Generic OAuth 2.0 Authorization Server")
templates = Jinja2Templates(directory="templates")

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "a-very-secret-key-that-is-long-and-secure")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 2. 模拟数据库 ---
# 在生产环境中，这些必须是真实的数据库！

# 用户数据库
USERS_DB = {
    "user1": {"hashed_password": pwd_context.hash("pass1"), "scopes": ["read", "write"]}
}

# 客户端数据库 (client_id, client_secret, redirect_uris)
CLIENTS_DB = {
    "my-web-app": {
        "hashed_secret": pwd_context.hash("app-secret-123"),
        "redirect_uris": ["http://localhost:8080/callback"],
    },
    "my-m2m-app": {
        "hashed_secret": pwd_context.hash("m2m-secret-456"),
        "redirect_uris": [],  # M2M 应用不需要重定向
    },
}

# 存储授权码和刷新令牌 (有状态部分)
AUTH_CODES_DB = {}  # {code: {client_id, redirect_uri, user_id, expiry, code_challenge}}
REFRESH_TOKENS_DB = {}  # {token: user_id}


# --- 3. 辅助函数和依赖 ---


def create_token(data: dict, expires_delta: timedelta):
    """创建 JWT"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_pkce_challenge(code_verifier: str, code_challenge: str):
    """验证 PKCE 挑战"""
    hashed_verifier = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    recreated_challenge = (
        base64.urlsafe_b64encode(hashed_verifier).decode("utf-8").rstrip("=")
    )
    return secrets.compare_digest(recreated_challenge, code_challenge)


async def get_current_user_from_token(
    token: str = Depends(lambda r: r.headers.get("Authorization")),
):
    """依赖项：从 Bearer Token 中验证并提取用户"""
    if not token or not token.lower().startswith("bearer "):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    token = token.split(" ")[1]
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None or user_id not in USERS_DB:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id


# --- 4. OAuth 2.0 端点实现 ---


@app.get("/authorize", response_class=HTMLResponse)
async def get_authorize_page(
    request: Request,
    response_type: str,
    client_id: str,
    redirect_uri: str,
    state: str | None = None,
    scope: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
):
    """
    授权端点 (GET)：显示登录和同意页面。
    这是授权码模式和隐式模式的起点。
    """
    # 验证客户端和重定向 URI
    client = CLIENTS_DB.get(client_id)
    if not client or redirect_uri not in client["redirect_uris"]:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Invalid client_id or redirect_uri"
        )

    # 对于授权码模式，PKCE 是必需的
    if response_type == "code" and (
        not code_challenge or code_challenge_method != "S256"
    ):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="PKCE S256 challenge is required for authorization code grant",
        )

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": response_type,
            "state": state,
            "scope": scope,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        },
    )


@app.post("/authorize")
async def handle_authorize_form(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    client_id: str = Form(),
    redirect_uri: str = Form(),
    response_type: str = Form(),
    state: str | None = Form(None),
    scope: str | None = Form(None),
    code_challenge: str | None = Form(None),
):
    """
    授权端点 (POST)：处理用户登录和授权。
    """
    # 1. 验证用户凭据
    user = USERS_DB.get(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password",
                # 重新填充表单所需的所有字段
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": response_type,
                "state": state,
                "scope": scope,
                "code_challenge": code_challenge,
            },
            status_code=400,
        )

    # 2. 根据 response_type 执行操作
    if response_type == "code":
        # === 授权码模式 ===
        auth_code = secrets.token_urlsafe(32)
        AUTH_CODES_DB[auth_code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "user_id": username,
            "expiry": time.time() + 600,  # 10分钟有效期
            "code_challenge": code_challenge,
        }
        # 构建重定向 URL
        redirect_url = f"{redirect_uri}?code={auth_code}"
        if state:
            redirect_url += f"&state={state}"
        return RedirectResponse(url=redirect_url)

    elif response_type == "token":
        # === 隐式模式 (不推荐) ===
        # 直接颁发访问令牌
        access_token = create_token(
            data={"sub": username, "scope": scope},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        # 构建重定向 URL，令牌在片段中
        redirect_url = f"{redirect_uri}#access_token={access_token}&token_type=bearer"
        if state:
            redirect_url += f"&state={state}"
        return RedirectResponse(url=redirect_url)

    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Unsupported response_type"
        )


@app.post("/token")
async def issue_token(
    request: Request,
    grant_type: str = Form(),
    # for 'authorization_code'
    code: str | None = Form(None),
    redirect_uri: str | None = Form(None),
    code_verifier: str | None = Form(None),
    # for 'password'
    username: str | None = Form(None),
    password: str | None = Form(None),
    # for 'refresh_token'
    refresh_token: str | None = Form(None),
):
    """
    令牌端点：处理所有非交互式授权流程。
    """
    # 解析 Basic Auth 获取 client_id 和 client_secret
    client_id, client_secret = None, None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("basic "):
        try:
            creds = base64.b64decode(auth_header.split(" ")[1]).decode()
            client_id, client_secret = creds.split(":", 1)
        except Exception:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid Basic auth credentials",
            )

    client = CLIENTS_DB.get(client_id)
    if not client or not pwd_context.verify(client_secret, client["hashed_secret"]):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid client credentials"
        )

    # --- 根据 grant_type 分支 ---
    if grant_type == "authorization_code":
        if not all([code, redirect_uri, code_verifier]):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Missing parameters for authorization_code grant",
            )

        auth_code_data = AUTH_CODES_DB.pop(code, None)
        if not auth_code_data or auth_code_data["expiry"] < time.time():
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid or expired authorization code",
            )

        # 验证 PKCE
        if not verify_pkce_challenge(code_verifier, auth_code_data["code_challenge"]):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Invalid PKCE code_verifier"
            )

        user_id = auth_code_data["user_id"]

    elif grant_type == "password":
        if not all([username, password]):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Missing username or password for password grant",
            )

        user = USERS_DB.get(username)
        if not user or not pwd_context.verify(password, user["hashed_password"]):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Invalid username or password"
            )
        user_id = username

    elif grant_type == "client_credentials":
        user_id = client_id  # 在客户端凭据模式中，主体是客户端本身

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Missing refresh_token"
            )
        user_id = REFRESH_TOKENS_DB.get(refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid or expired refresh token",
            )

        # 为了安全，刷新令牌通常是一次性的 (可选，但推荐)
        # del REFRESH_TOKENS_DB[refresh_token]

    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Unsupported grant type"
        )

    # --- 颁发令牌 ---
    # 所有成功的 grant type 都会在这里颁发令牌

    # 1. 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={
            "sub": user_id,
            "scope": "read write",
        },  # 范围可以根据请求和用户权限动态确定
        expires_delta=access_token_expires,
    )

    # 2. 创建刷新令牌 (如果适用)
    # 客户端凭据模式通常不需要刷新令牌
    new_refresh_token = None
    if grant_type in ["authorization_code", "password", "refresh_token"]:
        new_refresh_token = secrets.token_urlsafe(32)
        REFRESH_TOKENS_DB[new_refresh_token] = user_id
        # 清理旧的刷新令牌（如果正在刷新）
        if grant_type == "refresh_token" and refresh_token in REFRESH_TOKENS_DB:
            del REFRESH_TOKENS_DB[refresh_token]

    token_response = {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds(),
    }
    if new_refresh_token:
        token_response["refresh_token"] = new_refresh_token

    return token_response


# --- 5. 资源服务器：受保护的 API 端点 ---
@app.get("/me")
async def read_users_me(
    current_user_id: Annotated[str, Depends(get_current_user_from_token)],
):
    """
    一个受保护的端点，返回当前令牌持有者的信息。
    """
    if current_user_id in USERS_DB:
        # 这是一个用户
        user_info = USERS_DB[current_user_id]
        return {"user_id": current_user_id, "scopes": user_info.get("scopes")}
    elif current_user_id in CLIENTS_DB:
        # 这是一个客户端 (通过客户端凭据模式)
        client_info = CLIENTS_DB[current_user_id]
        return {"client_id": current_user_id, "name": client_info.get("name")}
    else:
        # 理论上不应该发生，因为 get_current_user_from_token 已经验证过
        raise HTTPException(status_code=404, detail="Entity not found")


@app.get("/")
def read_root():
    return {
        "message": "OAuth 2.0 Authorization Server is running. Visit /docs for API documentation."
    }
