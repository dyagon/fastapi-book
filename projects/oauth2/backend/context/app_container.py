from contextlib import asynccontextmanager
from pathlib import Path
from pydantic import BaseModel

from dependency_injector import containers, providers

from fastapi_book import load_yaml_config
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

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
from .app_infra import AppInfra, InfraSettings


class OAuth2ServiceConfig(BaseModel):
    client_credentials: ClientCredentialsClientConfig
    authorization_code: OAuthLoginServiceConfig


class AppSettings(InfraSettings):
    db: DatabaseConfig
    redis: RedisConfig
    oauth2: OAuth2ServiceConfig
    # auth_code: AuthorizationCodeClientConfig


yaml_config_file = Path(__file__).parent.parent / "config.yaml"

app_settings = AppSettings(**load_yaml_config(yaml_config_file))

infra = AppInfra(app_settings)


@asynccontextmanager
async def get_user_login_service(
    db_session_factory: async_sessionmaker[AsyncSession],
    ac_client: AuthorizationCodeClient,
    session_manager: SessionManager,
):
    async with db_session_factory() as session:
        user_repo = UserRepo(session)
        user_service = UserService(user_repo)
        yield OAuthLoginService(
            cfg=app_settings.oauth2.authorization_code,
            client=ac_client,
            session_manager=session_manager,
            user_service=user_service,
        )


class Container(containers.DeclarativeContainer):

    async_client = providers.Singleton(infra.get_async_client)

    redis_client = providers.Singleton(infra.get_redis)

    db_session_factory = providers.Singleton(infra.get_db_session_factory)

    # oauth2 client credentials flow client
    cc_client = providers.Singleton(
        ClientCredentialsClient,
        client=async_client,
        cfg=app_settings.oauth2.client_credentials,
    )

    # oauth2 authorization code flow client
    ac_client = providers.Singleton(
        AuthorizationCodeClient,
        client=async_client,
        cfg=app_settings.oauth2.authorization_code,
    )

    session_manager = providers.Singleton(
        SessionManager,
        redis_client=redis_client,
    )

    auth_login_service = providers.Factory(
        get_user_login_service,
        db_session_factory=db_session_factory,
        ac_client=ac_client,
        session_manager=session_manager,
    )
