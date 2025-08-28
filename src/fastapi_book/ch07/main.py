import asyncio
import time
from fastapi import FastAPI, Request

from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .custom.middleware import (
    TimeCalculateMiddleware,
    AuthMiddleware,
    TraceIDMiddleware,
    WhiteListMiddleware,
    LogMiddleware,
)   

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    await asyncio.sleep(0.1)
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(int(process_time * 1000)) + "ms"
    return response


@app.middleware("http")
async def log_1p(request: Request, call_next):
    print(f"--> log_1p: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"<-- log_1p: {request.method} {request.url.path}")
    return response


@app.middleware("http")
async def log_2p(request: Request, call_next):
    print(f"--> log_2p: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"<-- log_2p: {request.method} {request.url.path}")
    return response


app.add_middleware(TimeCalculateMiddleware)
app.add_middleware(AuthMiddleware, "123456")
app.add_middleware(TraceIDMiddleware)
app.add_middleware(WhiteListMiddleware, ["127.0.0.1", "localhost"])

app.middleware('http')(LogMiddleware())


@app.get("/test")
async def test():
    return {"message": "This is a test endpoint."}
