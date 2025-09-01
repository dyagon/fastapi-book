import functools
import inspect
import json
import dataclasses
from typing import Callable, Any

import redis.asyncio as redis
from pydantic import BaseModel
from pydantic.json import pydantic_encoder


class CacheManager:
    def __init__(self):
        self.redis_client = None
        self.prefix = "null"

    def setup(self, redis_client: redis.Redis, prefix: str = "cache"):
        self.redis_client = redis_client
        self.prefix = prefix

    def _generate_final_key(self, cache_name: str, key_template: str, func: Callable, *args: Any, **kwargs: Any) -> str:
        """根据 cache_name、key 模板和函数参数生成最终的 Redis 键。"""
        # 将位置参数和关键字参数统一到一个字典中
        sig = inspect.signature(func)
        
        # 提取 result 参数 (如果存在)，因为它不是函数签名的一部分
        result = kwargs.pop('result', None)
        
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        all_args = bound_args.arguments
        
        # 如果有 result，将其添加到参数字典中
        if result is not None:
            all_args['result'] = result
        
        # 使用函数参数来格式化 key 模板
        # 例如 key_template="user:{id}" 和 all_args={'id': 123} -> "user:123"
        try:
            rendered_key = key_template.format(**all_args)
        except KeyError as e:
            raise KeyError(f"Key template '{key_template}' references a non-existent parameter: {e}")

        return f"{self.prefix}:{cache_name}:{rendered_key}"

    def _serialize(self, value: Any) -> str:
        """
        一个更健壮的序列化方法。
        """
        # 1. 首先检查是否为 Pydantic 模型
        if isinstance(value, BaseModel):
            return value.model_dump_json()

        # 2. 检查是否为 dataclass
        if dataclasses.is_dataclass(value):
            return json.dumps(dataclasses.asdict(value), default=pydantic_encoder)
            
        # 3. 检查是否有 to_dict() 方法 (一个常见的自定义模式)
        if hasattr(value, 'to_dict') and callable(value.to_dict):
            return json.dumps(value.to_dict(), default=pydantic_encoder)

        # 4. 如果是一个列表，递归地序列化列表中的每个元素
        if isinstance(value, list):
            return json.dumps([self._serialize(item) for item in value])

        # 5. 最后的备选方案：尝试使用对象的 __dict__
        #    注意：这可能会暴露不想暴露的内部属性（如 SQLAlchemy 的 _sa_instance_state）
        #    因此，通常最好使用一个明确的 to_dict() 方法。
        #    但作为一个通用方法，我们可以先转换它。
        if hasattr(value, '__dict__'):
             # 我们需要一个辅助函数来清理 SQLAlchemy 的状态
            def clean_dict(obj_dict):
                return {k: v for k, v in obj_dict.items() if not k.startswith('_')}
            
            return json.dumps(clean_dict(value.__dict__))

        # 6. 如果以上都不行，就让它按原样失败，以便我们能发现问题
        return json.dumps(value)


    def _deserialize(self, value: str) -> Any:
        return json.loads(value)

    def cacheable(self, cache_name: str, key: str, expire: int = 3600):
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                final_key = self._generate_final_key(cache_name, key, func, *args, **kwargs)

                print(f"--- [CACHE CHECK] for key: {final_key} ---")
                cached_result = await self.redis_client.get(final_key)


                if cached_result:
                    print(f"--- [CACHE HIT] for key: {final_key} ---")
                    return self._deserialize(cached_result)

                print(f"--- [CACHE MISS] for key: {final_key} ---")
                result = await func(*args, **kwargs)
                
                if result is not None:
                    serialized_result = self._serialize(result)
                    await self.redis_client.set(final_key, serialized_result, ex=expire)
                
                return result
            return wrapper
        return decorator

    def cache_put(self, cache_name: str, key: str, expire: int = 3600):
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                final_key = self._generate_final_key(cache_name, key, func, *args, **kwargs, result=result)
                
                await self.redis_client.set(final_key, self._serialize(result), ex=expire)
                
                return result
            return wrapper
        return decorator

    def cache_evict(self, cache_name: str, key: str):
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # 在函数执行后删除缓存
                result = await func(*args, **kwargs)
                
                final_key = self._generate_final_key(cache_name, key, func, *args, **kwargs)
                print(f"--- [CACHE EVICT] Deleting key: {final_key} ---")
                await self.redis_client.delete(final_key)
                
                return result
            return wrapper
        return decorator

cache = CacheManager()