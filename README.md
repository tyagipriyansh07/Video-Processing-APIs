# Video Processing Backend

## Setup Instructions

### 1. Install Requirements
```
pip install -r requirements.txt
```

### 2. PostgreSQL Setup
- Ensure PostgreSQL is running on `localhost:5433` (or `5432`)
- Create a database (default: `postgres`)
- Update `.env` with your credentials

### 3. Redis Setup
- Install Redis (see below for Windows instructions)
- Start Redis server (default port: 6379)

### 4. Run Migrations
```
alembic upgrade head
```

### 5. Start Backend
```
uvicorn app.main:app --reload
```

### 6. Start Celery Worker
```
celery -A app.services.job_queue.celery worker --loglevel=info
```

---

## Redis on Windows
- Download from: https://github.com/tporadowski/redis/releases
- Extract and run `redis-server.exe`

---

## API Docs
Visit: `http://localhost:8000/docs`



