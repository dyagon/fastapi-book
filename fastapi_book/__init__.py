
import asyncio
import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

from dotenv import load_dotenv


from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


def load_yaml_config(config_file, env_file=".env") -> dict[str, Any]:
    # load env first
    load_dotenv(env_file)

    # load config.yaml
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found")
    config_path = Path(config_file)
    raw_content = config_path.read_text()

    # --- 3. 手动处理环境变量占位符 ---
    # 正则表达式查找 ${VAR} 或 ${VAR:default}
    placeholder_pattern = re.compile(r'\$\{([^}]+)\}')

    def replace_placeholder(match):
        # 分割变量名和默认值
        parts = match.group(1).split(':', 1)
        var_name = parts[0]
        
        # 使用 os.environ.get(VAR, DEFAULT) 来安全地获取环境变量
        default_value = parts[1] if len(parts) > 1 else None
        return os.environ.get(var_name, default_value)

    expanded_content = placeholder_pattern.sub(replace_placeholder, raw_content)

    # --- 4. 解析替换后的 YAML 并用 Pydantic 进行验证和映射 ---
    config_dict = yaml.safe_load(expanded_content)
    if not config_dict:
        raise ValueError("Configuration file is empty or invalid after processing.")

    return config_dict

class BaseInfra:
    async def setup(self):
        pass

    async def shutdown(self):
        pass


# 用于类型提示，使 get() 方法返回具体的类型
T = TypeVar("T", bound=BaseInfra)

class InfraRegistry:
    def __init__(self):
        # 这就是你提到的 "infra 字典"
        self._registry: Dict[str, BaseInfra] = {}

    def register(self, name: str, instance: BaseInfra):
        if name in self._registry:
            raise ValueError(f"Infrastructure component named '{name}' is already registered.")
        print(f"Registering infrastructure component: '{name}'")
        self._registry[name] = instance

    def get(self, name: str, *, of_type: Type[T]) -> T:
        instance = self._registry.get(name)
        if not instance:
            raise KeyError(f"No infrastructure component named '{name}' is registered.")
        if not isinstance(instance, of_type):
            raise TypeError(f"Component '{name}' is not of type {of_type.__name__}")
        return instance

    async def setup_all(self):
        print("--- Setting up all registered infrastructure... ---")
        # 使用 asyncio.gather 来并发执行所有 setup()，效率更高
        tasks = [infra.setup() for infra in self._registry.values()]
        await asyncio.gather(*tasks)
        print("--- All infrastructure setup complete. ---")

    async def shutdown_all(self):
        """
        【遍历处理】并发地关闭所有已注册的设施。
        """
        print("--- Shutting down all registered infrastructure... ---")
        tasks = [infra.shutdown() for infra in self._registry.values()]
        await asyncio.gather(*tasks)
        print("--- All infrastructure shutdown complete. ---")


__all__ = ["load_yaml_config", "BaseInfra", "InfraRegistry", "Base"]