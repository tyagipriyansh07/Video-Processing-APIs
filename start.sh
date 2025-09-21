#!/bin/bash

# Start the Celery worker in the background
celery -A app.services.job_queue.celery worker --loglevel=info &

# Start the Uvicorn server in the foreground
uvicorn app.main:app --host 0.0.0.0 --port $PORT
