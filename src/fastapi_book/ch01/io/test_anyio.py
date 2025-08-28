import anyio
import time

async def task_worker(name: str, delay: float):
    """一个简单的异步任务，打印信息并休眠"""
    print(f"[{time.monotonic():.2f}] 任务 {name} 开始执行...")
    await anyio.sleep(delay)  # 使用 anyio.sleep 而不是 asyncio.sleep
    print(f"[{time.monotonic():.2f}] 任务 {name} 执行完毕。")

async def main():
    """主协程，使用任务组并发运行 worker"""
    print(f"[{time.monotonic():.2f}] 主程序开始。")
    async with anyio.create_task_group() as tg:
        # start_soon 会立即返回，不会等待任务完成
        tg.start_soon(task_worker, "A", 1) # 启动任务 A，耗时 1 秒
        tg.start_soon(task_worker, "B", 2) # 启动任务 B，耗时 2 秒

    # 当 async with 代码块结束时，anyio 会确保任务组中的所有任务
    # (即 A 和 B) 都已执行完毕。
    print(f"[{time.monotonic():.2f}] 主程序结束。")

# 使用 anyio.run 来启动主协CHA序
# 你可以指定后端，默认是 asyncio
# anyio.run(main, backend="asyncio")
# anyio.run(main, backend="trio")
if __name__ == "__main__":
    anyio.run(main)

