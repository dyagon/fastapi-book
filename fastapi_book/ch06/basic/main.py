from typing_extensions import Annotated
from fastapi import FastAPI, Depends, Query
from fastapi.exceptions import HTTPException

import threading

app = FastAPI(
    dependencies=[],
)

def username_check(username: str = Query(..., min_length=3, max_length=12, regex="^[a-zA-Z0-9]+$")):
    if username != "alice":
        raise HTTPException(status_code=400, detail="Invalid username")
    print("Username validated in thread:", threading.current_thread().name, threading.current_thread().ident)
    return username

async def async_username_check(username: str = Query(..., min_length=3, max_length=12, regex="^[a-zA-Z0-9]+$")):
    if username != "alice":
        raise HTTPException(status_code=400, detail="Invalid username")
    print("Username validated in thread:", threading.current_thread().name, threading.current_thread().ident)
    return username

@app.get("/user/info")
def user_info(username: Annotated[str, Depends(async_username_check)]):
    return {"username": username, "info": "This is some user info."}

@app.get("/user/info_sync")
def user_login(username: str = Depends(username_check)):
    print("Login attempt for user:", username)
    return {"message": f"Welcome, {username}!"}
