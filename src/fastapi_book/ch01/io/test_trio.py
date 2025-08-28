import trio
import time

async def task_worker(name: str, delay: float):
    """一个简单的异步任务"""
    print(f"[{time.monotonic():.2f}] 任务 {name} 开始执行...")
    await trio.sleep(delay) # 使用 trio.sleep
    print(f"[{time.monotonic():.2f}] 任务 {name} 执行完毕。")

async def main():
    print(f"[{time.monotonic():.2f}] 主程序开始。")
    # nursery 是一个异步上下文管理器
    async with trio.open_nursery() as nursery:
        # 使用 nursery.start_soon 来启动并发任务
        # 这就像对 nursery 说：“请帮我照看这个任务”
        nursery.start_soon(task_worker, "A", 1) # 启动任务 A，耗时 1 秒
        nursery.start_soon(task_worker, "B", 2) # 启动任务 B，耗时 2 秒

    # 当 async with 代码块结束时，trio 保证任务 A 和 B 都已经执行完毕。
    print(f"[{time.monotonic():.2f}] 主程序结束。")

# 使用 trio.run() 来启动主协程
if __name__ == "__main__":
    trio.run(main)
