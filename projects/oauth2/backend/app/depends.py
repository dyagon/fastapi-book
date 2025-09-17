from fastapi import Depends, Cookie, Request

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..context import infra
from ..domain.services.auth_login import OAuthLoginService
from ..domain.services.user_service import UserService
from ..impl.session_manager import SessionManager, Session
from ..impl.repo.user import UserRepo
from ..domain.services.auth_service import OAuth2ClientCredentialsService

async def get_auth_service() -> OAuth2ClientCredentialsService:
    return infra.auth_service



async def get_db_session() -> AsyncSession:
    async with infra.db.db_sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis_client() -> Redis:
    return infra.redis.get_redis()


async def get_auth_login_service(
    db: AsyncSession = Depends(get_db_session),
) -> OAuthLoginService:
    session_manager = SessionManager(infra.redis.get_redis())
    user_service = UserService(UserRepo(db))
    return OAuthLoginService(infra.cc_client, session_manager, user_service)


async def get_session_manager() -> SessionManager:
    return SessionManager(infra.redis.get_redis())


async def get_current_session(request: Request) -> Session:
    """Get current session data."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    session_manager = SessionManager(infra.redis.get_redis())
    return await session_manager.get_session(session_id)
