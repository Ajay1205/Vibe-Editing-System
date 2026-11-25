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

## Fresh-session rebuild (verified 2026-11-18, Nikita 6 rebuilt end to end)

- Raw takes live in Google Drive (`Insta English Account/Raw Videos/<Name> Raw Videos/Video N...`). The environment
  allows drive.google.com and drive.usercontent.google.com, so download link-shared files with
  `curl -L "https://drive.usercontent.google.com/download?id=<FILE_ID>&export=download&confirm=t"` (the Drive
  connector's download returns base64 and is unusable for video). Put them in `footage/<edit>/raw/` under the names
  the edit's scripts expect (e.g. `footage/nikita6/raw/nikita_6.1.mov`).
- mix.py reads SFX from `~/.claude/skills/media-use/audio/assets/sfx`. After `npm ci`, link it:
  `ln -sfn "$PWD/node_modules/hyperframes/dist/skills/media-use" ~/.claude/skills/media-use`.
- `edits/*/overlay/fonts/` is git-ignored: copy the edit's fonts from `board/fonts/` into `overlay/fonts/` before
  rendering the overlay.
- Overlay render: `npx hyperframes render overlay --format webm -o build/overlay_v1_<1080|2160>.webm` (from the edit
  folder, with the proxy env vars above), then `mix.py` and `compose.py v1 [--preview]`.
- skia-python (used by some toolkit scripts) needs `apt-get install -y libegl1 libgl1 libfontconfig1`.

## GitHub is for the English-speaking account only (user rule)

This repo and its GitHub remote hold ONLY the English-speaking account's work (Nikita, Manisha). One-off client jobs
for other brands stay entirely local: work in a git-ignored folder (`footage/<client>/`), never commit or push their
scripts, notes or renders, and don't mention them in this file.

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
- Manisha: folder link to come from the user. (Manisha 7 was shared from a Drive file owned by another account.)
The Drive connector only uploads content passed inline (fine for small files, not for 4K videos of hundreds of MB), so
send the master in chat and the user drags it into the folder. Never shrink a master to make it fit an upload path.
Chat file limit is 400 MiB. A bigger master (Nikita 6: 426 MiB at CRF 15; slower x264 presets don't shrink it) is split
losslessly at a keyframe (`ffmpeg -i m.mp4 -c copy -map 0 -f segment -segment_times <t> -reset_timestamps 1 m_part%d.mp4`),
checked by rejoining (concat demuxer) and comparing the video MD5 with the master, then sent as parts.
BUT a Reel must be ONE file (user, 18 Nov: "it will go on Instagram, I cannot upload it in 2 parts"). For a reel master
over the limit, encode the final composite at CRF 16 instead (`compose.py v1 --crf 16`; Nikita 6: 361 MiB, -15 %),
built from the same 4K base + caption layer, never from the delivered file. Parts are only for non-reel deliveries.

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

## Template: "Situation Series" (`edits/nikita4`, v3 "Close & Bold")

The user wants this as the reusable template for all situation-based videos (restaurant, airport, hospital...).
New video: copy `edits/nikita4`, point `edl.py` at the new footage (CLIPS, EXCLUDE, HOLD_AFTER), then edit only
the CONTENT block of `cues.py` (series banner, hook lines, situations with word times and sticker emoji, recap,
CTA ideas) and run `build_all.sh`.
- The v2 "restaurant menu/ticket" look (wide shot, small text on the wall far above her head, cream tickets,
  letter board) was called boring and unappealing. Kept only as `build_overlay_v2_menu.py`; don't go back to it.
- Picture: shots from `cues.json` cut between mid (1.30x), ask (1.46x, on "English mein kaise bologe?") and
  close (1.68x, on every English line), each slowly pushing in 3.5%; warm edge flash on close cut-ins.
- Captions big and bold at CHEST level (y 1100-1600), like the reference reels; question title ("Restaurant mein / English kaise bolein?", user picked it over a label pill) + progress
  dots at the top; a big emoji sticker pops beside her head for each situation.
- Hindi need: big white Outfit 64 px, heavy shadow, NO panel (the user dislikes panels behind Hinglish).
  English line: butter-yellow card, maroon Outfit 900, key words on a tomato pill, "please" green + "🙏 polite".
- Reading time: keep her whole pause after each English line (HOLD_AFTER) and hold the card READ_HOLD (0.7 s)
  into the next situation. The user flagged a line that was gone half a second after she finished.
- Sound: no long or bright rings (the desk bell and receipt printer were "unbearable"). Pop when the English
  card lands, a soft synthesised cha-ching plus flying 💸 on money moments, quiet whooshes, the riser rules as before.

### Situation Series: Manisha 4 (`edits/manisha4`, bank English)
- Same template; palette from the footage (her navy top + warm lamp): ivory cards, navy ink, royal-blue key words
  on a soft gold marker, gold light sweeps, gold neon. The user asked: same placements and fonts, only colours change
  per reel.
- `cues.py` here is the multi-clip version of the content file: every situation, the recap and the CTA name their
  own clip. Optional per situation: `tag` (e.g. "⭐ IMPORTANT") and `hi2`/`hi2_t` (the Hindi meaning she gives after
  the English line). Use this version for new reels.
- Manisha's voice is more dynamic: loudnorm target -13.1 lands the limited mix at about -14 LUFS.

## Approved style: Manisha 5 "Pep Talk" (`edits/manisha5`, cheer-up / motivation sentences)

User reaction: "Looks amazing". Designed from a style board first (`edits/manisha5/board`).
- Palette from the footage (navy top + warm lamp): navy #1B2340, cream #FFF8EE, sunflower #FFC94A, apricot #FF9E6B,
  rose #FF7E9D. Fraunces (soft serif) for English and titles, Nunito (italic) for Hinglish and labels.
- A MOOD meter at the top fills from 😔 to 🤩 as each sentence is taught (ties the lesson together).
- English line in a cream speech bubble; key word gets a hand-drawn sunflower underline that draws in as she says it;
  Hinglish line on the wall above (white italic, shadow, no panel). Optional "more natural" upgrade swaps the bubble.
- One motion graphic per sentence (sun rays, floating hearts, 💪 pop, 👏 + confetti); hook rain cloud turns into a sun.
- "Sunrise glow" transitions (golden bloom + soft rays) on section cuts; soft chime per English line, sparkle when
  the meter rises; camera glides mid (1.24x) -> close (1.40x) with her face at 60% height so captions sit above her.

## Approved style: Nikita 6 "WH Family" (`edits/nikita6`, a set of words taught as a family)

Board: `edits/nikita6/board`. Cocoa #4A2E22 / latte #FFF4E6 / heart red #E8475A, one pastel per word; Baloo 2 (English)
+ Quicksand (Hinglish).
- Squircle tiles, one per word: locked "?" in the hook, then each flips "?" -> Hindi -> English as she says it.
- Examples: mini family bar at the top (full words) lights the current word; Hindi question on the wall; English question
  on a latte card with the word as a coloured chip; "QUESTION LEADER = FIRST WORD" below. Quiz card with a blank "?"
  chip + "Comment karo!" for engagement; ending 🔖 "Save karo!" + recap strip.
- "Tile shuffle" transitions (pastel columns sweep up) on section cuts, soft warm flash on other jump cuts.
- Sound: soft marimba notes (make_sfx.py) for the tiles. The user found the synthesised paper-flick/card-flip
  sound "very annoying"; never use it again.

### Nikita 6 cutaways (19 Nov): grown-up animated scenes on every example
- On each example's Hindi question the picture cuts to a 1.3-2 s animated scene (no AI apps: built in code with
  HyperFrames, `anim/make_scenes_grown.py`, rendered to `footage/nikita6/broll/*_v2_anim.mp4`) and the question pops
  BIG in the middle word by word with the WH word on a heart-red chip; back on her (0.1 s before the English card)
  the small caption returns. `cues.py` EXAMPLES[].broll + kw drive it; `compose.py` lays the clips with hard cuts.
- Audience is 20+: the first cartoon set (clock with eyes-and-bounce style, waving teacher, 👀) felt childish and was
  replaced by GROWN-UP scenes: real adult moments (food-delivery order, desk from above, family chat, class schedule,
  streaming grid, lost-and-found notice, lock screen with work notifications), flat editorial look, NO characters,
  calm power3 slides, few emoji. The key beat of each scene must land within the cutaway (shortest is 1.3 s).
- AI clips from Gemini work too (muted; prompts must show the person ASKING, adults only, "no dialogue, mouth
  closed"), but the user chose not to use other apps.

## Approved style: Nikita 7 "Feelings in English" (`edits/nikita7`, Hindi -> English word list)

Built from the user's reference (a full Hindi -> English list over the speaker), made more attention-grabbing.
- Curiosity hook: every Hindi word on screen from frame 1, every English answer blurred ("Guess before I say it! 👀");
  each answer pops out of the blur (yellow) as she says it, its emoji at the row end, counter 00 -> 11. Last row is her
  comment question (ईर्ष्या -> "? ? ?" + "Comment karo 👇"), answer left out on purpose for comments.
- Rows side by side like the reference: white Mukta Hindi pill -> big white Fraunces Black English with a thick plum
  outline; full width, may run over her (user: learning first, readability over face rule for this format).
- Video untouched: no grade, no zoom; soft marimba note per reveal (rising), no riser at the start, soft riser tail at
  the end.
- iPhone HDR (HLG) footage: every SDR tone-map made her look glossy/white. Deliver in HDR instead (`build.py hdr`):
  her video passes through untouched (10-bit HEVC, HLG/BT.2020 tags), only the caption layer is converted into HLG,
  colour and alpha separately, +1.8 stops and more saturated (at reference white the captions looked grey).
  Check her pixels against the raw and caption white against the wall brightness.
- Nikita 8 (`edits/nikita8`, positive feelings) reused this style: 8 bigger rows, her example sentence and a Follow tap
  below the list. A translate-app card (one word at a time, `build_v1_translate.py`) and a sticker-card idea were
  rejected: with a word list the user wants every word to STAY on screen so viewers can read and write them down.
- Nikita 10 (`edits/nikita10`, "Positive Words", 8 words, 25 Nov; user: "the style is similar to feelings in english"):
  copied from nikita8/build.py (words + onsets, `EXAMPLE` = her closing "practice kijiye" line, Follow tap). The whole
  list and "Guess before I say it!" are on screen from frame 1 (hook + cover). Hindi pills 44 px, longest row 37 px so it
  clears the frame edge. Her raw clip ended inside an extra syllable: cut on her last word (CLIP_OUT) and hold the last
  frame HOLD 1.2 s (tpad) for the tap. Voice loudnorm -13.1 + 0.4 dB -> -14.1 LUFS.

## Approved style: Manisha 7 "Pick One" quiz (`edits/manisha7`, fill in the blank + options + comment CTA)

Short single-take quiz (19 Nov). Built from `build.py` (cues / base / overlay / compose) + `mix.py` (Manisha's -13.1 chain).
- Palette from the footage (window plants, warm wood, her beige top): forest #1F4D3A, mint #D6F0DF, cream #FFF8EE,
  sunflower #FFC94A. Bricolage Grotesque for the sentence and options, Plus Jakarta Sans for the chip and letters,
  Caveat for the handwritten comment line.
- She is framed close (face fills the top half), so everything sits LOW (y 1075-1550): "FILL IN THE BLANK" chip top-left,
  the sentence on one line with a pulsing dashed yellow blank, option pills A and B side by side with C centred below
  (user's layout), each slides in as she reads it and lights yellow on the word; "Comment karo — A, B ya C?" at the end.
- Video untouched; trimmed to start on her first word and end before she lowers the phone. Whoosh, pop per option,
  ping on the CTA. The answer is never shown (for comments).

## Approved: Manisha 8 "NPAT Notebook" (`edits/manisha8`, nouns via the Name-Place-Animal-Thing game, 5 takes)

Multi-version reel (20-21 Nov). `lines.py` (24 lines with audio-measured cuts + trimmed variants) -> `render_base.py`
(alternating zoom so every cut is a punch, face at (0.50,0.54)) -> `overlay.py` (captions) -> `build.py` (cues, mix,
compose; `all <v> [--preview]`). Scenes: `anim/make_scenes.py`. Delivered: V2 and V3 4K (V1 kept, V4 dropped).
- Palette from the footage: deep teal #17423C, mint #CFEADF, paper #FFF9EE, pencil yellow #FFC94A, red #E8475A;
  Anton hook, Bricolage sentences, Caveat handwriting, Plus Jakarta chips. Notebook with NAME/PLACE/ANIMAL/THING columns
  fills on her words; examples get a noun highlight, a label chip and her "kyunki..." reason; Part-2 card at the end.
- Hooks: "Ratta? No!" (slashed textbook definition + stamp) or, when a version opens cold on "Name, place, animal,
  thing", the text hook "Bachpan ka YE game = poori NOUN grammar" readable on frame 1.
- User notes: highlight each column as she says "place, person, animal, thing"; cut her badly pronounced last
  "common noun" sentence (end on "dekhiye hamara part 2" + card held 1.2 s); Whisper can stop early on a take, so
  check every line's end against the audio energy; user timestamps for cuts refer to the V1 timeline.
- Animated scenes the user asked for: Ria = an illustrated girl waving ("Hi, I'm Ria!"), tiger = an illustrated tiger
  that growls, Mumbai = night skyline + Bandra-Worli Sea Link. Other scenes in the grown-up flat style.
- She looked a bit dark: the Nikita 6 grade is applied to HER picture only (build.py GRADE), before scenes and
  captions are laid on, so graphic colours never change. Mix: voice target -12.5 + 0.7 dB into a 0.75 limiter
  -> -13.9 LUFS, -2.0 dBFS after AAC. 4K masters at CRF 15 were 276-341 MiB (one file each).

## Manisha 9 "being: 3 uses" (`edits/manisha9`, two versions, 22-23 Nov)

Six single-line takes (iPhone HLG 4K60). `cut.py` (segments, energy-checked edges, T() source->output time) ->
`keys.py` (word times) -> `overlay.py a|b` -> `build.py cues|caps|compose <v> [--crf N]` + `mix.py` (M9_VERSION).
Delivered in HDR (HLG passthrough, captions converted into HLG as Nikita 7), 4K, one file each.
- A "Gold Tabs" (board/): Playfair "being" + numbered tabs 🎭🪪🏗️, chip + rule on the wall, ivory card with the
  being-phrase on a gold pill, Hinglish meaning under it, "is / are + being + V3" chip, recap tabs, comment box.
  In HDR, gold text straight on her warm wall vanished: wall highlights sit on dark ink pills, "being" has an ink outline.
- B "Explainer Panel" (board_b/), copied from the user's reference reel (a grammar-challenge reel): top progress bar
  (user: NO series title), one dark-glass panel at chest height with concept widgets (branches, toggles, ID slot,
  progress bar, tilted stamp), English sentence grey -> lit word by word in yellow, short subtitle pill under the
  panel, recap + typed comment box with her picture blurred at the end. Yellow #FFC83D, blue #5AA9FF, Poppins.
- Mix: loudnorm -13.1 then master volume +0.1 dB into the 0.75 limiter -> -14.0 LUFS, -2.0 dBFS.
- Sizes at 66.6 s: B 225 MiB (CRF 16); A was 400.07 MiB at CRF 16, so A ships at CRF 17 (344 MiB).

## Manisha 10 "Tag It" (`edits/manisha10`, prepositions on/in/under/at taught on real desk props, 23 Nov)

Seven single-line takes (SDR 4K30). `cut.py` -> `keys.py` -> `overlay.py` -> `build.py cues|caps|compose [--hevc] [--crf N]`
+ `mix.py`. User cut "0:02-0:05" = her question sentence in take 1 (cut at word edges, not the exact seconds).
- Look: AR corner brackets + name tags land on the real props (lamp, table, box, mic, pen, napkin) as she names them
  (`cut.stage()` maps raw-frame positions through each take's zoom); big amber word with ink outline + Caveat Hinglish
  meaning + mini icon; sentence card with the preposition on an amber pill; ON·IN·UNDER·AT strip with ✓; AT = clock
  turning to 5 PM, then a map pin "Gandhinagar"; quiz card (pulsing blank, A-D options, "Comment karo", no answer).
  Charcoal / cream / lamp amber #FFB547 / sage / tomato; Bricolage 800, Plus Jakarta Sans, Caveat.
- User: "make her look a little better, just the video" -> Nikita 6 grade + saturation 1.06 + light unsharp on her
  picture only (captions untouched). Gold/amber words on the wall need a dark pill.
- Size: 80.6 s was 558 MiB as H.264 CRF 15 and 409 MiB as HEVC CRF 16; delivered HEVC CRF 17 (353 MiB, one file).
  For long reels (> ~70 s) go straight to `--hevc --crf 17`.

## Nikita 9 "Office Chat" (`edits/nikita9`, 5 + 1 bonus office sentences, two versions, 25 Nov)

Seven takes (SDR 4K30). `cut.py` -> `keys.py` -> `overlay.py` -> `scenes_plan.py` + `anim/make_scenes.py render` ->
`build.py cues|compose <v>` + `mix.py` (N9_VERSION). V1 = captions only; V2 = V1 + an animated scene during each
situation (user: "version 2 with animations related EXACTLY to those sentences"), hard cuts, ending 0.12 s before her
English line so she is on screen with the chat card when she says it.
- Her head sits high in the frame: situation = yellow sticky note on the wall LEFT of her head (Caveat Hinglish,
  numbered 01/05..05/05, "BONUS 🎁" because she says 5 but teaches 6); English = a work-chat message at chest level typed
  word by word, key phrases on an indigo highlight, Sent ✓✓ + reaction, then meaning chips ("slight = thoda sa") for an
  explanatory edit; each card holds READ_HOLD 0.7 s into the next situation. Hook = "darr" pill + a message typed and
  struck out; quiz = message box + "Comment karo". Ink / sticky yellow #FFE45C / indigo #5E5CE6; Bricolage, Plus Jakarta,
  Caveat. Nikita 6 grade on her picture only.
- Scenes (grown-up flat office UI, no characters): video-call grid with your tile muted + lock, Kanban card moving to
  In Progress with a progress ring, deadline flag sliding +1 day + bell updates, teammate cursor fixing a "?" line,
  checklist + COMPLETED stamp, scattered tasks sorted 1-5 with HIGH flag, idea bulb + suggestion sticky + votes,
  calendar with tomorrow circled "Leave?" + empty message box. Visual wrapper scaled 1.07 (1.16 clipped wide scenes).
- Mix: Nikita's voice is louder: loudnorm -13.1, master -0.3 dB -> -14.0 LUFS. 81 s at HEVC CRF 17: V1 294 MiB, V2 181 MiB.

## Working rules (from the guide)

- NEW video with a new design: first send the user a style-board IMAGE (3-4 real frames of the speaker with the new
  captions, colours and motion graphics, composited from the raw footage) and wait for OK before building the video
  (user request, Manisha 5).

- Plan with a beat sheet and wait for approval before building.
- Rough cut first, effects after. Never cut inside a word.
- Snapshot frames and check them before showing work. Save a version (v1, v2...) before each round of notes.
- Reels safe zone: no text in the bottom 20% or near the right edge.
