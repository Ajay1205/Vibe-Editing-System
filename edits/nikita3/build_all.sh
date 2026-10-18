#!/usr/bin/env bash
# Full build of the approved Nikita 3 reel (version 2): 1080p preview first, then the 4K master.
# Re-run after changing edl.py / cues.py / build_overlay_v2.py / mix.py.
# Needs footage/raw/nikita_3.{1..4}.mov and assets/user/riser_user.mp3 (kept out of git).
set -euo pipefail
cd "$(dirname "$0")"
export NODE_USE_ENV_PROXY=1 NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt
HF="npx --prefix ../.. hyperframes"

python3 -I edl.py                       # cut list (only cuts inside measured silence)
python3 -I cues.py                      # captions, zooms, sound effects, all anchored to spoken words
python3 -I render_base.py voice         # frame-accurate voice track
python3 -I mix.py                       # voice -14 LUFS, effects by perceived loudness, peaks <= -1.5 dBFS

# 1080p preview for review
python3 -I render_base.py v2 --preview
python3 -I build_overlay_v2.py --preview
(cd overlay_v2 && $HF render --format webm --quality delivery --fps 30 -o ../build/overlay_v2_1080.webm)
python3 -I compose.py v2 --preview

# 4K master: picture straight from the raw 4K files, captions rendered natively at 4K
python3 -I render_base.py v2
python3 -I build_overlay_v2.py
(cd overlay_v2 && $HF render --format webm --quality delivery --fps 30 -o ../build/overlay_v2_2160.webm)
python3 -I compose.py v2
