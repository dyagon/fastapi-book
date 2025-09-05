# FastAPI WebSocket 聊天室项目

一个基于 FastAPI 和 WebSocket 的现代化实时聊天室应用，支持用户注册、登录和实时消息通信。

## 🚀 项目特性

- **实时通信**：基于 WebSocket 的实时消息传输
- **用户管理**：完整的用户注册、登录、登出功能
- **现代化UI**：响应式设计，支持桌面端和移动端
- **JWT认证**：安全的用户身份验证
- **房间管理**：支持多用户聊天室
- **在线状态**：实时显示在线用户列表

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代、快速的 Web 框架
- **WebSocket** - 实时双向通信
- **JWT** - JSON Web Token 身份验证
- **SQLAlchemy** - ORM 数据库操作
- **Alembic** - 数据库迁移工具

### 前端
- **Vue.js 3** - 渐进式 JavaScript 框架
- **现代CSS** - Flexbox 布局，响应式设计
- **原生JavaScript** - 无额外依赖的轻量级实现


## 🚀 快速开始

### 环境要求

- Python 3.8+
- PostgreSQL (或 SQLite)
- Redis (可选，用于缓存)

### 启动应用

```bash
# 开发模式启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000` 查看应用。

## 📖 API 文档

### 用户接口

#### 注册用户
```
GET /api/v1/user/register_action
参数:
- username: 用户名
- phone_number: 手机号
- password: 密码
```

#### 用户登录
```
GET /api/v1/user/login_action
参数:
- phone_number: 手机号
- password: 密码
返回: 重定向到聊天室页面，携带 JWT token
```

#### 用户登出
```
GET /api/v1/user/logout_action
返回: 重定向到登录页面
```

### WebSocket 接口

#### 聊天室连接
```
WebSocket /api/v1/room/socketws?token=<jwt_token>
```

支持的消息类型：
- `user_list`: 用户列表更新
- `login`: 用户加入
- `logout`: 用户离开
- `message`: 聊天消息

## 🎨 界面预览

### 登录页面
- 现代化卡片式设计
- 表单验证
- 响应式布局

### 注册页面
- 用户友好的注册流程
- 实时表单验证
- 清晰的错误提示

### 聊天室页面
- 全屏布局设计
- 左侧在线用户列表
- 右侧聊天区域
- 顶部导航栏（用户信息 + 登出）
