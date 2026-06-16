import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT.parent / "data")).resolve()
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

PHAROS_RPC = os.getenv("PHAROS_RPC", "https://testnet.pharosnetwork.xyz")
PHAROS_CHAIN_ID = int(os.getenv("PHAROS_CHAIN_ID", "500"))
PHAROS_REGISTRY_ADDRESS = os.getenv("PHAROS_REGISTRY_ADDRESS")
PHAROS_PAYMENT_ADDRESS = os.getenv("PHAROS_PAYMENT_ADDRESS")
AGENT_ADDRESS = os.getenv("AGENT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
