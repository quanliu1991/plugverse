#!/bin/bash

# PlugVerse 外网暴露脚本
# 支持：ngrok, localtunnel, cloudflared

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🌐 PlugVerse 外网暴露"
echo "===================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查本地服务是否运行
check_local_service() {
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 本地服务运行中${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ 本地服务未运行，正在启动...${NC}"
        source venv/bin/activate
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/expose.log 2>&1 &
        sleep 3
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 服务已启动${NC}"
            return 0
        else
            echo -e "${RED}✗ 服务启动失败${NC}"
            return 1
        fi
    fi
}

# 方案 1: ngrok
use_ngrok() {
    echo ""
    echo "使用 ngrok 暴露服务..."
    
    if ! command -v ngrok &> /dev/null; then
        echo -e "${YELLOW}ngrok 未安装，正在安装...${NC}"
        if command -v brew &> /dev/null; then
            brew install ngrok
        elif command -v snap &> /dev/null; then
            sudo snap install ngrok
        else
            echo "请手动安装 ngrok: https://ngrok.com/download"
            return 1
        fi
    fi
    
    # 检查是否已认证
    if [ ! -f ~/.config/ngrok/ngrok.yml ]; then
        echo -e "${YELLOW}请先配置 ngrok authtoken${NC}"
        echo "1. 访问 https://dashboard.ngrok.com/signup 注册"
        echo "2. 获取 authtoken"
        echo "3. 运行：ngrok config add-authtoken YOUR_TOKEN"
        echo ""
        read -p "输入 ngrok authtoken: " token
        ngrok config add-authtoken "$token"
    fi
    
    echo -e "${GREEN}启动 ngrok...${NC}"
    ngrok http 8000 --log=logs/ngrok.log &
    NGROK_PID=$!
    
    sleep 5
    
    # 获取公共 URL
    if command -v curl &> /dev/null; then
        PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4)
        if [ -n "$PUBLIC_URL" ]; then
            echo ""
            echo -e "${GREEN}================================${NC}"
            echo -e "${GREEN}🎉 外网访问地址:${NC}"
            echo -e "${GREEN}$PUBLIC_URL${NC}"
            echo -e "${GREEN}================================${NC}"
            echo ""
            echo "API 文档：$PUBLIC_URL/docs"
            echo "健康检查：$PUBLIC_URL/api/health"
            echo ""
            echo "按 Ctrl+C 停止"
            wait $NGROK_PID
        fi
    fi
}

# 方案 2: localtunnel
use_localtunnel() {
    echo ""
    echo "使用 localtunnel 暴露服务..."
    
    if ! command -v lt &> /dev/null; then
        echo -e "${YELLOW}安装 localtunnel...${NC}"
        npm install -g localtunnel
    fi
    
    # 生成随机子域名
    SUBDOMAIN="plugverse-$(date +%s)"
    
    echo -e "${GREEN}启动 localtunnel...${NC}"
    lt --port 8000 --subdomain $SUBDOMAIN &
    LT_PID=$!
    
    sleep 5
    
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}🎉 外网访问地址:${NC}"
    echo -e "${GREEN}https://$SUBDOMAIN.loca.lt${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "首次访问需要点击 'Click to Continue'"
    echo "API 文档：https://$SUBDOMAIN.loca.lt/docs"
    echo ""
    echo "按 Ctrl+C 停止"
    wait $LT_PID
}

# 方案 3: Cloudflare Tunnel
use_cloudflared() {
    echo ""
    echo "使用 Cloudflare Tunnel 暴露服务..."
    
    if ! command -v cloudflared &> /dev/null; then
        echo -e "${YELLOW}安装 cloudflared...${NC}"
        if command -v brew &> /dev/null; then
            brew install cloudflared
        elif [ -f /etc/os-release ]; then
            . /etc/os-release
            case $ID in
                ubuntu|debian)
                    curl -fsSL https://pkg.cloudflare.com/cloudflared.gpg | sudo apt-key add -
                    echo "deb https://pkg.cloudflare.com/cloudflared $VERSION_CODENAME main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
                    sudo apt-get update && sudo apt-get install -y cloudflared
                    ;;
                centos|rhel|fedora)
                    curl -fsSL https://pkg.cloudflare.com/cloudflared.gpg | sudo gpg --dearmor -o /etc/yum.repos.d/cloudflared.gpg
                    echo "[cloudflared]" | sudo tee /etc/yum.repos.d/cloudflared.repo
                    echo "baseurl=https://pkg.cloudflare.com/cloudflared" | sudo tee -a /etc/yum.repos.d/cloudflared.repo
                    sudo yum install -y cloudflared
                    ;;
            esac
        else
            # 直接下载
            curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
            chmod +x cloudflared
            sudo mv cloudflared /usr/local/bin/
        fi
    fi
    
    echo -e "${GREEN}启动 Cloudflare Tunnel...${NC}"
    cloudflared tunnel --url http://localhost:8000 &
    CF_PID=$!
    
    sleep 5
    
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}🎉 外网访问地址:${NC}"
    echo -e "${GREEN}查看上方日志中的 *.trycloudflare.com 地址${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "按 Ctrl+C 停止"
    wait $CF_PID
}

# 显示菜单
show_menu() {
    echo "请选择外网暴露方式:"
    echo ""
    echo "1) ngrok (推荐，稳定)"
    echo "2) localtunnel (免费，无需注册)"
    echo "3) Cloudflare Tunnel (免费，需要域名)"
    echo "4) 仅启动本地服务"
    echo ""
    read -p "选择 [1-4]: " choice
    
    case $choice in
        1)
            check_local_service
            use_ngrok
            ;;
        2)
            check_local_service
            use_localtunnel
            ;;
        3)
            check_local_service
            use_cloudflared
            ;;
        4)
            check_local_service
            echo ""
            echo "本地服务已启动："
            echo "  http://localhost:8000"
            echo "  http://$(hostname -I | awk '{print $1}'):8000"
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac
}

# 快速模式（使用 localtunnel）
quick_mode() {
    check_local_service
    use_localtunnel
}

# 解析参数
if [ "$1" = "--quick" ] || [ "$1" = "-q" ]; then
    quick_mode
elif [ "$1" = "--ngrok" ] || [ "$1" = "-n" ]; then
    check_local_service
    use_ngrok
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "用法：./expose.sh [选项]"
    echo ""
    echo "选项:"
    echo "  -q, --quick     快速模式（使用 localtunnel）"
    echo "  -n, --ngrok     使用 ngrok"
    echo "  -h, --help      显示帮助"
    echo ""
    echo "不带参数时显示菜单"
else
    show_menu
fi
