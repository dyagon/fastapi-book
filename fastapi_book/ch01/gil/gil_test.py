import threading
import time
import os

# CPU 密集型任务：累加到一个很大的数
def cpu_intensive_task():
    sum_val = 0
    for i in range(10_000_000):
        sum_val += i


def run_tasks_threads(num_tasks: int):
    threads = []
    start_time = time.time()

    # 创建并启动指定数量的线程
    for _ in range(num_tasks):
        thread = threading.Thread(target=cpu_intensive_task)
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    duration = time.time() - start_time
    print(f"多线程完成 {num_tasks} 个任务耗时: {duration:.2f} 秒")

def run_tasks_sequential(num_tasks: int):
    start_time = time.time()

    # 顺序执行任务
    for _ in range(num_tasks):
        cpu_intensive_task()

    duration = time.time() - start_time
    print(f"顺序完成 {num_tasks} 个任务耗时: {duration:.2f} 秒")

def main():
    # 设置要并发执行的任务数量
    num_tasks = os.cpu_count() # 理想情况下，设置为 CPU 核心数
    print(f"Python (threading) 实验：将在 {os.cpu_count()} 个 CPU 核心上运行 {num_tasks} 个线程。")

    run_tasks_sequential(num_tasks)
    run_tasks_threads(num_tasks)


if __name__ == "__main__":
    main()
