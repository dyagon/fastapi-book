

from fastapi_book.config import get_settings

settings = get_settings()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Dependency to get database session
def get_db():
    """Dependency for getting sync database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
