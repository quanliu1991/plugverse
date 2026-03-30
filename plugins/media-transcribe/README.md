# Media Transcribe Plugin - 音视频转文字插件

使用 [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) 实现高效的音视频转文字功能。

## 功能特性

- ✅ 支持多种音频格式（MP3, WAV, M4A, FLAC, OGG 等）
- ✅ 支持多种视频格式（MP4, AVI, MOV, MKV 等）
- ✅ 支持 99 种语言识别
- ✅ 多种输出格式（TXT, SRT, VTT, JSON）
- ✅ 可选模型大小（tiny/base/small/medium/large）
- ✅ 高效推理（CTranslate2 加速）
- ✅ 支持 GPU 加速（可选）

## 安装

```bash
# 在 PlugVerse 项目中
cd /Users/macstudio/.openclaw/workspace/plugverse
source venv/bin/activate

# 安装插件依赖
pip install -r plugins/media-transcribe/requirements.txt
```

## 使用

### 1. 通过 API 调用

```bash
# 执行转写
curl -X POST http://localhost:8000/api/plugins/media-transcribe/execute \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/audio.mp3"
  }'
```

### 2. 配置插件

```bash
# 更新配置
curl -X PUT http://localhost:8000/api/plugins/media-transcribe/config \
  -H "Content-Type: application/json" \
  -d '{
    "model_size": "small",
    "language": "zh",
    "output_format": "srt"
  }'
```

### 3. Python 代码调用

```python
from app.plugin_manager import PluginManager

# 执行转写
result = await plugin_manager.execute_plugin(
    "media-transcribe",
    {"file_path": "audio.mp3"}
)

print(result["text"])
```

## 配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_size | string | base | 模型大小：tiny/base/small/medium/large |
| language | string | zh | 识别语言：zh=中文，en=英文，auto=自动检测 |
| output_format | string | txt | 输出格式：txt/srt/vtt/json |
| compute_type | string | int8 | 计算类型：int8/float16/float32 |
| chinese_script | string | simplified | 中文：`simplified` 繁转简（默认）；`original` 保留模型字形 |

## 模型大小对比

| 模型 | 大小 | 速度 | 准确率 | 适用场景 |
|------|------|------|--------|----------|
| tiny | 75 MB | 最快 | 一般 | 快速测试 |
| base | 142 MB | 快 | 好 | 日常使用 |
| small | 466 MB | 中等 | 很好 | 生产环境 |
| medium | 1.5 GB | 慢 | 优秀 | 高准确率需求 |
| large | 2.9 GB | 最慢 | 最佳 | 专业场景 |

## 输出示例

### TXT 格式
```
今天天气真好，我们一起去公园散步吧。
```

### SRT 格式
```srt
1
00:00:00,000 --> 00:00:03,500
今天天气真好，

2
00:00:03,500 --> 00:00:06,000
我们一起去公园散步吧。
```

### JSON 格式
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "今天天气真好，"
    }
  ],
  "full_text": "今天天气真好，我们一起去公园散步吧。"
}
```

## 性能参考

在 M1 Mac Studio 上测试（音频长度：10 分钟）：

| 模型 | 处理时间 | 实时率 |
|------|----------|--------|
| tiny | ~30 秒 | 0.05x |
| base | ~60 秒 | 0.1x |
| small | ~120 秒 | 0.2x |
| medium | ~300 秒 | 0.5x |

*实时率 = 处理时间 / 音频长度，越小越快*

## 故障排查

### 问题：模型加载失败

```bash
# 确保安装了 faster-whisper
pip install faster-whisper

# 检查 FFmpeg 是否安装
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux
```

### 问题：内存不足

- 使用更小的模型（tiny 或 base）
- 关闭其他占用内存的应用
- 增加系统 swap 空间

### 问题：识别准确率低

- 尝试更大的模型（small 或 medium）
- 确保音频质量良好（无噪音）
- 指定正确的语言

## 开发插件扩展

参考 `app/plugin_base.py` 了解插件开发接口。

## 许可证

MIT License
