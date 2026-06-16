# Demo Flow

## What the demo shows

1. A sample pitch deck (`examples/pharos-agent-weekly-report.pptx`) is created programmatically.
2. The Deck-to-Video Skill parses the deck, generates narration, renders slide images, produces audio, and composes an MP4.
3. The Skill outputs video, subtitles, cover image, metadata JSON and a content hash.
4. (Optional) The content hash can be registered on the Pharos testnet via `AgentVideoRegistry`.
5. (Optional) A viewer can pay/tip the Agent through `PaymentGate`.

## Run the demo without the HTTP server

```bash
cd pharos-pitchflow
source backend/.venv/bin/activate
python examples/generate_sample_ppt.py
python examples/generate_demo.py
```

Outputs appear in:
- `data/outputs/{job_id}/` (served by the API)
- `examples/generated-output.mp4`
- `examples/generated-output.srt`
- `examples/generated-cover.png`
- `examples/generated-metadata.json`

## Run the full stack

Terminal 1 — backend:
```bash
cd pharos-pitchflow/backend
source .venv/bin/activate
python -m app.main
```

Terminal 2 — frontend (static files):
```bash
cd pharos-pitchflow/frontend
python3 -m http.server 3000
```

Open `http://localhost:3000` in a browser, upload the sample PPTX, and generate a video.

## Demo video

The pre-generated demo video is available at:
- `examples/generated-output.mp4`

It is a 5-slide, ~90-second narrated pitch about the Pharos Agent Economy and the PitchFlow Skill.
