from fastapi import FastAPI
from .api import upload, trim, overlay, job, quality

app = FastAPI(title="Video Processing Backend")

app.include_router(upload.router)
app.include_router(trim.router)
app.include_router(overlay.router)
app.include_router(job.router)
app.include_router(quality.router)


@app.get("/")
def root():
    return {"message": "Video Processing Backend is running!"}

# Routers will be included here
