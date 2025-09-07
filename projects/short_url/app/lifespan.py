
from contextlib import asynccontextmanager
from fastapi import FastAPI

from ..infra import async_engine, Base, SessionLocal
from ..infra.utils import PasslibHelper
from ..domain.service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 App startup")

    async def init_create_table():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def create_admin_user():
        async with SessionLocal() as db:
            await UserService(db).create_user(
                username="admin",
                password=PasslibHelper.hash_password("123456")
            )

    await init_create_table()
    await create_admin_user()

    yield
    print("👋 App shutdown")
