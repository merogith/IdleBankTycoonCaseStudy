#!/usr/bin/env bash
#
# Rebuild docs/case-study.pdf from the single source, idle-bank-tycoon.html.
#
# The PDF is a BUILD OUTPUT, not a hand-maintained file. The original was a
# browser "Print to PDF" (Producer: Skia/PDF, i.e. Chromium), which is why it
# drifted out of sync with the site. This script reproduces that pipeline so the
# PDF is always regenerated from the corrected HTML and can never drift again.
#
# Usage:   scripts/build-pdf.sh
# Needs:   Google Chrome or Chromium (a real binary, not the Ubuntu snap stub).
#
set -euo pipefail

cd "$(dirname "$0")/.."
SRC="idle-bank-tycoon.html"
OUT="docs/case-study.pdf"

# Find a usable Chrome/Chromium binary. google-chrome is tried first because the
# Ubuntu `chromium-browser` wrapper is often a snap stub that cannot run headless.
CHROME=""
for c in \
  google-chrome google-chrome-stable chrome chromium chromium-browser \
  microsoft-edge microsoft-edge-stable \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
  if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then CHROME="$c"; break; fi
done

if [ -z "$CHROME" ]; then
  echo "error: no Chrome/Chromium found. Install Google Chrome, or open" >&2
  echo "       $SRC in any browser and use Print → Save as PDF → $OUT." >&2
  exit 1
fi

echo "Rendering $SRC → $OUT  (via: $CHROME)"
"$CHROME" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=3000 \
  --print-to-pdf="$OUT" \
  "file://$PWD/$SRC"

if [ -s "$OUT" ]; then
  echo "ok: wrote $OUT ($(wc -c < "$OUT") bytes)"
else
  echo "error: $OUT was not produced" >&2
  exit 1
fi
