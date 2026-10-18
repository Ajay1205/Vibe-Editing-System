"""Cue sheet for the Manisha 3 reel (English replies for WhatsApp): captions, zoom punches, sound effects.

Times are SOURCE times (seconds into raw clip m31..m33, read off the word-timed transcript), so every cue
stays on its word when the rough cut changes. `at()` maps them onto the edited timeline -> cues.json.

Structure: hook -> four replies, ONE AT A TIME (English reply in a chat notification, its Hinglish meaning
outside the card, both leave before the next) -> comment challenge with the answer hidden.
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


# The four replies. en/hi use **...** for the highlighted phrase. Captions follow her words ("bahut busy").
REPLIES = [
    {"en": "I will **talk to you later**.", "hi": "Main **baad mein** baat karti hoon", "emoji": "⏰",
     "card": 0.40, "en_t": 0.92, "seen": 2.10, "hi_t": 2.64, "out": 4.62},
    {"en": "I am **a bit busy** now.", "hi": "Main **bahut busy** hoon", "emoji": "💼",
     "card": 4.62, "en_t": 5.00, "seen": 5.90, "hi_t": 6.48, "out": 8.30},
    {"en": "See you tomorrow **for sure**.", "hi": "Main kal **pakka** milungi", "emoji": "🤝",
     "card": 8.30, "en_t": 8.48, "seen": 9.90, "hi_t": 10.10, "out": 12.30},
    {"en": "I **didn't see** your message.", "hi": "Maine aapka message **nahi dekha**", "emoji": "🙈",
     "card": 14.10, "en_t": 14.19, "seen": 15.40, "hi_t": 15.62, "out": 17.86},
]

# Zoom punches only on the key sentences: (clip, source time, kind)
PUNCHES = [("m31", 1.60, "small"),                       # "Hi"
           ("m32", 0.92, "small"), ("m32", 5.00, "small"), ("m32", 8.48, "small"), ("m32", 14.19, "small"),
           ("m33", 4.96, "big")]                         # the challenge sentence


def build():
    caps, sfx = [], []
    # Hook: chat "Hi" -> seen, no reply -> headline
    hook_end = section_end("m31") - 0.05
    caps.append({"type": "hook", "start": at("m31", 0.0), "end": hook_end,
                 "beats": {"notif": at("m31", 0.20), "hi": at("m31", 1.60), "seen": at("m31", 2.10),
                           "noreply": at("m31", 2.40), "swap": at("m31", 4.44), "today": at("m31", 6.56)}})
    sfx.append(("whoosh", at("m31", 4.44) - 0.08, 0.0))

    flashes = [at("m32", 0.0), at("m33", 0.0)]
    for t in flashes:
        sfx.append(("whoosh", t - 0.12, 0.0))

    for i, r in enumerate(REPLIES):
        start = at("m32", r["card"])
        caps.append({"type": "reply", "n": i + 1, "en": r["en"], "hi": r["hi"], "emoji": r["emoji"],
                     "start": start, "en_t": at("m32", r["en_t"]), "seen": at("m32", r["seen"]),
                     "hi_t": at("m32", r["hi_t"]), "end": at("m32", r["out"])})
        sfx += [("pop", at("m32", r["en_t"]), -1.0), ("ping", at("m32", r["hi_t"]), -1.0)]

    end = section_end("m33")
    comment_tap = at("m33", 7.56)
    caps.append({"type": "challenge", "start": at("m33", 0.0), "q_t": at("m33", 4.96),
                 "box_t": at("m33", 6.54), "tap": comment_tap, "end": round(end, 3)})
    sfx += [("notification", at("m33", 4.96), -1.0), ("click", comment_tap, 0.0)]

    # Nikita's approved riser treatment: first 2 s voice only, riser crest at 0:02-0:03, last 2 s at the end
    risers = [(2.0, 2.0, 1.1), (comment_tap - 1.85, 1.1, 2.0)]

    punches = [{"t": at(c, s), "kind": k} for c, s, k in PUNCHES]
    out = {"duration": EDL["duration"], "fps": EDL["fps"], "captions": caps, "flashes": flashes,
           "punches": punches,
           "sfx": [{"name": n, "t": round(max(0, t), 3), "gain": 0.5, "lu": lu} for n, t, lu in sfx]
           + [{"name": "riser_user", "file": "assets/user/riser_user.mp3", "t": round(t, 3), "gain": 0.45,
               "lu": 1.0, "from": a, "dur": d} for t, a, d in risers]}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(caps)} captions, {len(punches)} punches, {len(out['sfx'])} sfx")


if __name__ == "__main__":
    build()
