
import time
import http
import uuid
import contextvars

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


request_context = contextvars.ContextVar("request_context", default=None)

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request_context.set(request)
        request.state.trace_id = str(uuid.uuid4())
        try:
            response = await call_next(request)
            response.headers["X-Trace-ID"] = request.state.trace_id
            return response
        finally:
            request_context.reset(token)
    
def log_info(message: str):
    request = request_context.get()
    trace_id = getattr(request.state, "trace_id", "no-trace-id") if request else "no-request"
    print(f"[TraceID: {trace_id}] {message}")


class TimeCalculateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(">>> TimeCalculateMiddleware: before call_next")
        start_time = time.monotonic()
        response = await call_next(request)
        process_time = time.monotonic() - start_time
        response.headers["X-Process-Time2"] = str(int(process_time * 1000)) + "ms"
        print("<<< TimeCalculateMiddleware: after call_next")
        return response
    
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_value='SecretToken'):
        super().__init__(app)
        self.header_value = header_value

    async def dispatch(self, request: Request, call_next):
        print(">>> AuthMiddleware: before call_next")
        # 在这里可以添加认证逻辑
        response = await call_next(request)
        response.headers["X-Auth-Checked"] = self.header_value
        print("<<< AuthMiddleware: after call_next")
        return response
    


class WhiteListMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, whitelist=None):
        super().__init__(app)
        self.whitelist = whitelist or []

    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host
        print(f"Client host: {client_host}")
        if client_host not in self.whitelist:
            from starlette.responses import JSONResponse
            return JSONResponse({"detail": "Forbidden"}, status_code=403)
        return await call_next(request)
    

class LogMiddleware:
    async def __call__(self, request: Request, call_next: RequestResponseEndpoint, *args, **kwargs):
        try:
            response = await call_next(request)
        except Exception as e:
            response_body = bytes(http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase.encode())
            response = http.Response(
                content=response_body,
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR.real,
            )
        else:
            response_body = b''
            async for chunk in response.body_iterator:
                response_body += chunk
            print(f"Response body: {response_body.decode()}")
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        return response