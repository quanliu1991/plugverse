# PlugVerse - 元插平台

> 🌌 插件宇宙，无限扩展

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 项目简介

**PlugVerse（元插平台）** 是一个插件化的 C 端客户平台，支持以插件方式扩展各种功能。

平台采用模块化架构，核心提供插件管理、事件总线、配置中心、权限管理等基础能力，开发者可以通过开发插件快速扩展平台功能。

### 📊 当前进度

- **Phase 1 - 核心框架:** ✅ 100% 完成
- **Phase 2 - 首个插件:** ✅ 100% 完成 (media-transcribe)
- **Phase 3 - 前端 UI:** 🔄 80% 进行中 (前端框架完成)
- **总体进度:** 75% (55/73 任务)

### ✨ 核心特性

- 🧩 **插件化架构** - 热插拔插件，无需重启服务
- 🔌 **标准化接口** - 统一的插件开发规范
- 🚌 **事件驱动** - 基于事件总线的松耦合通信
- 🔐 **权限管理** - 细粒度的插件权限控制
- ⚙️ **配置中心** - 统一的配置管理和验证
- 📊 **任务系统** - 异步任务处理和进度跟踪
- 🎨 **Web UI** - 美观的插件管理和使用界面

### 🚀 快速开始

#### 方式一：一键部署（推荐）

**支持:** Linux x86_64, Linux aarch64, macOS

```bash
git clone https://github.com/your-org/plugverse.git
cd plugverse
chmod +x deploy.sh
./deploy.sh prod --start
```

#### 方式二：Docker 部署

**支持:** 所有 Docker 平台

```bash
git clone https://github.com/your-org/plugverse.git
cd plugverse
docker-compose up -d
```

#### 方式三：手动部署

```bash
# 克隆项目
git clone https://github.com/your-org/plugverse.git
cd plugverse

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
open http://localhost:8000/docs
```

## 📦 核心模块

```
plugverse/
├── app/                    # 核心应用
│   ├── plugin_base.py      # 插件基类接口
│   ├── plugin_manager.py   # 插件管理器
│   ├── event_bus.py        # 事件总线
│   ├── config_center.py    # 配置中心
│   └── permission_manager.py # 权限管理
├── api/                    # API 路由
├── plugins/                # 插件目录
├── config/                 # 配置文件
└── frontend/               # 前端 UI
```

## 🔌 插件开发

### 插件结构

```
my-plugin/
├── manifest.json       # 插件元数据
├── main.py            # 插件主逻辑
├── requirements.txt   # Python 依赖
└── README.md          # 使用说明
```

### 快速示例

```python
# plugins/hello-world/main.py
from app.plugin_base import IPlugin, PluginMetadata, PluginType, PluginContext

class Plugin(IPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="hello-world",
            name="Hello World",
            version="1.0.0",
            description="一个简单的示例插件",
            author="Your Name",
            type=PluginType.CUSTOM
        )
    
    async def initialize(self, context: PluginContext) -> bool:
        self.context = context
        return True
    
    async def execute(self, input_data: dict) -> dict:
        return {"message": "Hello from plugin!"}
    
    async def shutdown(self) -> bool:
        return True
```

## 🎯 官方插件

| 插件 | 状态 | 描述 |
|------|------|------|
| 音视频转文字 | ✅ 已完成 | 使用 Faster-Whisper 进行语音识别 |
| Hello World | ✅ 已完成 | 示例插件 |
| 图片识别 | 📅 计划中 | OCR 和图片内容识别 |
| 数据导出 | 📅 计划中 | 导出为 Excel/CSV/PDF |
| AI 助手 | 📅 计划中 | 文本摘要、翻译、润色 |

## 📚 文档

### 快速开始
- [Linux 部署指南](DEPLOY-LINUX.md) - Ubuntu/CentOS/Debian
- [通用部署指南](DEPLOY.md) - 所有平台
- [Docker 部署](DEPLOY.md#docker-部署) - 容器化部署

### 开发文档
- [架构设计文档](docs/architecture.md)
- [插件开发指南](docs/plugin-development.md)
- [前端开发指南](frontend/README.md)
- [API 文档](http://localhost:8000/docs)

### 其他
- [测试报告](TEST-REPORT.md)
- [进度报告](PROGRESS-REPORT.md)

## 🛠️ 技术栈

**后端：**
- Python 3.11+
- FastAPI - Web 框架
- Pydantic - 数据验证
- Uvicorn - ASGI 服务器

**前端（计划）：**
- Vue 3 + TypeScript
- Element Plus
- Pinia 状态管理

**基础设施：**
- Docker & Docker Compose
- Redis（可选，用于任务队列）
- SQLite/PostgreSQL

## 🤝 贡献指南

欢迎贡献代码、文档或插件！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 [MIT 协议](LICENSE) 开源。

## 📬 联系方式

- 项目地址：https://github.com/your-org/plugverse
- 问题反馈：https://github.com/your-org/plugverse/issues
- 讨论区：https://github.com/your-org/plugverse/discussions

---

<p align="center">Made with ❤️ by PlugVerse Team</p>
