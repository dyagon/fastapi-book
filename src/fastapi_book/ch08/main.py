import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from ..context import lifespan
from .user_route import route as user_route
from .redis.lock import lock_manager, LockAcquisitionError, LockTimeoutError

app = FastAPI(lifespan=lifespan)

app.include_router(user_route)


@app.exception_handler(LockAcquisitionError)
async def lock_acquisition_exception_handler(request: Request, exc: LockAcquisitionError):
    return JSONResponse(
        status_code=429,
        content={"message": f"Service busy, please try again later. Reason: {exc}"},
    )

@app.exception_handler(LockTimeoutError)
async def lock_timeout_exception_handler(request: Request, exc: LockTimeoutError):
    return JSONResponse(
        status_code=429,
        content={"message": f"Service busy, please try again later. Reason: {exc}"},
    )

# 模拟一个共享的资源，比如用户的钱包余额
USER_WALLETS = {"user_123": 100.0}


# --- API 端点 ---
@app.post("/wallets/{user_id}/pay")
@lock_manager.lock2(key="wallet:{user_id}", blocking=False, blocking_timeout_s=5)
async def process_payment(user_id: str, amount: float):
    """
    处理支付。此操作被分布式锁保护，以防止并发支付导致余额错乱。
    """
    print(f">>> Critical section entered for user '{user_id}' <<<")
    
    current_balance = USER_WALLETS.get(user_id)
    if current_balance is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 模拟耗时的I/O操作，比如调用第三方支付网关
    print("... Simulating payment processing ...")
    await asyncio.sleep(5) 
    
    USER_WALLETS[user_id] -= amount
    
    print(f">>> Critical section finished. New balance for {user_id} is {USER_WALLETS[user_id]} <<<")
    return {"user_id": user_id, "new_balance": USER_WALLETS[user_id]}

