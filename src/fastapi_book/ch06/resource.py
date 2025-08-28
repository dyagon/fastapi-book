from fastapi import FastAPI, Depends, Request
import asyncio


# 全局资源本身是在这里创建和管理的
async def lifespan(app: FastAPI):
    print("🚀 App startup: Creating DB connection pool.")
    # 创建一个昂贵的、应全局共享的资源
    # pool = await asyncpg.create_pool(user='user', password='password', database='db')
    print("    -> Simulating DB connection pool creation...")
    await asyncio.sleep(1)  # 模拟创建连接池的延迟
    pool = {"user": "user", "password": "password", "database": "db"}  # 模拟连接池

    # 将它存储在 app.state 中
    app.state.db_pool = pool
    yield
    print("👋 App shutdown: Closing DB connection pool.")
    await asyncio.sleep(1)  # 模拟关闭连接池的延迟
    # await pool.close()
    print("    -> DB connection pool closed.")


async def get_db_connection(request: Request):
    # 1. 通过 request 对象访问 app，再访问 app.state
    pool = request.app.state.db_pool
    
    # 2. 模拟从池中获取一个连接
    print("    -> Connection acquired from pool")
    yield pool
    print("    <- Connection released back to pool")

