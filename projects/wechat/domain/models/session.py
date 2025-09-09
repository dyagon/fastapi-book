import time
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timezone, timedelta
import uuid
from typing import Optional, Dict, Any


class QRCodeStatus(str, Enum):
    """二维码状态枚举"""
    UNSCANNED = "unscanned"  # 未扫描
    SCANNED = "scanned"      # 已扫描，等待确认
    CONFIRMED = "confirmed"  # 已确认，登录成功
    EXPIRED = "expired"      # 已过期
    CANCELLED = "cancelled"  # 已取消


class UserInfo(BaseModel):
    """用户信息模型"""
    nickname: str
    avatar: str
    openid: Optional[str] = None
    unionid: Optional[str] = None


class QRSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    app_id: str
    redirect_uri: str
    response_type: str = "code"
    scope: str = "snsapi_login"
    state: str
    status: QRCodeStatus = QRCodeStatus.UNSCANNED

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))
    user_info: Optional[UserInfo] = None
    auth_code: Optional[str] = None
    
    
    def is_expired(self) -> bool:
        """检查会话是否已过期"""
        now = datetime.now(timezone.utc)
        return now > self.expires_at
    
    def can_scan(self) -> bool:
        """检查是否可以扫描"""
        return self.status == QRCodeStatus.UNSCANNED and not self.is_expired()
    
    def can_confirm(self) -> bool:
        """检查是否可以确认"""
        return self.status == QRCodeStatus.SCANNED and not self.is_expired()
    
    def can_cancel(self) -> bool:
        """检查是否可以取消"""
        return self.status in [QRCodeStatus.UNSCANNED, QRCodeStatus.SCANNED] and not self.is_expired()
    
    def mark_scanned(self, user_info: UserInfo) -> None:
        """标记为已扫描"""
        if not self.can_scan():
            raise ValueError("会话状态不允许扫描")
        self.status = QRCodeStatus.SCANNED
        self.user_info = user_info
    
    def mark_confirmed(self, code: str) -> None:
        """标记为已确认"""
        if not self.can_confirm():
            raise ValueError("会话状态不允许确认")
        self.status = QRCodeStatus.CONFIRMED
        self.auth_code = code
    
    def mark_cancelled(self) -> None:
        """标记为已取消"""
        if not self.can_cancel():
            raise ValueError("会话状态不允许取消")
        self.status = QRCodeStatus.CANCELLED
    
    def mark_expired(self) -> None:
        """标记为已过期"""
        self.status = QRCodeStatus.EXPIRED
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，兼容原有接口"""
        return {
            "status": self.status.value.upper(),
            "redirect_uri": self.redirect_uri,
            "state": self.state,
            "appid": self.app_id,
            "user_info": self.user_info.model_dump() if self.user_info else None,
            "code": self.auth_code,
            "created_at": self.created_at.timestamp(),
        }
