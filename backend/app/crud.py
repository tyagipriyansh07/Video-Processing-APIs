from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

def create_video(db: Session, video: schemas.VideoCreate):
    db_video = models.Video(**video.dict())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_videos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Video).offset(skip).limit(limit).all()

def get_video(db: Session, video_id: int):
    return db.query(models.Video).filter(models.Video.id == video_id).first()

def create_trimmed_video(db: Session, trimmed: schemas.TrimmedVideoBase):
    db_trimmed = models.TrimmedVideo(**trimmed.dict())
    db.add(db_trimmed)
    db.commit()
    db.refresh(db_trimmed)
    return db_trimmed

def create_overlay(db: Session, overlay: schemas.OverlayBase):
    db_overlay = models.Overlay(**overlay.dict())
    db.add(db_overlay)
    db.commit()
    db.refresh(db_overlay)
    return db_overlay

def create_watermark(db: Session, watermark: schemas.WatermarkBase):
    db_watermark = models.Watermark(**watermark.dict())
    db.add(db_watermark)
    db.commit()
    db.refresh(db_watermark)
    return db_watermark

def create_job(db: Session, job_id: str, job_type: str, meta: Optional[dict] = None):
    db_job = models.Job(job_id=job_id, type=job_type, meta=meta or {})
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job_status(db: Session, job_id: str, status: str, result_path: Optional[str] = None):
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if job:
        job.status = status
        if result_path:
            job.result_path = result_path
        db.commit()
        db.refresh(job)
    return job

def get_job(db: Session, job_id: str):
    return db.query(models.Job).filter(models.Job.job_id == job_id).first()

def create_video_quality(db: Session, quality: schemas.VideoQualityBase):
    db_quality = models.VideoQuality(**quality.dict())
    db.add(db_quality)
    db.commit()
    db.refresh(db_quality)
    return db_quality

def get_video_qualities(db: Session, video_id: int):
    return db.query(models.VideoQuality).filter(models.VideoQuality.video_id == video_id).all()

# ... (at the end of the file)
def get_video_quality_by_id(db: Session, quality_id: int):
    return db.query(models.VideoQuality).filter(models.VideoQuality.id == quality_id).first()