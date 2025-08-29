# YT-DLP API

基于 FastAPI 和 yt-dlp 的视频信息提取 API，支持 Docker 部署。

## 功能特性

- 提取视频标题、时长、上传者等信息
- 获取所有可用的视频清晰度和下载链接
- 获取音频格式和下载链接
- 支持单个或批量视频处理
- 支持播放列表
- Docker 容器化部署
- 自动 API 文档

## 快速开始

### Docker 部署（推荐）

```bash
# 构建并启动服务
docker-compose up --build

# 后台运行
docker-compose up -d --build
```

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

## API 使用

服务启动后访问：
- API 服务：http://localhost:8000
- 交互式文档：http://localhost:8000/docs
- API 文档：http://localhost:8000/redoc

### 提取视频信息

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.youtube.com/watch?v=VIDEO_ID"
    ]
  }'
```

### 响应格式

```json
{
  "success": true,
  "data": [
    {
      "title": "视频标题",
      "duration": 180,
      "uploader": "上传者",
      "upload_date": "20231201",
      "view_count": 1000000,
      "like_count": 50000,
      "description": "视频描述",
      "thumbnail": "缩略图URL",
      "video_formats": [
        {
          "format_id": "137",
          "ext": "mp4",
          "resolution": "1920x1080",
          "filesize": 50000000,
          "url": "下载链接",
          "vcodec": "avc1.640028",
          "acodec": "none",
          "fps": 30.0
        }
      ],
      "audio_formats": [
        {
          "format_id": "140",
          "ext": "m4a", 
          "filesize": 5000000,
          "url": "音频下载链接",
          "acodec": "mp4a.40.2",
          "abr": 128.0
        }
      ]
    }
  ],
  "errors": []
}
```

## 支持的网站

yt-dlp 支持 1000+ 网站，包括：
- YouTube
- Bilibili
- Twitter
- Facebook
- Instagram
- TikTok
- 等等...

## 环境要求

- Python 3.9+
- ffmpeg (Docker 镜像已包含)

## 注意事项

- API 不会下载视频文件，只返回下载链接
- 某些网站可能需要登录或有地区限制
- 下载链接通常有时效性，建议及时使用