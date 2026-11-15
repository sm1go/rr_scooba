#!/usr/bin/env bash
# Export the HTML slide decks in docs/04-pitch to PDF (one 16:9 page per slide) with headless Chrome.
set -euo pipefail
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
cd "$(dirname "$0")/../docs/04-pitch"
base="$(cygpath -m "$PWD" 2>/dev/null || pwd)"
for f in presentation team-projects/otapath-beyond-the-clinic team-projects/muutto-internet-butler team-projects/taimi-personal-economic-trainer; do
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --window-size=1920,1080 \
    --virtual-time-budget=8000 --print-to-pdf="$base/$f.pdf" "file:///$base/$f.html" 2>/dev/null
done
