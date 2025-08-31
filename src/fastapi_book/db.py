import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Database URL - can be overridden by environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:admin123@localhost:25432/fastapi_book"
)

# For sync operations, use psycopg2
# SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
# engine = create_engine(SYNC_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # Dependency to get database session
# def get_db():
#     """Dependency for getting sync database session"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# For async operations, use asyncpg driver
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
