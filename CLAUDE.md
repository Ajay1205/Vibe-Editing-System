# Vibe Editing System

Talking-head video editing with HyperFrames, following the Ideabro Studio "Vibe Editing System" guide:
transcribe -> pull frames -> beat sheet (wait for OK) -> rough cut -> effects -> snapshot -> render.

## Cloud environment notes (verified 2026-10-17)

- Prefix every `npx hyperframes` command with
  `NODE_USE_ENV_PROXY=1 NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt`, or model downloads fail with "fetch failed".
- cdn.jsdelivr.net is blocked. The render browser can't load GSAP from it and fails with
  `sub_timeline_script_failure`. Copy `node_modules/gsap/dist/gsap.min.js` into the project's `vendor/`
  folder and point the `<script src>` at it. Load any other CDN library from npm the same way.
- Transcription: `hyperframes transcribe <video> --engine parakeet` (word timings to `transcript.json`).
  Fix the spelling of names afterwards. Parakeet misspells them, e.g. "Ajay" -> "Adjay", "Ideabro" -> "IdeaBro".
- faster-whisper can't decode files here (PyAV 19 clash). Decode with ffmpeg to 16 kHz mono float32 and pass the array.
- Before building, re-encode phone footage with regular keyframes, or seeks freeze:
  `ffmpeg -i take.mp4 -c:v libx264 -r 30 -g 30 -keyint_min 30 -movflags +faststart -c:a copy take.cfr.mp4`
- No GPU. `remove-background` runs at about 1.4 fps at 1080p. Cut out only the sections that need it.
- No empty-room shot? Run `python3 -I tools/make_clean_plate.py take.mp4 take.fg.webm -o clean_plate.png`
  (the cutout comes from remove-background). Check `never_uncovered_pct` in its output.
- Installs live only in this container. In a new session, reinstall with `npm ci`,
  `pip3 install --break-system-packages faster-whisper opencv-python-headless onnxruntime`,
  `npx hyperframes browser ensure` and `npx hyperframes models install parakeet`.
- Don't commit raw footage or renders.

## Working rules (from the guide)

- Plan with a beat sheet and wait for approval before building.
- Rough cut first, effects after. Never cut inside a word.
- Snapshot frames and check them before showing work. Save a version (v1, v2...) before each round of notes.
- Reels safe zone: no text in the bottom 20% or near the right edge.
