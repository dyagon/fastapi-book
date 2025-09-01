# Fastapi Book

## setup

```bash
uv venv
uv sync
```

## Chapter 1, GIL, io, sync and async

- Python GIL: what it effects
- async and await keywords
- io libs: asyncio, trio, anyio

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
uv run uvicorn fastapi_book.main:app --reload
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

- BaseModel
- validators


```bash
uv run uvicorn fastapi_book.ch05.main:app --reload 
```


test
```
curl -X POST "http://127.0.0.1:8000/users/" \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "age": 30,
    "password_old": "oldpassword1",
    "password_new": "newpassword2"
}'
```

## Chapter 6 Dependencies

- python dependency injection
- FastAPI dependencies, how to use Depends
    - global dependencies
    - route dependencies
    - function dependencies
- use async def dependencies all the way, in the main thread, no thread switch

serve: `uv run uvicorn fastapi_book.ch06.main:app --reload`

test: 

```bash
curl http://localhost:8000/me
# return 422 because no X-Token header

curl "http://localhost:8000/me" -H "X-Token: fake" 
# return 401 Unauthorized

curl "http://localhost:8000/me" -H "X-Token:valid-user-token"
# return {"username":"johndoe"}

```
see how global dependency works:
```bash
curl http://localhost:8000/users/1
# return {"user_id":1,"db_connection":{"connection":"db_connection_object"}}
``` 

## Chapter 7 Middleware

run: `uv run uvicorn fastapi_book.ch07.main:app --reload`

test:
```bash
curl -X GET -i http://localhost:8000/test
# return {"message": "This is a test endpoint."} with X-Process-Time header
```


## Chapter 8 Database with SQLAlchemy and Alembic

- Sync and Async engines/sessions
- Declarative base and models
- Alembic for init and migration
- sqlacodegen, generate models from existing db
- redis usage
    - as cache
    - as distributed lock
    - as message broker ( pub/sub )


Alembic init
```bash
uv run alembic init alembic

# create tables based on Base metadata
uv run alembic revision --autogenerate -m "Initial migration" 
uv run alembic upgrade head
```

run:
```bash
uv run uvicorn fastapi_book.ch08.main:app --reload
```

test:
```bash
curl -X POST "http://localhost:8000/user" -H "Content-Type: application/json" -d '{"username": "testuser", "email": "zhagnsan@example.com", "password": "securepassword"}'
# return created user with id

curl -X GET "http://localhost:8000/user/1"
# return user with id 1
```

create models from existing db:
```bash
uv run sqlacodegen postgresql+asyncpg://user:password@localhost/fast
```

test redis cache:
```bash
curl -X GET "http://localhost:8000/user/1"
```

test redis pub/sub:
```bash
uv run python -m fastapi_book.ch08.redis.pubsub
```

test redis distributed lock and wallet debit:
```bash
curl -X POST "http://127.0.0.1:8000/wallets/user_123/pay?amount=10"
# return {"user_id":"user_123","new_balance":90}

curl -X POST "http://127.0.0.1:8000/wallets/user_123/pay?amount=10"
# blocked
```