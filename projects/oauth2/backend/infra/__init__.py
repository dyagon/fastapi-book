
from pathlib import Path
from pydantic import BaseModel


from fastapi_book import load_yaml_config

from fastapi_book import InfraRegistry, BaseInfra, load_yaml_config
from fastapi_book.infra import DatabaseConfig, RedisConfig, DatabaseInfra, RedisInfra

from .auth_client import OAuthClient, OAuthClientConfig


class AppSettings(BaseModel):
    db: DatabaseConfig
    redis: RedisConfig
    oauth: OAuthClientConfig


class AppInfra(InfraRegistry):

    def __init__(self, config_file: str):
        super().__init__()
        config_dict = load_yaml_config(config_file)
        cfg = AppSettings(**config_dict)
        self.register("db", DatabaseInfra(cfg.db))
        self.register("redis", RedisInfra(cfg.redis))
        self.register("oauth_client", OAuthClient(cfg.oauth))

    @property
    def db(self) -> DatabaseInfra:
        return self.get("db", of_type=DatabaseInfra)
    
    @property
    def redis(self) -> RedisInfra:
        return self.get("redis", of_type=RedisInfra)
    
    @property
    def oauth_client(self) -> OAuthClient:
        return self.get("oauth_client", of_type=OAuthClient)


config_file = Path(__file__).parent.parent / "config.yaml"

infra = AppInfra(config_file)
