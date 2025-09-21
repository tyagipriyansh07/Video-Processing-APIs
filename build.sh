#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Change to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Install FFmpeg (This part is tricky, we add it to the web service build instead)
# apt-get update && apt-get install -y ffmpeg

# Make the start script executable
chmod +x ./start.sh
