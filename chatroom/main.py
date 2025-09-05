from fastapi import FastAPI

from .app.routers.user import router as user_router
from .app.routers.room import router_chat

app = FastAPI(title="Chat Room Application")


app.include_router(user_router)
app.include_router(router_chat)
