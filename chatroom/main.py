import pathlib
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from .app.routers.user import router as user_router
from .app.routers.room import router_chat

app = FastAPI(title="Chat Room Application")

static_dir = pathlib.Path(__file__).parent / "app" / "static"

app.mount("/static", StaticFiles(directory=static_dir), name="static")


app.include_router(user_router)
app.include_router(router_chat)
