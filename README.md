# Video Processing Backend 🎥

A powerful FastAPI backend for asynchronous video processing. This application allows users to upload videos and perform various editing tasks like trimming, adding overlays, and generating multiple quality versions. It uses FFmpeg for video manipulation, Celery with Redis for handling background jobs, and PostgreSQL for metadata storage.

- Live Application URL: https://video-backend-ug3r.onrender.com

# ✨ Features
- Video Upload: Upload video files and store their metadata.

- Asynchronous Processing: All video operations are handled as background jobs, so the API responds instantly.

- Video Trimming: Trim videos to a specific start and end time.

- Overlays & Watermarking: Add text, image, or video overlays.

- Multiple Qualities: Generate different resolution versions of a video (e.g., 1080p, 720p, 480p).

- Job Tracking: Check the status of any processing job and download the result.

# 🚀 Using the Live API
You can interact with the deployed application using any API client like Postman, Insomnia, or curl.

# API Documentation (Swagger UI)
All endpoints are documented and can be tested live at:
https://video-backend-ug3r.onrender.com/docs

Key Endpoints
- POST /videos/upload: Upload a new video file.

- POST /trim/: Create a trimmed clip from an existing video.

- POST /overlay/add: Add a text, image, or video overlay.

- POST /quality/generate: Create multiple quality versions of a video.

- GET /job/status/{job_id}: Check the status of a processing job.

- GET /job/result/{job_id}: Download the output file from a completed job.

Example: Upload a Video with curl
curl -X POST -F "file=@/path/to/your/video.mp4" [https://video-backend-ug3r.onrender.com/videos/upload](https://video-backend-ug3r.onrender.com/videos/upload)

This will return a video id that you can use in other API calls.

# 💻 Local Development Setup
1. Prerequisites
```bash
- Python (3.8+)
- PostgreSQL (12+)
- Redis
- FFmpeg
```
2. Clone and Install
```bash
git clone [https://github.com/tyagipriyansh07/Video-Processing-APIs.git](https://github.com/tyagipriyansh07/Video-Processing-APIs.git)
cd Video-Processing-APIs/backend
```

### Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure Environment
Set up your PostgreSQL and Redis instances.
```bash
Create a .env file inside the backend/ directory and add your credentials. Use the app/database.py file as a reference for the required variables (e.g., POSTGRES_HOST, POSTGRES_USER, etc.).
```

4. Run Database Migrations
Ensure your database is running, then apply the schema:
```bash
alembic upgrade head
```

5. Start the Services
You need two separate terminals running inside the backend/ directory.

Terminal 1: Start the FastAPI Server
```bash
uvicorn app.main:app --reload
```

Terminal 2: Start the Celery Worker
```bash
celery -A app.services.job_queue.celery worker --loglevel=info
```

Your local application will be available at http://127.0.0.1:8000.

## Redis on Windows
- Download from: https://github.com/tporadowski/redis/releases
- Extract and run `redis-server.exe`

---

