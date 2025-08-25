
import time


def take_up_time(func):
    def wrapper(*args, **kwargs):
        print("开始执行--->")
        now = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"执行时间：{end - now}秒")
        return result
    return wrapper
