"""
Redis configuration for different environments
"""
import os
from typing import Optional

class RedisConfig:
    """Redis configuration class"""
    
    def __init__(self):
        # Default values for development
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "26379"))
        self.password = os.getenv("REDIS_PASSWORD", "redis_password")
        self.database = int(os.getenv("REDIS_DB", "0"))
        self.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
        
    def get_redis_url(self) -> str:
        """
        Generate Redis URL based on configuration
        
        Returns:
            Redis URL in format: redis://[username:]password@host:port/database
        """
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"redis://{self.host}:{self.port}/{self.database}"
    
    def get_connection_kwargs(self) -> dict:
        """
        Get additional connection parameters
        """
        return {
            "decode_responses": True,
            "max_connections": self.max_connections,
            "retry_on_timeout": True,
            "retry_on_error": [ConnectionError, TimeoutError],
            "health_check_interval": 30,
        }

# Global configuration instance
redis_config = RedisConfig()

# Different environment configurations
class RedisEnvironments:
    """Predefined Redis configurations for different environments"""
    
    @staticmethod
    def development() -> str:
        """Development environment (Docker Compose)"""
        return "redis://:redis_password@localhost:26379/0"
    
    @staticmethod
    def production() -> str:
        """Production environment (replace with your production Redis URL)"""
        return os.getenv("REDIS_URL", "redis://:your_prod_password@your-redis-host:6379/0")
    
    @staticmethod
    def testing() -> str:
        """Testing environment (usually without password or separate DB)"""
        return "redis://localhost:6379/1"
    
    @staticmethod
    def local_no_auth() -> str:
        """Local Redis without authentication"""
        return "redis://localhost:6379/0"

def get_redis_url_for_environment(env: str = None) -> str:
    """
    Get Redis URL based on environment
    
    Args:
        env: Environment name ('development', 'production', 'testing', 'local')
    
    Returns:
        Redis URL string
    """
    env = env or os.getenv("ENVIRONMENT", "development")
    
    if env == "development":
        return RedisEnvironments.development()
    elif env == "production":
        return RedisEnvironments.production()
    elif env == "testing":
        return RedisEnvironments.testing()
    elif env == "local":
        return RedisEnvironments.local_no_auth()
    else:
        # Fallback to config-based URL
        return redis_config.get_redis_url()

# Example usage:
if __name__ == "__main__":
    print("Redis URL Examples:")
    print(f"Development: {RedisEnvironments.development()}")
    print(f"Production: {RedisEnvironments.production()}")
    print(f"Testing: {RedisEnvironments.testing()}")
    print(f"Local (no auth): {RedisEnvironments.local_no_auth()}")
    print(f"Config-based: {redis_config.get_redis_url()}")
