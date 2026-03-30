# PlugVerse Docker 镜像
# 多阶段构建，支持多架构 (x86_64, aarch64)
# 平台：linux/amd64, linux/arm64

# ===== 阶段 1: 构建前端 =====
FROM --platform=$BUILDPLATFORM node:20-alpine AS frontend-builder

ARG TARGETPLATFORM
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

# ===== 阶段 2: Python 后端 =====
FROM python:3.11-slim

LABEL maintainer="PlugVerse Team"
LABEL version="0.3.0"
LABEL description="PlugVerse 插件化平台"
LABEL org.opencontainers.image.source="https://github.com/your-org/plugverse"

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖（包括 ffmpeg 用于音视频处理）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN groupadd -r plugverse && useradd -r -g plugverse plugverse

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY api/ ./api/
COPY config/ ./config/
COPY plugins/ ./plugins/

# 复制构建好的前端
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建必要目录
RUN mkdir -p output logs && chown -R plugverse:plugverse /app

# 切换到非 root 用户
USER plugverse

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
