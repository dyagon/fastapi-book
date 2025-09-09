"""微信应用配置"""
from pydantic_settings import BaseSettings
from typing import Optional


class WeChatConfig(BaseSettings):
    """微信应用配置"""
    
    # 应用基本信息
    app_id: str = "wx1234567890abcdef"
    app_secret: str = "your_app_secret_here"
    app_name: str = "微信模拟应用"
    
    # OAuth2 配置
    redirect_uri: str = "http://localhost:8000/wechat/oauth/callback"
    scope: str = "snsapi_userinfo"
    
    # 支付配置
    mch_id: str = "1234567890"  # 商户号
    api_key: str = "your_payment_api_key_here"
    notify_url: str = "http://localhost:8000/wechat/payment/notify"
    
    # 微信 API 地址
    wechat_api_base: str = "https://api.weixin.qq.com"
    wechat_pay_api_base: str = "https://api.mch.weixin.qq.com"
    
    # 数据库配置
    database_url: str = "sqlite:///./wechat.db"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    redis_db: int = 0
    


# 全局配置实例
config = WeChatConfig()

