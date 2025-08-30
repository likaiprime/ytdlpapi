from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import yt_dlp
import json

app = FastAPI(
    title="YT-DLP API",
    description="API for extracting video information and download links using yt-dlp",
    version="1.0.0"
)

class VideoUrlRequest(BaseModel):
    urls: List[HttpUrl]

class VideoFormat(BaseModel):
    format_id: str
    ext: str
    resolution: Optional[str] = None
    filesize: Optional[int] = None
    url: str
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    fps: Optional[float] = None

class AudioFormat(BaseModel):
    format_id: str
    ext: str
    filesize: Optional[int] = None
    url: str
    acodec: Optional[str] = None
    abr: Optional[float] = None

class VideoInfo(BaseModel):
    title: str
    duration: Optional[int] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    video_formats: List[VideoFormat]
    audio_formats: List[AudioFormat]

class ExtractResponse(BaseModel):
    success: bool
    data: List[VideoInfo]
    errors: List[str] = []

def extract_video_info(url: str) -> Dict[str, Any]:
    """Extract video information using yt-dlp"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extractaudio': False,
        'format': 'best',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract info from {url}: {str(e)}")

def parse_formats(formats: List[Dict]) -> tuple[List[VideoFormat], List[AudioFormat]]:
    """Parse formats into video and audio formats"""
    video_formats = []
    audio_formats = []
    
    for fmt in formats:
        if fmt.get('vcodec') != 'none' and fmt.get('height'):  # Video format
            video_format = VideoFormat(
                format_id=fmt.get('format_id', ''),
                ext=fmt.get('ext', ''),
                resolution=f"{fmt.get('width', 0)}x{fmt.get('height', 0)}" if fmt.get('width') and fmt.get('height') else None,
                filesize=fmt.get('filesize'),
                url=fmt.get('url', ''),
                vcodec=fmt.get('vcodec'),
                acodec=fmt.get('acodec'),
                fps=fmt.get('fps')
            )
            video_formats.append(video_format)
        elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':  # Audio only format
            audio_format = AudioFormat(
                format_id=fmt.get('format_id', ''),
                ext=fmt.get('ext', ''),
                filesize=fmt.get('filesize'),
                url=fmt.get('url', ''),
                acodec=fmt.get('acodec'),
                abr=fmt.get('abr')
            )
            audio_formats.append(audio_format)
    
    # Sort video formats by resolution (height) descending
    video_formats.sort(key=lambda x: int(x.resolution.split('x')[1]) if x.resolution else 0, reverse=True)
    
    # Sort audio formats by bitrate descending
    audio_formats.sort(key=lambda x: x.abr if x.abr else 0, reverse=True)
    
    return video_formats, audio_formats

@app.post("/extract", response_model=ExtractResponse)
async def extract_video_urls(request: VideoUrlRequest):
    """
    Extract video information and available formats for given URLs
    
    Returns video and audio download links with quality information
    """
    results = []
    errors = []
    
    for url in request.urls:
        try:
            info = extract_video_info(str(url))
            
            # Handle playlist
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        video_formats, audio_formats = parse_formats(entry.get('formats', []))
                        
                        video_info = VideoInfo(
                            title=entry.get('title', 'Unknown'),
                            duration=entry.get('duration'),
                            uploader=entry.get('uploader'),
                            upload_date=entry.get('upload_date'),
                            view_count=entry.get('view_count'),
                            like_count=entry.get('like_count'),
                            description=entry.get('description'),
                            thumbnail=entry.get('thumbnail'),
                            video_formats=video_formats,
                            audio_formats=audio_formats
                        )
                        results.append(video_info)
            else:
                # Single video
                video_formats, audio_formats = parse_formats(info.get('formats', []))
                
                video_info = VideoInfo(
                    title=info.get('title', 'Unknown'),
                    duration=info.get('duration'),
                    uploader=info.get('uploader'),
                    upload_date=info.get('upload_date'),
                    view_count=info.get('view_count'),
                    like_count=info.get('like_count'),
                    description=info.get('description'),
                    thumbnail=info.get('thumbnail'),
                    video_formats=video_formats,
                    audio_formats=audio_formats
                )
                results.append(video_info)
                
        except HTTPException:
            raise
        except Exception as e:
            errors.append(f"Error processing {url}: {str(e)}")
    
    return ExtractResponse(
        success=len(errors) == 0,
        data=results,
        errors=errors
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "YT-DLP API",
        "version": "1.0.0",
        "endpoints": {
            "/extract": "POST - Extract video information and download links",
            "/docs": "GET - Swagger documentation",
            "/redoc": "GET - ReDoc documentation"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=30022)