#!/bin/bash

# PKCE OAuth2 SPA 启动脚本

echo "🚀 启动 PKCE OAuth2 演示..."

# 检查是否安装了 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 请先安装 Node.js"
    echo "下载地址: https://nodejs.org/"
    exit 1
fi

# 检查是否安装了 npm
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 请先安装 npm"
    exit 1
fi

echo "📦 检查依赖..."

# 检查 package.json 是否存在
if [ ! -f "package.json" ]; then
    echo "❌ 错误: package.json 不存在"
    exit 1
fi

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📥 安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

echo "✅ 依赖检查完成"

# 检查端口是否被占用
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 端口 8080 已被占用"
    echo "请确保没有其他服务使用此端口"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $ACSII_REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🌐 启动 SPA 服务器..."
echo "服务器地址: http://localhost:8080"
echo "按 Ctrl+C 停止服务器"
echo

# 启动服务器
node server.js
