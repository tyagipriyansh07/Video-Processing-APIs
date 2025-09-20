from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .. import crud, schemas, utils
from ..services.ffmpeg_service import trim_task
from ..services.job_queue import submit_job
import os
import uuid

router = APIRouter(prefix="/trim", tags=["trim"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../uploads'))
TRIM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../trimmed'))
os.makedirs(TRIM_DIR, exist_ok=True)

class TrimRequest(BaseModel):
    video_id: int
    start_time: float
    end_time: float

@router.post("/", response_model=dict)
def trim_video(req: TrimRequest):
    with utils.get_db() as db:
        video = crud.get_video(db, req.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        input_path = os.path.join(UPLOAD_DIR, video.filename)
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Video file missing")
        job_id = str(uuid.uuid4())
        crud.create_job(db, job_id, 'trim', {"video_id": req.video_id, "start_time": req.start_time, "end_time": req.end_time})
        submit_job(trim_task, job_id, req.video_id, req.start_time, req.end_time, video.filename)
    return {"job_id": job_id, "status": "pending"}

