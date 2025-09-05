from fastapi import FastAPI, HTTPException, Request

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .exception import BusinessError, ExceptionEnum


app = FastAPI(
    title="FastAPI Book Chapter 4",
    description="Chapter 4 Example for FastAPI Book",
    docs_url=None,
    redoc_url=None,
    version="0.1.0",
)


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "The resource you are looking for is not found."},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! {exc.detail}"},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        {"code": 422, "message": "Validation Error", "errors": exc.errors()}
    )


@app.exception_handler(BusinessError)
async def business_exception_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        content={
            "return_code": "FAIL",
            "return_msg": "参数错误",
            "err_code": exc.err_code,
            "err_code_des": exc.err_code_des,
        }
    )



@app.get("/http-exception", tags=["default"])
async def http_exception(item_id: str):
    if item_id != "foo":
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item_id": item_id, "name": "The Foo Wrestlers"}


# test request validation error
@app.get("/user/{user_id}", tags=["default"])
async def read_user(user_id: int):
    return {"user_id": user_id, "name": "John Doe"}

# test business exception
@app.get("/business-exception", tags=["default"])
async def business_exception():
    raise BusinessError(ExceptionEnum.USER_NO_DATA)


# test middleware exception
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if "error" in request.query_params:
        raise BusinessError(ExceptionEnum.FAILED, err_code_des="自定义错误描述")
    response = await call_next(request)
    return response

@app.get("/hello", tags=["default"])
async def hello():
    return {"message": "Hello, FastAPI Book Chapter 4!"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )