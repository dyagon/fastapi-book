from contextlib import asynccontextmanager
from pathlib import Path
from pydantic import BaseModel

from dependency_injector import containers, providers

from fastapi_book import load_yaml_config


from ..impl.auth import (
    ClientCredentialsClient,
    ClientCredentialsClientConfig,
    AuthorizationCodeClient,
)
from ..impl.session_manager import SessionManager
from ..impl.repo.user import UserRepo
from ..domain.services.user_service import UserService
from ..domain.services.auth_login import OAuthLoginService, OAuthLoginServiceConfig
from ..domain.services.session_service import SessionService


class OAuth2ServiceConfig(BaseModel):
    client_credentials: ClientCredentialsClientConfig
    authorization_code: OAuthLoginServiceConfig


class AppConfig(BaseModel):
    secret_key: str


class AppSettings(BaseModel):
    app: AppConfig
    oauth2: OAuth2ServiceConfig
    # auth_code: AuthorizationCodeClientConfig


yaml_config_file = Path(__file__).parent.parent / "config.yaml"

app_settings = AppSettings(**load_yaml_config(yaml_config_file))


from ..infra import infra


# @asynccontextmanager
# async def get_user_service():
#     async with infra.get_db_session() as session:
#         user_repo = UserRepo(session)
#         yield UserService(user_repo)


# @asynccontextmanager
# async def get_user_login_service(
#     ac_client: AuthorizationCodeClient,
#     session_manager: SessionManager,
# ):
#     async with infra.get_db_session() as session:
#         user_repo = UserRepo(session)
#         user_service = UserService(user_repo)
#         yield OAuthLoginService(
#             cfg=app_settings.oauth2.authorization_code,
#             client=ac_client,
#             session_manager=session_manager,
#             user_service=user_service,
#         )


class Container(containers.DeclarativeContainer):

    async_client = providers.Singleton(infra.get_async_client)
    redis_client = providers.Singleton(infra.get_redis_client)

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

    user_repo = providers.Singleton(
        UserRepo,
    )

    user_service = providers.Singleton(
        UserService,
        user_repo=user_repo,
    )

    session_service = providers.Singleton(
        SessionService,
        session_manager=session_manager,
    )

    auth_login_service = providers.Singleton(
        OAuthLoginService,
        cfg=app_settings.oauth2.authorization_code,
        client=ac_client,
        session_service=session_service,
        user_service=user_service,
    )
