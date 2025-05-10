from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from TikTokApi import TikTokApi
from fastapi.responses import StreamingResponse
import io

app = FastAPI()

# Inisialisasi TikTokApi
api = TikTokApi()

class VideoMetadata(BaseModel):
    video_url: str
    author_name: str
    song_name: str
    description: str

@app.get("/get_video_info", response_model=VideoMetadata)
async def get_video_info(url: str = Query(..., description="Link TikTok Video")):
    try:
        video = api.video(url=url)
        # Pastikan atribut ini tersedia di versi TikTokApi 7.1.0
        return VideoMetadata(
            video_url=video.video_url,
            author_name=video.author.username,
            song_name=video.music.title,
            description=video.description
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching video info: {str(e)}")

@app.get("/download_video")
async def download_video(url: str = Query(..., description="Link TikTok Video")):
    try:
        video = api.video(url=url)
        video_bytes = video.bytes()
        file_like = io.BytesIO(video_bytes)
        return StreamingResponse(
            file_like,
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=tiktok_video.mp4"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading video: {str(e)}")