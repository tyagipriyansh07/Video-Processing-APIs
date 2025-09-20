from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    duration = Column(Float)
    size = Column(Integer)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    trimmed_videos = relationship("TrimmedVideo", back_populates="original_video")
    overlays = relationship("Overlay", back_populates="video")
    watermarks = relationship("Watermark", back_populates="video")
    qualities = relationship("VideoQuality", back_populates="video")

class TrimmedVideo(Base):
    __tablename__ = "trimmed_videos"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    filename = Column(String, nullable=False)
    start_time = Column(Float)
    end_time = Column(Float)
    duration = Column(Float)
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    original_video = relationship("Video", back_populates="trimmed_videos")

class Overlay(Base):
    __tablename__ = "overlays"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    type = Column(String)  # text, image, video
    config = Column(JSON)  # position, timing, etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    video = relationship("Video", back_populates="overlays")

class Watermark(Base):
    __tablename__ = "watermarks"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    config = Column(JSON)  # watermark config
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    video = relationship("Video", back_populates="watermarks")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    status = Column(String, default="pending")
    result_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    type = Column(String)  # upload, trim, overlay, watermark, quality
    meta = Column(JSON)

class VideoQuality(Base):
    __tablename__ = "video_qualities"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    quality = Column(String)  # 1080p, 720p, 480p
    filename = Column(String, nullable=False)
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    video = relationship("Video", back_populates="qualities")



