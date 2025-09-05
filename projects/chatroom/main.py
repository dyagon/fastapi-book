import pathlib
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.responses import FileResponse

from .app.routers.user import router as user_router
from .app.routers.room import router_chat

app = FastAPI(title="Chat Room Application")

static_dir = pathlib.Path(__file__).parent / "app" / "static"
templates_dir = pathlib.Path(__file__).parent / "app" / "templates"

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/login")
async def login():
    return FileResponse(templates_dir / "login.html")

@app.get("/register")
async def register():
    return FileResponse(templates_dir / "register.html")

@app.get("/room/online")
def room_online():
    return FileResponse(templates_dir / "room.html")


app.include_router(user_router)
app.include_router(router_chat)