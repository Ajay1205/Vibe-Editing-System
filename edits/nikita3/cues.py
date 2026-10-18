"""Cue sheet for the Nikita 3 reel: captions, zoom punches and sound effects.

Every time here is a SOURCE time (seconds into raw clip n31..n34, read off the word-timed
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
    # Hook
    {"type": "hook", "start": at("n31", 0.0), "end": at("n31", 3.05),
     "beats": {"num": at("n31", 1.10), "words": at("n31", 1.36), "sub": at("n31", 2.06)}},
    {"type": "promise", "start": at("n31", 7.80), "end": section_end("n31") - 0.05,
     "lines": [{"t": at("n31", 7.80), "text": "Natural"}, {"t": at("n31", 8.85), "text": "Confident"}]},
]

SECTIONS = [
    {"clip": "n32", "num": "01", "word": "Actually", "title": 1.05, "meaning_t": 3.30, "meaning": "Asal mein",
     "dock": 8.0,
     "examples": [
         {"t": 8.55, "end": 13.70, "en": "**Actually**, I don't like coffee.", "hi_t": 10.80,
          "hi": "Asal mein mujhe coffee pasand nahi hai", "emoji": "☕"},
         {"t": 14.85, "end": 19.20, "en": "**Actually**, I am from Delhi.", "hi_t": 17.05,
          "hi": "Asal mein main Delhi se hoon", "emoji": "📍"},
     ],
     "tip": {"t": 19.28, "lines": [(21.60, "Koi baat clarify karni ho"), (23.10, "ya sach kehna ho"),
                                   (24.65, "→ shuru karo **Actually** se")]}},
    {"clip": "n33", "num": "02", "word": "Instead", "title": 1.00, "meaning_t": 2.90,
     "meaning": "Iske bajaye / Uski jagah", "dock": 8.0,
     "examples": [
         {"t": 8.00, "end": 13.55, "en": "Let's have tea **instead of** coffee.", "hi_t": 10.78,
          "hi": "Coffee ki bajaye chai peete hain", "emoji": "🍵"},
         {"t": 14.70, "end": 20.50, "en": "I walked **instead of** taking a taxi.", "hi_t": 17.36,
          "hi": "Taxi lene ki bajaye main paidal chali gayi", "emoji": "🚶‍♀️"},
     ],
     "tip": {"t": 21.10, "lines": [(22.14, "2 options mein se 1 choose karna ho"),
                                   (26.18, "→ bolo **Instead** / **Instead of**")]}},
    {"clip": "n34", "num": "03", "word": "Finally", "title": 1.00, "meaning_t": 3.20,
     "meaning": "Aakhirkaar / Ant mein", "dock": 6.0,
     "examples": [
         {"t": 6.10, "end": 11.00, "en": "**Finally**, I finished my work.", "hi_t": 8.14,
          "hi": "Aakhirkaar maine apna kaam poora kar diya", "emoji": "✅"},
         {"t": 12.45, "end": 16.50, "en": "**Finally**, the bus arrived.", "hi_t": 14.30,
          "hi": "Aakhirkaar bus aa gayi", "emoji": "🚌"},
     ],
     "tip": {"t": 16.56, "lines": [(18.98, "Lamba intezaar khatam ho jaaye"),
                                   (21.04, "→ bolo **Finally**")]},
     "tip_end": 23.42},
]

OUTRO = {"recap": {"t": at("n34", 25.00), "rows_t": at("n34", 25.50), "end": at("n34", 31.40)},
         "boost": {"t": at("n34", 31.44), "end": at("n34", 33.36)},
         "cta": {"t": at("n34", 33.38), "follow": at("n34", 34.00), "comment": at("n34", 34.68),
                 "end": section_end("n34")}}

# Zoom punches: (clip, source time, "big"|"small")
PUNCHES = [("n31", 1.10, "big"), ("n31", 7.84, "small"), ("n31", 8.88, "small"),
           ("n32", 1.05, "big"), ("n32", 3.34, "small"), ("n32", 8.64, "small"), ("n32", 14.90, "small"),
           ("n32", 21.64, "small"), ("n32", 25.74, "small"),
           ("n33", 1.00, "big"), ("n33", 2.94, "small"), ("n33", 9.24, "small"), ("n33", 15.56, "small"),
           ("n33", 22.16, "small"), ("n33", 26.20, "small"),
           ("n34", 1.00, "big"), ("n34", 3.22, "small"), ("n34", 6.16, "small"), ("n34", 12.54, "small"),
           ("n34", 19.00, "small"), ("n34", 21.16, "small"), ("n34", 25.54, "small"), ("n34", 31.46, "small"),
           ("n34", 34.02, "small")]


def build():
    caps = list(CAPTIONS)
    sfx = [("impact-bass-1", caps[0]["beats"]["num"], 0.55), ("whoosh-short", caps[0]["beats"]["words"] - 0.05, 0.5),
           ("pop", caps[0]["beats"]["sub"], 0.45),
           ("pop", caps[1]["lines"][0]["t"], 0.45), ("sparkle", caps[1]["lines"][1]["t"], 0.35)]
    flashes = []
    for sec in SECTIONS:
        c = sec["clip"]
        start = at(c, 0)
        end = section_end(c) - 0.05
        flashes.append(start)
        sfx.append(("whoosh", start - 0.12, 0.6))
        tip_end = at(c, sec["tip_end"]) if "tip_end" in sec else end
        caps.append({"type": "title", "num": sec["num"], "word": sec["word"], "start": at(c, sec["title"]),
                     "meaning": sec["meaning"], "meaning_t": at(c, sec["meaning_t"]), "dock": at(c, sec["dock"]),
                     "end": tip_end})
        sfx += [("impact-bass-2" if sec["num"] == "01" else "impact-bass-1", at(c, sec["title"]), 0.4),
                ("pop", at(c, sec["meaning_t"]), 0.45)]
        for ex in sec["examples"]:
            caps.append({"type": "example", "en": ex["en"], "hi": ex["hi"], "emoji": ex["emoji"],
                         "start": at(c, ex["t"]), "hi_t": at(c, ex["hi_t"]), "end": at(c, ex["end"])})
            sfx += [("whoosh-short", at(c, ex["t"]) - 0.04, 0.4), ("sparkle", at(c, ex["t"]) + 0.45, 0.25),
                    ("click-soft", at(c, ex["hi_t"]), 0.5)]
        tip = sec["tip"]
        caps.append({"type": "tip", "start": at(c, tip["t"]), "end": tip_end,
                     "lines": [{"t": at(c, t), "text": s} for t, s in tip["lines"]]})
        sfx.append(("ping", at(c, tip["t"]), 0.3))
        sfx += [("click-soft", at(c, t), 0.45) for t, _ in tip["lines"]]

    r, b, cta = OUTRO["recap"], OUTRO["boost"], OUTRO["cta"]
    caps.append({"type": "recap", "start": r["t"], "rows_t": r["rows_t"], "end": r["end"]})
    caps.append({"type": "boost", "start": b["t"], "end": b["end"]})
    caps.append({"type": "cta", "start": cta["t"], "follow": cta["follow"], "comment": cta["comment"],
                 "end": round(cta["end"], 3)})
    sfx += [("whoosh-short", r["t"], 0.45)] + [("pop", r["rows_t"] + i * 0.32, 0.45) for i in range(3)]
    sfx += [("sparkle", b["t"], 0.4), ("pop", cta["t"], 0.4), ("click", cta["follow"], 0.6),
            ("click", cta["comment"], 0.6), ("chime", cta["comment"] + 0.5, 0.35)]

    punches = [{"t": at(c, s), "kind": k} for c, s, k in PUNCHES]
    out = {"duration": EDL["duration"], "fps": EDL["fps"], "captions": caps, "flashes": flashes,
           "punches": punches, "sfx": [{"name": n, "t": round(max(0, t), 3), "gain": g} for n, t, g in sfx]}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(caps)} captions, {len(punches)} punches, {len(out['sfx'])} sfx, {len(flashes)} flashes")


if __name__ == "__main__":
    build()
