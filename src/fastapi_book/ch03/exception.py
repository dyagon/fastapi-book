from fastapi import FastAPI
from fastapi.responses import JSONResponse

def exception_not_found(request, exc):
    return JSONResponse({
        "code": exc.status_code,
        "message": "The resource you are looking for is not found."
    })

exception_handlers = {404: exception_not_found}


