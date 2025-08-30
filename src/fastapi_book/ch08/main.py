
from fastapi import FastAPI

from .user_route import route as user_route



app = FastAPI()

app.include_router(user_route)


