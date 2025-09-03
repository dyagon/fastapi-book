from contextlib import asynccontextmanager
from fastapi import FastAPI


from .db import SessionLocal

from .service import UserService
from .utils import PasslibHelper

from .routes.user import router_user
from .routes.short import router_short
from ..utils import register_custom_docs


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 App startup")
    from .db import async_engine, Base
    from .models import User, ShortUrl

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


app = FastAPI(
    title="Chapter 10 - Short Url",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

register_custom_docs(app)

app.include_router(router_user)
app.include_router(router_short)
