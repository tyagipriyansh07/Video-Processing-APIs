from app.services.job_queue import celery
from app.services import ffmpeg_service  # Ensure tasks are registered

if __name__ == "__main__":
    celery.start()
