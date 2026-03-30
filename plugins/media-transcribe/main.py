"""
Media Transcribe Plugin - 音视频转文字插件

使用 Faster-Whisper 进行高效的语音识别
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.plugin_base import (
    IPlugin, 
    PluginMetadata, 
    PluginType, 
    PluginContext,
    PluginStatus
)
from app.event_bus import Event, PlatformEvents


class Plugin(IPlugin):
    """音视频转文字插件实现"""
    
    def __init__(self):
        self._context: PluginContext = None
        self._model = None
        self._config = {
            "model_size": "base",
            "language": "zh",
            "output_format": "txt",
            "compute_type": "int8",
            # simplified：中文转写统一为简体；original：保留模型输出（常为繁体）
            "chinese_script": "simplified",
        }
        self._model_loaded = False
        self._opencc_t2s = None  # lazy OpenCC('t2s')
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="media-transcribe",
            name="音视频转文字",
            version="1.0.0",
            description="使用 Faster-Whisper 将音视频文件转换为文字稿",
            author="PlugVerse Team",
            type=PluginType.MEDIA_PROCESS,
            icon="🎤",
            website="https://github.com/quanliu1991/plugverse",
            license="MIT",
            requirements={
                "faster-whisper": ">=0.10.0",
                "ffmpeg-python": ">=0.2.0",
                "opencc-python-reimplemented": ">=0.1.7",
            },
            permissions=["storage.read", "storage.write", "media.process"],
            config_schema={
                "type": "object",
                "properties": {
                    "model_size": {
                        "type": "string",
                        "enum": ["tiny", "base", "small", "medium", "large"]
                    },
                    "language": {"type": "string"},
                    "output_format": {
                        "type": "string",
                        "enum": ["txt", "srt", "vtt", "json"]
                    },
                    "compute_type": {
                        "type": "string",
                        "enum": ["int8", "float16", "float32"]
                    },
                    "chinese_script": {
                        "type": "string",
                        "enum": ["simplified", "original"],
                    },
                }
            }
        )
    
    async def initialize(self, context: PluginContext) -> bool:
        """初始化插件，加载模型"""
        try:
            self._context = context
            
            # 加载配置
            saved_config = self._context.config_center.get_plugin_config("media-transcribe")
            if saved_config:
                self._config.update(saved_config)
            
            self._context.logger.info(f"初始化音视频转文字插件，配置：{self._config}")
            
            # 延迟加载模型（第一次执行时加载）
            self._context.logger.info("插件已初始化，模型将在首次执行时加载")
            return True
            
        except Exception as e:
            self._context.logger.error(f"插件初始化失败：{e}")
            return False
    
    def _load_model(self):
        """加载 Whisper 模型"""
        try:
            from faster_whisper import WhisperModel
            
            self._context.logger.info(f"加载 Whisper 模型：{self._config['model_size']}")
            self._model = WhisperModel(
                self._config["model_size"],
                compute_type=self._config["compute_type"]
            )
            self._model_loaded = True
            self._context.logger.info("模型加载成功")
            
        except ImportError:
            self._context.logger.error("faster-whisper 未安装，请运行：pip install faster-whisper")
            raise
        except Exception as e:
            self._context.logger.error(f"模型加载失败：{e}")
            raise

    def _is_chinese_context(self, detected_language: Optional[str]) -> bool:
        """按配置或检测结果判断是否按中文处理（简体转换）。"""
        cfg = self._config.get("language") or "zh"
        if cfg != "auto":
            c = str(cfg).lower()
            return c.startswith("zh") or c in ("yue", "nan")
        if detected_language:
            d = str(detected_language).lower()
            return d.startswith("zh") or d in ("yue", "nan")
        return False

    def _normalize_segment_text(self, text: str, detected_language: Optional[str]) -> str:
        """Whisper 中文输出常为繁体，可选转为简体。"""
        if self._config.get("chinese_script", "simplified") != "simplified":
            return text
        if not self._is_chinese_context(detected_language):
            return text
        try:
            from opencc import OpenCC
        except ImportError:
            self._context.logger.warning(
                "opencc 未安装，无法输出简体字，请安装：pip install opencc-python-reimplemented"
            )
            return text
        if self._opencc_t2s is None:
            self._opencc_t2s = OpenCC("t2s")
        return self._opencc_t2s.convert(text)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行转写任务"""
        try:
            file_path = input_data.get("file_path")
            if not file_path:
                raise ValueError("缺少 file_path 参数")
            
            # 检查文件是否存在
            if not Path(file_path).exists():
                raise ValueError(f"文件不存在：{file_path}")
            
            self._context.logger.info(f"开始转写：{file_path}")
            
            # 发布任务创建事件
            await self._context.event_bus.publish(Event(
                name=PlatformEvents.TASK_CREATED,
                payload={"type": "transcribe", "file": file_path},
                source="media-transcribe"
            ))
            
            # 加载模型（如果未加载）
            if not self._model_loaded:
                self._load_model()
            
            # 执行转写
            segments, info = self._model.transcribe(
                file_path,
                language=self._config["language"] if self._config["language"] != "auto" else None
            )
            
            # 收集结果
            text_segments: List[Dict] = []
            full_text_parts = []
            
            for segment in segments:
                line = self._normalize_segment_text(
                    segment.text.strip(), info.language
                )
                text_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": line,
                })
                full_text_parts.append(line)
            
            output_text = " ".join(full_text_parts)
            
            # 保存结果
            output_path = await self._save_result(file_path, text_segments, output_text)
            
            # 发布完成事件
            await self._context.event_bus.publish(Event(
                name=PlatformEvents.TASK_COMPLETED,
                payload={
                    "type": "transcribe",
                    "file": file_path,
                    "output": output_path,
                    "duration": info.duration,
                    "language": info.language
                },
                source="media-transcribe"
            ))
            
            self._context.logger.info(f"转写完成：{output_path}")
            
            return {
                "success": True,
                "text": output_text,
                "segments": text_segments,
                "output_path": output_path,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "transcription_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self._context.logger.error(f"转写失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _save_result(self, original_path: str, segments: List[Dict], text: str) -> str:
        """保存转写结果"""
        output_dir = Path("./output/transcriptions")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        fmt = self._config["output_format"]
        base_name = Path(original_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if fmt == "txt":
            output_path = output_dir / f"{base_name}_{timestamp}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        
        elif fmt == "srt":
            output_path = output_dir / f"{base_name}_{timestamp}.srt"
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, seg in enumerate(segments, 1):
                    f.write(f"{i}\n")
                    f.write(f"{self._format_time(seg['start'], ',')} --> {self._format_time(seg['end'], ',')}\n")
                    f.write(f"{seg['text']}\n\n")
        
        elif fmt == "vtt":
            output_path = output_dir / f"{base_name}_{timestamp}.vtt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                for seg in segments:
                    f.write(f"{self._format_time(seg['start'], '.')} --> {self._format_time(seg['end'], '.')}")
                    f.write(f"\n{seg['text']}\n\n")
        
        elif fmt == "json":
            output_path = output_dir / f"{base_name}_{timestamp}.json"
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "source": original_path,
                        "timestamp": datetime.now().isoformat(),
                        "config": self._config
                    },
                    "segments": segments,
                    "full_text": text
                }, f, ensure_ascii=False, indent=2)
        
        else:
            # 默认 txt
            output_path = output_dir / f"{base_name}_{timestamp}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        
        return str(output_path)
    
    def _format_time(self, seconds: float, decimal_sep: str = ',') -> str:
        """格式化时间为 SRT/VTT 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}{decimal_sep}{millis:03d}"
    
    async def shutdown(self) -> bool:
        """关闭插件，释放模型"""
        try:
            if self._model:
                del self._model
                self._model = None
                self._model_loaded = False
                self._context.logger.info("模型已卸载")
            
            self._context.logger.info("音视频转文字插件已关闭")
            return True
            
        except Exception as e:
            self._context.logger.error(f"关闭插件失败：{e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        return self._config
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        try:
            # 验证配置
            schema = self.metadata.config_schema
            for key, value in config.items():
                if key in schema.get("properties", {}):
                    prop = schema["properties"][key]
                    if "enum" in prop and value not in prop["enum"]:
                        self._context.logger.error(f"配置值无效：{key}={value}")
                        return False
            
            self._config.update(config)
            self._context.config_center.save_plugin_config("media-transcribe", self._config)
            
            # 如果模型配置改变，重新加载模型
            if "model_size" in config or "compute_type" in config:
                self._model_loaded = False
                self._context.logger.info("配置已更新，模型将在下次执行时重新加载")
            
            self._context.logger.info(f"配置已更新：{self._config}")
            return True
            
        except Exception as e:
            self._context.logger.error(f"更新配置失败：{e}")
            return False
    
    def get_health(self) -> Dict[str, Any]:
        """获取插件健康状态"""
        return {
            "status": "healthy" if self._model_loaded else "initialized",
            "model_loaded": self._model_loaded,
            "model_size": self._config["model_size"],
            "config": self._config,
            "timestamp": datetime.now().isoformat()
        }
