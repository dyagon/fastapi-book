# Fastapi Book

## setup

```bash
uv venv
uv sync
```

## Chapter 1, sync and async

```bash
uv run python -m fastapi_book.ch01.request_sync
```

```bash
uv run python -m fastapi_book.ch01.request_async
```

## Chapter 2, Basic FastAPI app

- Basic FastAPI app
- Jinjia tempalates
- uvicorn and asgi

```bash
uv run uvicorn fastapi_book.ch02.main:app --reload 
```

## Chapter 3, FastAPI features

- global routes
- global exceptions
- APIRouter & dynamic routes
- sync and async routes
- mount sub applications ( mount other WSGI/ASGI apps )
- swagger and redoc
- how to config / set evnironment variable
- api route parameters
    - path parameters
    - query parameters
    - body
    - form
    - headers
- files
    - File, upload files
    - aiofiles for async file operations on server side
- response
    - streamingResponse for large file download
    - fileResponse for file download
    - custom response class
- background tasks
- lifespan


```bash
uv run uvicorn fastapi_book.ch03.main:app --reload 
```
or
```bash
uv run python -m fastapi_book.main:app --reload
```
but lifespan will not work in the subapp mode, need to run the ch03 main.py directly


## Chapter 4, Exceptions

- HTTPException, with headers
- global exception handlers, seem like one handler for each type, code or exception
- validation error exception handler
- custom exception class
- middleware exception handler, exception..


```bash
uv run uvicorn fastapi_book.ch04.main:app --reload 
```

## Chapter 5 Pydantic




