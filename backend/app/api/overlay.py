from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .. import crud, schemas, utils
from ..services.ffmpeg_service import overlay_task, watermark_task
from ..services.job_queue import submit_job
import os
import uuid
import ffmpeg

router = APIRouter(prefix="/overlay", tags=["overlay"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../uploads'))
OVERLAY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../overlays'))
os.makedirs(OVERLAY_DIR, exist_ok=True)

class OverlayRequest(BaseModel):
    video_id: int
    type: str  # 'text', 'image', 'video'
    config: dict  # e.g., {"text": "नमस्ते", "font_size": 24, "x": 10, "y": 10, "start": 2, "end": 8}

@router.post("/add", response_model=dict)
def add_overlay(req: OverlayRequest):
    with utils.get_db() as db:
        video = crud.get_video(db, req.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        input_path = os.path.join(UPLOAD_DIR, video.filename)
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Video file missing")
        job_id = str(uuid.uuid4())
        crud.create_job(db, job_id, 'overlay', {"video_id": req.video_id, "type": req.type, "config": req.config})
        submit_job(overlay_task, job_id, req.video_id, req.type, req.config, video.filename)
    return {"job_id": job_id, "status": "pending"}

class WatermarkRequest(BaseModel):
    video_id: int
    image_path: str  # Path to watermark image
    x: int = 10
    y: int = 10
    start: float = 0
    end: float = 5

@router.post("/watermark", response_model=dict)
def add_watermark(req: WatermarkRequest):
    with utils.get_db() as db:
        video = crud.get_video(db, req.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        input_path = os.path.join(UPLOAD_DIR, video.filename)
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Video file missing")
        if not os.path.exists(req.image_path):
            raise HTTPException(status_code=400, detail="Watermark image not found")
        job_id = str(uuid.uuid4())
        crud.create_job(db, job_id, 'watermark', {"video_id": req.video_id, "image_path": req.image_path, "x": req.x, "y": req.y, "start": req.start, "end": req.end})
        submit_job(watermark_task, job_id, req.video_id, req.image_path, req.x, req.y, req.start, req.end, video.filename)
    return {"job_id": job_id, "status": "pending"}
