"""Cue sheet for the Nikita 4 reel (restaurant English) -- the content file of the "Situation Series" template.

For a new situation video, copy edits/nikita4 and change only this file's CONTENT block (and EXCLUDE/CLIPS in
edl.py): the hook texts, the situations (Hindi need, English line, icon, word times), the recap title and the
CTA ideas. build_overlay.py, mix.py, render_base.py and compose.py stay the same.

Times are SOURCE times (seconds into raw clip n41/n42, read off the word-timed transcript and the speech
envelope), so every cue stays on its word when the rough cut changes. `at()` maps them onto the edited
timeline -> cues.json.

Structure: hook (myth stamped NAHI -> letter board -> neon topic sign) -> situations ONE AFTER ANOTHER
(icon + Hindi need, then the English line written onto an order ticket) -> recap card -> comment CTA.
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
EDL = json.load(open(HERE / "edl.json"))

# ------------------------------------------------------------------------------------------------ CONTENT
HOOK_CLIP, SIT_CLIP = "n41", "n42"
HOOK = {
    "series": "🍽️ RESTAURANT ENGLISH",                    # top banner for the whole series video
    "lines": [  # chest captions, word by word; **..** = highlight; t = source time the line starts
        {"t": 0.80, "text": "Grammar rules ka **ratta?**", "x_t": 3.00},   # x_t: red ✗ stamp lands ("nahi")
        {"t": 4.50, "text": "**Situations** mein", "sub": "communicate karke seekho ✅", "sub_t": 5.78},
        {"t": 7.50, "text": "Aaj seekhenge 👇"},
    ],
    "neon": "Restaurant", "neon_sub": "ENGLISH 🍽️", "neon_t": 8.68,
}
# en uses **...** for the key words; "please" gets the polite stamp. icon = a key of ICONS in build_overlay.py
# (table, menu, spoon, water, bill) or any emoji. start = Hindi need, q = "English mein kaise bologe?",
# en_t = English line, key = key word, pl = "please", hold_until = last frame of her pause after the line.
# Situation 3: she says "the spoon"; the caption teaches the natural "a spoon" (user decision).
SITUATIONS = [
    {"icon": "table", "hi": "Do logon ke liye table chahiye", "en": "A **table for two**, please.",
     "start": 0.34, "q": 3.97, "en_t": 5.74, "key": 5.92, "pl": 6.68},
    {"icon": "menu", "hi": "Kya mujhe menu mil sakta hai?", "en": "Can I get the **menu**, please?",
     "start": 8.06, "q": 9.84, "en_t": 11.74, "key": 12.32, "pl": 12.62},
    {"icon": "spoon", "hi": "Khaane ke liye chammach chahiye", "en": "Can I get a **spoon**, please?",
     "start": 14.30, "q": 16.34, "en_t": 18.10, "key": 18.64, "pl": 18.92},
    {"icon": "water", "hi": "Kya mujhe ek glass paani mil sakta hai?", "en": "Can I get a **glass of water**, please?",
     "start": 20.69, "q": 22.40, "en_t": 24.30, "key": 24.74, "pl": 25.56},
    {"icon": "bill", "hi": "Bill maangna hai", "en": "Can I get the **bill**, please?",
     "start": 27.02, "q": 27.98, "en_t": 29.74, "key": 30.46, "pl": 30.72, "kaching": True},
]
RECAP = {"t": 32.37, "title": "Save karo 📌", "sub": "5 restaurant lines",
         "say_t": 35.88, "say": "Real life mein bol kar dekhiye! 🗣️"}
CTA = {"t": 38.62, "head": "Next <m>situation</m> kaunsi? 🤔", "more_t": 39.98, "comment_t": 42.56, "ideas_t": 44.10,
       "tap_t": 48.70, "ideas": ["✈️ Airport", "🏥 Hospital", "🏦 Bank", "🛍️ Shopping", "💼 Interview", "🏨 Hotel"],
       "bar": "Aapki situation… comment karo"}
# English line stays up until this far into the next situation (she starts the next Hindi need meanwhile)
READ_HOLD = 0.7
# ---------------------------------------------------------------------------------------------------------



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


def build():
    caps, sfx = [], []
    hook_end = section_end(HOOK_CLIP)
    lines = [dict(ln, t=at(HOOK_CLIP, ln["t"]), **({"x_t": at(HOOK_CLIP, ln["x_t"])} if "x_t" in ln else {}),
                  **({"sub_t": at(HOOK_CLIP, ln["sub_t"])} if "sub_t" in ln else {})) for ln in HOOK["lines"]]
    neon_t = at(HOOK_CLIP, HOOK["neon_t"])
    caps.append({"type": "hook", "start": 0.0, "end": hook_end, "lines": lines, "neon": HOOK["neon"],
                 "neon_sub": HOOK["neon_sub"], "neon_t": neon_t})
    shots = [{"t": 0.0, "kind": "close"}, {"t": lines[1]["t"], "kind": "mid"}, {"t": neon_t, "kind": "close"}]
    for ln in lines:
        if "x_t" in ln:
            sfx.append(("stamp", ln["x_t"], -3.0, "assets/sfx/stamp.wav"))
    sfx.append(("whoosh-short", lines[1]["t"] - 0.08, -5.0, None))
    sfx.append(("neon", neon_t - 0.05, -5.0, "assets/sfx/neon.wav"))

    recap = at(SIT_CLIP, RECAP["t"]) + READ_HOLD
    starts = [hook_end] + [at(SIT_CLIP, s["start"]) + READ_HOLD for s in SITUATIONS[1:]]
    ends = starts[1:] + [recap]
    for i, s in enumerate(SITUATIONS):
        pl = at(SIT_CLIP, s["pl"])
        key = at(SIT_CLIP, s["key"])
        caps.append({"type": "situation", "n": i + 1, "of": len(SITUATIONS), "icon": s["icon"], "hi": s["hi"], "en": s["en"],
                     "start": starts[i], "hi_t": max(starts[i], at(SIT_CLIP, s["start"])), "q": at(SIT_CLIP, s["q"]),
                     "en_t": at(SIT_CLIP, s["en_t"]), "key": key, "pl": pl, "end": ends[i]})
        shots += [{"t": starts[i], "kind": "mid"}, {"t": at(SIT_CLIP, s["q"]) - 0.04, "kind": "ask"},
                  {"t": at(SIT_CLIP, s["en_t"]) - 0.04, "kind": "close"}]
        if i:
            sfx.append(("whoosh-short", starts[i] - 0.1, -5.0, None))  # card swipe
        if s.get("kaching"):
            sfx.append(("kaching", key - 0.02, -5.0, "assets/sfx/kaching.wav"))  # money for the bill
        else:
            sfx.append(("pop", at(SIT_CLIP, s["en_t"]) - 0.02, -4.0, None))  # English card lands

    cta = at(SIT_CLIP, CTA["t"])
    caps.append({"type": "recap", "start": recap, "end": cta, "items": [s["en"] for s in SITUATIONS],
                 "icons": [s["icon"] for s in SITUATIONS], "title": RECAP["title"], "sub": RECAP["sub"],
                 "say": RECAP["say"], "say_t": at(SIT_CLIP, RECAP["say_t"])})
    end = section_end(SIT_CLIP)
    tap = at(SIT_CLIP, CTA["tap_t"])  # the comment button is tapped, riser crests here
    caps.append({"type": "cta", "start": cta, "end": round(end, 3), "head": CTA["head"], "ideas": CTA["ideas"],
                 "bar": CTA["bar"], "more": at(SIT_CLIP, CTA["more_t"]), "comment": at(SIT_CLIP, CTA["comment_t"]),
                 "ideas_t": at(SIT_CLIP, CTA["ideas_t"]), "tap": tap})
    sfx += [("pop", at(SIT_CLIP, CTA["comment_t"]), -5.0, None), ("click", tap, -1.0, None)]
    shots += [{"t": recap, "kind": "mid"}, {"t": cta, "kind": "mid"}, {"t": tap - 1.6, "kind": "close"}]

    flashes = [hook_end, recap]  # candle-glow bloom + whoosh: into the situations, into the recap
    for t in flashes:
        sfx.append(("whoosh", t - 0.12, -4.0, None))

    # Approved riser treatment: first 2 s voice only, riser crest at 0:02-0:03, last 2 s at the end
    risers = [(2.0, 2.0, 1.1), (tap - 1.85, 1.1, 2.0)]

    out = {"duration": EDL["duration"], "fps": EDL["fps"], "captions": caps, "flashes": flashes,
           "series": HOOK["series"], "shots": sorted(shots, key=lambda x: x["t"]),
           "sfx": [dict({"name": n, "t": round(max(0, t), 3), "gain": 0.5, "lu": lu}, **({"file": f} if f else {}))
                   for n, t, lu, f in sfx]
           + [{"name": "riser_user", "file": "../../assets/shared/riser_user.mp3", "t": round(t, 3), "gain": 0.45,
               "lu": 1.0, "from": a, "dur": d} for t, a, d in risers]}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(caps)} captions, {len(shots)} shots, {len(out['sfx'])} sfx")
    for c in caps:
        if c["type"] == "situation":
            print(f"  situation {c['n']}: English up {c['en_t']:.2f} -> {c['end']:.2f}"
                  f" (readable {c['end'] - c['pl'] - 0.3:.2f}s after 'please')")


if __name__ == "__main__":
    build()
