# main.py

import hashlib
import secrets
import time
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security.http import HTTPBase

# --- 模拟的数据库和 Nonce 存储 ---

# 在生产环境中，应使用真实的数据库来存储用户信息。
# 这里的密码是明文的，因为摘要认证的服务器端需要它来做哈希计算。
# 或者，你可以预先计算并存储 HA1 = MD5(username:realm:password)。
USERS_DB = {"admin": "secretpassword", "user2": "pa$$w0rd"}

# 在生产环境中，应使用像 Redis 这样的缓存来存储 Nonce。
# 这里的字典用于演示目的。
# {nonce: creation_time}
VALID_NONCES: Dict[str, float] = {}
NONCE_EXPIRATION_SECONDS = 300  # Nonce 5 分钟后过期


# --- HTTP Digest 安全方案实现 ---


class HTTPDigest(HTTPBase):
    def __init__(self, realm: str = "Protected Area", scheme: str = "Digest"):
        self.realm = realm
        self.scheme = scheme
        self.qop = "auth"  # 仅支持 "auth" 模式
        # qop="auth" 表示仅认证，不包含消息完整性检查
        self.algorithm = "MD5"  # Digest 规范中主要是 MD5

    async def __call__(self, request: Request) -> Optional[str]:
        # 清理过期的 Nonce
        self._cleanup_expired_nonces()

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            # 1. 质询 (Challenge) 阶段：客户端首次请求，没有凭据
            return self._issue_challenge()

        # 解析 Authorization 头
        try:
            scheme, creds_str = authorization.split(" ", 1)
            if scheme.lower() != self.scheme.lower():
                # 如果方案不是 "Digest"，则不由此认证器处理
                return None

            # 将 "key1=value1, key2="value2"" 解析为字典
            creds = dict(item.strip().split("=", 1) for item in creds_str.split(","))
            # 去除值两边的引号
            creds = {k: v.strip('"') for k, v in creds.items()}
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid Authorization header")

        # 2. 响应 (Response) 验证阶段
        return self._verify_response(request, creds)

    def _issue_challenge(self):
        """生成并发送 401 质询"""
        nonce = secrets.token_hex(16)
        VALID_NONCES[nonce] = time.time()

        headers = {
            "WWW-Authenticate": f'{self.scheme} realm="{self.realm}", qop={self.qop}, nonce="{nonce}", algorithm="{self.algorithm}"'
        }
        raise HTTPException(status_code=401, headers=headers)

    def _verify_response(self, request: Request, creds: Dict):
        """验证客户端发来的摘要响应"""
        # 检查所有必需的字段是否存在
        required_fields = [
            "username",
            "realm",
            "nonce",
            "uri",
            "response",
            "qop",
            "nc",
            "cnonce",
        ]
        if not all(field in creds for field in required_fields):
            raise HTTPException(
                status_code=400, detail="Missing fields in Digest credentials"
            )

        # 验证 realm 和 nonce
        if creds["realm"] != self.realm:
            raise HTTPException(status_code=401, detail="Invalid realm")

        server_nonce = creds.get("nonce")
        if server_nonce not in VALID_NONCES:
            raise HTTPException(status_code=401, detail="Invalid or expired nonce")

        # 使用后立即删除 Nonce，确保一次性
        del VALID_NONCES[server_nonce]

        # 从数据库获取用户信息
        username = creds["username"]
        if username not in USERS_DB:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        password = USERS_DB[username]

        # 在服务器端重新计算摘要
        ha1 = self._md5(f"{username}:{self.realm}:{password}")
        ha2 = self._md5(f'{request.method}:{creds["uri"]}')

        expected_response = self._md5(
            f'{ha1}:{server_nonce}:{creds["nc"]}:{creds["cnonce"]}:{creds["qop"]}:{ha2}'
        )

        # 比较客户端的 response 和服务器计算的 response
        if not secrets.compare_digest(creds["response"], expected_response):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # 认证成功，返回用户名
        return username

    def _md5(self, data: str) -> str:
        """计算字符串的 MD5 哈希值"""
        return hashlib.md5(data.encode("utf-8")).hexdigest()

    def _cleanup_expired_nonces(self):
        """从存储中移除过期的 Nonce"""
        current_time = time.time()
        expired = [
            nonce
            for nonce, ts in VALID_NONCES.items()
            if ts < current_time - NONCE_EXPIRATION_SECONDS
        ]
        for nonce in expired:
            del VALID_NONCES[nonce]
