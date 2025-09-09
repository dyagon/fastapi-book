"""支付服务"""
import secrets
import hashlib
import hmac
import time
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.config import config
from app.models import PaymentOrder, PaymentNotify
from app.dto import PaymentRequest, PaymentResponse, PaymentNotifyRequest, PaymentNotifyResponse


class PaymentService:
    """支付服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config = config
    
    def generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 过滤空值并排序
        filtered_params = {k: v for k, v in params.items() if v is not None and v != ""}
        sorted_params = sorted(filtered_params.items())
        
        # 拼接字符串
        string_a = "&".join([f"{k}={v}" for k, v in sorted_params])
        string_sign_temp = f"{string_a}&key={self.config.api_key}"
        
        # MD5签名
        return hashlib.md5(string_sign_temp.encode('utf-8')).hexdigest().upper()
    
    def verify_sign(self, params: Dict[str, Any], sign: str) -> bool:
        """验证签名"""
        expected_sign = self.generate_sign(params)
        return expected_sign == sign
    
    async def create_order(self, payment_request: PaymentRequest) -> PaymentResponse:
        """创建支付订单"""
        # 检查订单号是否已存在
        existing_order = self.db.query(PaymentOrder).filter(
            PaymentOrder.out_trade_no == payment_request.out_trade_no
        ).first()
        
        if existing_order:
            raise ValueError("订单号已存在")
        
        # 创建订单记录
        order = PaymentOrder(
            out_trade_no=payment_request.out_trade_no,
            openid=payment_request.openid,
            total_fee=payment_request.total_fee,
            body=payment_request.body,
            detail=payment_request.detail,
            attach=payment_request.attach,
            trade_type="JSAPI",
            status="PENDING"
        )
        
        self.db.add(order)
        self.db.commit()
        
        # 调用微信统一下单API（模拟）
        prepay_id = await self._unified_order(payment_request)
        
        # 更新订单的prepay_id
        order.prepay_id = prepay_id
        self.db.commit()
        
        # 生成JSAPI支付参数
        jsapi_params = self._generate_jsapi_params(prepay_id)
        
        return PaymentResponse(
            prepay_id=prepay_id,
            out_trade_no=payment_request.out_trade_no,
            jsapi_params=jsapi_params
        )
    
    async def _unified_order(self, payment_request: PaymentRequest) -> str:
        """调用微信统一下单API（模拟）"""
        # 在真实环境中，这里应该调用微信支付API
        # 这里我们模拟返回prepay_id
        
        params = {
            "appid": self.config.app_id,
            "mch_id": self.config.mch_id,
            "nonce_str": secrets.token_hex(16),
            "body": payment_request.body,
            "out_trade_no": payment_request.out_trade_no,
            "total_fee": payment_request.total_fee,
            "spbill_create_ip": "127.0.0.1",
            "notify_url": self.config.notify_url,
            "trade_type": "JSAPI",
            "openid": payment_request.openid
        }
        
        if payment_request.detail:
            params["detail"] = payment_request.detail
        if payment_request.attach:
            params["attach"] = payment_request.attach
        
        # 生成签名
        params["sign"] = self.generate_sign(params)
        
        # 模拟API调用成功，返回prepay_id
        prepay_id = f"wx{secrets.token_hex(16)}"
        
        return prepay_id
    
    def _generate_jsapi_params(self, prepay_id: str) -> Dict[str, Any]:
        """生成JSAPI支付参数"""
        timestamp = str(int(time.time()))
        nonce_str = secrets.token_hex(16)
        
        params = {
            "appId": self.config.app_id,
            "timeStamp": timestamp,
            "nonceStr": nonce_str,
            "package": f"prepay_id={prepay_id}",
            "signType": "MD5"
        }
        
        # 生成签名
        params["paySign"] = self.generate_sign(params)
        
        return params
    
    async def handle_payment_notify(self, notify_data: str) -> PaymentNotifyResponse:
        """处理支付通知"""
        try:
            # 解析XML数据
            root = ET.fromstring(notify_data)
            notify_dict = {child.tag: child.text for child in root}
            
            # 验证签名
            sign = notify_dict.pop("sign", "")
            if not self.verify_sign(notify_dict, sign):
                return PaymentNotifyResponse(return_code="FAIL", return_msg="签名验证失败")
            
            # 创建通知记录
            notify_record = PaymentNotify(
                transaction_id=notify_dict["transaction_id"],
                out_trade_no=notify_dict["out_trade_no"],
                openid=notify_dict["openid"],
                total_fee=int(notify_dict["total_fee"]),
                result_code=notify_dict["result_code"],
                return_code=notify_dict["return_code"],
                notify_data=notify_data
            )
            
            self.db.add(notify_record)
            
            # 如果支付成功，更新订单状态
            if (notify_dict["return_code"] == "SUCCESS" and 
                notify_dict["result_code"] == "SUCCESS"):
                
                order = self.db.query(PaymentOrder).filter(
                    PaymentOrder.out_trade_no == notify_dict["out_trade_no"]
                ).first()
                
                if order:
                    order.status = "PAID"
                    order.transaction_id = notify_dict["transaction_id"]
                    order.paid_at = datetime.now()
                    notify_record.processed = True
            
            self.db.commit()
            
            return PaymentNotifyResponse(return_code="SUCCESS", return_msg="OK")
            
        except Exception as e:
            return PaymentNotifyResponse(return_code="FAIL", return_msg=f"处理失败: {str(e)}")
    
    def get_order_status(self, out_trade_no: str) -> Optional[Dict[str, Any]]:
        """查询订单状态"""
        order = self.db.query(PaymentOrder).filter(
            PaymentOrder.out_trade_no == out_trade_no
        ).first()
        
        if not order:
            return None
        
        return {
            "out_trade_no": order.out_trade_no,
            "transaction_id": order.transaction_id,
            "status": order.status,
            "total_fee": order.total_fee,
            "created_at": order.created_at,
            "paid_at": order.paid_at
        }
    
    async def close_order(self, out_trade_no: str) -> bool:
        """关闭订单"""
        order = self.db.query(PaymentOrder).filter(
            PaymentOrder.out_trade_no == out_trade_no
        ).first()
        
        if not order or order.status != "PENDING":
            return False
        
        # 在真实环境中，这里应该调用微信关闭订单API
        # 这里我们直接更新订单状态
        order.status = "CLOSED"
        self.db.commit()
        
        return True
