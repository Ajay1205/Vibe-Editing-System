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

## Quality bar (non-negotiable, set by the user)

No compromise on video quality, sound, transitions, captions or sound effects.
- Picture: cut and zoom straight from the raw 4K files (Lanczos), deliver 2160x3840, H.264 CRF 15. Never re-encode a
  delivered file to make a new one; rebuild from the raw footage.
- Captions: render the HyperFrames layer natively at 4K for masters (1080p only for previews).
- Sound: voice is the hero at -14 LUFS; effects levelled by perceived loudness (EBU R128 momentary) to about her speaking
  level; true peak at or below -1.5 dBFS after AAC. Check with `ffmpeg -af ebur128=peak=true`.
- Safe zone (1080x1920 stage): nothing in the top 250 px, the bottom 320 px or 120 px each side. Never cover her face.
- Before sending any render: decode the whole file, check loudness and peaks, and look at frames at every caption beat.
- Never let two encodes write the same output file; wait loops must not `pgrep` their own command line.

## Approved style: Nikita 3 "version 2" (`edits/nikita3`)

The reference for future reels in this account.
- Raw framing, light punch-ins (1.07-1.12x) on the hook, each word title and the word inside each example; face never lifted.
- Captions above her head (y 262-850): Bricolage Grotesque + Poppins Italic for Hinglish; white / electric lime #D7FF3F /
  coral #FF7A59 / peach #FFE2CF on soft dark glass; words blur in one by one; keyword turns lime when it is spoken;
  lime light-sweep transitions between sections; small top chip "1/3 Word Meaning" after each title.
- Hinglish in Roman script ("Yaad rakhiye"), key captions only, never full subtitles.
- Sound: no music; whoosh per section, pop/ping on each example keyword, hits on "better" and "confident", click on the
  comment tap; the user's riser (assets/user/riser_user.mp3) only at its crest (0:02-0:03) and its last 2 s at the end;
  first 2 s voice only.
- Build: `edits/nikita3/build_all.sh` (preview, then 4K master).

## Working rules (from the guide)

- Plan with a beat sheet and wait for approval before building.
- Rough cut first, effects after. Never cut inside a word.
- Snapshot frames and check them before showing work. Save a version (v1, v2...) before each round of notes.
- Reels safe zone: no text in the bottom 20% or near the right edge.
