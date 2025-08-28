import asyncio
import contextvars
import random

# 1. 创建一个 ContextVar，用于存储请求 ID
request_id_var = contextvars.ContextVar('request_id', default='N/A')

async def database_query():
    """模拟一个深层函数，它需要记录日志"""
    # 无需传递 request_id，直接从上下文中获取
    current_req_id = request_id_var.get()
    print(f"[DB Query]  日志: 开始查询... [Request ID: {current_req_id}]")
    await asyncio.sleep(random.uniform(0.1, 0.5))
    print(f"[DB Query]  日志: 查询完成.   [Request ID: {current_req_id}]")

async def handle_request(req_id: str):
    """
    处理单个请求的主函数。
    它负责为这个任务的上下文设置 request_id。
    """
    print(f"[Handler]   开始处理请求 [Request ID: {req_id}]")
    
    # 2. 设置上下文变量，并获取 token
    token = request_id_var.set(req_id)
    
    try:
        # 3. 调用业务逻辑，这些逻辑现在可以访问到正确的 request_id
        await database_query()
    finally:
        # 4. 保证在任务结束时重置上下文，防止状态泄露
        request_id_var.reset(token)
    
    print(f"[Handler]   完成处理请求 [Request ID: {req_id}]")

async def main():
    """模拟服务器接收到两个并发的请求"""
    # 使用 asyncio.gather 来并发运行两个 handle_request 任务
    await asyncio.gather(
        handle_request("req-abc-123"),
        handle_request("req-xyz-789")
    )

if __name__ == "__main__":
    asyncio.run(main())
