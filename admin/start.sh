#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m streamlit run admin/app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
