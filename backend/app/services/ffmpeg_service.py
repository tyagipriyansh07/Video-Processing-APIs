import os
import ffmpeg
import uuid
from app.services.job_queue import celery
from app.database import SessionLocal
from app import crud, schemas
from app.utils import get_video_size

TRIM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../trimmed'))
OVERLAY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../overlays'))
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../uploads'))
# Add this directory at the top with your other directory constants
QUALITY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../qualities'))
os.makedirs(QUALITY_DIR, exist_ok=True)
os.makedirs(TRIM_DIR, exist_ok=True)
os.makedirs(OVERLAY_DIR, exist_ok=True)

@celery.task(bind=True)
def trim_task(self, job_id, video_id, start_time, end_time, filename):
    db = SessionLocal()
    try:
        video = crud.get_video(db, video_id)
        input_path = os.path.join(UPLOAD_DIR, filename)
        trimmed_filename = f"trimmed_{uuid.uuid4().hex[:8]}_{filename}"
        output_path = os.path.join(TRIM_DIR, trimmed_filename)
        ffmpeg.input(input_path, ss=start_time, to=end_time).output(output_path, codec="copy").run(overwrite_output=True)
        size = get_video_size(output_path)
        duration = end_time - start_time
        trimmed_in = schemas.TrimmedVideoBase(
            video_id=video_id,
            filename=trimmed_filename,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            size=size
        )
        crud.create_trimmed_video(db, trimmed_in)
        crud.update_job_status(db, job_id, 'completed', output_path)
        return output_path
    except Exception as e:
        crud.update_job_status(db, job_id, 'failed', None)
        raise e
    finally:
        db.close()

@celery.task(bind=True)
def overlay_task(self, job_id, video_id, overlay_type, config, filename):
    db = SessionLocal()
    try:
        input_path = os.path.join(UPLOAD_DIR, filename)
        output_filename = f"overlay_{uuid.uuid4().hex[:8]}_{filename}"
        output_path = os.path.join(OVERLAY_DIR, output_filename)
        if overlay_type == "text":
            text = config.get("text", "")
            font_size = config.get("font_size", 24)
            x = config.get("x", 10)
            y = config.get("y", 10)
            start = config.get("start", 0)
            end = config.get("end", 5)
            fontfile = config.get("fontfile", None)
            drawtext_args = [
                f"text='{text}'",
                f"fontsize={font_size}",
                f"x={x}",
                f"y={y}",
                f"enable='between(t,{start},{end})'"
            ]
            if fontfile:
                drawtext_args.append(f"fontfile='{fontfile}'")
            drawtext_filter = "drawtext=" + ":".join(drawtext_args)
            ffmpeg.input(input_path).output(output_path, vf=drawtext_filter).run(overwrite_output=True)
        elif overlay_type == "image":
            image_path = config.get("image_path")
            x = config.get("x", 10)
            y = config.get("y", 10)
            start = config.get("start", 0)
            end = config.get("end", 5)
            ffmpeg.filter([
                ffmpeg.input(input_path),
                ffmpeg.input(image_path)
            ], 'overlay', x, y, enable=f'between(t,{start},{end})').output(output_path).run(overwrite_output=True)
        elif overlay_type == "video":
            overlay_video_path = config.get("video_path")
            x = config.get("x", 10)
            y = config.get("y", 10)
            start = config.get("start", 0)
            end = config.get("end", 5)
            ffmpeg.filter([
                ffmpeg.input(input_path),
                ffmpeg.input(overlay_video_path)
            ], 'overlay', x, y, enable=f'between(t,{start},{end})').output(output_path).run(overwrite_output=True)
        else:
            raise Exception("Invalid overlay type")
        overlay_in = schemas.OverlayBase(video_id=video_id, type=overlay_type, config=config)
        crud.create_overlay(db, overlay_in)
        crud.update_job_status(db, job_id, 'completed', output_path)
        return output_path
    except Exception as e:
        crud.update_job_status(db, job_id, 'failed', None)
        raise e
    finally:
        db.close()

@celery.task(bind=True)
def watermark_task(self, job_id, video_id, image_path, x, y, start, end, filename):
    db = SessionLocal()
    try:
        input_path = os.path.join(UPLOAD_DIR, filename)
        output_filename = f"watermark_{uuid.uuid4().hex[:8]}_{filename}"
        output_path = os.path.join(OVERLAY_DIR, output_filename)
        input_stream = ffmpeg.input(input_path)
        watermark_stream = ffmpeg.input(image_path)
        ffmpeg.filter([input_stream, watermark_stream], 'overlay', x, y, enable=f'between(t,{start},{end})').output(output_path).run(overwrite_output=True)
        watermark_in = schemas.WatermarkBase(
            video_id=video_id,
            config={
                "image_path": image_path,
                "x": x,
                "y": y,
                "start": start,
                "end": end
            }
        )
        crud.create_watermark(db, watermark_in)
        crud.update_job_status(db, job_id, 'completed', output_path)
        return output_path
    except Exception as e:
        crud.update_job_status(db, job_id, 'failed', None)
        raise e
    finally:
        db.close()

# Quality settings: resolution height and average video bitrate
QUALITY_PRESETS = {
    "1080p": {"height": 1080, "bitrate": "5000k"},
    "720p": {"height": 720, "bitrate": "2500k"},
    "480p": {"height": 480, "bitrate": "1000k"},
    "360p": {"height": 360, "bitrate": "700k"}
}

@celery.task(bind=True)
def quality_task(self, job_id, video_id, qualities, filename):
    db = SessionLocal()
    try:
        input_path = os.path.join(UPLOAD_DIR, filename)
        generated_files = []

        for quality in qualities:
            if quality not in QUALITY_PRESETS:
                # Skip invalid quality requests
                continue

            preset = QUALITY_PRESETS[quality]
            height = preset["height"]
            bitrate = preset["bitrate"]

            output_filename = f"{quality}_{uuid.uuid4().hex[:8]}_{filename}"
            output_path = os.path.join(QUALITY_DIR, output_filename)

            # FFmpeg command to scale video and set bitrate
            # -vf "scale=-2:H": scales video to height H, width is adjusted automatically to maintain aspect ratio (-2 ensures width is even)
            # -b:v sets the average video bitrate
            # -c:a copy: copies the audio stream without re-encoding
            ffmpeg.input(input_path).output(
                output_path,
                vf=f'scale=-2:{height}',
                **{'b:v': bitrate, 'c:a': 'copy'}
            ).run(overwrite_output=True)

            # Save metadata to the database
            size = get_video_size(output_path)
            quality_in = schemas.VideoQualityBase(
                video_id=video_id,
                quality=quality,
                filename=output_filename,
                size=size
            )
            crud.create_video_quality(db, quality_in)
            generated_files.append(output_path)
        
        # Mark the job as completed
        # The result path can be a simple message since details are in the DB
        result_message = f"Successfully generated qualities: {', '.join(qualities)}"
        crud.update_job_status(db, job_id, 'completed', result_message)
        return {"generated_files": generated_files}

    except Exception as e:
        crud.update_job_status(db, job_id, 'failed', str(e))
        raise e
    finally:
        db.close()