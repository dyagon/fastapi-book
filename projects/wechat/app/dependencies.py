"""依赖注入"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession

from ..infra import SessionLocal, redis_client
from ..domain import WechatLoginService
from ..domain.models.session import UserInfo

from ..domain.repos.session_repo import SessionRepository


# HTTP Bearer 认证
security = HTTPBearer()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session



async def get_current_user(
):
    yield UserInfo(
        nickname="test",
        avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=test",
        openid="test",
        unionid="test"

    )


async def get_session_repo() -> SessionRepository:
    yield SessionRepository(redis_client)


async def get_login_service() -> WechatLoginService:
    repo = SessionRepository(redis_client)
    yield WechatLoginService(repo)