# API Documentation

## Base URL

Local development: `http://localhost:8000`

## Endpoints

### `GET /health`

Health check.

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status":"ok","service":"agent-deck-to-video-skill"}
```

### `POST /skill/generate`

Generate a narrated video from a PPTX file.

```bash
curl -X POST http://localhost:8000/skill/generate \
  -F "pptx_file=@examples/pharos-agent-weekly-report.pptx" \
  -F "video_style=crypto_pitch" \
  -F "voice=female_en" \
  -F "language=en" \
  -F "include_subtitles=true" \
  -F "register_onchain=false"
```

Using a remote URL:

```bash
curl -X POST http://localhost:8000/skill/generate \
  -F "ppt_url=https://example.com/deck.pptx" \
  -F "video_style=business" \
  -F "voice=male_en"
```

Response:
```json
{
  "status": "success",
  "job_id": "e664bf78-8a15-454e-b0e5-df29a16e5752",
  "video_url": "http://localhost:8000/outputs/e664bf78-8a15-454e-b0e5-df29a16e5752/output.mp4",
  "subtitle_url": "http://localhost:8000/outputs/e664bf78-8a15-454e-b0e5-df29a16e5752/output.srt",
  "cover_image_url": "http://localhost:8000/outputs/e664bf78-8a15-454e-b0e5-df29a16e5752/cover.png",
  "metadata_url": "http://localhost:8000/outputs/e664bf78-8a15-454e-b0e5-df29a16e5752/metadata.json",
  "duration_seconds": 87.7,
  "slides_count": 5,
  "content_hash": "972a7fd44274b5b53743e9f0080782fa2db863d4fe0e7175dbcc41a5df480ea0",
  "pharos_tx_hash": null,
  "metadata": {
    "title": "Pharos Agent Economy",
    "language": "en",
    "voice": "female_en",
    "style": "crypto_pitch"
  }
}
```

### `GET /videos/{job_id}`

Fetch the generated `metadata.json` for a job.

```bash
curl http://localhost:8000/videos/e664bf78-8a15-454e-b0e5-df29a16e5752
```

## Serving Output Files

The backend mounts `/outputs` as a static file directory. Any file written to `data/outputs/{job_id}/` is accessible at `http://localhost:8000/outputs/{job_id}/{filename}`.

In production, replace this with an object-store (IPFS, S3, Arweave) and return those URIs.
