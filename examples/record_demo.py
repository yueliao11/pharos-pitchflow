"""
Record a browser demo of the PitchFlow frontend using Playwright.
The output webm is converted to MP4 with ffmpeg.
"""

import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PPTX = ROOT / "examples" / "demo_one_slide.pptx"
RECORD_DIR = ROOT / "examples" / "recordings"
RECORD_DIR.mkdir(exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(RECORD_DIR),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        print("Open frontend...")
        page.goto("http://localhost:3000")
        page.wait_for_load_state("networkidle")
        time.sleep(1.5)

        print("Upload PPTX...")
        page.set_input_files("#pptxFile", str(PPTX))
        time.sleep(1)

        print("Click generate...")
        page.click("#generateBtn")

        print("Wait for result...")
        page.wait_for_selector("#resultCard", state="visible", timeout=300_000)
        time.sleep(2)

        print("Play generated video...")
        page.evaluate("document.querySelector('#previewVideo').play()")
        time.sleep(12)

        video_path = Path(page.video.path())
        print(f"WebM recorded: {video_path}")

        context.close()
        browser.close()

    mp4_path = ROOT / "examples" / "demo_recording.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-nostdin",
            "-i",
            str(video_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "30",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "1",
            str(mp4_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    print(f"MP4 saved: {mp4_path}")


if __name__ == "__main__":
    main()
