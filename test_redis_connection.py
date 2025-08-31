#!/usr/bin/env python3
"""
Redis connection test script
Run this to verify your Redis configuration
"""
import asyncio
import redis.asyncio as redis
from src.fastapi_book.redis_config import get_redis_url_for_environment, redis_config

async def test_redis_connection():
    """Test Redis connection with different configurations"""
    
    print("🔍 Testing Redis Connections...\n")
    
    # Test 1: Environment-based URL
    print("1️⃣ Testing environment-based Redis URL...")
    redis_url = get_redis_url_for_environment()
    print(f"   URL: {redis_url.replace(':redis_password', ':***')}")
    
    try:
        pool = redis.ConnectionPool.from_url(redis_url, **redis_config.get_connection_kwargs())
        client = redis.Redis(connection_pool=pool)
        
        # Test basic operations
        await client.ping()
        print("   ✅ Ping successful")
        
        # Test set/get
        await client.set("test:connection", "success", ex=10)
        value = await client.get("test:connection")
        print(f"   ✅ Set/Get test: {value}")
        
        # Test authentication works
        info = await client.info("server")
        print(f"   ✅ Server info accessible: Redis {info.get('redis_version', 'unknown')}")
        
        await client.delete("test:connection")
        await client.close()
        await pool.disconnect()
        
        print("   ✅ Connection test passed!\n")
        
    except redis.AuthenticationError:
        print("   ❌ Authentication failed - check password")
        print("      Docker: Make sure Redis is running with password 'redis_password'")
        print("      Command: docker-compose up redis\n")
        return False
        
    except redis.ConnectionError:
        print("   ❌ Connection failed - check if Redis is running")
        print("      Docker: docker-compose up redis")
        print("      Local: redis-server\n")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}\n")
        return False
    
    # Test 2: Different environments
    print("2️⃣ Testing different environment URLs...")
    environments = ["development", "testing", "local"]
    
    for env in environments:
        env_url = get_redis_url_for_environment(env)
        print(f"   {env}: {env_url.replace(':redis_password', ':***')}")
    
    print("\n✅ All tests completed successfully!")
    return True

async def test_cache_operations():
    """Test advanced cache operations"""
    
    print("🧪 Testing Cache Operations...\n")
    
    redis_url = get_redis_url_for_environment()
    pool = redis.ConnectionPool.from_url(redis_url, **redis_config.get_connection_kwargs())
    client = redis.Redis(connection_pool=pool)
    
    try:
        # Test JSON serialization
        test_data = {
            "user_id": 123,
            "username": "testuser",
            "email": "test@example.com",
            "metadata": {"last_login": "2025-08-31T10:00:00Z"}
        }
        
        import json
        await client.set("test:user:123", json.dumps(test_data), ex=60)
        cached_data = await client.get("test:user:123")
        retrieved_data = json.loads(cached_data)
        
        print(f"   ✅ JSON caching test: {retrieved_data['username']}")
        
        # Test counters
        counter_key = "test:counter"
        count = await client.incr(counter_key)
        await client.expire(counter_key, 60)
        print(f"   ✅ Counter test: {count}")
        
        # Test pattern operations
        await client.set("test:pattern:1", "value1", ex=60)
        await client.set("test:pattern:2", "value2", ex=60)
        
        keys = await client.keys("test:pattern:*")
        print(f"   ✅ Pattern test: Found {len(keys)} keys")
        
        # Cleanup
        await client.delete("test:user:123", counter_key)
        if keys:
            await client.delete(*keys)
        
        print("   ✅ Cache operations test passed!\n")
        
    except Exception as e:
        print(f"   ❌ Cache operations failed: {e}")
        return False
    finally:
        await client.close()
        await pool.disconnect()
    
    return True

def print_connection_guide():
    """Print connection guide for different scenarios"""
    
    print("📋 Redis Connection Guide\n")
    
    print("🐳 Docker Compose (Recommended):")
    print("   docker-compose up redis")
    print("   URL: redis://:redis_password@localhost:26379/0\n")
    
    print("🔧 Local Redis (No Auth):")
    print("   redis-server")
    print("   URL: redis://localhost:6379/0\n")
    
    print("🔐 Local Redis (With Auth):")
    print("   redis-server --requirepass redis_password")
    print("   URL: redis://:redis_password@localhost:6379/0\n")
    
    print("🌐 Production:")
    print("   Set REDIS_URL environment variable")
    print("   Example: redis://:password@redis-host:6379/0\n")
    
    print("🔧 Configuration:")
    print("   1. Copy .env.example to .env")
    print("   2. Modify Redis settings as needed")
    print("   3. Set ENVIRONMENT variable (development/production/testing/local)\n")

async def main():
    """Main test function"""
    print("🚀 Redis Configuration Test\n")
    
    # Basic connection test
    connection_ok = await test_redis_connection()
    
    if connection_ok:
        # Advanced operations test
        await test_cache_operations()
    else:
        print_connection_guide()
        return
    
    print("🎉 All Redis tests passed! Your configuration is working correctly.")

if __name__ == "__main__":
    asyncio.run(main())
