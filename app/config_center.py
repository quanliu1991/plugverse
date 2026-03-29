"""
配置中心

统一管理平台和插件的配置。
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from loguru import logger


class ConfigCenter:
    """
    配置中心
    
    功能：
    - 平台配置管理
    - 插件配置管理
    - 配置验证（JSON Schema）
    - 配置持久化
    - 配置变更通知
    """
    
    def __init__(self, config_dir: str = "./config"):
        """
        初始化配置中心
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._platform_config: Dict[str, Any] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        # 加载平台配置
        self._load_platform_config()
        
        logger.info(f"配置中心初始化完成，目录：{self.config_dir}")
    
    def _load_platform_config(self):
        """加载平台配置"""
        config_files = [
            self.config_dir / "app.yaml",
            self.config_dir / "app.yml",
            self.config_dir / "config.yaml",
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self._platform_config = yaml.safe_load(f) or {}
                    logger.info(f"已加载平台配置：{config_file}")
                    break
                except Exception as e:
                    logger.error(f"加载配置文件失败 {config_file}: {e}")
        
        # 应用环境变量覆盖
        self._apply_env_overrides()
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖配置"""
        import os
        
        # 示例：PLUGVERSE_APP_PORT 覆盖 app.port
        for key, value in os.environ.items():
            if key.startswith("PLUGVERSE_"):
                config_key = key[10:].lower().replace("_", ".")
                keys = config_key.split(".")
                
                config = self._platform_config
                for k in keys[:-1]:
                    if k not in config:
                        config[k] = {}
                    config = config[k]
                
                # 尝试类型转换
                try:
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                    elif value.isdigit():
                        value = int(value)
                except:
                    pass
                
                config[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取平台配置项
        
        Args:
            key: 配置键，支持点号分隔（如：server.port）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._platform_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, save: bool = False):
        """
        设置平台配置项
        
        Args:
            key: 配置键
            value: 配置值
            save: 是否保存到文件
        """
        keys = key.split(".")
        config = self._platform_config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        if save:
            self.save_platform_config()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有平台配置"""
        return self._platform_config.copy()
    
    def save_platform_config(self):
        """保存平台配置到文件"""
        config_file = self.config_dir / "app.yaml"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                self._platform_config, 
                f, 
                default_flow_style=False,
                allow_unicode=True
            )
        
        logger.info(f"平台配置已保存：{config_file}")
    
    # ========== 插件配置管理 ==========
    
    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """
        获取插件配置
        
        Args:
            plugin_id: 插件 ID
            
        Returns:
            插件配置字典
        """
        if plugin_id in self._plugin_configs:
            return self._plugin_configs[plugin_id].copy()
        
        # 从文件加载
        config_file = self.config_dir / "plugins" / f"{plugin_id}.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self._plugin_configs[plugin_id] = config
                return config.copy()
            except Exception as e:
                logger.error(f"加载插件配置失败 {plugin_id}: {e}")
        
        return {}
    
    def save_plugin_config(self, plugin_id: str, config: Dict[str, Any]):
        """
        保存插件配置
        
        Args:
            plugin_id: 插件 ID
            config: 配置字典
        """
        # 确保目录存在
        plugins_config_dir = self.config_dir / "plugins"
        plugins_config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = plugins_config_dir / f"{plugin_id}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self._plugin_configs[plugin_id] = config
        logger.info(f"插件配置已保存：{plugin_id}")
    
    def update_plugin_config(
        self, 
        plugin_id: str, 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新插件配置
        
        Args:
            plugin_id: 插件 ID
            updates: 配置更新字典
            
        Returns:
            更新后的配置
        """
        config = self.get_plugin_config(plugin_id)
        config.update(updates)
        self.save_plugin_config(plugin_id, config)
        return config
    
    def validate_config(
        self, 
        config: Dict[str, Any], 
        schema: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        验证配置是否符合 Schema
        
        Args:
            config: 配置字典
            schema: JSON Schema
            
        Returns:
            (是否有效，错误信息)
        """
        try:
            from jsonschema import validate, ValidationError
            
            validate(instance=config, schema=schema)
            return True, None
        except ImportError:
            # jsonschema 未安装，跳过验证
            logger.warning("jsonschema 未安装，跳过配置验证")
            return True, None
        except ValidationError as e:
            return False, str(e.message)
    
    def reset_plugin_config(self, plugin_id: str):
        """
        重置插件配置
        
        Args:
            plugin_id: 插件 ID
        """
        config_file = self.config_dir / "plugins" / f"{plugin_id}.json"
        
        if config_file.exists():
            config_file.unlink()
            logger.info(f"插件配置已重置：{plugin_id}")
        
        if plugin_id in self._plugin_configs:
            del self._plugin_configs[plugin_id]
    
    # ========== 工具方法 ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """获取配置中心统计信息"""
        return {
            "platform_config_keys": len(self._flatten_dict(self._platform_config)),
            "plugin_configs": len(self._plugin_configs),
            "config_dir": str(self.config_dir.absolute())
        }
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """扁平化嵌套字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
