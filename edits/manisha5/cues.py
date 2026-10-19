"""Cue sheet for the Manisha 5 reel -- "Pep Talk" (English to cheer up / motivate a friend).

Times are SOURCE times (clip, seconds into the raw take) read off the word-timed transcript; `at()` maps them
onto the edited timeline -> cues.json (captions, camera shots, sound effects).

Structure: hook (mood off? rain cloud -> sun) -> intro -> four pep-talk sentences, one at a time (Hindi line on
the wall, the English line in a speech bubble, a motion graphic each) with a MOOD meter that fills up across the
video -> "kisi ka din better" -> follow CTA.
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


# ------------------------------------------------------------------------------------------------ CONTENT
HOOK = {"clip": "m51", "title_t": 1.22, "sun_t": 3.96, "sub_t": 7.40,
        "title": "Dost ka <em>mood off?</em>", "sub": "English mein cheer up kaise karein? ☀️"}
INTRO = {"clip": "m52", "t": 0.45, "simple_t": 6.10, "line": "Kabhi na kabhi sabko <em>motivation</em> chahiye",
         "sub": "4 simple English sentences ✨"}
# en uses **...** for the key words (hand-drawn underline). hi = Hinglish line on the wall.
# en2/en2_t/tag2 = an upgrade line that replaces the first ("more natural").
PEP = [
    {"clip": "m53", "n": 1, "fx": "sun", "start": 0.94, "hi": "Sab theek ho jaayega", "en_t": 4.46, "key_t": 5.58,
     "en": "Everything will be **fine.**", "mood": 38, "face": "🙂"},
    {"clip": "m53", "n": 2, "fx": "hearts", "start": 6.30, "hi": "Main aapke saath hoon", "en_t": 10.28, "key_t": 10.96,
     "en": "I am **with you.**", "mood": 62, "face": "😊",
     "en2": "I've got your **back.**", "en2_t": 14.72, "key2_t": 15.70, "tag2": "MORE NATURAL ✨", "up_t": 11.46},
    {"clip": "m54", "n": 3, "fx": "muscle", "start": 0.73, "hi": "Himmat mat haaro", "en_t": 8.98, "key_t": 9.64,
     "en": "Do not **give up.**", "mood": 82, "face": "😄"},
    {"clip": "m54", "n": 4, "fx": "confetti", "start": 10.56, "hi": "Tumne sach mein bahut achha kiya", "en_t": 16.92,
     "key_t": 18.08, "en": "You really did **well!**", "mood": 100, "face": "🤩", "tag": "TAARIF"},
]
BETTER = {"clip": "m54", "t": 18.56, "better_t": 21.52,
          "line": "Aise sentences kisi ka din <em>better</em> bana sakte hain"}
CTA = {"clip": "m55", "t": 0.30, "follow_t": 5.78, "daily_t": 6.92, "line": "Simple & useful English ke liye",
       "daily": "Roz kuch naya seekhiye 📚"}
READ_HOLD = 1.0  # each pep card stays this long into the next section's setup
# ---------------------------------------------------------------------------------------------------------


def build():
    caps, sfx, shots = [], [], []
    h = HOOK
    hook_end = section_end(h["clip"])
    caps.append({"type": "hook", "start": 0.0, "end": hook_end, "title": h["title"], "sub": h["sub"],
                 "title_t": at(h["clip"], h["title_t"]), "sun_t": at(h["clip"], h["sun_t"]),
                 "sub_t": at(h["clip"], h["sub_t"])})
    shots += [{"t": 0.0, "kind": "mid"}, {"t": at(h["clip"], h["sun_t"]), "kind": "close"}]
    sfx += [("sparkle", at(h["clip"], h["sun_t"]), -5.0, None)]

    i = INTRO
    intro_s, intro_e = section_end(h["clip"]), section_end(i["clip"])
    caps.append({"type": "intro", "start": intro_s, "end": intro_e, "line": i["line"], "sub": i["sub"],
                 "simple_t": at(i["clip"], i["simple_t"])})
    shots += [{"t": intro_s, "kind": "mid"}]

    starts = [intro_e] + [at(p["clip"], p["start"]) + READ_HOLD for p in PEP[1:]]
    better_t = at(BETTER["clip"], BETTER["t"])
    ends = starts[1:] + [better_t]
    mood = [{"t": 0.05, "pct": 12, "face": "😔"}, {"t": intro_s + 0.3, "pct": 20, "face": "😐"}]
    for k, p in enumerate(PEP):
        c = p["clip"]
        cap = {"type": "pep", "n": p["n"], "fx": p["fx"], "hi": p["hi"], "en": p["en"], "tag": p.get("tag"),
               "start": starts[k], "hi_t": max(starts[k], at(c, p["start"])), "en_t": at(c, p["en_t"]),
               "key_t": at(c, p["key_t"]), "end": ends[k]}
        if "en2" in p:
            cap.update(en2=p["en2"], en2_t=at(c, p["en2_t"]), key2_t=at(c, p["key2_t"]), tag2=p["tag2"],
                       up_t=at(c, p["up_t"]))
        caps.append(cap)
        mood.append({"t": at(c, p["key_t"]) + 0.2, "pct": p["mood"], "face": p["face"]})
        shots += [{"t": at(c, p["start"]) if k else starts[k], "kind": "mid"},
                  {"t": at(c, p["en_t"]) - 0.05, "kind": "close"}]
        sfx += [("chime", at(c, p["en_t"]) - 0.03, -6.0, None), ("sparkle", at(c, p["key_t"]) + 0.2, -7.0, None)]
        if k:
            sfx.append(("whoosh-short", starts[k] - 0.1, -6.0, None))
        if "en2" in p:
            shots += [{"t": at(c, p["up_t"]), "kind": "mid"}, {"t": at(c, p["en2_t"]) - 0.05, "kind": "close"}]
            sfx += [("chime", at(c, p["en2_t"]) - 0.03, -6.0, None), ("pop", at(c, p["key2_t"]), -6.0, None)]
        if p["fx"] == "confetti":
            sfx.append(("pop", at(c, p["key_t"]), -4.0, None))

    b = BETTER
    cta_t = at(CTA["clip"], CTA["t"])
    caps.append({"type": "better", "start": better_t, "end": section_end(b["clip"]), "line": b["line"],
                 "better_t": at(b["clip"], b["better_t"])})
    shots += [{"t": better_t, "kind": "mid"}]
    end = section_end(CTA["clip"])
    tap = at(CTA["clip"], CTA["follow_t"])
    caps.append({"type": "cta", "start": section_end(b["clip"]), "end": round(end, 3), "line": CTA["line"],
                 "daily": CTA["daily"], "tap": tap, "daily_t": at(CTA["clip"], CTA["daily_t"])})
    shots += [{"t": section_end(b["clip"]), "kind": "mid"}, {"t": tap - 1.2, "kind": "close"}]
    sfx += [("click", tap, -2.0, None)]

    # "sunrise glow" transitions on the picture cuts between sections
    glows = [intro_s, intro_e, section_end("m53"), section_end(b["clip"])]
    for t in glows:
        sfx.append(("whoosh", t - 0.12, -5.0, None))

    risers = [(2.0, 2.0, 1.1), (tap - 1.85, 1.1, 2.0)]  # crest at 0:02-0:03, last 2 s on the follow tap
    shots = sorted(shots, key=lambda x: x["t"])
    spaced = []
    for sh in shots:
        if spaced and sh["t"] - spaced[-1]["t"] < 1.0:
            spaced.pop()
        if not spaced or spaced[-1]["kind"] != sh["kind"]:
            spaced.append(sh)
    out = {"duration": EDL["duration"], "fps": EDL["fps"], "captions": caps, "mood": mood, "glows": glows,
           "flashes": glows, "shots": spaced,
           "sfx": [{"name": n, "t": round(max(0, t), 3), "gain": 0.5, "lu": lu} for n, t, lu, f in sfx]
           + [{"name": "riser_user", "file": "../../assets/shared/riser_user.mp3", "t": round(t, 3), "gain": 0.45,
               "lu": 1.0, "from": a, "dur": d} for t, a, d in risers]}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(caps)} captions, {len(spaced)} shots, {len(out['sfx'])} sfx, {out['duration']:.1f}s")
    for c in caps:
        print(f"  {c['type']:7} {c['start']:6.2f} -> {c['end']:6.2f}")


if __name__ == "__main__":
    build()
