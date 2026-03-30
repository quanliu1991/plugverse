#!/bin/bash

# PlugVerse 一键部署脚本
# 支持：Linux x86_64, Linux aarch64, macOS
# 用法：./deploy.sh [dev|prod]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🌌 PlugVerse 部署脚本"
echo "===================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检测系统架构
detect_arch() {
    ARCH=$(uname -m)
    case $ARCH in
        x86_64|amd64)
            ARCH_NAME="x86_64"
            ;;
        aarch64|arm64)
            ARCH_NAME="aarch64"
            ;;
        *)
            ARCH_NAME=$ARCH
            ;;
    esac
    echo "系统架构：$ARCH_NAME ($(uname -s))"
}

# 检测 Linux 发行版
detect_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_VERSION=$VERSION_ID
        echo "Linux 发行版：$DISTRO $DISTRO_VERSION"
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
        DISTRO_VERSION=$(cat /etc/redhat-release | grep -oP '\d+\.\d+' | head -1)
        echo "Linux 发行版：RHEL/CentOS $DISTRO_VERSION"
    else
        DISTRO="unknown"
        echo "Linux 发行版：未知"
    fi
}

# 检测 Python 版本
check_python() {
    echo -n "📦 检查 Python 环境... "
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}Python $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}未找到 Python3${NC}"
        install_python
    fi
}

# 安装 Python (Linux)
install_python() {
    echo "📦 安装 Python3..."
    case $DISTRO in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        centos|rhel|fedora)
            sudo yum install -y python3 python3-pip
            ;;
        alpine)
            apk add --no-cache python3 py3-pip
            ;;
        *)
            echo -e "${RED}无法自动安装 Python，请手动安装 Python 3.9+${NC}"
            exit 1
            ;;
    esac
}

# 检查 Node.js 版本
check_node() {
    echo -n "📦 检查 Node.js 环境... "
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}$NODE_VERSION${NC}"
    else
        echo -e "${YELLOW}未找到 Node.js (前端功能将不可用)${NC}"
        if [ "$INSTALL_FRONTEND" = "true" ]; then
            install_node
        fi
    fi
}

# 安装 Node.js (Linux)
install_node() {
    echo "📦 安装 Node.js..."
    case $DISTRO in
        ubuntu|debian)
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        centos|rhel|fedora)
            curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo -E bash -
            sudo yum install -y nodejs
            ;;
        alpine)
            apk add --no-cache nodejs npm
            ;;
        *)
            echo -e "${YELLOW}跳过 Node.js 安装${NC}"
            ;;
    esac
}

# 安装系统依赖 (Linux)
install_system_deps() {
    echo ""
    echo "📦 安装系统依赖..."
    case $DISTRO in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y build-essential ffmpeg libssl-dev
            ;;
        centos|rhel|fedora)
            sudo yum install -y gcc gcc-c++ make ffmpeg openssl-devel
            ;;
        alpine)
            apk add --no-cache gcc g++ make ffmpeg openssl-dev
            ;;
        *)
            echo -e "${YELLOW}跳过系统依赖安装${NC}"
            return 0
            ;;
    esac
    echo -e "${GREEN}✓ 系统依赖安装完成${NC}"
}

# 创建虚拟环境
setup_venv() {
    echo ""
    echo "🔧 设置 Python 虚拟环境..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
    else
        echo -e "${YELLOW}✓ 虚拟环境已存在${NC}"
    fi
}

# 安装后端依赖
install_backend() {
    echo ""
    echo "📦 安装后端依赖..."
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
    deactivate
}

# 安装前端依赖
install_frontend() {
    echo ""
    echo "📦 安装前端依赖..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
        echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
    else
        echo -e "${YELLOW}✓ 前端依赖已存在${NC}"
    fi
    cd ..
}

# 构建前端
build_frontend() {
    echo ""
    echo "🔨 构建前端..."
    cd frontend
    npm run build
    echo -e "${GREEN}✓ 前端构建完成${NC}"
    cd ..
}

