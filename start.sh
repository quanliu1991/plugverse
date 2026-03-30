#!/bin/bash

# PlugVerse 启动脚本

echo "🚀 启动 PlugVerse..."

# 优先使用 Python 3.9+（FastAPI 0.109+ 需要；系统默认 python3 若为 3.7 会安装失败）
pick_python() {
    for cmd in python3.12 python3.11 python3.10 python3.9 python3; do
        if command -v "$cmd" &> /dev/null; then
            if "$cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}
if ! PY="$(pick_python)"; then
    echo "❌ 错误：需要 Python 3.9 或更高版本（当前未找到）"
    exit 1
fi

# 检查虚拟环境（若 venv 由旧版 Python 创建，可删除 venv 后重新运行本脚本）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境（$("$PY" -c 'import sys; print(sys.executable)')）..."
    "$PY" -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt -q

# 创建必要目录
mkdir -p logs data output config/plugins

# 前端生产构建（frontend/dist 被 git 忽略，首次启动需生成）
if [ ! -f "frontend/dist/index.html" ]; then
    if command -v npm &>/dev/null; then
        echo "📦 构建前端（frontend/dist）..."
        (cd frontend && npm ci && npm run build) || echo "⚠️  前端构建失败，首页可能无法显示，请手动: cd frontend && npm ci && npm run build"
    else
        echo "⚠️  未检测到 npm，跳过前端构建。首页需先执行: cd frontend && npm ci && npm run build"
    fi
fi

# 启动服务
echo "✅ 启动服务..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
