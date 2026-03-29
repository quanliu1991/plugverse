"""
PlugVerse 主应用入口

FastAPI 应用初始化和路由注册。
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
import asyncio

from loguru import logger

from .plugin_base import PluginContext
from .event_bus import EventBus
from .config_center import ConfigCenter
from .permission_manager import PermissionManager
from .plugin_manager import PluginManager


# ========== 全局变量 ==========
event_bus: EventBus
config_center: ConfigCenter
permission_manager: PermissionManager
plugin_manager: PluginManager


# ========== 服务类 ==========
class LoggerService:
    """日志服务包装器"""
    
    def info(self, msg: str):
        logger.info(msg)
    
    def error(self, msg: str):
        logger.error(msg)
    
    def warning(self, msg: str):
        logger.warning(msg)
    
    def debug(self, msg: str):
        logger.debug(msg)


class StorageService:
    """存储服务（简化版）"""
    
    def __init__(self, storage_dir: str = "./output"):
        from pathlib import Path
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    async def save(self, filename: str, content: bytes) -> str:
        """保存文件"""
        filepath = self.storage_dir / filename
        with open(filepath, 'wb') as f:
            f.write(content)
        return str(filepath)
    
    async def load(self, filename: str) -> bytes:
        """加载文件"""
        filepath = self.storage_dir / filename
        with open(filepath, 'rb') as f:
            return f.read()
    
    async def delete(self, filename: str):
        """删除文件"""
        filepath = self.storage_dir / filename
        if filepath.exists():
            filepath.unlink()


# ========== 应用类 ==========
class PlugVerseApp:
    """PlugVerse 平台应用"""
    
    def __init__(self):
        self.services: Dict[str, Any] = {}
    
    def register_service(self, name: str, service: Any):
        """注册服务"""
        self.services[name] = service
    
    def get_service(self, name: str) -> Any:
        """获取服务"""
        return self.services.get(name)


# ========== 生命周期管理 ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    
    # 启动时
    logger.info("🚀 PlugVerse 启动中...")
    
    # 初始化全局组件
    global event_bus, config_center, permission_manager, plugin_manager
    
    event_bus = EventBus()
    config_center = ConfigCenter()
    permission_manager = PermissionManager()
    
    app_instance = PlugVerseApp()
    app_instance.register_service("logger", LoggerService())
    app_instance.register_service("storage", StorageService())
    
    plugin_manager = PluginManager(
        app_instance=app_instance,
        event_bus=event_bus,
        config_center=config_center,
        permission_manager=permission_manager
    )
    
    # 自动加载已安装的插件
    await load_installed_plugins()
    
    logger.info("✅ PlugVerse 启动完成")
    
    yield
    
    # 关闭时
    logger.info("👋 PlugVerse 关闭中...")
    await unload_all_plugins()
    logger.info("✅ PlugVerse 已关闭")


async def load_installed_plugins():
    """加载所有已安装的插件"""
    discovered = await plugin_manager.discover_plugins()
    
    for metadata in discovered:
        logger.info(f"加载插件：{metadata.id}")
        await plugin_manager.load_plugin(metadata.id)


async def unload_all_plugins():
    """卸载所有插件"""
    for plugin_id in list(plugin_manager._plugins.keys()):
        logger.info(f"卸载插件：{plugin_id}")
        await plugin_manager.unload_plugin(plugin_id)


# ========== 创建 FastAPI 应用 ==========
app = FastAPI(
    title="PlugVerse",
    description="插件化客户平台 API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== API 路由 ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "PlugVerse",
        "version": "0.1.0",
        "description": "插件化客户平台",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": "2026-03-29T23:59:59Z"
    }


@app.get("/api/stats")
async def get_stats():
    """获取平台统计信息"""
    return {
        "event_bus": event_bus.get_stats(),
        "config_center": config_center.get_stats(),
        "permission_manager": permission_manager.get_stats(),
        "plugin_manager": plugin_manager.get_stats()
    }


# ========== 插件管理 API ==========

@app.get("/api/plugins")
async def list_plugins():
    """获取所有插件列表"""
    return plugin_manager.list_plugins()


@app.get("/api/plugins/{plugin_id}")
async def get_plugin(plugin_id: str):
    """获取插件详情"""
    metadata = plugin_manager.get_metadata(plugin_id)
    status = plugin_manager.get_status(plugin_id)
    error = plugin_manager.get_error(plugin_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="插件未找到")
    
    return {
        "id": plugin_id,
        "status": status.value if status else "unknown",
        "metadata": metadata,
        "error": error
    }


@app.post("/api/plugins/{plugin_id}/load")
async def load_plugin(plugin_id: str):
    """加载插件"""
    success = await plugin_manager.load_plugin(plugin_id)
    
    if not success:
        error = plugin_manager.get_error(plugin_id)
        raise HTTPException(
            status_code=500, 
            detail=f"加载失败：{error}"
        )
    
    return {"success": True, "message": f"插件 {plugin_id} 已加载"}


@app.post("/api/plugins/{plugin_id}/unload")
async def unload_plugin(plugin_id: str):
    """卸载插件"""
    success = await plugin_manager.unload_plugin(plugin_id)
    
    if not success:
        raise HTTPException(
            status_code=500, 
            detail="卸载失败"
        )
    
    return {"success": True, "message": f"插件 {plugin_id} 已卸载"}


@app.post("/api/plugins/{plugin_id}/execute")
async def execute_plugin(plugin_id: str, input_data: Dict):
    """执行插件"""
    try:
        result = await plugin_manager.execute_plugin(plugin_id, input_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@app.get("/api/plugins/{plugin_id}/config")
async def get_plugin_config(plugin_id: str):
    """获取插件配置"""
    config = config_center.get_plugin_config(plugin_id)
    return {"plugin_id": plugin_id, "config": config}


@app.put("/api/plugins/{plugin_id}/config")
async def update_plugin_config(plugin_id: str, config: Dict):
    """更新插件配置"""
    config_center.save_plugin_config(plugin_id, config)
    return {"success": True, "plugin_id": plugin_id, "config": config}


# ========== 事件 API ==========

@app.get("/api/events")
async def get_events(limit: int = 50):
    """获取事件历史"""
    events = event_bus.get_history(limit=limit)
    return {"events": [e.to_dict() for e in events]}


# ========== 启动命令 ==========

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
