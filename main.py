from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
import requests
from TikTokApi import TikTokApi

app = FastAPI()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Inisialisasi TikTokApi
api = TikTokApi()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "error": None})

@app.post("/download")
async def download(request: Request):
    form = await request.form()
    url = form.get("url")
    if not url or not url.startswith("http"):
        return templates.TemplateResponse("index.html", {"request": request, "error": "URL tidak valid"})

    try:
        # Mengambil data video dengan TikTokApi
        tiktok_data = api.get_video_by_url(url)
        video_url = tiktok_data.get('video', {}).get('downloadAddr')
        if not video_url:
            raise Exception("Tidak dapat mendapatkan URL video")
    except Exception:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Gagal mendapatkan video dari TikTok API."})

    # Download video dari URL
    filename = f"videos/{uuid.uuid4()}.mp4"
    os.makedirs("videos", exist_ok=True)

    response = requests.get(video_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Gagal mengunduh video."})

    # Kirim file ke pengguna
    return FileResponse(path=filename, media_type='video/mp4', filename='tiktok_video.mp4')