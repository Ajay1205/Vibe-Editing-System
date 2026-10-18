#!/usr/bin/env bash
# Full build of the Nikita 4 reel ("Restaurant Menu" style): 1080p preview first, then the 4K master.
# Re-run after changing edl.py / cues.py / build_overlay.py / mix.py.
# Needs footage/nikita4/raw/nikita_4.{1,2}.mov (+ audio/transcripts) and assets/shared/riser_user.mp3.
set -euo pipefail
cd "$(dirname "$0")"
export NODE_USE_ENV_PROXY=1 NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt
HF="npx --prefix ../.. hyperframes"

python3 -I make_sfx.py                  # desk bell, receipt printer, stamp, neon (synthesised)
python3 -I edl.py                       # cut list (only cuts inside measured silence)
python3 -I cues.py                      # captions, zooms, sound effects, all anchored to spoken words
python3 -I render_base.py voice         # frame-accurate voice track
python3 -I mix.py                       # voice -14 LUFS, effects by perceived loudness, peaks <= -1.5 dBFS

# 1080p preview for review
python3 -I render_base.py v1 --preview
python3 -I build_overlay.py --preview
(cd overlay && $HF render --format webm --quality delivery --fps 30 -o ../build/overlay_v1_1080.webm)
python3 -I compose.py v1 --preview

# 4K master: picture straight from the raw 4K files, captions rendered natively at 4K
python3 -I render_base.py v1
python3 -I build_overlay.py
(cd overlay && $HF render --format webm --quality delivery --fps 30 -o ../build/overlay_v1_2160.webm)
python3 -I compose.py v1
