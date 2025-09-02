# PKCE OAuth2 SPA Demo

这是一个使用 **Vue 3** 和 **Node.js** 构建的单页应用(SPA)，用于演示 **PKCE (Proof Key for Code Exchange)** OAuth2 流程。

## 🚀 快速开始

### 1. 安装依赖
```bash
cd /path/to/spa
npm install
```

### 2. 启动 SPA 服务器
```bash
npm run dev
```
或者
```bash
node server.js
```

SPA 将运行在 http://localhost:8080

### 3. 启动 OAuth2 授权服务器
确保 OAuth2 服务器运行在 http://localhost:8000：
```bash
cd /path/to/oauth2
uvicorn auth_server:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问演示
在浏览器中打开 http://localhost:8080 开始 PKCE 流程演示。

## 🔐 PKCE 流程演示

### 步骤 1: 生成 PKCE 参数
- 生成随机的 `code_verifier` (43-128 字符)
- 使用 SHA256 哈希生成 `code_challenge`
- 生成 `state` 参数防止 CSRF 攻击

### 步骤 2: 用户授权
- 构建包含 PKCE 参数的授权 URL
- 跳转到授权服务器进行用户登录
- 用户同意授权后返回授权码

### 步骤 3: 交换访问令牌
- 使用授权码和 `code_verifier` 交换访问令牌
- 无需客户端密钥（公共客户端）
- 获取访问令牌和刷新令牌

### 步骤 4: 测试 API 调用
- 使用访问令牌调用受保护的 API
- 测试不同的权限范围 (scopes)
- 展示 API 响应结果

## 🛠️ 技术栈

- **Frontend**: Vue 3 (CDN)
- **Backend**: Node.js + Express
- **OAuth2**: PKCE (Proof Key for Code Exchange)
- **Crypto**: Web Crypto API (浏览器原生)

## 🔧 配置

### OAuth2 配置 (在 `app.js` 中)
```javascript
const OAUTH_CONFIG = {
    clientId: 'pkce-public-client',
    redirectUri: 'http://localhost:8080/callback',
    authServerUrl: 'http://localhost:8000',
    scopes: ['get_user_info', 'get_admin_info', 'get_user_role']
};
```

### 测试账户
- 用户名: `alice`, 密码: `wonderland`
- 用户名: `bob`, 密码: `builder`

## 📋 功能特性

### 🔒 安全特性
- ✅ PKCE (Proof Key for Code Exchange) 支持
- ✅ State 参数防止 CSRF 攻击
- ✅ 无客户端密钥（公共客户端）
- ✅ SHA256 代码挑战方法
- ✅ 安全的随机数生成

### 🖥️ 用户界面
- ✅ 响应式设计
- ✅ 步骤式流程指导
- ✅ 实时状态反馈
- ✅ 错误处理和展示
- ✅ API 响应可视化

### 🔄 流程控制
- ✅ 自动状态管理
- ✅ 回调处理
- ✅ 会话存储
- ✅ URL 清理

## 🧪 测试场景

1. **完整 PKCE 流程**: 从生成参数到获取令牌
2. **权限范围测试**: 测试不同的 API 端点
3. **错误处理**: 模拟各种错误情况
4. **安全验证**: State 参数验证

## 📁 项目结构

```
spa/
├── package.json          # 项目依赖和脚本
├── server.js            # Express 服务器
├── README.md            # 项目文档
└── public/
    ├── index.html       # 主 HTML 文件
    └── app.js          # Vue 3 应用逻辑
```

## 🔍 开发说明

### 关键文件

1. **server.js**: 简单的 Express 服务器，提供静态文件服务
2. **index.html**: 包含完整的 UI 和样式
3. **app.js**: Vue 3 应用，实现 PKCE 流程逻辑

### PKCE 实现要点

1. **Code Verifier 生成**: 使用 `crypto.getRandomValues()` 生成 32 字节随机数
2. **Code Challenge**: 使用 Web Crypto API 的 SHA256 哈希
3. **Base64 URL 编码**: 移除填充字符，替换特殊字符
4. **状态管理**: 使用 `sessionStorage` 在重定向间保持状态

### 与授权服务器交互

- **授权端点**: `/oauth2/authorize` (GET)
- **令牌端点**: `/oauth2/token` (POST)
- **API 端点**: `/user/info`, `/admin/info`, `/user/me`

## 🚨 注意事项

1. 确保授权服务器的 CORS 配置正确
2. 客户端配置必须匹配授权服务器中的设置
3. HTTPS 在生产环境中是必需的
4. 浏览器必须支持 Web Crypto API

## 🐛 故障排除

### 常见问题

1. **CORS 错误**: 检查授权服务器的 CORS 设置
2. **重定向失败**: 确认 `redirect_uri` 配置正确
3. **PKCE 验证失败**: 检查 `code_verifier` 和 `code_challenge` 生成逻辑
4. **State 不匹配**: 确保会话存储正常工作

### 调试技巧

1. 打开浏览器开发者工具查看控制台日志
2. 检查网络请求和响应
3. 验证 PKCE 参数的生成和传递
4. 确认授权服务器的日志
