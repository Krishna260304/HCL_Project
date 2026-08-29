#!/usr/bin/env bash
# ==============================================================================
# LearnPath AI - AI/ML Service Development Launcher
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")"

cd "$SERVICE_DIR"

# Export Python path
export PYTHONPATH="$SERVICE_DIR:$PYTHONPATH"

echo "============================================================"
echo " Starting LearnPath AI/ML Service on http://0.0.0.0:8001"
echo "============================================================"

exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
