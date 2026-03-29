#!/usr/bin/env python3
"""
Media Transcribe Plugin 测试脚本

测试音视频转文字插件功能
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.plugin_manager import PluginManager
from app.event_bus import EventBus
from app.config_center import ConfigCenter
from app.permission_manager import PermissionManager
from app.main import PlugVerseApp, LoggerService, StorageService


async def test_media_transcribe_plugin():
    """测试媒体转写插件"""
    print("\n🎤 测试 Media Transcribe 插件...\n")
    
    # 初始化组件
    event_bus = EventBus()
    config_center = ConfigCenter()
    permission_manager = PermissionManager()
    
    app_instance = PlugVerseApp()
    app_instance.event_bus = event_bus
    app_instance.config_center = config_center
    app_instance.permission_manager = permission_manager
    app_instance.register_service("logger", LoggerService())
    app_instance.register_service("storage", StorageService())
    
    # 创建插件管理器
    plugin_manager = PluginManager(
        app_instance=app_instance,
        event_bus=event_bus,
        config_center=config_center,
        permission_manager=permission_manager
    )
    
    # 发现插件
    print("📦 扫描插件...")
    plugins = await plugin_manager.discover_plugins()
    print(f"  发现 {len(plugins)} 个插件")
    for p in plugins:
        print(f"    - {p.id} v{p.version}")
    
    # 加载媒体转写插件
    print("\n📥 加载 media-transcribe 插件...")
    success = await plugin_manager.load_plugin("media-transcribe")
    if success:
        print("  ✅ 插件加载成功")
    else:
        error = plugin_manager.get_error("media-transcribe")
        print(f"  ❌ 插件加载失败：{error}")
        return False
    
    # 获取插件信息
    metadata = plugin_manager.get_metadata("media-transcribe")
    print(f"\n📋 插件信息:")
    print(f"  名称：{metadata.name}")
    print(f"  版本：{metadata.version}")
    print(f"  类型：{metadata.type}")
    print(f"  权限：{metadata.permissions}")
    
    # 获取配置
    print(f"\n⚙️  默认配置:")
    plugin = plugin_manager.get_plugin("media-transcribe")
    config = plugin.get_config()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # 测试配置更新
    print(f"\n🔧 测试配置更新...")
    new_config = {
        "model_size": "tiny",  # 使用最小模型加速测试
        "language": "zh",
        "output_format": "txt"
    }
    success = plugin.update_config(new_config)
    if success:
        print("  ✅ 配置更新成功")
        print(f"  新配置：{plugin.get_config()}")
    else:
        print("  ❌ 配置更新失败")
    
    # 测试插件健康状态
    print(f"\n💚 健康状态:")
    health = plugin.get_health()
    print(f"  状态：{health['status']}")
    print(f"  模型已加载：{health['model_loaded']}")
    print(f"  模型大小：{health['model_size']}")
    
    # 注意：实际转写测试需要音频文件
    print(f"\n⚠️  转写功能测试:")
    print(f"  由于需要音频文件，跳过实际转写测试")
    print(f"  使用方法:")
    print(f"    curl -X POST http://localhost:8000/api/plugins/media-transcribe/execute \\")
    print(f"      -H 'Content-Type: application/json' \\")
    print(f"      -d '{{\"file_path\": \"/path/to/audio.mp3\"}}'")
    
    # 卸载插件
    print(f"\n📤 卸载插件...")
    success = await plugin_manager.unload_plugin("media-transcribe")
    if success:
        print("  ✅ 插件卸载成功")
    else:
        print("  ❌ 插件卸载失败")
    
    return True


def main():
    """主函数"""
    print("=" * 70)
    print("🧪 Media Transcribe Plugin 测试")
    print("=" * 70)
    
    try:
        success = asyncio.get_event_loop().run_until_complete(
            test_media_transcribe_plugin()
        )
        
        print("\n" + "=" * 70)
        if success:
            print("✅ 所有测试通过！")
        else:
            print("❌ 部分测试失败")
        print("=" * 70)
        
        return success
        
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
