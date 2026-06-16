from __future__ import annotations

from pathlib import Path
from typing import List


def _format_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds % 1) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_srt(
    narrations: List[str],
    durations: List[float],
    output_path: Path,
) -> Path:
    """Build an SRT subtitle file aligned to slide durations."""
    entries: List[str] = []
    cursor = 0.0
    for idx, (text, duration) in enumerate(zip(narrations, durations), start=1):
        duration = max(2.0, duration)
        start = cursor
        end = cursor + duration
        entries.append(str(idx))
        entries.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
        entries.append(text.strip())
        entries.append("")
        cursor = end

    output_path.write_text("\n".join(entries).strip(), encoding="utf-8")
    return output_path
