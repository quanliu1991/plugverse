#!/bin/bash

# PlugVerse 综合测试脚本

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "PlugVerse 综合测试"
echo "===================="
echo ""

PASSED=0
FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo "✓ $2"
        ((PASSED++))
    else
        echo "✗ $2"
        ((FAILED++))
    fi
}

# 1. 环境检查
echo "1. 环境检查"
if python3 --version >/dev/null 2>&1; then
    test_result 0 "Python 已安装"
else
    test_result 1 "Python"
fi
if node --version >/dev/null 2>&1; then
    test_result 0 "Node.js 已安装"
else
    test_result 1 "Node.js"
fi
echo ""

# 2. 后端测试
echo "2. 后端测试"
if [ -d "venv" ]; then
    source venv/bin/activate
    python3 -c "from app.main import app" 2>/dev/null && test_result 0 "后端模块导入" || test_result 1 "后端模块导入"
    deactivate
else
    test_result 1 "虚拟环境"
fi
echo ""

# 3. 前端测试
echo "3. 前端测试"
[ -d "frontend/node_modules" ] && test_result 0 "前端依赖已安装" || test_result 1 "前端依赖"
[ -d "frontend/dist" ] && test_result 0 "前端已构建" || test_result 1 "前端构建"
echo ""

# 4. 插件测试
echo "4. 插件测试"
PLUGIN_COUNT=$(find plugins -name "manifest.json" 2>/dev/null | wc -l | tr -d ' ')
test_result 0 "发现 $PLUGIN_COUNT 个插件"
[ -f "plugins/media-transcribe/main.py" ] && test_result 0 "media-transcribe 插件" || test_result 1 "media-transcribe"
[ -f "plugins/hello-world/main.py" ] && test_result 0 "hello-world 插件" || test_result 1 "hello-world"
echo ""

# 5. 文档检查
echo "5. 文档检查"
[ -f "README.md" ] && test_result 0 "README.md" || test_result 1 "README.md"
[ -f "DEPLOY.md" ] && test_result 0 "DEPLOY.md" || test_result 1 "DEPLOY.md"
[ -f "TASKS.md" ] && test_result 0 "TASKS.md" || test_result 1 "TASKS.md"
echo ""

# 6. 部署工具
echo "6. 部署工具"
[ -f "deploy.sh" ] && test_result 0 "deploy.sh" || test_result 1 "deploy.sh"
[ -f "Dockerfile" ] && test_result 0 "Dockerfile" || test_result 1 "Dockerfile"
[ -f "docker-compose.yml" ] && test_result 0 "docker-compose.yml" || test_result 1 "docker-compose.yml"
echo ""

echo "===================="
echo "结果：$PASSED 通过，$FAILED 失败"

if [ $FAILED -eq 0 ]; then
    echo "所有测试通过"
    exit 0
else
    echo "部分测试失败"
    exit 1
fi