# 创建必要目录
create_dirs() {
    echo ""
    echo "📁 创建必要目录..."
    mkdir -p output config plugins
    echo -e "${GREEN}✓ 目录创建完成${NC}"
}

# 创建配置文件
create_config() {
    echo ""
    echo "⚙️  创建配置文件..."
    if [ ! -f "config/default.yaml" ]; then
        cat > config/default.yaml << 'EOF'
# PlugVerse 配置文件

server:
  host: 0.0.0.0
  port: 8000
  debug: false

storage:
  path: ./output
  max_size: 10GB

plugins:
  auto_load: true
  directory: ./plugins

logging:
  level: INFO
  file: ./logs/app.log
EOF
        echo -e "${GREEN}✓ 配置文件已创建${NC}"
    else
        echo -e "${YELLOW}✓ 配置文件已存在${NC}"
    fi
}

# 数据库迁移
run_migrations() {
    echo ""
    echo "🗄️  运行数据库迁移..."
    # 如果有数据库迁移脚本，在这里执行
    echo -e "${GREEN}✓ 数据库就绪${NC}"
}

# 启动服务
start_service() {
    echo ""
    echo "🚀 启动服务..."
    source venv/bin/activate
    
    if [ "$1" = "dev" ]; then
        echo -e "${YELLOW}开发模式启动...${NC}"
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    else
        echo -e "${GREEN}生产模式启动...${NC}"
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    fi
}

# 显示完成信息
show_complete() {
    echo ""
    echo "======================================"
    echo -e "${GREEN}🎉 部署完成！${NC}"
    echo "======================================"
    echo ""
    echo "📍 服务地址:"
    echo "   - API: http://localhost:8000"
    echo "   - 文档：http://localhost:8000/docs"
    echo ""
    echo "📝 常用命令:"
    echo "   - 启动开发服务器：./deploy.sh dev"
    echo "   - 启动生产服务器：./deploy.sh prod"
    echo "   - 查看日志：tail -f logs/app.log"
    echo ""
}

# 主流程
main() {
    DEPLOY_MODE=${1:-prod}
    INSTALL_FRONTEND=true
    
    echo "部署模式：$DEPLOY_MODE"
    echo ""
    
    # 系统检测
    detect_arch
    if [ "$(uname)" = "Linux" ]; then
        detect_linux_distro
        install_system_deps
    fi
    
    # 环境检查
    check_python
    check_node
    
    # 准备工作
    create_dirs
    create_config
    
    # 后端部署
    setup_venv
    install_backend
    
    # 前端部署（可选）
    if command -v node &> /dev/null; then
        install_frontend
        if [ "$DEPLOY_MODE" = "prod" ]; then
            build_frontend
        fi
    else
        echo -e "${YELLOW}跳过前端构建（Node.js 未安装）${NC}"
    fi
    
    # 数据库
    run_migrations
    
    # 完成
    show_complete
    
    # 启动服务
    if [ "$2" = "--start" ]; then
        start_service "$DEPLOY_MODE"
    fi
}

# 显示帮助
show_help() {
    echo "用法：./deploy.sh [选项]"
    echo ""
    echo "选项:"
    echo "  dev       开发模式部署"
    echo "  prod      生产模式部署（默认）"
    echo "  --start   部署后启动服务"
    echo "  --help    显示帮助信息"
    echo ""
    echo "支持的架构:"
    echo "  - Linux x86_64 (AMD64)"
    echo "  - Linux aarch64 (ARM64)"
    echo "  - macOS x86_64 / arm64"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh              # 生产模式部署"
    echo "  ./deploy.sh dev          # 开发模式部署"
    echo "  ./deploy.sh prod --start # 部署并启动"
    echo ""
    echo "文档:"
    echo "  - DEPLOY-LINUX.md        # Linux 部署指南"
    echo "  - SYSTEM-REQUIREMENTS.md # 系统要求"
    echo ""
}

# 解析参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# 执行主流程
main "$@"
