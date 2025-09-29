import os

from functools import wraps
from contextvars import ContextVar
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DB_URI = os.environ["DB_URI"]
DB_DEBUG_ECHO = os.environ.get("DB_DEBUG_ECHO", True)
DB_POOL_SIZE = os.environ.get("DB_POOL_SIZE", 10)
DB_MAX_OVERFLOW = os.environ.get("DB_MAX_OVERFLOW", 20)


engine = create_async_engine(
    DB_URI, echo=DB_DEBUG_ECHO, pool_size=DB_POOL_SIZE, max_overflow=DB_MAX_OVERFLOW
)

session_maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


_async_session_context: ContextVar[Optional[AsyncSession]] = ContextVar(
    "async_session_context", default=None
)


class Repository:
    @property
    def session(self) -> AsyncSession:
        session = _async_session_context.get()
        if session is None:
            raise Exception("Database session not found")
        return session


def transactional_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = _async_session_context.get()
        if session is not None:
            return await func(*args, **kwargs)
        async with session_maker() as session:
            print(f"    -> (Transactional) New ASYNC session created: {id(session)}")
            token = _async_session_context.set(session)
            try:
                result = await func(*args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
            finally:
                print(f"    <- (Transactional) ASYNC Session closed: {id(session)}")
                _async_session_context.reset(token)
                if session.is_active:
                    await session.close()

    return wrapper


def read_only_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = _async_session_context.get()
        if session is not None:
            return await func(*args, **kwargs)
        async with session_maker() as session:
            print(f"    -> (Read Only) New ASYNC session created: {id(session)}")
            token = _async_session_context.set(session)
            try:
                return await func(*args, **kwargs)
            finally:
                print(f"    <- (Read Only) ASYNC Session closed: {id(session)}")
                _async_session_context.reset(token)
                if session.is_active:
                    await session.close()

    return wrapper
