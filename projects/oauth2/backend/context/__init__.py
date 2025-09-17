from pathlib import Path
from pydantic import BaseModel

import httpx

from fastapi_book import load_yaml_config

from fastapi_book import InfraRegistry, load_yaml_config
from fastapi_book.infra import DatabaseConfig, RedisConfig, DatabaseInfra, RedisInfra

from ..infra.web_client import WebClient
from ..impl.auth import (
    OAuth2ClientCredentialsConfig,
    OAuth2ClientCredentialsClient,
    OAuth2ClientCredentialsAuth,
    AuthClient,
)
from ..domain.services.auth_service import (
    OAuth2ClientCredentialsService,
    OAuth2ClientCredentialsServiceConfig,
)


class AppSettings(BaseModel):
    db: DatabaseConfig
    redis: RedisConfig
    cc_service: OAuth2ClientCredentialsServiceConfig
    # auth_code: AuthorizationCodeClientConfig


class AppInfra(InfraRegistry):

    def __init__(self, config_file: str):
        super().__init__()
        config_dict = load_yaml_config(config_file)
        self.cfg = AppSettings(**config_dict)

        self.db = DatabaseInfra(self.cfg.db)
        self.redis = RedisInfra(self.cfg.redis)
        self.webclient = WebClient()

        self.register("db", self.db)
        self.register("redis", self.redis)
        self.register("webclient", self.webclient)

    async def setup(self):
        await self.setup_all()
        self.async_client = self.webclient.client
        assert self.async_client is not None

        # client credentials
        self.cc_client = OAuth2ClientCredentialsClient(
            self.async_client, self.cfg.cc_service
        )
        self.cc_auth = OAuth2ClientCredentialsAuth(self.cc_client)
        self.auth_client = AuthClient(self.async_client, self.cc_auth)
        self.auth_service = OAuth2ClientCredentialsService(
            self.cfg.cc_service.base_url, self.auth_client
        )

    async def shutdown(self):
        await self.shutdown_all()


config_file = Path(__file__).parent.parent / "config.yaml"

infra = AppInfra(config_file)
