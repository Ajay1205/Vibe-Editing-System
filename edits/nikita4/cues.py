"""Cue sheet for the Nikita 4 reel (restaurant English, situation based): captions, zoom punches, sound effects.

Times are SOURCE times (seconds into raw clip n41/n42, read off the word-timed transcript and the speech
envelope), so every cue stays on its word when the rough cut changes. `at()` maps them onto the edited
timeline -> cues.json.

Structure: hook (ratta vs situations, neon "Restaurant English") -> five situations ONE AFTER ANOTHER
(Hindi need as a waiter's note + animated icon, then the English line written on an order ticket) ->
"Today's Menu" recap -> comment CTA.
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


# The five situations (clip n42). en uses **...** for the key words; "please" gets the polite badge.
# start = Hindi need, q = "English mein kaise bologe?", en = English line, key = key word, pl = "please".
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
     "start": 27.02, "q": 27.98, "en_t": 29.74, "key": 30.46, "pl": 30.72},
]
RECAP, CTA = 32.37, 38.62  # n42 source times

# Calm punch-ins (raw framing otherwise): two on the hook, one on each English line. (clip, source time, kind)
PUNCHES = [("n41", 4.50, "small"), ("n41", 8.68, "small")] + [("n42", s["en_t"], "small") for s in SITUATIONS]


def build():
    caps, sfx = [], []
    hook_end = section_end("n41")
    caps.append({"type": "hook", "start": 0.0, "end": hook_end,
                 "beats": {"book": at("n41", 1.48), "stamp": at("n41", 3.00), "sit": at("n41", 4.50),
                           "talk": at("n41", 5.78), "aaj": at("n41", 7.50), "neon": at("n41", 8.68)}})
    sfx += [("stamp", at("n41", 3.00), 0.0, "assets/sfx/stamp.wav"), ("pop", at("n41", 4.50), -1.0, None),
            ("neon", at("n41", 8.68) - 0.05, -2.0, "assets/sfx/neon.wav")]

    starts = [at("n42", s["start"]) - (0.2 if i else 0.0) for i, s in enumerate(SITUATIONS)]
    starts[0] = hook_end
    recap = at("n42", RECAP)
    ends = starts[1:] + [recap]
    for i, s in enumerate(SITUATIONS):
        pl = at("n42", s["pl"])
        caps.append({"type": "situation", "n": i + 1, "icon": s["icon"], "hi": s["hi"], "en": s["en"],
                     "start": starts[i], "hi_t": max(starts[i], at("n42", s["start"])), "q": at("n42", s["q"]),
                     "en_t": at("n42", s["en_t"]), "key": at("n42", s["key"]), "pl": pl, "end": ends[i]})
        if i:
            sfx.append(("whoosh-short", starts[i] - 0.05, -2.0, None))  # ticket swipe
        sfx.append(("bell", pl + 0.32, -1.0, "assets/sfx/bell.wav"))  # order placed: ding after "please"
        if s["icon"] == "bill":
            sfx.append(("printer", at("n42", s["key"]) - 0.1, -4.0, "assets/sfx/printer.wav"))

    cta = at("n42", CTA)
    caps.append({"type": "recap", "start": recap, "end": cta, "items": [s["en"] for s in SITUATIONS],
                 "icons": [s["icon"] for s in SITUATIONS], "say": at("n42", 35.88)})
    end = section_end("n42")
    tap = at("n42", 48.70)  # "...videos banaungi": the comment button is tapped, riser crests here
    caps.append({"type": "cta", "start": cta, "end": round(end, 3), "more": at("n42", 39.98),
                 "comment": at("n42", 42.56), "ideas": at("n42", 44.10), "tap": tap})
    sfx += [("pop", at("n42", 42.56), -2.0, None), ("click", tap, 0.0, None)]

    flashes = [hook_end, recap]  # candle-glow bloom + whoosh: into the situations, into the recap
    for t in flashes:
        sfx.append(("whoosh", t - 0.12, 0.0, None))

    # Approved riser treatment: first 2 s voice only, riser crest at 0:02-0:03, last 2 s at the end
    risers = [(2.0, 2.0, 1.1), (tap - 1.85, 1.1, 2.0)]

    punches = [{"t": at(c, s), "kind": k} for c, s, k in PUNCHES]
    out = {"duration": EDL["duration"], "fps": EDL["fps"], "captions": caps, "flashes": flashes,
           "punches": punches,
           "sfx": [dict({"name": n, "t": round(max(0, t), 3), "gain": 0.5, "lu": lu}, **({"file": f} if f else {}))
                   for n, t, lu, f in sfx]
           + [{"name": "riser_user", "file": "../../assets/shared/riser_user.mp3", "t": round(t, 3), "gain": 0.45,
               "lu": 1.0, "from": a, "dur": d} for t, a, d in risers]}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(caps)} captions, {len(punches)} punches, {len(out['sfx'])} sfx")
    for s in sorted(out["sfx"], key=lambda x: x["t"]):
        print(f"  {s['t']:6.2f} {s['name']}")


if __name__ == "__main__":
    build()
