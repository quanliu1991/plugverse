#!/usr/bin/env bash
# 下载测试用 YouTube 视频与单独音频到 testdata/youtube_QJUceJvPrmA/
# 依赖: yt-dlp（pip install -U yt-dlp）、ffmpeg（brew install ffmpeg）
# YouTube 网页端常触发 403/SABR，此处使用 android 客户端；纯音频常不可用，故用 ffmpeg 从 mp4 抽取 AAC 到 audio.m4a
# URL 中 &t=1011s 仅影响网页播放起点；若要只下某一段可加 --download-sections

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ROOT}/testdata/youtube_QJUceJvPrmA"
URL="https://www.youtube.com/watch?v=QJUceJvPrmA"

mkdir -p "$OUT"
cd "$OUT"

# 优先使用较新的 Python 模块（pip install -U yt-dlp 常装在该解释器下）
YTDLP=()
if command -v yt-dlp &>/dev/null; then
  YTDLP=(yt-dlp)
elif command -v python3.12 &>/dev/null && python3.12 -m yt_dlp --version &>/dev/null; then
  YTDLP=(python3.12 -m yt_dlp)
elif command -v python3.11 &>/dev/null && python3.11 -m yt_dlp --version &>/dev/null; then
  YTDLP=(python3.11 -m yt_dlp)
elif command -v python3.10 &>/dev/null && python3.10 -m yt_dlp --version &>/dev/null; then
  YTDLP=(python3.10 -m yt_dlp)
elif command -v python3.9 &>/dev/null && python3.9 -m yt_dlp --version &>/dev/null; then
  YTDLP=(python3.9 -m yt_dlp)
elif python3 -m yt_dlp --version &>/dev/null; then
  YTDLP=(python3 -m yt_dlp)
elif [[ -x "${HOME}/.local/bin/yt-dlp" ]]; then
  YTDLP=("${HOME}/.local/bin/yt-dlp")
else
  echo "未找到 yt-dlp。请先安装: pip install -U yt-dlp  或  brew install yt-dlp" >&2
  exit 1
fi

EXTRACTOR_ARGS=(--extractor-args "youtube:player_client=android")

echo "正在下载视频 (android 客户端，合并为 mp4)..."
"${YTDLP[@]}" "${EXTRACTOR_ARGS[@]}" -o "video.%(ext)s" -f "bestvideo+bestaudio/best" --merge-output-format mp4 --no-playlist "$URL"

if ! command -v ffmpeg &>/dev/null; then
  echo "未找到 ffmpeg，无法生成独立 audio.m4a。请安装: brew install ffmpeg" >&2
  exit 1
fi

echo "正在从 video 抽取音频轨到 audio.m4a..."
ffmpeg -y -nostdin -loglevel error -i "video.mp4" -vn -c:a copy "audio.m4a"

echo "完成。输出目录: $OUT"
ls -la
