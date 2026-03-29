"""
插件管理器

负责插件的发现、加载、卸载、执行和生命周期管理。
"""

import importlib
import importlib.util
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from loguru import logger

from .plugin_base import (
    IPlugin, 
    PluginMetadata, 
    PluginStatus, 
    PluginContext,
    PluginType
)
from .event_bus import EventBus, Event, PlatformEvents
from .config_center import ConfigCenter
from .permission_manager import PermissionManager


class PluginManager:
    """
    插件管理器
    
    功能：
    - 插件发现（扫描插件目录）
    - 插件加载（动态导入）
    - 插件卸载（清理资源）
    - 插件执行（调用 execute）
    - 状态管理
    """
    
    def __init__(
        self,
        app_instance: Any,
        event_bus: EventBus,
        config_center: ConfigCenter,
        permission_manager: PermissionManager,
        plugins_dir: str = "./plugins"
    ):
        """
        初始化插件管理器
        
        Args:
            app_instance: 平台应用实例
            event_bus: 事件总线
            config_center: 配置中心
            permission_manager: 权限管理器
            plugins_dir: 插件目录路径
        """
        self._app = app_instance
        self._event_bus = event_bus
        self._config_center = config_center
        self._permission_manager = permission_manager
        self._plugins_dir = Path(plugins_dir)
        
        # 确保插件目录存在
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # 插件存储
        self._plugins: Dict[str, IPlugin] = {}
        self._statuses: Dict[str, PluginStatus] = {}
        self._metadatas: Dict[str, PluginMetadata] = {}
        self._errors: Dict[str, str] = {}
        
        # 创建插件上下文
        self._context = PluginContext(app_instance)
        
        logger.info(f"插件管理器初始化完成，插件目录：{self._plugins_dir}")
    
    async def discover_plugins(self) -> List[PluginMetadata]:
        """
        扫描并发现可用的插件
        
        Returns:
            插件元数据列表
        """
        available = []
        
        for item in self._plugins_dir.iterdir():
            if not item.is_dir():
                continue
            
            manifest_path = item / "manifest.json"
            if not manifest_path.exists():
                logger.debug(f"跳过（无 manifest.json）: {item.name}")
                continue
            
            try:
                metadata = await self._load_manifest(manifest_path)
                available.append(metadata)
                logger.info(f"发现插件：{metadata.id} v{metadata.version}")
            except Exception as e:
                logger.error(f"加载 manifest 失败 {item.name}: {e}")
        
        return available
    
    async def _load_manifest(self, manifest_path: Path) -> PluginMetadata:
        """加载插件 manifest 文件"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return PluginMetadata(**data)
    
    async def load_plugin(self, plugin_id: str) -> bool:
        """
        加载单个插件
        
        Args:
            plugin_id: 插件 ID（目录名）
            
        Returns:
            bool: 加载是否成功
        """
        plugin_dir = self._plugins_dir / plugin_id
        
        if not plugin_dir.exists():
            logger.error(f"插件目录不存在：{plugin_id}")
            return False
        
        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            logger.error(f"插件 manifest 不存在：{plugin_id}")
            return False
        
        try:
            # 设置状态为加载中
            self._statuses[plugin_id] = PluginStatus.LOADING
            
            # 加载 manifest
            metadata = await self._load_manifest(manifest_path)
            self._metadatas[plugin_id] = metadata
            
            # 检查依赖
            if not await self._check_dependencies(metadata):
                raise RuntimeError("依赖检查失败")
            
            # 动态导入插件模块
            main_path = plugin_dir / "main.py"
            if not main_path.exists():
                raise FileNotFoundError("main.py 不存在")
            
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_id}.main",
                main_path
            )
            
            if spec is None or spec.loader is None:
                raise ImportError("无法创建模块 spec")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 实例化插件
            if not hasattr(module, "Plugin"):
                raise AttributeError("main.py 中未找到 Plugin 类")
            
            plugin_class = getattr(module, "Plugin")
            plugin = plugin_class()
            
            # 初始化插件
            success = await asyncio.wait_for(
                plugin.initialize(self._context),
                timeout=30.0  # 30 秒超时
            )
            
            if not success:
                raise RuntimeError("插件初始化失败")
            
            # 注册插件
            self._plugins[plugin_id] = plugin
            self._statuses[plugin_id] = PluginStatus.ACTIVE
            
            # 授予 manifest 中声明的权限
            if metadata.permissions:
                self._permission_manager.grant_permissions(
                    plugin_id,
                    metadata.permissions
                )
            
            # 发布事件
            await self._event_bus.publish(Event(
                name=PlatformEvents.PLUGIN_LOADED,
                payload={"plugin_id": plugin_id, "version": metadata.version},
                source="plugin_manager"
            ))
            
            logger.info(f"插件加载成功：{plugin_id}")
            return True
            
        except asyncio.TimeoutError:
            self._handle_load_error(plugin_id, "初始化超时（30 秒）")
            return False
        except Exception as e:
            self._handle_load_error(plugin_id, str(e))
            return False
    
    def _handle_load_error(self, plugin_id: str, error_msg: str):
        """处理插件加载错误"""
        self._statuses[plugin_id] = PluginStatus.ERROR
        self._errors[plugin_id] = error_msg
        
        logger.error(f"插件加载失败：{plugin_id}, 错误：{error_msg}")
        
        # 发布错误事件
        asyncio.create_task(self._event_bus.publish(Event(
            name=PlatformEvents.PLUGIN_ERROR,
            payload={
                "plugin_id": plugin_id,
                "error": error_msg
            },
            source="plugin_manager"
        )))
    
    async def _check_dependencies(self, metadata: PluginMetadata) -> bool:
        """检查插件依赖"""
        if not metadata.requirements:
            return True
        
        missing = []
        
        for package, version_spec in metadata.requirements.items():
            try:
                # 简化检查，实际应该用 pkg_resources
                __import__(package.replace("-", "_"))
            except ImportError:
                missing.append(f"{package} {version_spec}")
        
        if missing:
            logger.warning(f"插件 {metadata.id} 缺少依赖：{missing}")
            # 不阻止加载，仅警告
        
        return True
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_id: 插件 ID
            
        Returns:
            bool: 卸载是否成功
        """
        if plugin_id not in self._plugins:
            logger.warning(f"插件未加载：{plugin_id}")
            return False
        
        try:
            plugin = self._plugins[plugin_id]
            
            # 调用插件的 shutdown
            success = await plugin.shutdown()
            
            if success:
                # 撤销权限
                self._permission_manager.revoke_permissions(plugin_id)
                
                # 移除插件
                del self._plugins[plugin_id]
                self._statuses[plugin_id] = PluginStatus.INACTIVE
                
                if plugin_id in self._errors:
                    del self._errors[plugin_id]
                
                # 发布事件
                await self._event_bus.publish(Event(
                    name=PlatformEvents.PLUGIN_UNLOADED,
                    payload={"plugin_id": plugin_id},
                    source="plugin_manager"
                ))
                
                logger.info(f"插件卸载成功：{plugin_id}")
                return True
            else:
                logger.error(f"插件 shutdown 失败：{plugin_id}")
                return False
                
        except Exception as e:
            logger.error(f"插件卸载异常：{plugin_id}, {e}")
            return False
    
    async def execute_plugin(
        self,
        plugin_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行插件功能
        
        Args:
            plugin_id: 插件 ID
            input_data: 输入数据
            
        Returns:
            执行结果
            
        Raises:
            ValueError: 插件未找到
            PermissionError: 权限不足
        """
        if plugin_id not in self._plugins:
            raise ValueError(f"插件未加载：{plugin_id}")
        
        plugin = self._plugins[plugin_id]
        metadata = self._metadatas.get(plugin_id)
        
        # 权限检查
        if metadata and metadata.permissions:
            if not self._permission_manager.check_permissions(
                plugin_id,
                metadata.permissions
            ):
                raise PermissionError(f"插件权限不足：{plugin_id}")
        
        # 执行插件
        try:
            result = await plugin.execute(input_data)
            return result
        except Exception as e:
            logger.error(f"插件执行失败：{plugin_id}, {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_plugin(self, plugin_id: str) -> Optional[IPlugin]:
        """获取插件实例"""
        return self._plugins.get(plugin_id)
    
    def get_status(self, plugin_id: str) -> Optional[PluginStatus]:
        """获取插件状态"""
        return self._statuses.get(plugin_id)
    
    def get_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """获取插件元数据"""
        return self._metadatas.get(plugin_id)
    
    def get_error(self, plugin_id: str) -> Optional[str]:
        """获取插件错误信息"""
        return self._errors.get(plugin_id)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        列出所有插件
        
        Returns:
            插件信息列表
        """
        result = []
        
        for plugin_id in self._plugins:
            info = {
                "id": plugin_id,
                "status": self._statuses[plugin_id].value,
                "metadata": self._metadatas.get(plugin_id),
                "error": self._errors.get(plugin_id)
            }
            result.append(info)
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """获取插件管理器统计信息"""
        status_counts = {}
        for status in self._statuses.values():
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
        
        return {
            "total_plugins": len(self._plugins),
            "status_counts": status_counts,
            "error_count": len(self._errors),
            "plugins_dir": str(self._plugins_dir.absolute())
        }
