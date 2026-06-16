# Agent Narrated Deck-to-Video Skill (PitchFlow)

> **A reusable AI-Agent Skill that turns decks, reports, and on-chain analysis into narrated videos — verifiable, payable, and composable on Pharos.**

Instead of treating this as a "PPT-to-video tool", PitchFlow is positioned as the **expression layer** of the AI-Agent economy:

- Any Agent can call it to produce human-readable video content.
- Other Skills can feed it wallet analysis, DAO reports, RWA data, or research summaries.
- Generated videos receive a `sha256` content hash that can be registered on Pharos for provenance.
- Users can pay or tip Agents via the on-chain `PaymentGate`.

This makes the Skill natively compatible with the Pharos AI-Agent economy, RealFi/RWA, stablecoin payments, and cross-chain content distribution.

---

## Problem

Agents on Pharos can already trade, analyze wallets, monitor transactions, and generate reports. But they usually output:

- Raw JSON
- Static tables
- Text walls

Most humans cannot quickly parse these outputs. Project teams, DAOs, and educators need a way for Agents to **explain, present, and monetize** their work.

## Solution

**Agent Narrated Deck-to-Video Skill** gives Agents a standardized multimedia output:

1. Accepts a PPTX file or URL.
2. Extracts slide text and speaker notes.
3. Generates narration (auto or from speaker notes / custom script).
4. Renders each slide as a styled 1920×1080 frame.
5. Synthesizes voice-over with neural TTS.
6. Composes an MP4 with synchronized slides, audio, and burned-in subtitles.
7. Produces cover image, SRT subtitle, and structured metadata.
8. Computes `sha256(video)` and optionally registers it on Pharos.

---

## Repository Structure

```
pharos-pitchflow/
├── README.md
├── docs/
│   ├── skill-spec.md
│   ├── api.md
│   ├── pharos-integration.md
│   └── demo-flow.md
├── contracts/
│   ├── AgentVideoRegistry.sol
│   └── PaymentGate.sol
├── test/
│   ├── AgentVideoRegistry.test.js
│   └── PaymentGate.test.js
├── hardhat.config.js
├── deploy.js
├── package.json
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py                 # FastAPI Skill server
│       ├── config.py
│       ├── parsers/pptx_parser.py
│       └── core/
│           ├── narration.py
│           ├── tts.py
│           ├── renderer.py
│           ├── video_builder.py
│           ├── subtitles.py
│           └── pharos.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── examples/
│   ├── pharos-agent-weekly-report.pptx
│   ├── generate_sample_ppt.py
│   ├── generate_demo.py
│   ├── run_demo.sh
│   ├── pitchflow-demo-video.mp4
│   ├── generated-output.mp4
│   ├── generated-output.srt
│   ├── generated-cover.png
│   └── generated-metadata.json
├── assets/
│   ├── logo.png
│   └── cover.png
└── data/
    ├── uploads/
    └── outputs/
```

---

## Architecture

```
User / DAO / Project Team
        ↓
Upload PPTX / document / on-chain data
        ↓
AI Agent Orchestrator
        ↓
Deck-to-Video Skill (this repo)
  - PPT parsing
  - Narration generation
  - TTS audio
  - Slide rendering
  - Video composition
  - Subtitles + metadata
        ↓
Storage Layer (local / IPFS / S3 / Arweave)
        ↓
Pharos On-chain Layer
  - Content hash registry
  - Agent execution record
  - Payment / tip record
        ↓
Distribution Layer
  - Telegram, Discord, X, DAO forum
```

---

## Quick Start

### 1. Clone & setup

```bash
cd pharos-pitchflow
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Generate the demo video (no server needed)

```bash
bash examples/run_demo.sh
```

Or step by step:

```bash
python examples/generate_sample_ppt.py
python examples/generate_demo.py
```

You will get:
- `examples/pitchflow-demo-video.mp4` — narrated product intro + auto-generated pitch video
- `examples/generated-output.mp4` — the auto-generated pitch video only
- `examples/generated-output.srt`
- `examples/generated-cover.png`
- `examples/generated-metadata.json`

### 3. Run the API server

```bash
cd backend
source .venv/bin/activate
python -m app.main
```

Server starts at `http://localhost:8000`.

### 4. Call the Skill

```bash
curl -X POST http://localhost:8000/skill/generate \
  -F "pptx_file=@../examples/pharos-agent-weekly-report.pptx" \
  -F "video_style=crypto_pitch" \
  -F "voice=female_en" \
  -F "include_subtitles=true"
```

### 5. Run the frontend

```bash
cd frontend
python3 -m http.server 3000
```

Open `http://localhost:3000`, upload a PPTX, and watch the Agent generate a video.

---

## Smart Contracts

```bash
npm install
cp .env.example .env
# edit .env with your private key and Pharos RPC
npm run compile
npm run deploy:testnet
```

Then copy the printed contract addresses into `backend/.env` to enable on-chain registration and payments.

---

## Skill Input / Output

See [`docs/skill-spec.md`](docs/skill-spec.md) and [`docs/api.md`](docs/api.md) for the full schema.

Minimal input:

```json
{
  "ppt_url": "https://example.com/deck.pptx",
  "script_mode": "auto_from_slide_text",
  "voice": "female_en",
  "language": "en",
  "video_style": "crypto_pitch",
  "output_format": "mp4",
  "include_subtitles": true,
  "register_onchain": false
}
```

Minimal output:

```json
{
  "status": "success",
  "video_url": "...",
  "subtitle_url": "...",
  "cover_image_url": "...",
  "duration_seconds": 87.7,
  "slides_count": 5,
  "content_hash": "0x...",
  "pharos_tx_hash": "0x..."
}
```

---

## Use Cases

1. **Web3 project auto-pitch video** — upload a whitepaper or pitch deck; Agent produces a 3-minute English pitch.
2. **DAO weekly report video** — treasury, proposals, and on-chain activity narrated automatically.
3. **Wallet analysis video report** — combine with a wallet-analyzer Skill and turn JSON into a video summary.
4. **On-chain education** — generate tutorials for Pharos testnet, RWA, stablecoins, cross-chain bridging.
5. **Agent-paid content service** — user pays USDC/native token, Agent generates and registers a video, creator earns.

---

## Differentiation

| Traditional PPT-to-video tool | PitchFlow Skill |
|------------------------------|-----------------|
| Built for humans clicking buttons | Built for AI Agents calling an API |
| Outputs a file | Outputs a verifiable, composable content asset |
| No provenance | Content hash registered on Pharos |
| No payments | Native / stablecoin payment & tipping layer |
| Standalone | Composable with wallet, DAO, research, and social Skills |

---

## Future: PitchFlow Agent (Agent Arena)

In the next stage we will extend this Skill into a full Agent:

- Accept project links, whitepapers, DAO treasury addresses, or wallet addresses.
- Auto-generate or refine a pitch deck.
- Call this Skill to produce a narrated video.
- Register the content hash on Pharos.
- Accept on-chain payment, tips, or subscriptions.
- Distribute the video to Telegram, Discord, X, and DAO forums.

**Agent name:** PitchFlow Agent  
**Tagline:** *From deck to on-chain narrated video.*

---

## License

MIT — built for the Pharos AI Agent Hackathon.
