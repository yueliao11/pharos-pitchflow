#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

if [ ! -d "backend/.venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv backend/.venv
fi

source backend/.venv/bin/activate
pip install -q -r backend/requirements.txt

echo "Generating sample PPTX..."
python examples/generate_sample_ppt.py

echo "Generating demo video (this takes ~2 minutes)..."
python examples/generate_demo.py

echo ""
echo "Demo artifacts are in examples/generated-*"
