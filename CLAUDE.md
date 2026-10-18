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

## Where final videos go

Final masters go, untouched (no re-encode, no size reduction), into the speaker's Google Drive folder:
- Nikita: https://drive.google.com/drive/folders/18O_CX2kY7W_qWNL5P_cW8LlSi1v1QAod (folder id 18O_CX2kY7W_qWNL5P_cW8LlSi1v1QAod)
- Manisha: folder link to come from the user.
The Drive connector only uploads content passed inline (fine for small files, not for 4K videos of hundreds of MB), so
send the master in chat and the user drags it into the folder. Never shrink a master to make it fit an upload path.

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

## Approved style: Manisha 3 "Chat Pop" (`edits/manisha3`)

Each video gets a NEW presentation style; only the core rules above carry over. Learned from this one:
- Chat theme for a WhatsApp-replies lesson: notification cards (typing dots, ticks turning blue), ONE reply at a time,
  Hinglish meaning OUTSIDE the card with key words on pink pills; Plus Jakarta Sans + Caveat; mint/teal/cream + pink.
- Text sits straight on the wall with a strong soft shadow. The user disliked solid coloured panels behind Hinglish.
- Pink-peach light-leak bloom transitions (light-style transitions are liked).
- Pacing: keep natural pauses for learners (shorten only long ones), but cut moments where the speaker looks
  down or away, and end right after the last word. Never cut into a word to hit an exact time.
- Readable on a phone but not oversized: modest sizes, contrast from shadows rather than big fonts.
- Manisha's Drive folder: not shared yet; she gets the master from chat.

## Template: "Situation Series" (`edits/nikita4`, restaurant English)

The user wants this as the reusable template for all situation-based videos (restaurant, airport, hospital...).
New video: copy `edits/nikita4`, point `edl.py` at the new footage (CLIPS, EXCLUDE, HOLD_AFTER), then edit only
the CONTENT block of `cues.py` (hook texts, situations with word times, recap, CTA ideas) and run `build_all.sh`.
- Look: tomato #E8452C / mustard #F4B63F / cream #FFF4E0 / charcoal; DM Serif Display titles, Outfit English,
  Kalam for Hinglish (58-60 px with a heavy shadow, the user found 48 px unreadable), Pacifico neon sign.
- Hook: myth book stamped "✗ NAHI" -> felt letter board, letters pop in per spoken word -> neon topic sign.
  (Chat bubbles there were called boring; don't bring them back.)
- Each situation, one after another: animated icon on a dinner plate (or any emoji), "SITUATION n/N" chip, Hindi
  need on the wall, then the English line written word by word on an order ticket; key words get a mustard
  marker; "please" gets a "✨ polite!" stamp. Paper-ticket swipe between situations, candle-glow bloom between sections.
- Reading time: keep her whole pause after each English line (HOLD_AFTER) and hold the ticket READ_HOLD
  (0.7 s) into the next situation. The user flagged a line that was gone half a second after she finished.
- Recap "Today's Menu" card with all lines, then a comment CTA with floating idea chips and a tapped button.
- Sound: no long or bright rings. The desk bell and receipt printer were "unbearable". Use short, soft effects
  well under her voice: pop on the polite stamp, a soft synthesised cha-ching on money moments, quiet whooshes.

## Working rules (from the guide)

- Plan with a beat sheet and wait for approval before building.
- Rough cut first, effects after. Never cut inside a word.
- Snapshot frames and check them before showing work. Save a version (v1, v2...) before each round of notes.
- Reels safe zone: no text in the bottom 20% or near the right edge.
