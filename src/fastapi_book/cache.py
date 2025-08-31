import functools
import json
from redis.asyncio import Redis

class CacheManager:
    """
    A class-based decorator for caching that allows for dependency injection.
    """
    def __init__(self):
        # The Redis client will be injected after initialization.
        self._redis_client: Redis | None = None

    def setup(self, redis_client: Redis):
        """Inject the Redis client into the cache manager."""
        print("CacheManager: Redis client has been injected.")
        self._redis_client = redis_client

    def __call__(self, ttl: int = 60):
        """This is the actual decorator factory."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # 1. Check if the Redis client was injected. If not, bypass cache.
                if self._redis_client is None:
                    # This happens if setup() was never called.
                    # We bypass caching to ensure the app still works.
                    print("Warning: Redis client not available. Bypassing cache.")
                    return await func(*args, **kwargs)

                # 2. Generate a stable cache key.
                # Important: We must not include non-serializable dependencies 
                # like the database session in the cache key.
                serializable_kwargs = {
                    k: v for k, v in kwargs.items() 
                    if isinstance(v, (str, int, float, bool, dict, list, tuple))
                }
                
                kwargs_str = json.dumps(serializable_kwargs, sort_keys=True)
                # Note: This simple args serialization might not cover all cases.
                args_str = str(args) 
                
                cache_key = f"cache:{func.__name__}:{args_str}:{kwargs_str}"

                # 3. Try to get from cache (Cache HIT)
                try:
                    cached_result = await self._redis_client.get(cache_key)
                    if cached_result:
                        print(f"Cache HIT for key: {cache_key}")
                        return json.loads(cached_result)
                except Exception as e:
                    print(f"Redis Error: Could not read from cache. Bypassing. Error: {e}")

                # 4. Execute function on Cache MISS
                print(f"Cache MISS for key: {cache_key}")
                result = await func(*args, **kwargs)

                # 5. Store the result in cache
                try:
                    await self._redis_client.set(
                        cache_key, json.dumps(result), ex=ttl
                    )
                except Exception as e:
                    print(f"Redis Error: Could not write to cache. Error: {e}")

                return result
            return wrapper
        return decorator

# Create a single, global instance of the cache manager.
# We will import this instance in other parts of our app.
cache = CacheManager()
