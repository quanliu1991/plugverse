"""
Hello World 示例插件

这是一个简单的示例插件，展示如何开发 PlugVerse 插件。
"""

from datetime import datetime
from typing import Any, Dict

from app.plugin_base import (
    IPlugin, 
    PluginMetadata, 
    PluginType, 
    PluginContext
)


class Plugin(IPlugin):
    """Hello World 插件实现"""
    
    def __init__(self):
        self._context: PluginContext = None
        self._config = {
            "greeting": "Hello",
            "show_timestamp": True
        }
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="hello-world",
            name="Hello World",
            version="1.0.0",
            description="一个示例插件，用于演示插件开发",
            author="PlugVerse Team",
            type=PluginType.CUSTOM,
            icon="👋",
            website="https://github.com/your-org/plugverse",
            license="MIT",
            requirements={},
            permissions=[],
            config_schema={
                "type": "object",
                "properties": {
                    "greeting": {
                        "type": "string",
                        "default": "Hello"
                    },
                    "show_timestamp": {
                        "type": "boolean",
                        "default": True
                    }
                }
            }
        )
    
    async def initialize(self, context: PluginContext) -> bool:
        """初始化插件"""
        self._context = context
        
        # 加载配置
        saved_config = self._context.config_center.get_plugin_config("hello-world")
        if saved_config:
            self._config.update(saved_config)
        
        self._context.logger.info("Hello World 插件已初始化")
        return True
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行插件功能
        
        输入数据:
        - name: 要问候的名字（可选）
        
        返回:
        - message: 问候消息
        - timestamp: 时间戳（如果启用）
        """
        name = input_data.get("name", "World")
        greeting = self._config.get("greeting", "Hello")
        
        result = {
            "success": True,
            "message": f"{greeting}, {name}!",
        }
        
        if self._config.get("show_timestamp", True):
            result["timestamp"] = datetime.now().isoformat()
        
        # 发布一个事件
        await self._context.event_bus.publish({
            "name": "plugin.hello_world.executed",
            "payload": {"name": name},
            "source": "hello-world"
        })
        
        return result
    
    async def shutdown(self) -> bool:
        """关闭插件"""
        self._context.logger.info("Hello World 插件已关闭")
        return True
    
    def get_config(self) -> Dict[str, Any]:
        return self._config
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        self._config.update(config)
        self._context.config_center.save_plugin_config("hello-world", self._config)
        return True
