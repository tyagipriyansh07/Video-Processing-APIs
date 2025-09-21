import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = os.getenv("REDIS_PORT", "6379")
# REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "video_jobs",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

def submit_job(task_func, *args, **kwargs):
    return task_func.delay(*args, **kwargs)
