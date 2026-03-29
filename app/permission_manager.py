"""
权限管理器

管理插件的权限授予、检查和审计。
"""

from enum import Enum
from typing import Dict, List, Set, Optional
from datetime import datetime
from dataclasses import dataclass, field

from loguru import logger


class Permission(str, Enum):
    """
    权限定义
    
    权限命名规范：资源。操作
    """
    
    # 存储相关
    STORAGE_READ = "storage.read"
    STORAGE_WRITE = "storage.write"
    STORAGE_DELETE = "storage.delete"
    
    # 媒体处理
    MEDIA_PROCESS = "media.process"
    MEDIA_UPLOAD = "media.upload"
    MEDIA_DOWNLOAD = "media.download"
    
    # 网络访问
    NETWORK_ACCESS = "network.access"
    NETWORK_EXTERNAL = "network.external"
    
    # 用户数据
    USER_DATA_READ = "user.data.read"
    USER_DATA_WRITE = "user.data.write"
    
    # 支付相关
    PAYMENT_ACCESS = "payment.access"
    PAYMENT_PROCESS = "payment.process"
    
    # 通知
    EMAIL_SEND = "email.send"
    NOTIFICATION_SEND = "notification.send"
    
    # 文件
    FILE_UPLOAD = "file.upload"
    FILE_DOWNLOAD = "file.download"
    
    # 管理
    ADMIN_ACCESS = "admin.access"
    PLUGIN_MANAGE = "plugin.manage"
    CONFIG_MANAGE = "config.manage"
    
    # 任务
    TASK_CREATE = "task.create"
    TASK_CANCEL = "task.cancel"


@dataclass
class PermissionGrant:
    """权限授予记录"""
    plugin_id: str
    permissions: Set[Permission]
    granted_at: datetime = field(default_factory=datetime.now)
    granted_by: str = "system"
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def has_permission(self, permission: Permission) -> bool:
        """检查是否有指定权限"""
        return permission in self.permissions and not self.is_expired()


class PermissionManager:
    """
    权限管理器
    
    功能：
    - 权限授予
    - 权限检查
    - 权限撤销
    - 权限审计日志
    """
    
    def __init__(self):
        """初始化权限管理器"""
        self._grants: Dict[str, PermissionGrant] = {}
        self._audit_log: List[Dict] = []
        self._max_audit_log = 1000
        
        logger.info("权限管理器初始化完成")
    
    def grant_permissions(
        self,
        plugin_id: str,
        permissions: List[str],
        granted_by: str = "system",
        expires_at: Optional[datetime] = None
    ) -> bool:
        """
        授予插件权限
        
        Args:
            plugin_id: 插件 ID
            permissions: 权限列表
            granted_by: 授权人
            expires_at: 过期时间
            
        Returns:
            bool: 是否成功
        """
        try:
            # 转换字符串为 Permission 枚举
            perm_set = set()
            for p in permissions:
                try:
                    perm_set.add(Permission(p))
                except ValueError:
                    logger.warning(f"未知权限：{p}")
            
            grant = PermissionGrant(
                plugin_id=plugin_id,
                permissions=perm_set,
                granted_by=granted_by,
                expires_at=expires_at
            )
            
            self._grants[plugin_id] = grant
            
            self._log_audit(
                action="grant",
                plugin_id=plugin_id,
                permissions=[p.value for p in perm_set],
                granted_by=granted_by
            )
            
            logger.info(f"已授予插件权限：{plugin_id}, 权限数：{len(perm_set)}")
            return True
            
        except Exception as e:
            logger.error(f"授予权限失败：{e}")
            return False
    
    def check_permissions(
        self, 
        plugin_id: str, 
        required: List[str]
    ) -> bool:
        """
        检查插件是否有足够权限
        
        Args:
            plugin_id: 插件 ID
            required: 所需权限列表
            
        Returns:
            bool: 是否有足够权限
        """
        if plugin_id not in self._grants:
            logger.warning(f"插件未授权：{plugin_id}")
            return False
        
        grant = self._grants[plugin_id]
        
        if grant.is_expired():
            logger.warning(f"插件权限已过期：{plugin_id}")
            return False
        
        # 检查所有所需权限
        for perm_str in required:
            try:
                perm = Permission(perm_str)
                if not grant.has_permission(perm):
                    logger.warning(
                        f"插件缺少权限：{plugin_id}, 需要：{perm_str}"
                    )
                    return False
            except ValueError:
                logger.warning(f"未知权限：{perm_str}")
                return False
        
        return True
    
    def check_permission(
        self, 
        plugin_id: str, 
        permission: str
    ) -> bool:
        """
        检查单个权限
        
        Args:
            plugin_id: 插件 ID
            permission: 权限名称
            
        Returns:
            bool: 是否有权限
        """
        return self.check_permissions(plugin_id, [permission])
    
    def revoke_permissions(self, plugin_id: str) -> bool:
        """
        撤销插件所有权限
        
        Args:
            plugin_id: 插件 ID
            
        Returns:
            bool: 是否成功
        """
        if plugin_id in self._grants:
            del self._grants[plugin_id]
            
            self._log_audit(
                action="revoke",
                plugin_id=plugin_id,
                permissions=["all"]
            )
            
            logger.info(f"已撤销插件权限：{plugin_id}")
            return True
        
        return False
    
    def get_permissions(self, plugin_id: str) -> List[str]:
        """
        获取插件的所有权限
        
        Args:
            plugin_id: 插件 ID
            
        Returns:
            权限列表
        """
        if plugin_id not in self._grants:
            return []
        
        grant = self._grants[plugin_id]
        if grant.is_expired():
            return []
        
        return [p.value for p in grant.permissions]
    
    def _log_audit(
        self,
        action: str,
        plugin_id: str,
        permissions: List[str],
        granted_by: str = "system"
    ):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "plugin_id": plugin_id,
            "permissions": permissions,
            "granted_by": granted_by
        }
        
        self._audit_log.append(log_entry)
        
        # 限制日志数量
        if len(self._audit_log) > self._max_audit_log:
            self._audit_log.pop(0)
    
    def get_audit_log(
        self,
        plugin_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        获取审计日志
        
        Args:
            plugin_id: 过滤插件 ID
            limit: 最大返回数量
            
        Returns:
            审计日志列表
        """
        logs = self._audit_log
        
        if plugin_id:
            logs = [l for l in logs if l["plugin_id"] == plugin_id]
        
        return logs[-limit:]
    
    def get_stats(self) -> Dict[str, any]:
        """获取权限管理器统计信息"""
        active_grants = sum(
            1 for g in self._grants.values() if not g.is_expired()
        )
        
        return {
            "total_plugins": len(self._grants),
            "active_grants": active_grants,
            "audit_log_size": len(self._audit_log),
            "permissions_defined": len(Permission)
        }
