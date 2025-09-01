from fastapi import Depends, FastAPI

from fastapi_book.utils import register_custom_docs

from .security import HTTPDigest


app = FastAPI(
    title="HTTPBasic Auth Example",
    docs_url=None,
    redoc_url=None,
    version="0.1.0"
)

# 实例化我们的 Digest 认证方案
digest_auth = HTTPDigest(realm="My FastAPI Protected Realm")

@app.get("/")
def read_root():
    return {"message": "This is a public endpoint."}

@app.get("/login")
async def login(username: str = Depends(digest_auth)):
    # 如果认证成功，`username` 将会被注入到这里
    # 如果失败，`HTTPDigest` 类会抛出 HTTPException，代码不会执行到这里
    return {"message": f"Welcome, {username}! You are accessing secret data."}

register_custom_docs(app)