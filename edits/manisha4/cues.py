"""Cue sheet for the Manisha 4 reel (bank English) -- the content file of the "Situation Series" template.

Same template as edits/nikita4 (layout, fonts, motion); only the CONTENT block, the clips and the palette in
build_overlay.py differ. Times are SOURCE times (clip, seconds into the raw take), read off the word-timed
transcript and the speech envelope; `at()` maps them onto the edited timeline -> cues.json.

Structure: hook -> four situations ONE AFTER ANOTHER (Hindi need, then the English line on a card) ->
"Save karo" recap while she asks for comments -> comment CTA.
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
EDL = json.load(open(HERE / "edl.json"))

# ------------------------------------------------------------------------------------------------ CONTENT
HOOK_CLIP = "m41"
HOOK = {
    "series": "Bank mein<br/><m>English kaise bolein?</m>",  # top title for the whole video (<m> = gold marker)
    "lines": [  # chest captions, word by word; **..** = highlight; t = source time the line starts
        {"t": 0.05, "text": "Bank mein English bolne se **darr?** 😰"},
    ],
    "neon": "Bank", "neon_sub": "4 USEFUL LINES 🏦", "neon_t": 2.54,   # "chaliye ... 4 useful sentences"
}
# Each situation lives in one clip; all its times are source times in that clip.
# en uses **...** for the key words; "please" gets the polite tag. icon = sticker emoji.
# start = Hindi need, q = "kaise bologe?", en_t = English line, key = key word, pl = end of the English line.
# hi2/hi2_t (optional) = the Hindi meaning she gives after the English line.
SITUATIONS = [
    {"clip": "m42", "icon": "🏦", "hi": "Bank mein naya savings account kholna hai",
     "en": "I want to **open a new savings account**.",
     "start": 0.0, "q": 4.14, "en_t": 6.90, "key": 7.98, "pl": 9.90},
    {"clip": "m43", "icon": "💸", "hi": "Transaction fail ho gaya, phir bhi paise kat gaye",
     "en": "My **transaction failed**, but the **money was deducted**.",
     "start": 0.23, "q": 4.48, "en_t": 6.28, "key": 6.62, "pl": 9.55},
    {"clip": "m43", "icon": "💳", "hi": "ATM card kho gaya, block karwana hai",
     "en": "I want to **block my ATM card**.",
     "start": 10.63, "q": 14.52, "en_t": 16.66, "key": 17.84, "pl": 19.40},
    {"clip": "m43", "icon": "🤔", "tag": "⭐ IMPORTANT", "hi": "Bank wale ki English samajh nahi aayi?",
     "en": "Could you **please explain this** to me again?",
     "start": 20.38, "q": 27.92, "en_t": 30.95, "key": 31.62, "pl": 33.35,
     "hi2": "Matlab: Kya aap mujhe ye dobara samjha sakte ho?", "hi2_t": 33.44},
]
RECAP = {"clip": "m44", "t": 0.30, "title": "Save karo 📌", "sub": "4 bank lines",
         "say_t": 0.84, "say": "Ab aap bataiye 👇"}
CTA = {"clip": "m44", "t": 4.94, "head": "Aapka <m>sentence</m>? 🤔", "more_t": 5.36, "comment_t": 5.60,
       "ideas_t": 6.50, "tap_t": 8.66,
       "ideas": ["🧾 Cheque book", "🏠 Loan", "📱 Net banking", "🪪 KYC", "💰 FD", "💳 Credit card"],
       "bar": "Apna sentence comment karo"}
# English line stays up until this far into the next situation (she starts the next Hindi need meanwhile)
READ_HOLD = 1.2
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


def cut_before(clip, src):
    """Output time of the picture cut just before source time `src` (start of the kept segment holding it)."""
    seg = max((x for x in EDL["segments"] if x["clip"] == clip and x["in"] <= src + 0.1), key=lambda x: x["in"])
    return round(seg["start"], 3)


def spaced(shots, gap=1.0):
    """Sorted shots with no two framing moves closer than `gap` s (the later one wins), so glides never overlap."""
    out = []
    for sh in sorted(shots, key=lambda x: x["t"]):
        if out and sh["t"] - out[-1]["t"] < gap:
            out.pop()
        if not out or out[-1]["kind"] != sh["kind"]:
            out.append(sh)
    return out


def build():
    caps, sfx = [], []
    hook_end = section_end(HOOK_CLIP)
    lines = [dict(ln, t=at(HOOK_CLIP, ln["t"]), **({"x_t": at(HOOK_CLIP, ln["x_t"])} if "x_t" in ln else {}),
                  **({"sub_t": at(HOOK_CLIP, ln["sub_t"])} if "sub_t" in ln else {})) for ln in HOOK["lines"]]
    neon_t = at(HOOK_CLIP, HOOK["neon_t"])
    caps.append({"type": "hook", "start": 0.0, "end": hook_end, "lines": lines, "neon": HOOK["neon"],
                 "neon_sub": HOOK["neon_sub"], "neon_t": neon_t})
    shots = [{"t": 0.0, "kind": "close"}] + [{"t": ln["t"], "kind": "mid"} for ln in lines[1:]] + [{"t": neon_t, "kind": "close"}]
    for ln in lines:
        if "x_t" in ln:
            sfx.append(("stamp", ln["x_t"], -3.0, "assets/sfx/stamp.wav"))
    sfx.append(("neon", neon_t - 0.05, -5.0, "assets/sfx/neon.wav"))

    def a(item, key):
        return at(item["clip"], item[key])

    recap = a(RECAP, "t") + READ_HOLD
    starts = [hook_end] + [a(s, "start") + READ_HOLD for s in SITUATIONS[1:]]
    ends = starts[1:] + [recap]
    for i, s in enumerate(SITUATIONS):
        key = a(s, "key")
        cap = {"type": "situation", "n": i + 1, "of": len(SITUATIONS), "icon": s["icon"], "hi": s["hi"], "en": s["en"],
               "start": starts[i], "hi_t": max(starts[i], a(s, "start")), "q": a(s, "q"), "en_t": a(s, "en_t"),
               "key": key, "pl": a(s, "pl"), "end": ends[i], "tag": s.get("tag")}
        if "hi2" in s:
            cap.update(hi2=s["hi2"], hi2_t=a(s, "hi2_t"))
        caps.append(cap)
        shots += [{"t": a(s, "start") if i else starts[i], "kind": "mid"}, {"t": a(s, "q") - 0.04, "kind": "ask"},
                  {"t": a(s, "en_t") - 0.04, "kind": "close"}]
        if i:
            sfx.append(("whoosh-short", cut_before(s["clip"], s["start"]) - 0.1, -5.0, None))  # with the light sweep
        if s.get("kaching"):
            sfx.append(("kaching", key - 0.02, -5.0, "assets/sfx/kaching.wav"))
        else:
            sfx.append(("pop", a(s, "en_t") - 0.02, -4.0, None))  # English card lands

    cta = a(CTA, "t")
    caps.append({"type": "recap", "start": recap, "end": cta, "items": [s["en"] for s in SITUATIONS],
                 "icons": [s["icon"] for s in SITUATIONS], "title": RECAP["title"], "sub": RECAP["sub"],
                 "say": RECAP["say"], "say_t": max(recap + 0.6, a(RECAP, "say_t"))})
    end = section_end(CTA["clip"])
    tap = a(CTA, "tap_t")  # the comment button is tapped, riser crests here
    caps.append({"type": "cta", "start": cta, "end": round(end, 3), "head": CTA["head"], "ideas": CTA["ideas"],
                 "bar": CTA["bar"], "more": a(CTA, "more_t"), "comment": a(CTA, "comment_t"),
                 "ideas_t": a(CTA, "ideas_t"), "tap": tap})
    sfx += [("pop", a(CTA, "comment_t"), -5.0, None), ("click", tap, -1.0, None)]
    shots += [{"t": recap, "kind": "mid"}, {"t": cta, "kind": "mid"}, {"t": tap - 1.6, "kind": "close"}]

    # light sweeps land exactly on the picture cuts: big ones into the situations and into the recap,
    # softer ones between situations
    flashes = [hook_end, cut_before(RECAP["clip"], RECAP["t"])]
    sweeps = sorted(set(flashes + [cut_before(s["clip"], s["start"]) for s in SITUATIONS[1:]]))
    for t in flashes:
        sfx.append(("whoosh", t - 0.12, -4.0, None))

    # Approved riser treatment: first 2 s voice only, riser crest at 0:02-0:03, last 2 s at the end
    risers = [(2.0, 2.0, 1.1), (tap - 1.85, 1.1, 2.0)]

    out = {"duration": EDL["duration"], "fps": EDL["fps"], "captions": caps, "flashes": flashes,
           "series": HOOK["series"], "shots": spaced(shots), "sweeps": sweeps,
           "sfx": [dict({"name": n, "t": round(max(0, t), 3), "gain": 0.5, "lu": lu}, **({"file": f} if f else {}))
                   for n, t, lu, f in sfx]
           + [{"name": "riser_user", "file": "../../assets/shared/riser_user.mp3", "t": round(t, 3), "gain": 0.45,
               "lu": 1.0, "from": a, "dur": d} for t, a, d in risers]}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(caps)} captions, {len(out['shots'])} shots, {len(out['sfx'])} sfx, {out['duration']:.1f}s")
    for c in caps:
        if c["type"] == "situation":
            print(f"  situation {c['n']}: {c['start']:.2f} hi {c['hi_t']:.2f} en {c['en_t']:.2f} -> {c['end']:.2f}"
                  f" (readable {c['end'] - c['pl']:.2f}s after the line)")


if __name__ == "__main__":
    build()
