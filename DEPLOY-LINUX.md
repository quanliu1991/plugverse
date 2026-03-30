# PlugVerse Linux x86_64 部署指南

本文档针对 Linux x86_64 架构服务器提供详细部署说明。

## 📋 系统要求

### 最低配置
- **CPU:** 2 核心
- **内存:** 2 GB RAM
- **存储:** 10 GB 可用空间
- **系统:** Linux x86_64 (Ubuntu 20.04+, CentOS 7+, Debian 10+)

### 推荐配置
- **CPU:** 4 核心
- **内存:** 4 GB RAM
- **存储:** 50 GB SSD
- **系统:** Ubuntu 22.04 LTS

---

## 🚀 快速部署（一键脚本）

### 1. 下载项目

```bash
cd /opt
git clone https://github.com/your-org/plugverse.git
cd plugverse
```

### 2. 执行一键部署

```bash
chmod +x deploy.sh
sudo ./deploy.sh prod --start
```

脚本会自动：
- ✅ 检测系统架构和发行版
- ✅ 安装 Python 3.11+ 和 Node.js 20+
- ✅ 安装系统依赖（ffmpeg、gcc 等）
- ✅ 创建虚拟环境
- ✅ 安装 Python 和前端依赖
- ✅ 构建前端
- ✅ 配置服务

### 3. 验证安装

```bash
curl http://localhost:8000/api/health
```

预期输出：
```json
{"status":"healthy","timestamp":"2026-03-30T00:00:00Z","version":"0.3.0"}
```

---

## 📦 手动部署

### Ubuntu/Debian

#### 1. 安装系统依赖

```bash
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nodejs \
    npm \
    ffmpeg \
    git \
    curl \
    build-essential
```

#### 2. 克隆项目

```bash
cd /opt
sudo git clone https://github.com/your-org/plugverse.git
sudo chown -R $USER:$USER plugverse
cd plugverse
```

#### 3. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. 安装前端依赖

```bash
cd frontend
npm install
npm run build
cd ..
```

#### 5. 创建配置文件

```bash
mkdir -p config output logs
cp config/default.yaml.example config/default.yaml
```

#### 6. 启动服务

```bash
# 开发模式
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（后台运行）
nohup venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 > logs/app.log 2>&1 &
```

---

### CentOS/RHEL

#### 1. 安装 EPEL 和 Remi 仓库

```bash
sudo yum install -y epel-release
sudo yum install -y https://rpms.remirepo.net/enterprise/remi-release-8.rpm
```

#### 2. 安装依赖

```bash
sudo yum install -y \
    python3.11 \
    python3.11-pip \
    nodejs \
    npm \
    ffmpeg \
    git \
    curl \
    gcc \
    gcc-c++ \
    make
```

#### 3. 后续步骤

与 Ubuntu/Debian 相同（从步骤 2 开始）

---

## 🔧 Systemd 服务配置

### 1. 创建服务文件

```bash
sudo tee /etc/systemd/system/plugverse.service > /dev/null << 'EOF'
[Unit]
Description=PlugVerse Plugin Platform
After=network.target

[Service]
Type=notify
User=plugverse
Group=plugverse
WorkingDirectory=/opt/plugverse
Environment="PATH=/opt/plugverse/venv/bin"
ExecStart=/opt/plugverse/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=plugverse

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
```

### 2. 创建用户

```bash
sudo useradd -r -s /bin/false plugverse
sudo chown -R plugverse:plugverse /opt/plugverse
```

### 3. 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable plugverse
sudo systemctl start plugverse
sudo systemctl status plugverse
```

### 4. 查看日志

```bash
sudo journalctl -u plugverse -f
```

---

## 🐳 Docker 部署

### 1. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker

# CentOS
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. 构建镜像（x86_64）

```bash
docker build -t plugverse:latest .
```

### 3. 运行容器

```bash
docker run -d \
  --name plugverse \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/plugins:/app/plugins \
  -v $(pwd)/logs:/app/logs \
  -e ENV=production \
  --restart unless-stopped \
  plugverse:latest
```

### 4. Docker Compose

```bash
docker-compose up -d
```

---

## 🔐 Nginx 反向代理

### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt-get install -y nginx

# CentOS
sudo yum install -y nginx
```

### 2. 配置 Nginx

```bash
sudo tee /etc/nginx/sites-available/plugverse > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/plugverse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL 证书（Let's Encrypt）

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔍 故障排查

### 常见问题

**1. 端口被占用**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

**2. 权限问题**
```bash
sudo chown -R $USER:$USER /opt/plugverse
chmod +x deploy.sh
```

**3. Python 版本过低**
```bash
# Ubuntu
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11

# CentOS
sudo yum install -y python311
```

**4. ffmpeg 缺失**
```bash
# Ubuntu/Debian
sudo apt-get install -y ffmpeg

# CentOS
sudo yum install -y ffmpeg
```

### 查看日志

```bash
# 应用日志
tail -f logs/app.log

# Systemd 日志
sudo journalctl -u plugverse -f

# Docker 日志
docker logs -f plugverse
```

---

## 📊 性能优化

### 1. 使用多进程

```bash
# 在 config/default.yaml 中设置
server:
  workers: 4  # 根据 CPU 核心数调整
```

### 2. 启用 Redis 缓存

```bash
# 安装 Redis
sudo apt-get install -y redis-server

# 配置 docker-compose
docker-compose --profile with-redis up -d
```

### 3. 数据库优化

使用 PostgreSQL 替代 SQLite：

```bash
docker-compose --profile with-postgres up -d
```

---

## 🔄 更新部署

```bash
cd /opt/plugverse

# 拉取最新代码
git pull origin main

# 重新部署
sudo ./deploy.sh prod

# 重启服务
sudo systemctl restart plugverse
```

---

## 📞 技术支持

- 📖 文档：https://docs.plugverse.com
- 🐛 问题反馈：https://github.com/your-org/plugverse/issues
- 💬 社区：https://discord.gg/plugverse

---

**最后更新:** 2026-03-30  
**适用架构:** Linux x86_64, Linux aarch64  
**版本:** v0.3.0
