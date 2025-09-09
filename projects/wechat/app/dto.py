"""数据传输对象 (DTO)"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime



class ScanRequest(BaseModel):
    """扫描请求模型"""

    session_id: str


class ConfirmRequest(BaseModel):
    """确认请求模型"""
    session_id: str


class CancelRequest(BaseModel):
    """取消请求模型"""

    session_id: str


class OAuthAuthorizeRequest(BaseModel):
    """OAuth2 授权请求"""
    redirect_uri: str = Field(..., description="回调地址")
    scope: str = Field(default="snsapi_userinfo", description="授权范围")
    state: Optional[str] = Field(None, description="状态参数")


class OAuthCallbackRequest(BaseModel):
    """OAuth2 回调请求"""
    code: str = Field(..., description="授权码")
    state: Optional[str] = Field(None, description="状态参数")


class AccessTokenResponse(BaseModel):
    """访问令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    expires_in: int = Field(..., description="过期时间（秒）")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")
    scope: str = Field(..., description="授权范围")
    openid: str = Field(..., description="用户唯一标识")


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    openid: str = Field(..., description="用户唯一标识")
    nickname: str = Field(..., description="用户昵称")
    sex: int = Field(..., description="性别")
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    country: str = Field(..., description="国家")
    headimgurl: str = Field(..., description="头像URL")
    privilege: list = Field(default=[], description="用户特权信息")
    unionid: Optional[str] = Field(None, description="用户统一标识")


class PaymentRequest(BaseModel):
    """支付请求"""
    out_trade_no: str = Field(..., description="商户订单号")
    total_fee: int = Field(..., description="订单金额（分）")
    body: str = Field(..., description="商品描述")
    detail: Optional[str] = Field(None, description="商品详情")
    attach: Optional[str] = Field(None, description="附加数据")
    openid: str = Field(..., description="用户openid")


class PaymentResponse(BaseModel):
    """支付响应"""
    prepay_id: str = Field(..., description="预支付交易会话标识")
    out_trade_no: str = Field(..., description="商户订单号")
    jsapi_params: Dict[str, Any] = Field(..., description="JSAPI支付参数")


class PaymentNotifyRequest(BaseModel):
    """支付通知请求"""
    return_code: str = Field(..., description="返回状态码")
    return_msg: str = Field(..., description="返回信息")
    appid: str = Field(..., description="应用ID")
    mch_id: str = Field(..., description="商户号")
    nonce_str: str = Field(..., description="随机字符串")
    sign: str = Field(..., description="签名")
    result_code: str = Field(..., description="业务结果")
    openid: str = Field(..., description="用户标识")
    is_subscribe: str = Field(..., description="是否关注公众账号")
    trade_type: str = Field(..., description="交易类型")
    bank_type: str = Field(..., description="付款银行")
    total_fee: int = Field(..., description="订单金额")
    settlement_total_fee: Optional[int] = Field(None, description="应结订单金额")
    fee_type: str = Field(..., description="货币种类")
    cash_fee: int = Field(..., description="现金支付金额")
    cash_fee_type: str = Field(..., description="现金支付货币类型")
    transaction_id: str = Field(..., description="微信支付订单号")
    out_trade_no: str = Field(..., description="商户订单号")
    attach: Optional[str] = Field(None, description="附加数据")
    time_end: str = Field(..., description="支付完成时间")


class PaymentNotifyResponse(BaseModel):
    """支付通知响应"""
    return_code: str = Field(..., description="返回状态码")
    return_msg: str = Field(..., description="返回信息")


class OrderStatusResponse(BaseModel):
    """订单状态响应"""
    out_trade_no: str = Field(..., description="商户订单号")
    transaction_id: Optional[str] = Field(None, description="微信支付订单号")
    status: str = Field(..., description="订单状态")
    total_fee: int = Field(..., description="订单金额")
    created_at: datetime = Field(..., description="创建时间")
    paid_at: Optional[datetime] = Field(None, description="支付时间")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误代码")
    error_description: str = Field(..., description="错误描述")
