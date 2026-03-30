# PlugVerse 系统要求

本文档详细说明了部署 PlugVerse 所需的硬件和软件要求。

---

## 🖥️ 硬件要求

### 最低配置

| 组件 | 要求 |
|------|------|
| CPU | 2 核心 (x86_64 或 aarch64) |
| 内存 | 2 GB RAM |
| 存储 | 10 GB 可用空间 |
| 网络 | 10 Mbps 带宽 |

### 推荐配置

| 组件 | 要求 |
|------|------|
| CPU | 4 核心 |
| 内存 | 4-8 GB RAM |
| 存储 | 50 GB SSD |
| 网络 | 100 Mbps 带宽 |

### 生产环境配置

| 组件 | 要求 |
|------|------|
| CPU | 8 核心+ |
| 内存 | 16 GB+ RAM |
| 存储 | 100 GB+ NVMe SSD |
| 网络 | 1 Gbps 带宽 |

---

## 💿 操作系统支持

### 完全支持

| 系统 | 版本 | 架构 |
|------|------|------|
| Ubuntu | 20.04, 22.04, 24.04 | x86_64, aarch64 |
| Debian | 10, 11, 12 | x86_64, aarch64 |
| CentOS | 7, 8, 9 | x86_64 |
| RHEL | 7, 8, 9 | x86_64 |
| Fedora | 38, 39, 40 | x86_64, aarch64 |
| Alpine | 3.18+ | x86_64, aarch64 |
| macOS | 12+ | x86_64, arm64 |

### 部分支持

| 系统 | 说明 |
|------|------|
| Windows | 需要 WSL2 或 Docker Desktop |
| Other Linux | 需要手动安装依赖 |

---

## 📦 软件依赖

### 运行时依赖

| 软件 | 最低版本 | 推荐版本 |
|------|----------|----------|
| Python | 3.9 | 3.11+ |
| Node.js | 18 | 20+ |
| pip | 21.0 | 23.0+ |
| npm | 8 | 10+ |

### 可选依赖

| 软件 | 用途 |
|------|------|
| Docker | 容器化部署 |
| Docker Compose | 多容器编排 |
| Nginx | 反向代理 |
| Redis | 缓存/任务队列 |
| PostgreSQL | 生产数据库 |
| ffmpeg | 音视频处理 |

### 系统库

| 库 | Ubuntu/Debian | CentOS/RHEL |
|----|---------------|-------------|
| GCC | build-essential | gcc gcc-c++ |
| Make | make | make |
| OpenSSL | libssl-dev | openssl-devel |
| FFmpeg | ffmpeg | ffmpeg |

---

## 🌐 网络要求

### 端口

| 端口 | 协议 | 用途 |
|------|------|------|
| 8000 | TCP | 应用服务 |
| 80 | TCP | HTTP (Nginx) |
| 443 | TCP | HTTPS (Nginx) |
| 6379 | TCP | Redis (可选) |
| 5432 | TCP | PostgreSQL (可选) |

### 防火墙配置

```bash
# Ubuntu (UFW)
sudo ufw allow 8000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## 🐳 Docker 要求

### Docker 版本

| 组件 | 最低版本 |
|------|----------|
| Docker Engine | 20.10+ |
| Docker Compose | 2.0+ |
| containerd | 1.6+ |

### 存储驱动

推荐使用 `overlay2` 存储驱动。

```bash
docker info | grep "Storage Driver"
```

### 内存限制

确保 Docker 有足够的内存：

```bash
# 检查 Docker 内存限制
docker system info | grep -i memory
```

---

## 📊 性能基准

### 启动时间

| 部署方式 | 冷启动 | 热启动 |
|----------|--------|--------|
| 直接运行 | ~100ms | ~50ms |
| Docker | ~500ms | ~200ms |
| Systemd | ~2s | ~1s |

### 资源使用

| 状态 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| 空闲 | <5% | ~200MB | ~1GB |
| 中等负载 | 20-40% | ~500MB | ~5GB |
| 高负载 | 80-100% | ~2GB | ~20GB |

---

## 🔧 架构特定说明

### x86_64 (AMD64)

- 完全支持所有功能
- 最佳性能
- 推荐用于生产环境

### aarch64 (ARM64)

- 完全支持所有功能
- 适用于 ARM 服务器（如 AWS Graviton）
- 性能与 x86_64 相当

### macOS (Apple Silicon)

- 开发环境完全支持
- 生产环境不推荐
- 使用 Docker Desktop 运行

---

## ✅ 系统检查脚本

运行以下命令检查系统是否满足要求：

```bash
#!/bin/bash

echo "系统检查"
echo "========"

# CPU
echo "CPU: $(uname -m) ($(nproc 核))"

# 内存
echo "内存：$(free -h | awk '/^Mem:/ {print $2}')"

# 磁盘
echo "磁盘：$(df -h . | awk 'NR==2 {print $4}') 可用"

# Python
if command -v python3 &> /dev/null; then
    echo "Python: $(python3 --version)"
else
    echo "Python: ❌ 未安装"
fi

# Node.js
if command -v node &> /dev/null; then
    echo "Node.js: $(node --version)"
else
    echo "Node.js: ❌ 未安装"
fi

# Docker
if command -v docker &> /dev/null; then
    echo "Docker: $(docker --version)"
else
    echo "Docker: ❌ 未安装"
fi
```

---

## 🆘 故障排查

### 常见问题

**1. Python 版本过低**
```bash
# Ubuntu
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11

# CentOS
sudo yum install python311
```

**2. 内存不足**
```bash
# 添加 swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**3. 磁盘空间不足**
```bash
# 清理 Docker
docker system prune -a

# 清理 pip 缓存
pip cache purge
```

---

**最后更新:** 2026-03-30  
**版本:** v0.3.0
