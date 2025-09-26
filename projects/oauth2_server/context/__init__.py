from pathlib import Path
from pydantic import BaseModel
from dependency_injector import containers, providers

from fastapi_book import load_yaml_config

from .app_infra import AppInfra, InfraSettings

from ..domain.services import (
    TokenService,
    ClientCredentialsFlowService,
    AuthorizationCodeFlowService,
    RefreshTokenFlowService,
)
from ..impl.repo import ClientRepo, UserRepo


class AppSettings(BaseModel):
    token_secret_key: str
    token_algorithm: str

class Settings(InfraSettings):
    app: AppSettings


config_file = Path(__file__).parent.parent / "config.yaml"
settings = Settings(**load_yaml_config(config_file))
infra = AppInfra(settings)


class AppContainer(containers.DeclarativeContainer):
    redis_client = providers.Singleton(infra.redis.get_redis)

    token_service = providers.Singleton(
        TokenService,
        redis_client=redis_client,
        secret_key=settings.app.token_secret_key,
        algorithm=settings.app.token_algorithm,
    )

    client_repo = providers.Singleton(ClientRepo)
    user_repo = providers.Singleton(UserRepo)

    client_credentials_flow_service = providers.Singleton(
        ClientCredentialsFlowService,
        client_repo=client_repo,
        token_service=token_service,
    )

    authorization_code_flow_service = providers.Singleton(
        AuthorizationCodeFlowService,
        client_repo=client_repo,
        user_repo=user_repo,
        token_service=token_service,
    )

    refresh_token_flow_service = providers.Singleton(
        RefreshTokenFlowService,
        client_repo=client_repo,
        token_service=token_service,
    )
