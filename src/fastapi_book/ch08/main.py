
from fastapi import FastAPI

from .user_route import route as user_route

from ..context import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(user_route)


