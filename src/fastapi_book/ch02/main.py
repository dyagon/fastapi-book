
import pathlib
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="FastAPI Book Chapter 2",
    description="Chapter 2 Example for FastAPI Book",
    docs_url=None,
    redoc_url=None,
    version="0.1.0")

templates = Jinja2Templates(directory=f"{pathlib.Path(__file__).parent}/templates")

# Add a root endpoint
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/hello", tags=["default"])
async def hello():
    return {"message": "Hello, FastAPI Book Chapter 2!"}
