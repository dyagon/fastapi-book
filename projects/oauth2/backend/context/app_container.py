from pathlib import Path
from pydantic import BaseModel

from dependency_injector import containers, providers

from fastapi_book import load_yaml_config

from ..infra.resource import (
    DatabaseConfig,
    RedisConfig,
    Database,
    get_redis_client,
    get_async_client,
)

from ..impl.auth import (
    ClientCredentialsClient,
    ClientCredentialsClientConfig,
    AuthorizationCodeClient,
)

from ..impl.session_manager import SessionManager

from ..impl.repo.user import UserRepo


from ..domain.services.user_service import UserService
from ..domain.services.auth_login import OAuthLoginService, OAuthLoginServiceConfig


class OAuth2ServiceConfig(BaseModel):
    client_credentials: ClientCredentialsClientConfig
    authorization_code: OAuthLoginServiceConfig


class AppSettings(BaseModel):
    db: DatabaseConfig
    redis: RedisConfig
    oauth2: OAuth2ServiceConfig
    # auth_code: AuthorizationCodeClientConfig


yaml_config_file = Path(__file__).parent.parent / "config.yaml"

app_settings = AppSettings(**load_yaml_config(yaml_config_file))


class Container(containers.DeclarativeContainer):

    db = providers.Resource(Database, db_cfg=app_settings.db)
    redis = providers.Resource(get_redis_client, cfg=app_settings.redis)
    async_client = providers.Resource(get_async_client)

    db_session = providers.Factory(db.provided.get_session)

    # oauth2 client credentials flow client
    cc_client = providers.Singleton(
        ClientCredentialsClient,
        client=async_client,
        cfg=app_settings.oauth2.client_credentials,
    )

    ac_client = providers.Singleton(
        AuthorizationCodeClient,
        client=async_client,
        cfg=app_settings.oauth2.authorization_code,
    )

    session_manager = providers.Singleton(
        SessionManager,
        redis_client=redis.provided,
    )

    user_service = providers.Factory(
        UserService,
        user_repo=providers.Factory(UserRepo, db=db_session.provided),
    )

    auth_login_service = providers.Factory(
        OAuthLoginService,
        cfg=app_settings.oauth2.authorization_code,
        client=ac_client.provided,
        session_manager=session_manager.provided,
        user_service=user_service.provided,
    )
