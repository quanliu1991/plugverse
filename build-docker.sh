#!/bin/bash

# PlugVerse Docker 多架构构建脚本
# 支持：linux/amd64 (x86_64), linux/arm64 (aarch64)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🐳 PlugVerse Docker 构建"
echo "======================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误：Docker 未安装${NC}"
    exit 1
fi

# 检查 buildx
if ! docker buildx version &> /dev/null; then
    echo -e "${YELLOW}警告：docker buildx 不可用，将只构建当前架构镜像${NC}"
    docker build -t plugverse:latest .
    exit 0
fi

# 解析参数
ARCH=${1:-all}
PUSH=${2:-false}

echo "架构：$ARCH"
echo "推送：$PUSH"
echo ""

# 创建 builder
docker buildx create --name plugverse-builder --use 2>/dev/null || true

case $ARCH in
    amd64|x86_64)
        echo "构建 linux/amd64 镜像..."
        docker buildx build \
            --platform linux/amd64 \
            -t plugverse:latest \
            -t plugverse:$(date +%Y%m%d) \
            --load \
            .
        ;;
    arm64|aarch64)
        echo "构建 linux/arm64 镜像..."
        docker buildx build \
            --platform linux/arm64 \
            -t plugverse:latest \
            -t plugverse:$(date +%Y%m%d) \
            --load \
            .
        ;;
    all)
        echo "构建多架构镜像..."
        if [ "$PUSH" = "true" ]; then
            docker buildx build \
                --platform linux/amd64,linux/arm64 \
                -t plugverse:latest \
                -t plugverse:$(date +%Y%m%d) \
                --push \
                .
        else
            echo -e "${YELLOW}注意：多架构构建需要推送到仓库，使用 --push 参数${NC}"
            docker buildx build \
                --platform linux/amd64,linux/arm64 \
                -t plugverse:latest \
                -t plugverse:$(date +%Y%m%d) \
                .
        fi
        ;;
    *)
        echo -e "${RED}错误：不支持的架构 $ARCH${NC}"
        echo "支持的架构：amd64, arm64, all"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ 构建完成${NC}"
echo ""
echo "镜像列表:"
docker images plugverse
