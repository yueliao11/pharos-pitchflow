from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List


def build_video(
    slide_images: List[Path],
    audio_files: List[Path],
    durations: List[float],
    output_path: Path,
    fps: int = 30,
) -> Path:
    """
    Build the final MP4 from slide images and per-slide audio files.
    Each slide is shown for the corresponding duration (audio length).
    """
    if not slide_images or not audio_files:
        raise ValueError("At least one slide image and one audio file are required.")

    work_dir = output_path.parent
    video_only = work_dir / "video_only.mp4"
    audio_list = work_dir / "audio_list.txt"
    audio_only = work_dir / "audio_only.aac"

    # Clamp durations to a minimum visible length.
    safe_durations = [max(2.0, d) for d in durations]

    # ---------- 1. Build silent video from images ----------
    inputs: List[str] = []
    for img, duration in zip(slide_images, safe_durations):
        inputs.extend(["-loop", "1"])
        inputs.extend(["-t", str(duration)])
        inputs.extend(["-i", str(img)])

    filter_parts: List[str] = []
    for idx, duration in enumerate(safe_durations):
        filter_parts.append(
            f"[{idx}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"fps={fps},format=yuv420p,setpts=PTS-STARTPTS[v{idx}];"
        )
    concat_inputs = "".join(f"[v{idx}]" for idx in range(len(slide_images)))
    filter_parts.append(
        f"{concat_inputs}concat=n={len(slide_images)}:v=1:a=0[vv]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-nostdin",
        *inputs,
        "-filter_complex",
        "".join(filter_parts),
        "-map",
        "[vv]",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(video_only),
    ]
    log1 = work_dir / "ffmpeg_video.log"
    with log1.open("w") as log:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=log, check=True)

    # ---------- 2. Build concatenated audio ----------
    audio_list.write_text(
        "\n".join(f"file '{a.resolve()}'" for a in audio_files), encoding="utf-8"
    )
    log2 = work_dir / "ffmpeg_audio.log"
    with log2.open("w") as log:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-nostdin",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(audio_list),
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-ar",
                "48000",
                str(audio_only),
            ],
            stdout=subprocess.DEVNULL,
            stderr=log,
            check=True,
        )

    # ---------- 3. Merge video + audio ----------
    log3 = work_dir / "ffmpeg_merge.log"
    with log3.open("w") as log:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-nostdin",
                "-i",
                str(video_only),
                "-i",
                str(audio_only),
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-ar",
                "48000",
                "-shortest",
                str(output_path),
            ],
            stdout=subprocess.DEVNULL,
            stderr=log,
            check=True,
        )

    return output_path
