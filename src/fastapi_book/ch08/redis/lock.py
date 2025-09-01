import asyncio
import functools
import inspect
import uuid
from typing import Callable, Any

import redis.asyncio as redis

# --- 自定义异常 ---
class LockAcquisitionError(Exception):
    """当无法立即获取非阻塞锁时抛出。"""
    pass

class LockTimeoutError(Exception):
    """当在指定时间内无法获取阻塞锁时抛出。"""
    pass

class DistributedLockManager:
    def __init__(self):
        self.redis_client: redis.Redis | None = None
        self.prefix = ""

        # 安全释放锁的 Lua 脚本
        self.release_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
    def setup(self, redis_client: redis.Redis, prefix: str = "dist-lock"):
        self.redis_client = redis_client
        self.prefix = prefix

    def _generate_final_key(self, key_template: str, func: Callable, *args: Any, **kwargs: Any) -> str:
        """根据 key 模板和函数参数生成最终的 Redis 键。"""
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        all_args = bound_args.arguments
        
        try:
            rendered_key = key_template.format(**all_args)
        except KeyError as e:
            raise KeyError(f"Lock key template '{key_template}' references a non-existent parameter: {e}")
        return f"{self.prefix}:{rendered_key}"

    def lock(
        self, 
        key: str, 
        timeout_ms: int = 30000, 
        blocking: bool = True, 
        blocking_timeout_s: float = 10.0
    ):
        """
        分布式锁装饰器工厂。

        :param key: 锁的键模板，可引用函数参数，如 "user:{user_id}"。
        :param timeout_ms: 锁的过期时间（租约），单位为毫秒。
        :param blocking: 如果为 True，当锁被占用时，会等待直到获取锁或超时。
                         如果为 False，会立即失败并抛出 LockAcquisitionError。
        :param blocking_timeout_s: 阻塞模式下的总等待超时时间，单位为秒。
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                final_key = self._generate_final_key(key, func, *args, **kwargs)
                lock_value = str(uuid.uuid4())  # 每个锁实例的唯一凭证
                
                acquired = False
                start_time = asyncio.get_event_loop().time()

                while (asyncio.get_event_loop().time() - start_time) < blocking_timeout_s:
                    # 尝试原子性地设置键
                    acquired = await self.redis_client.set(
                        final_key, lock_value, nx=True, px=timeout_ms
                    )
                    
                    if acquired:
                        print(f"--- [LOCK] Acquired lock '{final_key}' ---")
                        break
                    
                    if not blocking:
                        raise LockAcquisitionError(f"Could not acquire non-blocking lock for '{final_key}'")

                    # 如果是阻塞模式，等待一小段时间再重试
                    await asyncio.sleep(0.1) 
                
                if not acquired:
                    raise LockTimeoutError(f"Timeout while waiting to acquire lock for '{final_key}' after {blocking_timeout_s}s")

                try:
                    # 成功获取锁，执行被保护的业务逻辑
                    return await func(*args, **kwargs)
                finally:
                    # 无论业务逻辑成功与否，都必须安全地释放锁
                    print(f"--- [LOCK] Releasing lock '{final_key}' ---")
                    await self.redis_client.eval(self.release_script, 1, final_key, lock_value)
            
            return wrapper
        return decorator

    def lock2(
        self,
        key: str,
        timeout_ms: int = 30000,
        blocking: bool = True,
        blocking_timeout_s: float = 10.0
    ):
        """
        使用 Redis 原生锁的分布式锁装饰器工厂。

        :param key: 锁的键模板，可引用函数参数，如 "user:{user_id}"。
        :param timeout_ms: 锁的过期时间（租约），单位为毫秒。
        :param blocking: 如果为 True，当锁被占用时，会等待直到获取锁或超时。
                         如果为 False，会立即失败并抛出 LockAcquisitionError。
        :param blocking_timeout_s: 阻塞模式下的总等待超时时间，单位为秒。
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                final_key = self._generate_final_key(key, func, *args, **kwargs)
                
                # 使用 Redis 原生锁
                lock = self.redis_client.lock(
                    name=final_key,
                    timeout=timeout_ms / 1000.0,  # Redis lock expects seconds
                    blocking=blocking,
                    blocking_timeout=blocking_timeout_s if blocking else None
                )
                
                acquired = False
                try:
                    # 尝试获取锁
                    acquired = await lock.acquire()
                    
                    if not acquired:
                        if not blocking:
                            raise LockAcquisitionError(f"Could not acquire non-blocking lock for '{final_key}'")
                        else:
                            raise LockTimeoutError(f"Timeout while waiting to acquire lock for '{final_key}' after {blocking_timeout_s}s")
                    
                    print(f"--- [LOCK2] Acquired Redis native lock '{final_key}' ---")
                    
                    # 成功获取锁，执行被保护的业务逻辑
                    return await func(*args, **kwargs)
                
                finally:
                    # 只有在成功获取锁的情况下才尝试释放
                    if acquired:
                        try:
                            if lock.owned():
                                print(f"--- [LOCK2] Releasing Redis native lock '{final_key}' ---")
                                await lock.release()
                            else:
                                print(f"--- [LOCK2] Lock '{final_key}' is no longer owned (may have expired) ---")
                        except Exception as e:
                            # 记录释放锁时的错误，但不要让它影响主要的业务逻辑
                            print(f"--- [LOCK2] Error releasing lock '{final_key}': {e} ---")
            
            return wrapper
        return decorator


lock_manager = DistributedLockManager()