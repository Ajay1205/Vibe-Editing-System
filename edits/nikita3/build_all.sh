#!/usr/bin/env bash
# Full 4K build of both versions. Re-run after changing edl.py / cues.py / build_overlay.py / mix.py.
set -euo pipefail
cd "$(dirname "$0")"
export NODE_USE_ENV_PROXY=1 NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt
HF="npx --prefix ../.. hyperframes"

python3 -I edl.py
python3 -I cues.py
python3 -I build_overlay.py
python3 -I render_base.py voice
python3 -I mix.py
(cd overlay && $HF render --format webm --quality delivery --fps 30 -o ../build/overlay.webm)
python3 -I render_base.py v1
python3 -I render_base.py v2
python3 -I compose.py v1
python3 -I compose.py v2
