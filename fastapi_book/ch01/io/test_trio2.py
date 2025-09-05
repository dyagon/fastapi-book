import trio
import time

async def success_task():
    print("成功任务正在运行...")
    await trio.sleep(5) # 假设这个任务需要很长时间
    print("成功任务完成。 (这句话永远不会被打印)")

async def failure_task():
    print("失败任务开始，将在1秒后崩溃...")
    await trio.sleep(1)
    raise ValueError("我崩溃了！")

async def main():
    try:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(success_task)
            nursery.start_soon(failure_task)
    except ValueError as e:
        print(f"捕获到了预期的错误: {e}")

    print("所有任务都已清理完毕，程序干净地退出。")

if __name__ == "__main__":
    trio.run(main)
