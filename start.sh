#!/bin/bash

# PlugVerse 启动脚本

echo "🚀 启动 PlugVerse..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt -q

# 创建必要目录
mkdir -p logs data output config/plugins

# 启动服务
echo "✅ 启动服务..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
