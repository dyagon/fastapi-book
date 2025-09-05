from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 定义连接异步引擎数据库的URL地址
    ASYNC_DATABASE_URI: str
    # 定义TOEKN的签名信息值
    TOKEN_SIGN_SECRET: str
    TOKEN_SIGN_ALGORITHM: str

    REDIS_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()
