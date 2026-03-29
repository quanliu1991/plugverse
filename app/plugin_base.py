"""
插件基类接口定义

所有插件必须继承 IPlugin 基类并实现其抽象方法。
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class PluginType(str, Enum):
    """插件类型枚举"""
    
    MEDIA_PROCESS = "media_process"      # 音视频处理
    IMAGE_PROCESS = "image_process"      # 图片处理
    DATA_EXPORT = "data_export"          # 数据导出
    AI_ASSISTANT = "ai_assistant"        # AI 助手
    INTEGRATION = "integration"          # 第三方集成
    CUSTOM = "custom"                    # 自定义


class PluginStatus(str, Enum):
    """插件状态枚举"""
    
    ACTIVE = "active"       # 已激活
    INACTIVE = "inactive"   # 未激活
    ERROR = "error"         # 错误状态
    LOADING = "loading"     # 加载中
    UPDATING = "updating"   # 更新中


class PluginMetadata(BaseModel):
    """
    插件元数据
    
    定义在 manifest.json 中，描述插件的基本信息。
    """
    
    id: str                                   # 插件唯一标识
    name: str                                 # 插件名称
    version: str                              # 版本号
    description: str                          # 描述
    author: str                               # 作者
    type: PluginType                          # 插件类型
    icon: Optional[str] = None                # 图标（emoji 或 URL）
    website: Optional[str] = None             # 官网
    license: Optional[str] = "MIT"            # 开源协议
    requirements: Dict[str, str] = {}         # Python 依赖
    permissions: List[str] = []               # 所需权限
    config_schema: Dict[str, Any] = {}        # 配置 JSON Schema
    min_platform_version: Optional[str] = None  # 最低平台版本
    
    class Config:
        use_enum_values = True


class PluginContext:
    """
    插件上下文
    
    提供插件访问平台核心服务的接口。
    插件不应直接访问平台内部模块，而应通过上下文进行操作。
    """
    
    def __init__(self, app_instance: Any = None):
        self._app = app_instance
        self._event_bus = None
        self._config_center = None
        self._permission_manager = None
        self._storage = None
        self._logger = None
    
    @property
    def app(self) -> Any:
        """获取平台应用实例"""
        return self._app
    
    @property
    def event_bus(self) -> Any:
        """获取事件总线"""
        if self._event_bus is None and self._app:
            self._event_bus = self._app.event_bus
        return self._event_bus
    
    @property
    def config_center(self) -> Any:
        """获取配置中心"""
        if self._config_center is None and self._app:
            self._config_center = self._app.config_center
        return self._config_center
    
    @property
    def permission_manager(self) -> Any:
        """获取权限管理器"""
        if self._permission_manager is None and self._app:
            self._permission_manager = self._app.permission_manager
        return self._permission_manager
    
    @property
    def storage(self) -> Any:
        """获取存储服务"""
        if self._storage is None and self._app:
            self._storage = self._app.get_service("storage")
        return self._storage
    
    @property
    def logger(self) -> Any:
        """获取日志服务"""
        if self._logger is None and self._app:
            self._logger = self._app.get_service("logger")
        return self._logger
    
    def get_service(self, service_name: str) -> Any:
        """获取指定名称的平台服务"""
        if self._app:
            return self._app.get_service(service_name)
        return None


class IPlugin(ABC):
    """
    插件基类接口
    
    所有插件必须继承此类并实现所有抽象方法。
    
    插件生命周期：
    1. 实例化：Plugin()
    2. 初始化：initialize(context)
    3. 执行：execute(input_data) - 可多次调用
    4. 关闭：shutdown()
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        返回插件元数据
        
        Returns:
            PluginMetadata: 插件元数据对象
        """
        pass
    
    @abstractmethod
    async def initialize(self, context: PluginContext) -> bool:
        """
        初始化插件
        
        在插件加载时调用，用于：
        - 保存上下文引用
        - 加载配置
        - 初始化资源（如模型、连接等）
        - 注册事件监听
        
        Args:
            context: 插件上下文
            
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行插件功能
        
        插件的主要功能实现。可以多次调用。
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            dict: 执行结果字典，应包含 success 字段
            
        Raises:
            ValueError: 输入数据无效
            PermissionError: 权限不足
            Exception: 其他执行错误
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """
        关闭插件
        
        在插件卸载时调用，用于：
        - 释放资源
        - 保存状态
        - 关闭连接
        
        Returns:
            bool: 关闭是否成功
        """
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取插件配置
        
        Returns:
            dict: 配置字典
        """
        return {}
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        更新插件配置
        
        Args:
            config: 新配置字典
            
        Returns:
            bool: 更新是否成功
        """
        return False
    
    def get_health(self) -> Dict[str, Any]:
        """
        获取插件健康状态
        
        Returns:
            dict: 健康状态信息
        """
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
