"""
PlugVerse 主应用入口

FastAPI 应用初始化和路由注册。
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
from datetime import datetime
import shutil
import uuid
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
        # 这些会在初始化后设置
        self.event_bus = None
        self.config_center = None
        self.permission_manager = None
    
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
    app_instance.event_bus = event_bus
    app_instance.config_center = config_center
    app_instance.permission_manager = permission_manager
    app_instance.register_service("logger", LoggerService())
    app_instance.register_service("storage", StorageService())
    
    plugin_manager = PluginManager(
        app_instance=app_instance,
        event_bus=event_bus,
        config_center=config_center,
        permission_manager=permission_manager
    )
    
    # 自动加载已安装的插件
    await load_installed_plugins(plugin_manager)
    
    logger.info("✅ PlugVerse 启动完成")
    
    yield
    
    # 关闭时
    logger.info("👋 PlugVerse 关闭中...")
    await unload_all_plugins(plugin_manager)
    logger.info("✅ PlugVerse 已关闭")


async def load_installed_plugins(pm: PluginManager):
    """加载所有已安装的插件"""
    discovered = await pm.discover_plugins()
    
    for metadata in discovered:
        logger.info(f"加载插件：{metadata.id}")
        await pm.load_plugin(metadata.id)


async def unload_all_plugins(pm: PluginManager):
    """卸载所有插件"""
    for plugin_id in list(pm._plugins.keys()):
        logger.info(f"卸载插件：{plugin_id}")
        await pm.unload_plugin(plugin_id)


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

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """健康检查"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "0.3.0"
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
    plugins = plugin_manager.list_plugins()
    return {"plugins": plugins}


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


# ========== 文件管理 API ==========

@app.get("/api/files")
async def list_files():
    """获取文件列表"""
    import os
    upload_dir = Path("./output/uploads")
    if not upload_dir.exists():
        return {"files": []}
    
    files = []
    for f in upload_dir.iterdir():
        if f.is_file():
            files.append({
                "id": f.stem,
                "name": f.name,
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_ctime).isoformat()
            })
    return {"files": files}

@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """获取文件信息"""
    upload_dir = Path("./output/uploads")
    file_path = upload_dir / file_id
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return {
        "id": file_id,
        "name": file_path.name,
        "size": file_path.stat().st_size,
        "path": str(file_path.absolute())
    }

@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str):
    """下载文件"""
    upload_dir = Path("./output/uploads")
    file_path = upload_dir / file_id
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(str(file_path))

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """删除文件"""
    upload_dir = Path("./output/uploads")
    file_path = upload_dir / file_id
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_path.unlink()
    return {"success": True, "message": "文件已删除"}


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        # 创建上传目录
        upload_dir = Path("./output/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())[:8]
        file_ext = Path(file.filename).suffix
        safe_filename = f"{file_id}{file_ext}"
        file_path = upload_dir / safe_filename
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "success": True,
            "file_path": str(file_path.absolute()),
            "filename": file.filename,
            "size": file.size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")


# ========== 任务管理 API ==========

# 内存中的任务存储（简化版）
_tasks_store: Dict[str, dict] = {}

@app.get("/api/tasks")
async def list_tasks():
    """获取任务列表"""
    return {"tasks": list(_tasks_store.values())}

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    if task_id not in _tasks_store:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _tasks_store[task_id]

@app.post("/api/tasks")
async def create_task(task_data: dict):
    """创建任务"""
    import uuid
    from datetime import datetime
    task_id = str(uuid.uuid4())[:8]
    task = {
        "id": task_id,
        "name": task_data.get("name", "Unnamed Task"),
        "plugin": task_data.get("plugin", ""),
        "status": "pending",
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "result": None
    }
    _tasks_store[task_id] = task
    return task

@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    """取消任务"""
    if task_id not in _tasks_store:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    _tasks_store[task_id]["status"] = "cancelled"
    return {"success": True, "message": "任务已取消"}

@app.get("/api/tasks/{task_id}/result")
async def get_task_result(task_id: str):
    """获取任务结果"""
    if task_id not in _tasks_store:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _tasks_store[task_id].get("result")


# ========== 静态文件服务 ==========

# 前端构建目录
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"

def _frontend_missing_html() -> str:
    """未构建 frontend/dist 时的说明页（dist 在 .gitignore 中，需本地 npm run build）。"""
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><title>PlugVerse</title></head>
<body style="font-family:system-ui,sans-serif;max-width:42rem;margin:2rem;line-height:1.6">
<h1>PlugVerse — 前端未构建</h1>
<p>后端从 <code>frontend/dist/</code> 提供页面，该目录由 Vite 生成，不在仓库中。</p>
<p>请在项目根目录执行：</p>
<pre style="background:#f4f4f5;padding:1rem;border-radius:8px">cd frontend
npm ci
npm run build</pre>
<p>然后重启服务，再访问本页。开发调试可另开终端：<code>cd frontend && npm run dev</code>（默认 <a href="http://localhost:3000">localhost:3000</a>，已代理 /api 到后端）。</p>
<p>API 文档：<a href="/docs">/docs</a></p>
</body></html>"""


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """提供前端首页"""
    frontend_index = frontend_path / "index.html"
    if frontend_index.exists():
        with open(frontend_index, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(_frontend_missing_html())

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_static_or_spa(full_path: str):
    """提供静态文件或 SPA 路由"""
    # 跳过 API 路径
    if full_path.startswith("api/") or full_path.startswith("docs"):
        return
    
    # 尝试返回静态文件
    file_path = frontend_path / full_path
    if file_path.exists() and file_path.is_file():
        from fastapi.responses import FileResponse
        return FileResponse(str(file_path))
    
    # 否则返回 index.html（SPA 路由）
    frontend_index = frontend_path / "index.html"
    if frontend_index.exists():
        with open(frontend_index, "r", encoding="utf-8") as f:
            return f.read()
    
    return HTMLResponse("<h1>404 - Not Found</h1>", status_code=404)


# ========== 启动命令 ==========

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
