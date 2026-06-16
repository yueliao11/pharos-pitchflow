from __future__ import annotations

import asyncio
import json
import shutil
import uuid
from pathlib import Path
from typing import Optional

import requests
import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.core import narration, pharos, renderer, subtitles, tts, video_builder
from app.parsers.pptx_parser import parse_pptx
from app.utils import hash as hash_util
from app.utils import storage as storage_util

app = FastAPI(
    title="Agent Narrated Deck-to-Video Skill",
    description="Reusable AI Agent Skill that transforms decks into narrated, verifiable videos.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=config.OUTPUTS_DIR), name="outputs")


def _base_url(request) -> str:
    return f"{request.url.scheme}://{request.url.netloc}"


def _download(url: str, dest: Path) -> None:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)


def _run_pipeline(
    request,
    work_dir: Path,
    input_path: Path,
    script_mode: str,
    voice: str,
    language: str,
    video_style: str,
    include_subtitles: bool,
    watermark: bool,
    custom_script: Optional[str],
    register_onchain: bool,
) -> dict:
    # 1. Parse deck.
    slides = parse_pptx(input_path)
    if not slides:
        raise HTTPException(status_code=400, detail="No slides found in the uploaded deck.")

    # 2. Narration.
    narrations = narration.generate_narration(
        slides,
        mode=script_mode,
        style=video_style,
        language=language,
        custom_script=custom_script,
    )

    # 3. Render slide images.
    image_paths: list[Path] = []
    for idx, slide in enumerate(slides):
        img_path = work_dir / f"slide_{idx:03d}.png"
        renderer.render_slide(
            slide,
            idx,
            len(slides),
            style=video_style,
            language=language,
            watermark=watermark,
            caption=narrations[idx] if include_subtitles else None,
            output_path=img_path,
        )
        image_paths.append(img_path)

    # 4. Text-to-speech.
    audio_infos = asyncio.run(
        tts.synthesize_slide_audio(narrations, voice, language, work_dir)
    )
    audio_paths = [info["path"] for info in audio_infos]
    durations = [info["duration_seconds"] for info in audio_infos]

    # 5. Subtitles.
    srt_path = work_dir / "output.srt"
    subtitles.build_srt(narrations, durations, srt_path)

    # 6. Cover image.
    cover_path = work_dir / "cover.png"
    first_title = slides[0].get("title") or "Agent Generated Video"
    renderer.render_cover(
        first_title,
        subtitle="Powered by Pharos · AI Agent Economy",
        style=video_style,
        language=language,
        output_path=cover_path,
    )

    # 7. Compose final video.
    video_path = work_dir / "output.mp4"
    video_builder.build_video(image_paths, audio_paths, durations, video_path)

    # 8. Hash & metadata.
    content_hash = hash_util.sha256_file(video_path)

    title = slides[0].get("title") or "Agent Narrated Video"
    metadata = {
        "title": title,
        "language": language,
        "voice": voice,
        "style": video_style,
        "slides_count": len(slides),
        "duration_seconds": round(sum(durations), 2),
        "content_hash": content_hash,
        "files": {
            "video": "output.mp4",
            "subtitle": "output.srt",
            "cover": "cover.png",
            "metadata": "metadata.json",
        },
        "narrations": narrations,
    }
    metadata_path = storage_util.save_metadata(work_dir, metadata)

    # 9. Build public URLs.
    base = _base_url(request)
    job_id = work_dir.name
    video_url = f"{base}/outputs/{job_id}/output.mp4"
    subtitle_url = f"{base}/outputs/{job_id}/output.srt"
    cover_url = f"{base}/outputs/{job_id}/cover.png"
    metadata_url = f"{base}/outputs/{job_id}/metadata.json"

    # 10. On-chain registration.
    tx_hash: Optional[str] = None
    if register_onchain:
        tx_hash = pharos.register_video(
            title=title,
            video_uri=video_url,
            metadata_uri=metadata_url,
            content_hash_hex=content_hash,
        )

    return {
        "status": "success",
        "job_id": job_id,
        "video_url": video_url,
        "subtitle_url": subtitle_url,
        "cover_image_url": cover_url,
        "metadata_url": metadata_url,
        "duration_seconds": metadata["duration_seconds"],
        "slides_count": len(slides),
        "content_hash": content_hash,
        "pharos_tx_hash": tx_hash,
        "metadata": {
            "title": title,
            "language": language,
            "voice": voice,
            "style": video_style,
        },
    }


def _send_callback(callback_url: str, payload: dict) -> None:
    try:
        requests.post(callback_url, json=payload, timeout=30)
    except Exception as exc:
        print(f"[callback] failed to notify {callback_url}: {exc}")


@app.get("/health")
def health():
    return {"status": "ok", "service": "agent-deck-to-video-skill"}


@app.post("/skill/generate")
async def generate(
    request: Request,
    background_tasks: BackgroundTasks,
    pptx_file: Optional[UploadFile] = File(None),
    ppt_url: Optional[str] = Form(None),
    script_mode: str = Form("auto_from_slide_text"),
    voice: str = Form("female_en"),
    language: str = Form("en"),
    video_style: str = Form("crypto_pitch"),
    output_format: str = Form("mp4"),
    include_subtitles: bool = Form(True),
    watermark: bool = Form(False),
    callback_url: Optional[str] = Form(None),
    custom_script: Optional[str] = Form(None),
    register_onchain: bool = Form(False),
):
    """
    Main Skill endpoint.
    Accepts either an uploaded PPTX file or a remote ppt_url.
    """
    if not pptx_file and not ppt_url:
        raise HTTPException(status_code=400, detail="Provide either pptx_file or ppt_url.")

    job_id = str(uuid.uuid4())
    work_dir = config.OUTPUTS_DIR / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    input_path = work_dir / "input.pptx"

    if pptx_file:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(pptx_file.file, f)
    else:
        await asyncio.to_thread(_download, ppt_url, input_path)

    try:
        result = await asyncio.to_thread(
            _run_pipeline,
            request,
            work_dir,
            input_path,
            script_mode,
            voice,
            language,
            video_style,
            include_subtitles,
            watermark,
            custom_script,
            register_onchain,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {exc}")

    if callback_url:
        background_tasks.add_task(_send_callback, callback_url, result)

    return JSONResponse(content=result)


@app.get("/videos/{job_id}")
def get_video_metadata(job_id: str):
    meta_path = config.OUTPUTS_DIR / job_id / "metadata.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Video not found.")
    return JSONResponse(content=json.loads(meta_path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    uvicorn.run(app, host=config.HOST, port=config.PORT)
