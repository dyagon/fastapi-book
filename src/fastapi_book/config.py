# src/fastapi_book/config.py

from functools import lru_cache
from typing import List
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

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

class Settings(BaseSettings):
    
    # 应用程序配置
    APP_NAME: str = "FastAPI App"
    DEBUG_MODE: bool = False

    # 数据库配置
    REDIS_URL: str
    DATABASE_URL: str
    
    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    # 安全配置
    # API_SECRET_KEY: str
    
    # 嵌套配置演示 (从环境变量 CORS_ORIGINS 读取)
    # Pydantic 会自动处理字符串到 List[str] 的转换
    CORS_ORIGINS: List[str] = []

    # 使用 SettingsConfigDict 来指定 .env 文件
    # 更多选项: https://docs.pydantic.dev/latest/concepts/settings/
    model_config = SettingsConfigDict(
        env_file=".env",          # 指定 .env 文件路径
        env_file_encoding="utf-8" # 指定编码
    )

# 使用 @lru_cache(maxsize=1) 实现配置的单例模式
# 当 get_settings() 被第一次调用时，它会创建一个 Settings 实例，
# 并从环境变量和 .env 文件中读取数据。
# 后续的调用将直接返回缓存的实例，而不会重复读取。
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


