from fastapi import FastAPI, Depends

import asyncio

from .resource import lifespan, get_db_connection
from .router import router

app = FastAPI(lifespan=lifespan)

app.include_router(router)

# 现在，路径函数可以像消费任何普通依赖一样来消费这个“桥梁”
@app.get("/users/{user_id}")
async def get_user(
    user_id: int, 
    # 这里显式地“请求”一个数据库连接
    conn: dict = Depends(get_db_connection)
):
    # conn 就是 get_db_connection yield 出来的那个连接对象
    # user_data = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    await asyncio.sleep(0.1)  # 模拟数据库查询延迟
    return {"user_id": user_id, "db_connection": conn}
