from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class VideoBase(BaseModel):
    filename: str
    duration: Optional[float]
    size: Optional[int]

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int
    upload_time: datetime
    class Config:
        orm_mode = True

class TrimmedVideoBase(BaseModel):
    video_id: int
    filename: str
    start_time: float
    end_time: float
    duration: Optional[float]
    size: Optional[int]

class TrimmedVideo(TrimmedVideoBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class OverlayBase(BaseModel):
    video_id: int
    type: str
    config: Dict[str, Any]

class Overlay(OverlayBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class WatermarkBase(BaseModel):
    video_id: int
    config: Dict[str, Any]

class Watermark(WatermarkBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class JobBase(BaseModel):
    type: str
    meta: Optional[Dict[str, Any]]

class Job(JobBase):
    id: int
    job_id: str
    status: str
    result_path: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

class VideoQualityBase(BaseModel):
    video_id: int
    quality: str
    filename: str
    size: Optional[int]

class VideoQuality(VideoQualityBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class VideoQualityBase(BaseModel):
    video_id: int
    quality: str
    filename: str
    size: int

class VideoQuality(VideoQualityBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True