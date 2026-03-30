# PlugVerse 部署指南

本文档提供多种部署方式，选择适合你的方案。

---

## 🚀 快速部署（推荐）

### 方式一：一键脚本部署

```bash
# 克隆项目
git clone https://github.com/your-org/plugverse.git
cd plugverse

# 执行一键部署
chmod +x deploy.sh
./deploy.sh prod --start
```

**访问地址：**
- API: http://localhost:8000
- 文档：http://localhost:8000/docs

---

### 方式二：Docker 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**访问地址：** http://localhost:8000

---

### 方式三：Docker（完整栈）

包含 Nginx 反向代理、Redis、PostgreSQL：

```bash
# 启动完整服务栈
docker-compose --profile with-nginx --profile with-redis --profile with-postgres up -d
```

**访问地址：**
- HTTP: http://localhost:80
- HTTPS: https://localhost (需配置 SSL 证书)

---

## 📋 手动部署

### 1. 环境要求

- Python 3.11+
- Node.js 18+ (前端构建)
- Git

### 2. 克隆项目

```bash
git clone https://github.com/your-org/plugverse.git
cd plugverse
```

### 3. 安装后端

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 安装前端

```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. 配置

```bash
# 复制配置模板
cp config/default.yaml.example config/default.yaml

# 编辑配置
vim config/default.yaml
```

### 6. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🔧 生产环境部署

### Systemd 服务（Linux）

```bash
# 复制服务文件
sudo cp plugverse.service /etc/systemd/system/

# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start plugverse

# 设置开机自启
sudo systemctl enable plugverse

# 查看状态
sudo systemctl status plugverse

# 查看日志
sudo journalctl -u plugverse -f
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

---

## 🐳 Docker 部署详解

### 构建镜像

```bash
docker build -t plugverse:latest .
```

### 运行容器

```bash
docker run -d \
  --name plugverse \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/plugins:/app/plugins \
  -e ENV=production \
  plugverse:latest
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ENV` | 运行环境 | `production` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `STORAGE_PATH` | 存储路径 | `/app/output` |
| `MAX_STORAGE_SIZE` | 最大存储 | `10GB` |

---

## 📊 性能优化

### 1. 使用 Gunicorn

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. 启用缓存

```bash
# 安装 Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 配置中使用 Redis 缓存
```

### 3. 数据库优化

使用 PostgreSQL 替代 SQLite：

```yaml
# docker-compose.yml 中启用 postgres
docker-compose --profile with-postgres up -d
```

---

## 🔍 故障排查

### 常见问题

**1. 端口被占用**
```bash
# 查看占用端口的进程
lsof -i :8000
# 杀死进程
kill -9 <PID>
```

**2. 权限问题**
```bash
# 修复权限
sudo chown -R $(whoami):$(whoami) /path/to/plugverse
```

**3. 依赖安装失败**
```bash
# 更新 pip
pip install --upgrade pip
# 清除缓存重装
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### 查看日志

```bash
# 应用日志
tail -f logs/app.log

# Docker 日志
docker-compose logs -f

# Systemd 日志
journalctl -u plugverse -f
```

---

## 📈 监控

### 健康检查

```bash
curl http://localhost:8000/api/health
```

### 性能监控

- 启用 Prometheus 指标
- 集成 Grafana 仪表盘
- 配置告警规则

---

## 🔄 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新部署
./deploy.sh prod --start

# Docker 更新
docker-compose pull
docker-compose up -d
```

---

## 📞 支持

遇到问题？

- 📖 查看 [文档](docs/)
- 🐛 提交 [Issue](https://github.com/your-org/plugverse/issues)
- 💬 加入 [Discord](https://discord.gg/xxx)

---

**最后更新:** 2026-03-30  
**版本:** v0.3.0
