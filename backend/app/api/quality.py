from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from .. import crud, schemas, utils
from ..services.ffmpeg_service import quality_task
from ..services.job_queue import submit_job
import os
import uuid
from fastapi.responses import FileResponse

router = APIRouter(prefix="/quality", tags=["quality"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../uploads'))
QUALITY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../qualities'))
os.makedirs(QUALITY_DIR, exist_ok=True)

class QualityRequest(BaseModel):
    video_id: int
    qualities: List[str] = Field(..., example=["720p", "480p"])

@router.post("/generate", response_model=dict)
def generate_qualities(req: QualityRequest):
    """
    Submits a job to generate multiple quality versions of a video.
    """
    job_id = str(uuid.uuid4())
    
    with utils.get_db() as db:
        video = crud.get_video(db, req.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        input_path = os.path.join(UPLOAD_DIR, video.filename)
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Video file missing from server")

        # Read the filename into a variable BEFORE the session closes
        filename = video.filename
        
        crud.create_job(db, job_id, 'quality', {"video_id": req.video_id, "qualities": req.qualities})
    
    # Now, use the simple 'filename' variable. The 'video' object is no longer needed.
    submit_job(quality_task, job_id, req.video_id, req.qualities, filename)
    
    return {"job_id": job_id, "status": "pending"}

@router.get("/{video_id}", response_model=List[schemas.VideoQuality])
def list_available_qualities(video_id: int):
    """
    Lists all available quality versions for a specific video.
    """
    with utils.get_db() as db:
        qualities = crud.get_video_qualities(db, video_id=video_id)
        if not qualities:
            raise HTTPException(status_code=404, detail="No quality versions found for this video. Please generate them first.")
        return qualities

@router.get("/download/{quality_id}")
def download_quality_video(quality_id: int):
    """
    Downloads a specific quality version of a video.
    """
    with utils.get_db() as db:
        quality_video = crud.get_video_quality_by_id(db, quality_id=quality_id)
        if not quality_video:
            raise HTTPException(status_code=404, detail="Video quality version not found.")
        
        # Similarly, get the filename before the session closes
        filename = quality_video.filename

    file_path = os.path.join(QUALITY_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server. It may have been moved or deleted.")

    return FileResponse(file_path, filename=filename)