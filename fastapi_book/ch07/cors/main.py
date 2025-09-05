from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 定义允许访问你的 API 的前端源列表
# 在开发环境中，通常是 localhost 加端口
# 在生产环境中，应该是你的前端应用的域名
origins = [
    "<http://localhost>",
    "<http://localhost:3000>", # 例如，你的 React 前端
    "<https://your-production-frontend.com>",
]

# 添加 CORSMiddleware 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # 允许访问的源
    allow_credentials=True,             # 是否支持携带 cookie
    allow_methods=["*"],                # 允许的 HTTP 方法 (GET, POST, etc.)
    allow_headers=["*"],                # 允许的 HTTP 请求头
)

@app.get("/")
async def main():
    return {"message": "Hello World"}
