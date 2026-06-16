from __future__ import annotations

import asyncio
import platform
import subprocess
from pathlib import Path
from typing import List

# Voice mapping for edge-tts (Microsoft Azure neural voices)
EDGE_TTS_VOICES = {
    "male_en": "en-US-GuyNeural",
    "female_en": "en-US-JennyNeural",
    "male_zh": "zh-CN-YunxiNeural",
    "female_zh": "zh-CN-XiaoxiaoNeural",
    "male_ja": "ja-JP-KeitaNeural",
    "female_ja": "ja-JP-NanamiNeural",
    "male_ko": "ko-KR-InJoonNeural",
    "female_ko": "ko-KR-SunHiNeural",
}


def _voice_for(language: str, voice: str) -> str:
    key = f"{voice}_{language}"
    return EDGE_TTS_VOICES.get(key, EDGE_TTS_VOICES.get("female_en", "en-US-JennyNeural"))


def _get_audio_duration(path: Path) -> float:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


async def _edge_tts(text: str, voice: str, out_path: Path) -> bool:
    try:
        import edge_tts

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(out_path))
        return out_path.exists() and out_path.stat().st_size > 0
    except Exception as exc:
        print(f"[tts] edge-tts failed: {exc}")
        return False


def _pyttsx3_tts(text: str, language: str, out_path: Path) -> bool:
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", 170)

        if language == "zh":
            if platform.system() == "Darwin":
                engine.setProperty("voice", "com.apple.speech.synthesis.voice.ting-ting")
        else:
            if platform.system() == "Darwin":
                engine.setProperty("voice", "com.apple.speech.synthesis.voice.samantha")

        engine.save_to_file(text, str(out_path))
        engine.runAndWait()
        return out_path.exists() and out_path.stat().st_size > 0
    except Exception as exc:
        print(f"[tts] pyttsx3 fallback failed: {exc}")
        return False


async def synthesize_slide_audio(
    narrations: List[str],
    voice: str,
    language: str,
    work_dir: Path,
) -> List[dict]:
    """
    Generate one audio file per slide narration.
    Returns a list of {path, duration_seconds} dicts.
    """
    selected_voice = _voice_for(language, voice)
    audio_files = []

    for idx, text in enumerate(narrations):
        out_path = work_dir / f"slide_{idx:03d}.mp3"
        success = await _edge_tts(text, selected_voice, out_path)
        if not success:
            success = _pyttsx3_tts(text, language, out_path)
        if not success:
            # Last resort: create a silent placeholder so the pipeline can continue.
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-nostdin",
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=r=24000:cl=mono",
                    "-t",
                    "3",
                    "-acodec",
                    "libmp3lame",
                    str(out_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        duration = _get_audio_duration(out_path)
        audio_files.append({"path": out_path, "duration_seconds": duration})

    return audio_files
