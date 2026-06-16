"""
Run the Deck-to-Video pipeline locally to generate the demo video.
This script does not require the HTTP server to be running.
"""

import sys
from pathlib import Path

# Add backend to path.
BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app import config
from app.core import narration, pharos, renderer, subtitles, tts, video_builder
from app.main import _run_pipeline
from app.parsers.pptx_parser import parse_pptx
from app.utils import hash as hash_util
from app.utils import storage as storage_util


class FakeRequest:
    """Minimal stand-in for FastAPI Request so we can build public URLs."""

    class URL:
        scheme = "http"
        netloc = "localhost:8000"

    url = URL()


def main():
    pptx_path = Path(__file__).resolve().parent / "pharos-agent-weekly-report.pptx"
    if not pptx_path.exists():
        print(f"Sample deck not found: {pptx_path}")
        print("Run: python examples/generate_sample_ppt.py")
        return

    from uuid import uuid4

    job_id = str(uuid4())
    work_dir = config.OUTPUTS_DIR / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    input_path = work_dir / "input.pptx"
    input_path.write_bytes(pptx_path.read_bytes())

    result = _run_pipeline(
        request=FakeRequest(),
        work_dir=work_dir,
        input_path=input_path,
        script_mode="auto_from_slide_text",
        voice="female_en",
        language="en",
        video_style="crypto_pitch",
        include_subtitles=True,
        watermark=False,
        custom_script=None,
        register_onchain=False,
    )

    # Also copy artifacts into /examples for convenience.
    example_dir = Path(__file__).resolve().parent
    for name in ["output.mp4", "output.srt", "cover.png", "metadata.json"]:
        src = work_dir / name
        if src.exists():
            dst = example_dir / f"generated-{name}"
            dst.write_bytes(src.read_bytes())
            print(f"Copied to {dst}")

    print("\nDemo generation complete:")
    print(f"  Job ID: {job_id}")
    print(f"  Video:  {result['video_url']}")
    print(f"  Hash:   {result['content_hash']}")


if __name__ == "__main__":
    main()
