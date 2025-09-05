import asyncio
from contextvars import ContextVar

# 1. 定义一个上下文变量，比如用于追踪请求ID
request_id_var = ContextVar('request_id', default='N/A')

async def sub_task():
    # 这个子任务可以访问由父任务设置的上下文
    print(f"  [Sub Task] 开始执行, request_id = {request_id_var.get()}")
    await asyncio.sleep(0.5)
    print(f"  [Sub Task] 执行结束")

async def handler():
    # 这个 "handler" 运行在由 "middleware" 创建的上下文中
    print(f" [Handler] 开始处理, request_id = {request_id_var.get()}")
    # 创建一个子任务，它将自动继承当前上下文
    await asyncio.create_task(sub_task())
    print(f" [Handler] 处理结束")

async def middleware(request_name: str):
    # 这个 "middleware" 为每个 "请求" 设置一个唯一的上下文
    token = request_id_var.set(f"req-{request_name}")
    print(f"[Middleware] 收到请求 {request_name}, 设置 request_id = {request_id_var.get()}")
    await handler()
    # 恢复上下文到之前的状态
    request_id_var.reset(token)
    print(f"[Middleware] 请求 {request_name} 完成, request_id 恢复为 = {request_id_var.get()}")

async def independent_task():
    # 这个任务独立运行，拥有自己的上下文
    print(f"[Independent Task] 开始执行, request_id = {request_id_var.get()}")
    await asyncio.sleep(1)
    print(f"[Independent Task] 执行结束, request_id = {request_id_var.get()}")


async def main():
    print("--- 演示 asyncio 和 ContextVar ---")
    
    # 创建一个独立运行的任务
    task_independent = asyncio.create_task(independent_task())

    # 模拟两个并发的 "请求"，每个都有自己的上下文
    await asyncio.gather(
        middleware("A"),
        middleware("B")
    )

    await task_independent
    print("\n--- 演示结束 ---")


if __name__ == "__main__":
    asyncio.run(main())
