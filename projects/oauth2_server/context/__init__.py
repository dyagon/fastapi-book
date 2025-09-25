from pathlib import Path
from pydantic import BaseModel

from fastapi_book import load_yaml_config

from fastapi_book import InfraRegistry, load_yaml_config
from fastapi_book.infra import DatabaseConfig, RedisConfig, DatabaseInfra, RedisInfra


class AppSettings(BaseModel):
    redis: RedisConfig


class AppInfra(InfraRegistry):

    def __init__(self, config_file: str):
        super().__init__()
        config_dict = load_yaml_config(config_file)
        cfg = AppSettings(**config_dict)
        self.register("redis", RedisInfra(cfg.redis))

    # @property
    # def db(self) -> DatabaseInfra:
    #     return self.get("db", of_type=DatabaseInfra)

    @property
    def redis(self) -> RedisInfra:
        return self.get("redis", of_type=RedisInfra)



config_file = Path(__file__).parent.parent / "config.yaml"

infra = AppInfra(config_file)
