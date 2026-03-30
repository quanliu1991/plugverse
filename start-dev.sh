#!/bin/bash

# PlugVerse 快速启动脚本

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "🌌 PlugVerse 快速启动"
echo "===================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -q -r requirements.txt

# 创建必要目录
mkdir -p output config logs

# 启动服务
echo ""
echo "启动服务..."
echo "访问地址：http://localhost:8000"
echo "API 文档：http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
