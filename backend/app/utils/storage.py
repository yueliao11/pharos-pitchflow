from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict


def save_metadata(work_dir: Path, metadata: Dict[str, Any]) -> Path:
    path = work_dir / "metadata.json"
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def make_public_copy(src: Path, public_dir: Path) -> Path:
    public_dir.mkdir(parents=True, exist_ok=True)
    dst = public_dir / src.name
    shutil.copy2(src, dst)
    return dst
