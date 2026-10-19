"""Cue sheet for the Nikita 5 reel (3 English words, Part 2: Probably / Almost / Already), Nikita 3 v2 style.

Every time here is a SOURCE time (seconds into raw clip n51..n56, read off the word-timed
transcript), so a cue stays on its word even when the rough cut changes. `at()` maps it onto
the edited timeline. Writes cues.json for the overlay, zoom and audio builders.

To change something, edit the text or the source time below and re-run the build.
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
EDL = json.load(open(HERE / "edl.json"))


def at(clip, src):
    """Source time -> output time. A time inside a removed pause snaps to the next kept frame."""
    segs = [s for s in EDL["segments"] if s["clip"] == clip]
    for s in segs:
        if src < s["in"]:
            return round(s["start"], 3)
        if src < s["out"]:
            return round(s["start"] + src - s["in"], 3)
    last = segs[-1]
    return round(last["start"] + last["out"] - last["in"], 3)


def section_end(clip):
    return at(clip, 999)


CAPTIONS = [
    # Hook: "Add these three English words to your vocabulary" -> locked ??? chips on "in teen words" ->
    # "aaj se ... use karte ho" -> Natural & Confident
    {"type": "hook", "start": at("n51", 0.95), "end": at("n51", 8.10),
     "beats": {"num": at("n51", 1.34), "words": at("n51", 1.56), "sub": at("n51", 2.38),
               "teaser": at("n51", 3.96), "today": at("n51", 4.72)}},
    {"type": "promise", "start": at("n51", 8.12), "end": section_end("n51") - 0.05,
     "lines": [{"t": at("n51", 8.18), "text": "Natural"}, {"t": at("n51", 9.16), "text": "Confident"}]},
]

SECTIONS = [
    {"clip": "n52", "num": "01", "word": "Probably", "title": 1.22, "meaning_t": 3.62, "meaning": "Shayad",
     "dock": 6.9,
     "examples": [
         {"t": 6.92, "word_t": 7.50, "end": 11.30, "en": "I will **probably** be late.", "hi_t": 8.78,
          "hi": "Shayad mujhe der ho jaayegi", "emoji": "⏰"},
         {"t": 12.58, "word_t": 13.34, "end": 16.62, "en": "She will **probably** come tomorrow.", "hi_t": 14.72,
          "hi": "Shayad woh kal aayegi", "emoji": "📅"},
     ],
     "tip": {"t": 16.72, "lines": [(17.90, "Jab poori guarantee na de sako"),
                                   (21.04, "→ bolo **Probably**")]}},
    {"clip": "n53", "num": "02", "word": "Almost", "title": 1.22, "meaning_t": 3.64, "meaning": "Lagbhag",
     "dock": 6.9,
     "examples": [
         {"t": 7.04, "word_t": 7.70, "end": 10.70, "en": "I am **almost** ready.", "hi_t": 8.84,
          "hi": "Main lagbhag taiyaar hoon", "emoji": "👗"},
         {"t": 11.96, "word_t": 12.32, "end": 16.22, "en": "It's **almost** 8 o'clock.", "hi_t": 13.98,
          "hi": "Lagbhag 8 bajne waale hain", "emoji": "🕗"},
     ],
     "tip": {"t": 16.28, "lines": [(17.16, "Jab kaam poora hone ke bahut kareeb ho"),
                                   (20.80, "→ bolo **Almost**")]}},
    {"clip": "n54", "num": "03", "word": "Already", "title": 2.68, "meaning_t": 4.66, "meaning": "Pehle se hi",
     "dock": 8.1,
     "examples": [
         {"t": 8.20, "word_t": 8.98, "end": 12.85, "en": "I have **already** eaten.", "hi_t": 10.44,
          "hi": "Main pehle se hi kha chuki hoon", "emoji": "🍽️"},
         {"t": 14.04, "word_t": 14.94, "end": 18.40, "en": "She has **already** left.", "hi_t": 16.24,
          "hi": "Woh pehle se hi ja chuki hai", "emoji": "🚶‍♀️"},
     ],
     "tip": {"t": 18.46, "lines": [(19.54, "Jab koi kaam time se pehle ho jaaye"),
                                   (24.06, "→ bolo **Already**")]}},
]

RECAP_ROWS = [("Probably", "Shayad"), ("Almost", "Lagbhag"), ("Already", "Pehle se hi")]
BOOST = ("Fluent", "Natural", "English")
OUTRO = {"recap": {"t": at("n55", 0.0), "rows_t": at("n55", 0.6), "end": at("n55", 7.70)},
         "boost": {"t": at("n55", 7.84), "confident": at("n55", 8.72), "end": section_end("n55") - 0.05},
         "cta": {"t": at("n56", 0.10), "follow": at("n56", 2.40), "comment": at("n56", 5.0),
                 "end": section_end("n56"), "line": "Part 3 chahiye? Comment karo", "tag": "PART 2 ✓"}}

# Zoom punches: (clip, source time, "big"|"small"): the hook, each word title, the word inside each example
PUNCHES = [("n51", 1.34, "big"),
           ("n52", 1.22, "big"), ("n52", 7.50, "small"), ("n52", 13.34, "small"),
           ("n53", 1.22, "big"), ("n53", 7.70, "small"), ("n53", 12.32, "small"),
           ("n54", 2.68, "big"), ("n54", 8.98, "small"), ("n54", 14.94, "small"),
           ("n55", 8.72, "small")]


def build():
    caps = list(CAPTIONS)
    # Sound effects stay sparse: hook hit, a whoosh per word transition, a light hit each time
    # she says the word inside an example sentence, "better" + "confident" at the end, comment tap.
    sfx = []  # no hit on the hook: the opening second stays clean (user note)
    # (timeline start, slice start in the riser file, slice length): only the crest of the provided riser
    risers = [(2.0, 2.0, 1.1)]  # opening: just the 0:02-0:03 crest
    flashes = []
    for sec in SECTIONS:
        c = sec["clip"]
        start = at(c, 0)
        end = section_end(c) - 0.05
        flashes.append(start)
        sfx.append(("whoosh", start - 0.12, 0.55))
        tip_end = at(c, sec["tip_end"]) if "tip_end" in sec else end
        caps.append({"type": "title", "num": sec["num"], "word": sec["word"], "start": at(c, sec["title"]),
                     "meaning": sec["meaning"], "meaning_t": at(c, sec["meaning_t"]), "dock": at(c, sec["dock"]),
                     "end": tip_end})
        for k, ex in enumerate(sec["examples"]):
            sfx.append(("pop" if k == 0 else "ping", at(c, ex["word_t"]), 0.35 if k == 0 else 0.25))
            caps.append({"type": "example", "en": ex["en"], "hi": ex["hi"], "emoji": ex["emoji"],
                         "start": at(c, ex["t"]), "word_t": at(c, ex["word_t"]), "hi_t": at(c, ex["hi_t"]),
                         "end": at(c, ex["end"])})
        tip = sec["tip"]
        caps.append({"type": "tip", "start": at(c, tip["t"]), "end": tip_end,
                     "lines": [{"t": at(c, t), "text": s} for t, s in tip["lines"]]})

    r, b, cta = OUTRO["recap"], OUTRO["boost"], OUTRO["cta"]
    caps.append({"type": "recap", "start": r["t"], "rows_t": r["rows_t"], "end": r["end"], "rows": RECAP_ROWS})
    caps.append({"type": "boost", "start": b["t"], "confident": b["confident"], "end": b["end"], "words": BOOST})
    caps.append({"type": "cta", "start": cta["t"], "follow": cta["follow"], "comment": cta["comment"],
                 "end": round(cta["end"], 3), "line": cta["line"], "tag": cta["tag"]})
    sfx += [("impact-bass-1", b["t"], 0.4), ("impact-bass-2", b["confident"], 0.4),
            ("click", max(cta["comment"], cta["t"] + 1.1), 0.45)]

    comment_tap = max(cta["comment"], cta["t"] + 1.1)
    risers.append((comment_tap - 1.85, 1.1, 2.0))  # ending: last 2 s of the riser, crest (~2.95 s in file) on the tap
    punches = [{"t": at(c, s), "kind": k} for c, s, k in PUNCHES]
    out = {"duration": EDL["duration"], "fps": EDL["fps"], "captions": caps, "flashes": flashes,
           "punches": punches, "sfx": [{"name": n, "t": round(max(0, t), 3), "gain": g, "lu": -1.0 if n in ("pop", "ping") else 0.0}
                   for n, t, g in sfx]
           + [{"name": "riser_user", "file": "../../assets/shared/riser_user.mp3", "t": round(t, 3), "gain": 0.45, "lu": 1.0,
               "from": a, "dur": d} for t, a, d in risers]}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(caps)} captions, {len(punches)} punches, {len(out['sfx'])} sfx, {len(flashes)} flashes")


if __name__ == "__main__":
    build()
