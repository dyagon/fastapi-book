"""支付路由"""
import time
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.payment_service import PaymentService
from app.dto import (
    PaymentRequest, 
    PaymentResponse, 
    PaymentNotifyResponse,
    OrderStatusResponse
)

router = APIRouter(prefix="/wechat/payment", tags=["Payment"])


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment_request: PaymentRequest,
    db: Session = Depends(get_db)
):
    """创建支付订单"""
    payment_service = PaymentService(db)
    
    try:
        payment_response = await payment_service.create_order(payment_request)
        return payment_response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")


@router.post("/notify", response_class=PlainTextResponse)
async def payment_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """支付结果通知"""
    payment_service = PaymentService(db)
    
    try:
        # 获取原始XML数据
        notify_data = await request.body()
        notify_data_str = notify_data.decode('utf-8')
        
        # 处理支付通知
        response = await payment_service.handle_payment_notify(notify_data_str)
        
        # 返回XML格式的响应
        if response.return_code == "SUCCESS":
            return """<xml>
<return_code><![CDATA[SUCCESS]]></return_code>
<return_msg><![CDATA[OK]]></return_msg>
</xml>"""
        else:
            return f"""<xml>
<return_code><![CDATA[FAIL]]></return_code>
<return_msg><![CDATA[{response.return_msg}]]></return_msg>
</xml>"""
            
    except Exception as e:
        return f"""<xml>
<return_code><![CDATA[FAIL]]></return_code>
<return_msg><![CDATA[处理失败: {str(e)}]]></return_msg>
</xml>"""


@router.get("/order/{out_trade_no}", response_model=OrderStatusResponse)
async def get_order_status(
    out_trade_no: str,
    db: Session = Depends(get_db)
):
    """查询订单状态"""
    payment_service = PaymentService(db)
    
    order_info = payment_service.get_order_status(out_trade_no)
    if not order_info:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    return OrderStatusResponse(**order_info)


@router.post("/close/{out_trade_no}")
async def close_order(
    out_trade_no: str,
    db: Session = Depends(get_db)
):
    """关闭订单"""
    payment_service = PaymentService(db)
    
    try:
        success = await payment_service.close_order(out_trade_no)
        if not success:
            raise HTTPException(status_code=400, detail="订单无法关闭")
        
        return {"message": "订单已关闭"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_payment_flow(db: Session = Depends(get_db)):
    """测试支付流程（模拟环境专用）"""
    payment_service = PaymentService(db)
    
    try:
        # 1. 创建测试订单
        test_request = PaymentRequest(
            out_trade_no=f"TEST_{int(time.time())}",
            total_fee=100,  # 1元
            body="测试商品",
            detail="这是一个测试订单",
            openid="test_openid_123"
        )
        
        payment_response = await payment_service.create_order(test_request)
        
        # 2. 模拟支付成功通知
        mock_notify_data = f"""<xml>
<return_code><![CDATA[SUCCESS]]></return_code>
<return_msg><![CDATA[OK]]></return_msg>
<appid><![CDATA[{payment_service.config.app_id}]]></appid>
<mch_id><![CDATA[{payment_service.config.mch_id}]]></mch_id>
<nonce_str><![CDATA[test_nonce]]></nonce_str>
<sign><![CDATA[TEST_SIGN]]></sign>
<result_code><![CDATA[SUCCESS]]></result_code>
<openid><![CDATA[test_openid_123]]></openid>
<is_subscribe><![CDATA[Y]]></is_subscribe>
<trade_type><![CDATA[JSAPI]]></trade_type>
<bank_type><![CDATA[CFT]]></bank_type>
<total_fee>100</total_fee>
<fee_type><![CDATA[CNY]]></fee_type>
<cash_fee>100</cash_fee>
<cash_fee_type><![CDATA[CNY]]></cash_fee_type>
<transaction_id><![CDATA[wx_test_transaction_id]]></transaction_id>
<out_trade_no><![CDATA[{test_request.out_trade_no}]]></out_trade_no>
<attach><![CDATA[test_attach]]></attach>
<time_end><![CDATA[20231201120000]]></time_end>
</xml>"""
        
        notify_response = await payment_service.handle_payment_notify(mock_notify_data)
        
        # 3. 查询订单状态
        order_status = payment_service.get_order_status(test_request.out_trade_no)
        
        return {
            "payment_response": payment_response,
            "notify_response": notify_response,
            "order_status": order_status,
            "message": "支付流程测试完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
