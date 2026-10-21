"""Cue sheet for the Nikita 6 reel -- "The WH Family" (7 WH question words).

Times are SOURCE times (clip, seconds into the raw take). Whisper word starts ran ~0.4 s early on these takes,
so every time below was checked against the audio energy (speech onsets after the measured dips).
`at()` maps them onto the edited timeline -> cues.json (captions, camera shots, sound effects, transitions).

Structure: hook (the family, still locked "?" tiles) -> "7 words family / question leaders" -> meanings
(tiles flip Hindi -> English one by one) -> examples (mini family bar lights the WH word, Hindi question on the
wall, English question on a latte card with the WH word as a coloured chip) -> quiz for the comments -> save.
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


def section_start(clip):
    return at(clip, 0)


def section_end(clip):
    return at(clip, 999)


# ------------------------------------------------------------------------------------------------ CONTENT
FAMILY = ["What", "When", "Where", "Why", "Who", "Which", "Whose"]
HOOK = {"clip": "n61", "tiles_t": 4.20, "sub_t": 6.95, "rule_t": 10.30,
        "title": "The <b>WH</b> Family", "sub": "7 words · 100s of English questions", "rule": "📌 English grammar ka rule"}
LEADERS = {"clip": "n62", "family_t": 4.24, "leaders_t": 7.45, "start_t": 9.70,
           "label": "👑 Question Leaders", "label2": "Question inhi se start hota hai"}
# meanings: (English, Hindi, clip, Hindi time, English time) -- times from the energy onsets
MEANINGS = [("What", "kya", "n63", 4.13, 5.80), ("When", "kab", "n63", 6.75, 8.35),
            ("Where", "kahan", "n64", 0.65, 1.53), ("Why", "kyun", "n64", 2.62, 3.43),
            ("Who", "kaun", "n64", 5.11, 5.96), ("Which", "kaunsa", "n64", 6.96, 7.92),
            ("Whose", "kiska", "n64", 8.98, 9.93)]
EX_INTRO = {"clip": "n65", "t": 0.50, "line": "Ab examples dekhte hain 👇"}
# examples: the WH word is the first word of `en`
EXAMPLES = [
    {"clip": "n65", "hi": "Aaj aapne kya khaya?", "hi_t": 2.80, "en": "What did you eat today?", "en_t": 4.70},
    {"clip": "n65", "hi": "Meri book kahan hai?", "hi_t": 6.72, "en": "Where is my book?", "en_t": 8.35},
    {"clip": "n65", "hi": "Tum late kyun ho?", "hi_t": 11.30, "en": "Why are you late today?", "en_t": 13.10},
    {"clip": "n65", "hi": "Tum kab aaoge?", "hi_t": 15.67, "en": "When will you come?", "en_t": 17.05},
    {"clip": "n65", "hi": "Tumhare class teacher kaun hain?", "hi_t": 19.53, "en": "Who is your class teacher?", "en_t": 21.63},
    {"clip": "n65", "hi": "Tumhari favourite movie kaun si hai?", "hi_t": 23.80, "en": "Which is your favourite movie?", "en_t": 25.72},
    {"clip": "n66", "hi": "Ye bag kiska hai?", "hi_t": 0.48, "en": "Whose bag is it?", "en_t": 1.92},
]
QUIZ = {"clip": "n66", "hi": "Tumhara favourite colour kaun sa hai?", "hi_t": 4.22, "en": "is your favourite colour?",
        "ask_t": 6.15, "ask": "💬 Kaun sa WH word? Comment karo!"}
SAVE = {"clip": "n67", "save_t": 1.50, "strip_t": 7.15, "line": "<b>Save</b> karo!", "sub": "Confusion ho toh revisit karo"}
READ_HOLD = 0.7  # each English card stays this long into the next Hindi question
# ---------------------------------------------------------------------------------------------------------


def build():
    caps, sfx, shots = [], [], []
    # hook + leaders: one caption clip so the family grid stays put across the n61 -> n62 cut
    h, l = HOOK, LEADERS
    caps.append({"type": "family", "start": 0.0, "end": section_end(l["clip"]), "title": h["title"], "sub": h["sub"],
                 "rule": h["rule"], "label": l["label"], "label2": l["label2"], "words": FAMILY,
                 "tiles_t": at(h["clip"], h["tiles_t"]), "sub_t": at(h["clip"], h["sub_t"]),
                 "rule_t": at(h["clip"], h["rule_t"]), "family_t": at(l["clip"], l["family_t"]),
                 "leaders_t": at(l["clip"], l["leaders_t"]), "start_t": at(l["clip"], l["start_t"])})
    shots += [{"t": 0.0, "kind": "mid"}, {"t": at(h["clip"], h["rule_t"]) - 0.3, "kind": "close"},
              {"t": section_start(l["clip"]), "kind": "mid"}, {"t": at(l["clip"], l["leaders_t"]) - 0.3, "kind": "close"}]
    sfx += [("pop", at(h["clip"], h["tiles_t"]), -6.0), ("sparkle", at(l["clip"], l["family_t"]), -7.0),
            ("ping", at(l["clip"], l["leaders_t"]), -8.0)]
    for k in range(7):
        sfx.append(("flip", at(h["clip"], h["tiles_t"]) + 0.08 * k, -12.0))

    # meanings across n63 + n64
    m_s, m_e = section_start("n63"), section_end("n64")
    tiles = [{"en": en, "hi": hi, "hi_t": at(c, ht), "en_t": at(c, et)} for en, hi, c, ht, et in MEANINGS]
    caps.append({"type": "meanings", "start": m_s, "end": m_e, "tiles": tiles})
    shots += [{"t": m_s, "kind": "mid"}]
    for tl in tiles:
        sfx += [("flip", tl["hi_t"], -9.0), ("flip", tl["en_t"] - 0.05, -5.0)]

    # examples
    ex_s = section_start("n65")
    caps.append({"type": "exintro", "start": ex_s, "end": at("n65", EXAMPLES[0]["hi_t"]),
                 "line": EX_INTRO["line"]})
    starts = [at(e["clip"], e["hi_t"]) for e in EXAMPLES]
    quiz_t = at(QUIZ["clip"], QUIZ["hi_t"])
    ends = [starts[k + 1] + READ_HOLD for k in range(len(EXAMPLES) - 1)] + [quiz_t]
    for k, e in enumerate(EXAMPLES):
        c = e["clip"]
        en_t = at(c, e["en_t"])
        wh = e["en"].split()[0]
        caps.append({"type": "example", "n": k + 1, "wh": wh, "idx": FAMILY.index(wh), "hi": e["hi"],
                     "en": e["en"], "start": starts[k], "hi_t": starts[k], "en_t": en_t, "end": ends[k],
                     "next": starts[k + 1] if k + 1 < len(EXAMPLES) else None, "words": FAMILY})
        shots += [{"t": starts[k] - 0.1, "kind": "mid"}, {"t": en_t - 0.1, "kind": "close"}]
        sfx += [("pop", en_t - 0.03, -6.0)]
        if k:
            sfx.append(("whoosh-short", starts[k] - 0.12, -10.0))

    q = QUIZ
    caps.append({"type": "quiz", "start": quiz_t, "end": section_end(q["clip"]), "hi": q["hi"], "en": q["en"],
                 "ask": q["ask"], "ask_t": at(q["clip"], q["ask_t"]), "words": FAMILY})
    shots += [{"t": quiz_t - 0.1, "kind": "mid"}, {"t": at(q["clip"], q["ask_t"]), "kind": "close"}]
    sfx += [("pop", quiz_t + 0.2, -7.0), ("ping", at(q["clip"], q["ask_t"]), -7.0)]

    s = SAVE
    sv_s, end = section_start(s["clip"]), section_end(s["clip"])
    save_t, strip_t = at(s["clip"], s["save_t"]), at(s["clip"], s["strip_t"])
    caps.append({"type": "save", "start": sv_s, "end": round(end, 3), "line": s["line"], "sub": s["sub"],
                 "save_t": save_t, "strip_t": strip_t, "words": FAMILY})
    shots += [{"t": sv_s, "kind": "mid"}, {"t": strip_t - 0.3, "kind": "close"}]
    sfx += [("sparkle", save_t, -5.0), ("pop", strip_t, -8.0)]

    # tile-shuffle transitions on the section cuts; a soft warm flash on the other jump cuts
    shuffles = [section_start("n63"), section_start("n65"), section_start("n67")]
    flashes = [section_start("n62"), section_start("n64"), section_start("n66")]
    for t in shuffles:
        sfx += [("shuffle", t - 0.25, -6.0), ("whoosh", t - 0.15, -9.0)]
    for t in flashes:
        sfx.append(("whoosh-short", t - 0.1, -11.0))

    risers = [(2.0, 2.0, 1.1), (end - 2.0, 1.1, 2.0)]  # crest at 0:02-0:03, last 2 s at the end
    shots = sorted(shots, key=lambda x: x["t"])
    spaced = []
    for sh in shots:
        if spaced and sh["t"] - spaced[-1]["t"] < 1.0:
            spaced.pop()
        if not spaced or spaced[-1]["kind"] != sh["kind"]:
            spaced.append(sh)
    lib = {"flip": "assets/sfx/flip.wav", "shuffle": "assets/sfx/shuffle.wav"}
    out = {"duration": EDL["duration"], "fps": EDL["fps"], "captions": caps, "shuffles": shuffles,
           "flashes": flashes, "shots": spaced,
           "sfx": [dict({"name": n, "t": round(max(0, t), 3), "gain": 0.5, "lu": lu},
                        **({"file": lib[n]} if n in lib else {})) for n, t, lu in sfx]
           + [{"name": "riser_user", "file": "../../assets/shared/riser_user.mp3", "t": round(t, 3), "gain": 0.45,
               "lu": 1.0, "from": a, "dur": d} for t, a, d in risers]}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(caps)} captions, {len(spaced)} shots, {len(out['sfx'])} sfx, {out['duration']:.1f}s")
    for c in caps:
        print(f"  {c['type']:8} {c['start']:6.2f} -> {c['end']:6.2f}")


if __name__ == "__main__":
    build()
