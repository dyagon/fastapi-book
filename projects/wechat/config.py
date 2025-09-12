"""应用配置"""
import os
from typing import Optional


class Config:
    """应用配置类"""
    
    # 微信应用配置
    WECHAT_APP_ID: str = os.getenv("WECHAT_APP_ID", "wx1234567890abcdef")
    WECHAT_APP_SECRET: str = os.getenv("WECHAT_APP_SECRET", "your_app_secret_here")
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./wechat.db")
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # 令牌配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "7200"))  # 2小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30天


# 全局配置实例
config = Config()
