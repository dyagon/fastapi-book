import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from dependency_injector import containers, providers, resources
from fastapi import FastAPI

from httpx import AsyncClient

# --- 1. 模拟业务对象和数据库 ---


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from redis.asyncio import Redis, from_url

DB_URI = "postgresql+asyncpg://admin:admin123@localhost:25432/fastapi_book"

REDIS_URI = "redis://:redis_password@localhost:26379/0"


async def init_redis_pool() -> AsyncGenerator[Redis, None]:
    print("Initializing Redis pool...")
    session = from_url(REDIS_URI, encoding="utf-8", decode_responses=True)
    yield session
    session.close()
    print("Redis pool closed")
    await session.wait_closed()


class RedisService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def process(self) -> str:
        await self._redis.set("my-key", "value")
        return await self._redis.get("my-key")


class Database:

    def __init__(self):
        """初始化数据库引擎和 session 工厂。"""
        print("Initializing Database...")
        self._db_engine = create_async_engine(DB_URI, echo=True)
        self._db_sessionmaker = async_sessionmaker(
            self._db_engine, expire_on_commit=False
        )
        print("Database engine and session factory created.")

    # async def __aenter__(self):
    #     return self

    async def shutdown(self):
        """关闭数据库引擎。"""
        if self._db_engine:
            print("Closing Database engine...")
            await self._db_engine.dispose()
            print("Database engine closed.")

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._db_sessionmaker

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        print("get_session")
        try:
            session: AsyncSession = self._db_sessionmaker()
            print(f"session: {id(session)}")
            yield session
        finally:
            print("close session, ", id(session))
            await session.close()


class AysncDatabase(resources.AsyncResource):

    async def init(self):
        """初始化数据库引擎和 session 工厂。"""
        print("Initializing Database...")
        self._db_engine = create_async_engine(DB_URI, echo=True)
        self._db_sessionmaker = async_sessionmaker(
            self._db_engine, expire_on_commit=False
        )
        print("Database engine and session factory created.")
        return self

    async def shutdown(self, db):
        """关闭数据库引擎。"""
        if self._db_engine:
            print("Closing Database engine...")
            await self._db_engine.dispose()
            print("Database engine closed.")

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._db_sessionmaker

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        print("get_session")
        try:
            session: AsyncSession = self._db_sessionmaker()
            print(f"session: {id(session)}")
            yield session
        finally:
            print("close session, ", id(session))
            await session.close()


@asynccontextmanager
async def init_database():
    """初始化数据库引擎和 session 工厂。"""
    db = Database()
    yield db
    await db.shutdown()
    print("Closing Database...")


class UserRepo:
    """数据仓库，依赖于 SQLAlchemy 的 AsyncSession"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_by_id(self, user_id: int):
        await asyncio.sleep(0.1)
        return {"user_id": user_id}


class UserService:
    """业务服务，依赖于数据仓库"""

    def __init__(self, repo: UserRepo):
        self._repo = repo

    async def get_user(self, user_id: int):
        print("Service: Processing get_user logic")
        return await self._repo.get_user_by_id(user_id)


@asynccontextmanager
async def get_db_session(db_session_factory: async_sessionmaker[AsyncSession]):
    print("get_session")
    try:
        session: AsyncSession = db_session_factory()
        print(f"session: {id(session)}")
        yield session
    finally:
        print("close session, ", id(session))
        await session.close()


@asynccontextmanager
async def get_user_service(db: Database):
    async with db.get_session() as session:
        user_repo = UserRepo(session)
        user_service = UserService(user_repo)
        print("new user_service, ", id(user_service))
        yield user_service
        print("close user_service, ", id(user_service))


# --- 2. 定义依赖注入容器 ---


async def init_http_client():
    return AsyncClient()


class AppContainer(containers.DeclarativeContainer):

    # db = providers.Resource(Database)
    # db = providers.Resource(init_database)
    db = providers.Resource(AysncDatabase)

    client = providers.Resource(init_http_client)

    user_service = providers.Factory(get_user_service, db=db)

    redis_pool = providers.Resource(init_redis_pool)

    service = providers.Factory(
        RedisService,
        redis=redis_pool,
    )


async def lifespan(app: FastAPI):
    app_container = AppContainer()
    # app_container.db.init()
    print("🚀 App startup")
    app.state.app_container = app_container
    yield
    # app_container.db.shutdown()
    print("👋 App shutdown")


# --- 3. 在 FastAPI 中手动注入和使用 ---

app = FastAPI(lifespan=lifespan)
container = AppContainer()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """
    在这个路由中，我们手动控制依赖的生命周期。
    """
    print("\n--- Request Started ---")

    # 步骤 3: 使用 async with 管理 Resource 的生命周期
    # 这会触发 db_session 的创建
    async with await AppContainer.user_service() as user_service:
        # 使用服务
        user_data = await user_service.get_user(user_id)

    # 当 `async with` 块结束时, db_session.close() 会被自动调用

    print("--- Request Finished ---")
    return user_data


@app.get("/redis")
async def get_redis():
    redis_service = await AppContainer.service()
    return await redis_service.process()