from contextlib import asynccontextmanager
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from dependency_injector.ext.starlette import Lifespan
from fastapi import FastAPI, Request, Depends, APIRouter


class Connection: ...


@asynccontextmanager
async def init_database():
    print("opening database connection")
    yield Connection()
    print("closing database connection")


router = APIRouter()


@router.get("/")
@inject
async def index(request: Request, db: Connection = Depends(Provide["db"])):
    # use the database connection here
    return "OK!"


class Container(containers.DeclarativeContainer):
    __self__ = providers.Self()
    db = providers.Resource(init_database)
    lifespan = providers.Singleton(Lifespan, __self__)
    app = providers.Singleton(FastAPI, lifespan=lifespan)
    _include_router = providers.Resource(
        app.provided.include_router.call(),
        router,
    )


# uv run python -m fastapi_book.ch06.di.app
if __name__ == "__main__":
    import uvicorn

    container = Container()
    app = container.app()
    uvicorn.run(app, host="localhost", port=8004)
