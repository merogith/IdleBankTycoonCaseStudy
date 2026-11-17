#!/usr/bin/env bash
# Compatibility entry point; the Python builder serves local assets and records freshness.
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/build_pdf.py
