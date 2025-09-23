# from contextlib import asynccontextmanager
# from pathlib import Path
# from pydantic import BaseModel

# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi_book import load_yaml_config


# from ..infra.resource import (
#     DatabaseConfig,
#     RedisConfig,
#     Database,
#     get_redis_client,
#     get_async_client,
# )

# from ..impl.auth import (
#     ClientCredentialsClient,
#     ClientCredentialsClientConfig,
#     AuthorizationCodeClient,
# )
# from ..impl.session_manager import SessionManager
# from ..impl.repo.user import UserRepo
# from ..domain.services.user_service import UserService
# from ..domain.services.auth_login import OAuthLoginService, OAuthLoginServiceConfig
# from .app_infra import AppInfra, InfraSettings


# class OAuth2ServiceConfig(BaseModel):
#     client_credentials: ClientCredentialsClientConfig
#     authorization_code: OAuthLoginServiceConfig


# class AppSettings(InfraSettings):
#     db: DatabaseConfig
#     redis: RedisConfig
#     oauth2: OAuth2ServiceConfig
#     # auth_code: AuthorizationCodeClientConfig


# yaml_config_file = Path(__file__).parent.parent / "config.yaml"

# app_settings = AppSettings(**load_yaml_config(yaml_config_file))

# infra = AppInfra(app_settings)

# cc_client = ClientCredentialsClient(
#     infra.async_client, app_settings.oauth2.client_credentials
# )

# ac_client = AuthorizationCodeClient(
#     infra.async_client, app_settings.oauth2.authorization_code
# )

# # session_manager = SessionManager(infra.redis.get_redis())


# async def get_db_session() -> AsyncSession:
#     async with infra.get_db_session() as session:
#         yield session


# async def get_user_login_service(
#     db: AsyncSession = Depends(get_db_session),
# ):
#     user_service = UserService(UserRepo(db))
#     yield OAuthLoginService(
#         cfg=app_settings.oauth2.authorization_code,
#         client=ac_client,
#         session_manager=session_manager,
#         user_service=user_service,
#     )
