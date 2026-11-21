#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if curl --silent --fail http://127.0.0.1:8501/_stcore/health >/dev/null 2>&1; then
  echo "Vexa Admin already running"
  exit 0
fi
python -m streamlit --version >/dev/null
nohup python -m streamlit run admin/app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false </dev/null >/tmp/vexa-admin.log 2>&1 &
echo "Vexa Admin starting on private port 8501. Log: /tmp/vexa-admin.log"
