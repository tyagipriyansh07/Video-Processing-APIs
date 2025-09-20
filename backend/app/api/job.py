from fastapi import APIRouter, HTTPException
from .. import crud, utils
from ..database import SessionLocal
import os
from fastapi.responses import FileResponse

router = APIRouter(prefix="/job", tags=["job"])

@router.get("/status/{job_id}")
def get_job_status(job_id: str):
    with utils.get_db() as db:
        job = crud.get_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"job_id": job.job_id, "status": job.status, "result_path": job.result_path}

@router.get("/result/{job_id}")
def get_job_result(job_id: str):
    with utils.get_db() as db:
        job = crud.get_job(db, job_id)
        if not job or not job.result_path:
            raise HTTPException(status_code=404, detail="Result not available")
        if not os.path.exists(job.result_path):
            raise HTTPException(status_code=404, detail="Result file missing")
        return FileResponse(job.result_path, filename=os.path.basename(job.result_path))
