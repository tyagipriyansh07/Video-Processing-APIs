from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from .. import crud, schemas, utils
from ..database import SessionLocal
import os
from datetime import datetime

router = APIRouter(prefix="/videos", tags=["videos"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../uploads'))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.Video)
def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    size = utils.get_video_size(file_path)
    duration = utils.get_video_duration(file_path)
    video_in = schemas.VideoCreate(filename=file.filename, duration=duration, size=size)
    with utils.get_db() as db:
        db_video = crud.create_video(db, video_in)
    return db_video

@router.get("/", response_model=list[schemas.Video])
def list_videos():
    with utils.get_db() as db:
        videos = crud.get_videos(db)
    return videos



