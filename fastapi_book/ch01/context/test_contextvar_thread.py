import threading
from contextvars import ContextVar, copy_context

user_var = ContextVar('user', default='guest')


def thread_target():
    # 这个函数在新的线程中运行
    print(f"在当前线程中, user = {user_var.get()}")


def run_in_thread_with_context():
    # 在新线程中运行 thread_target 函数
    # 但我们使用 context.run() 来应用捕获到的上下文
    print("\n--- 运行在带有复制上下文的新线程中 ---")
    thread = threading.Thread(target=context.run, args=(thread_target,))
    thread.start()
    thread.join()


def run_in_thread_without_context():
    # 在新线程中直接运行 thread_target 函数
    # 它将无法访问主线程的上下文
    print("\n--- 运行在没有复制上下文的新线程中 ---")
    thread = threading.Thread(target=thread_target)
    thread.start()
    thread.join()


# 在主线程（或 asyncio 任务）中
user_var.set('admin')
print(f"主线程中, user = {user_var.get()}")

# 捕获当前上下文
context = copy_context()

# 运行带有上下文的线程
run_in_thread_with_context()

# 运行没有上下文的线程
run_in_thread_without_context()
