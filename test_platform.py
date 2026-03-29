#!/usr/bin/env python3
"""
PlugVerse 平台测试脚本

测试核心功能：
1. 插件管理器
2. 事件总线
3. 配置中心
4. 权限管理
5. Hello World 插件
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.plugin_base import PluginMetadata, PluginType, PluginContext
from app.event_bus import EventBus, Event, PlatformEvents
from app.config_center import ConfigCenter
from app.permission_manager import PermissionManager, Permission


def test_event_bus():
    """测试事件总线"""
    print("\n📡 测试事件总线...")
    
    event_bus = EventBus()
    
    # 测试订阅
    received_events = []
    
    async def handler(event: Event):
        received_events.append(event)
    
    event_bus.subscribe("test.event", handler)
    
    # 测试发布
    asyncio.get_event_loop().run_until_complete(
        event_bus.publish(Event(
            name="test.event",
            payload={"message": "Hello"},
            source="test"
        ))
    )
    
    assert len(received_events) == 1, "事件未接收到"
    assert received_events[0].payload["message"] == "Hello"
    
    print("  ✅ 事件订阅/发布正常")
    print(f"  📊 统计：{event_bus.get_stats()}")
    return True


def test_config_center():
    """测试配置中心"""
    print("\n⚙️  测试配置中心...")
    
    config_center = ConfigCenter(config_dir="./config")
    
    # 测试读取平台配置
    app_name = config_center.get("app.name", "Unknown")
    print(f"  ✅ 平台名称：{app_name}")
    
    # 测试插件配置
    config_center.save_plugin_config("test-plugin", {"key": "value"})
    config = config_center.get_plugin_config("test-plugin")
    assert config["key"] == "value"
    print("  ✅ 插件配置保存/读取正常")
    
    print(f"  📊 统计：{config_center.get_stats()}")
    return True


def test_permission_manager():
    """测试权限管理"""
    print("\n🔐 测试权限管理...")
    
    pm = PermissionManager()
    
    # 授予权限
    pm.grant_permissions(
        "test-plugin",
        ["storage.read", "storage.write"]
    )
    
    # 检查权限
    assert pm.check_permissions("test-plugin", ["storage.read"])
    assert not pm.check_permissions("test-plugin", ["admin.access"])
    print("  ✅ 权限授予/检查正常")
    
    # 撤销权限
    pm.revoke_permissions("test-plugin")
    assert not pm.check_permissions("test-plugin", ["storage.read"])
    print("  ✅ 权限撤销正常")
    
    print(f"  📊 统计：{pm.get_stats()}")
    return True


async def test_hello_world_plugin():
    """测试 Hello World 插件"""
    print("\n👋 测试 Hello World 插件...")
    
    from app.plugin_manager import PluginManager
    from app.main import PlugVerseApp, LoggerService, StorageService
    
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
    plugins = await plugin_manager.discover_plugins()
    print(f"  📦 发现插件：{len(plugins)} 个")
    
    # 加载插件
    success = await plugin_manager.load_plugin("hello-world")
    if success:
        print("  ✅ 插件加载成功")
    else:
        error = plugin_manager.get_error("hello-world")
        print(f"  ⚠️  插件加载失败：{error}")
        return False
    
    # 执行插件
    result = await plugin_manager.execute_plugin(
        "hello-world",
        {"name": "PlugVerse"}
    )
    
    assert result["success"] == True
    assert "Hello" in result["message"]
    print(f"  ✅ 插件执行成功：{result['message']}")
    
    # 获取状态
    status = plugin_manager.get_status("hello-world")
    print(f"  📊 插件状态：{status.value}")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 PlugVerse 平台测试套件")
    print("=" * 60)
    
    tests = [
        ("事件总线", test_event_bus),
        ("配置中心", test_config_center),
        ("权限管理", test_permission_manager),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"  ❌ 测试失败：{e}")
    
    # 异步测试
    print("\n" + "=" * 60)
    try:
        result = asyncio.get_event_loop().run_until_complete(
            test_hello_world_plugin()
        )
        results.append(("Hello World 插件", result, None))
    except Exception as e:
        results.append(("Hello World 插件", False, str(e)))
        print(f"  ❌ 测试失败：{e}")
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for name, result, error in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if error:
            print(f"   错误：{error}")
    
    print("=" * 60)
    print(f"总计：{passed}/{total} 通过")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
