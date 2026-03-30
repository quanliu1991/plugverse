#!/usr/bin/env python3
"""
测试 media-transcribe 插件
"""

import asyncio
import sys
sys.path.insert(0, '/Users/macstudio/.openclaw/workspace/plugverse')

from app.plugin_manager import PluginManager
from app.config_center import ConfigCenter
from app.event_bus import EventBus
from app.permission_manager import PermissionManager

async def test_transcribe():
    # 创建测试环境
    config_center = ConfigCenter()
    event_bus = EventBus()
    permission_manager = PermissionManager()
    
    class DummyApp:
        def get_service(self, name):
            return None
    
    plugin_manager = PluginManager(
        app_instance=DummyApp(),
        event_bus=event_bus,
        config_center=config_center,
        permission_manager=permission_manager
    )
    
    # 加载插件
    print("加载 media-transcribe 插件...")
    await plugin_manager.load_plugin('media-transcribe')
    
    # 测试转写（需要一个真实的音频文件）
    print("\n插件已加载，可以执行转写")
    print("使用方法：访问 https://succinic-chronic-kyla.ngrok-free.dev/transcribe")
    print("\n或者用 curl 测试:")
    print("curl -X POST http://localhost:9000/api/plugins/media-transcribe/execute \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"file_path\": \"/path/to/your/audio.mp3\", \"model_size\": \"tiny\", \"language\": \"zh\"}'")

if __name__ == '__main__':
    asyncio.run(test_transcribe())
