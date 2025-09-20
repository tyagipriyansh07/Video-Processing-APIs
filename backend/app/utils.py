from .database import SessionLocal
from contextlib import contextmanager
import ffmpeg
import os

def get_video_size(file_path: str) -> int:
    return os.path.getsize(file_path)

def get_video_duration(file_path: str) -> float:
    try:
        probe = ffmpeg.probe(file_path)
        return float(probe['format']['duration'])
    except Exception:
        return 0.0

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



