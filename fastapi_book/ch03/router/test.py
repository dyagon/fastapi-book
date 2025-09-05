import time
import threading
import asyncio

from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Header, Response, Request
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for testing
class TestData(BaseModel):
    message: str
    data: Dict[str, Any]
    timestamp: float


class BulkTestData(BaseModel):
    items: List[TestData]
    batch_id: str


@router.get("/sync")
def sync_hello():
    time.sleep(2)
    thread_info = f"Thread Name: {threading.current_thread().name}, {threading.current_thread().ident}"
    print(thread_info)
    return {"message": f"Hello from Sync! {thread_info}"}


@router.get("/async")
async def async_hello():
    await asyncio.sleep(2)
    thread_info = f"Thread Name: {threading.current_thread().name}, {threading.current_thread().ident}"
    print(thread_info)
    return {"message": f"Hello from Async! {thread_info}"}


@router.get("/demo/header")
async def demo_header(x_token: Optional[str] = Header(None, convert_underscores=True)):
    return {"message": "This is a demo header endpoint.", "x_token": x_token}

@router.get("/demo/header2")
async def demo_header2(x_token: list[str] = Header(None, convert_underscores=True)):
    return {"message": "This is a demo header endpoint.", "x_token": x_token}


@router.get("/demo/cookie")
async def demo_cookie(response: Response):
    response.set_cookie(key="fancy_cookie", value="cookie_value_123")
    return {"message": "Cookie has been set!"}


@router.get("/demo/request")
async def demo_request(request: Request):
    form_data = await request.form()
    body_data = await request.body()
    query_params = request.query_params
    headers = request.headers
    cookies = request.cookies
    return {
        "url": str(request.url),
        "base_url": str(request.base_url),
        "client_host": request.client.host if request.client else None,
        "headers": dict(headers),
        "cookies": dict(cookies),
        "query_params": dict(query_params),
        "form_data": dict(form_data),
        "body_data": body_data.decode('utf-8'),
        "json_data": await request.json() if body_data else None,
    }