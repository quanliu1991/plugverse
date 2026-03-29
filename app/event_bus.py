"""
事件总线

提供插件间、插件与平台间的松耦合通信机制。
"""

import asyncio
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from loguru import logger


class EventPriority(str, Enum):
    """事件优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    """
    事件对象
    
    Attributes:
        name: 事件名称
        payload: 事件数据
        timestamp: 事件时间戳
        source: 事件来源（插件 ID 或模块名）
        priority: 事件优先级
        id: 事件唯一 ID
    """
    name: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    priority: EventPriority = EventPriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "priority": self.priority.value
        }


class EventBus:
    """
    事件总线
    
    支持：
    - 同步和异步订阅
    - 事件过滤
    - 一次性订阅
    - 事件历史（可选）
    """
    
    def __init__(self, max_history: int = 100):
        """
        初始化事件总线
        
        Args:
            max_history: 最大事件历史数量，0 表示不记录历史
        """
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []
        self._max_history = max_history
        self._lock = asyncio.Lock()
        
        logger.info("事件总线初始化完成")
    
    def subscribe(
        self, 
        event_name: str, 
        callback: Callable,
        once: bool = False
    ):
        """
        订阅事件
        
        Args:
            event_name: 事件名称，支持通配符 *
            callback: 回调函数，可以是同步或异步
            once: 是否只触发一次
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        # 包装回调以支持 once
        if once:
            original_callback = callback
            async def wrapper(event: Event):
                await self.unsubscribe(event_name, wrapper)
                if asyncio.iscoroutinefunction(original_callback):
                    await original_callback(event)
                else:
                    original_callback(event)
            callback = wrapper
        
        self._subscribers[event_name].append(callback)
        logger.debug(f"订阅事件：{event_name}, 当前订阅数：{len(self._subscribers[event_name])}")
    
    async def unsubscribe(self, event_name: str, callback: Callable):
        """
        取消订阅
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        if event_name in self._subscribers:
            if callback in self._subscribers[event_name]:
                self._subscribers[event_name].remove(callback)
                logger.debug(f"取消订阅：{event_name}")
    
    async def publish(self, event: Event):
        """
        发布事件
        
        Args:
            event: 事件对象
        """
        async with self._lock:
            # 记录历史
            if self._max_history > 0:
                self._history.append(event)
                if len(self._history) > self._max_history:
                    self._history.pop(0)
            
            # 收集所有匹配的订阅者
            callbacks = self._get_matching_subscribers(event.name)
        
        logger.debug(f"发布事件：{event.name}, 订阅者数量：{len(callbacks)}")
        
        # 并行执行所有回调
        tasks = []
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(event))
                else:
                    # 同步回调在线程池中执行
                    tasks.append(asyncio.get_event_loop().run_in_executor(
                        None, callback, event
                    ))
            except Exception as e:
                logger.error(f"执行回调失败：{e}")
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"事件回调异常：{result}")
    
    def _get_matching_subscribers(self, event_name: str) -> List[Callable]:
        """
        获取匹配事件名称的所有订阅者
        
        支持通配符匹配，如：
        - "plugin.*" 匹配所有 plugin 开头的事件
        - "*" 匹配所有事件
        """
        callbacks = []
        
        for pattern, subs in self._subscribers.items():
            if self._match_pattern(event_name, pattern):
                callbacks.extend(subs)
        
        return callbacks
    
    def _match_pattern(self, event_name: str, pattern: str) -> bool:
        """匹配事件名称和模式"""
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_name.startswith(prefix + ".")
        return event_name == pattern
    
    def get_history(
        self, 
        event_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Event]:
        """
        获取事件历史
        
        Args:
            event_name: 过滤事件名称
            limit: 最大返回数量
            
        Returns:
            List[Event]: 事件列表
        """
        history = self._history
        
        if event_name:
            history = [e for e in history if e.name == event_name]
        
        return history[-limit:]
    
    def clear_history(self):
        """清空事件历史"""
        self._history.clear()
        logger.info("事件历史已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取事件总线统计信息"""
        return {
            "total_subscribers": sum(len(subs) for subs in self._subscribers.values()),
            "event_types": len(self._subscribers),
            "history_size": len(self._history),
            "subscribers_by_event": {
                name: len(subs) for name, subs in self._subscribers.items()
            }
        }


# 预定义平台事件
class PlatformEvents:
    """平台预定义事件常量"""
    
    # 插件生命周期
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ERROR = "plugin.error"
    PLUGIN_CONFIG_UPDATED = "plugin.config_updated"
    
    # 任务
    TASK_CREATED = "task.created"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    
    # 用户
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_REGISTER = "user.register"
    
    # 文件
    FILE_UPLOADED = "file.uploaded"
    FILE_DELETED = "file.deleted"
    
    # 媒体
    MEDIA_UPLOADED = "media.uploaded"
    MEDIA_PROCESSING = "media.processing"
    MEDIA_PROCESSED = "media.processed"
    MEDIA_FAILED = "media.failed"
