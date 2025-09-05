
from fastapi import APIRouter, Depends, HTTPException, Header


# 依赖 1: 从 token 中解析用户，这是真正干活的
async def get_current_user_from_token(token: str = Header(..., alias="X-Token")):
    # 假设这里会解码 token 并返回用户对象
    if token != "valid-user-token": return None
    return {"username": "alice", "roles": ["user"]}

# 依赖 2: “守卫”依赖，它依赖于上面的函数
async def verify_user_is_authenticated(
    user: dict = Depends(get_current_user_from_token)
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

# ---- 设置路由 ----
router = APIRouter(
    # 设置“守卫”依赖
    dependencies=[Depends(verify_user_is_authenticated)]
)

@router.get("/me")
async def read_users_me(
    # 路径函数如果需要用户信息，必须再次显式地请求它！
    current_user: dict = Depends(get_current_user_from_token)
):
    # 由于 FastAPI 的依赖缓存机制，get_current_user_from_token 在本次请求中
    # 只会执行一次。这里只是从缓存中读取结果。
    return current_user
