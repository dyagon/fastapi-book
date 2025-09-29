# from contextlib import asynccontextmanager
# from pathlib import Path
# from typing import AsyncGenerator, Callable
# from pydantic import BaseModel

# from httpx import AsyncClient
# from fastapi_book import InfraRegistry
# from fastapi_book.infra import DatabaseConfig, RedisConfig, DatabaseInfra, RedisInfra

# from redis.asyncio import Redis
# from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


# class InfraSettings(BaseModel):
#     db: DatabaseConfig
#     redis: RedisConfig


# class AppInfra(InfraRegistry):

#     def __init__(self, settings: InfraSettings):
#         super().__init__()
#         self.cfg = settings

#         self.db = DatabaseInfra(self.cfg.db)
#         self.redis = RedisInfra(self.cfg.redis)
#         self.async_client: AsyncClient | None = None

#         self.register("db", self.db)
#         self.register("redis", self.redis)

#     def get_redis(self) -> Redis:
#         return self.redis.get_redis()

#     def get_async_client(self) -> AsyncClient:
#         return self.async_client

#     def get_db_session_factory(self) -> async_sessionmaker[AsyncSession]:
#         return self.db.db_sessionmaker
    
#     @asynccontextmanager
#     async def get_db_session(self) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
#         try:
#             session: AsyncSession = self.db.db_sessionmaker()
#             print(f"    -> (Factory) New ASYNC session created: {id(session)}")
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()
#             print(f"    <- (Factory) ASYNC Session closed: {id(session)}")


#     async def setup(self):
#         await self.setup_all()
#         self.async_client = AsyncClient()

#         # client credentials
#         # self.cc_client = OAuth2ClientCredentialsClient(
#         #     self.async_client, self.cfg.cc_service
#         # )
#         # self.cc_auth = OAuth2ClientCredentialsAuth(self.cc_client)
#         # self.auth_client = AuthClient(self.async_client, self.cc_auth)
#         # self.auth_service = OAuth2ClientCredentialsService(
#         #     self.cfg.cc_service.base_url, self.auth_client
#         # )

#     async def shutdown(self):
#         await self.shutdown_all()
#         if self.async_client:
#             await self.async_client.aclose()


# # config_file = Path(__file__).parent.parent / "config.yaml"

# # infra = AppInfra(config_file)
