
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

async_engine = create_async_engine(get_settings().ASYNC_DATABASE_URL, echo=False)

class Base(DeclarativeBase):
    pass


SessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)
