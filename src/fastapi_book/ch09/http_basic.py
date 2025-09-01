from fastapi import Depends, FastAPI, HTTPException

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from fastapi_book.utils import register_custom_docs

app = FastAPI(
    title="HTTPBasic Auth Example",
    docs_url=None,
    redoc_url=None,
    version="0.1.0"
)

security = HTTPBasic()

@app.get("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    correct_password = "secret"
    if credentials.username == correct_username and credentials.password == correct_password:
        return {"message": f"Welcome, {credentials.username}!"}
    raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Basic"})

register_custom_docs(app)