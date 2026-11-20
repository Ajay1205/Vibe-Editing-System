"""Manisha 8 -- "Noun = Name, Place, Animal, Thing" (5 takes). Content map + the four versions.

Every spoken line is cut from its raw take at audio-measured boundaries (never inside a word); a version is just an
ordered list of line ids. Gaps between lines are replaced by GAP seconds of her own room tone (the cut sits in the
silence), so pacing is tight but natural.

    python3 -I lines.py            # print every line with its measured in/out and each version's length
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "footage" / "manisha8" / "raw"
WORDS = json.load(open(ROOT / "footage" / "manisha8" / "words.json"))
FPS = 30
GAP = 0.0           # lines butt together; each keeps its own measured head and tail of silence
SILENT_DB = -40     # energy below this = pause

# id: (take, first word start, last word start, text). Times from Whisper, refined below with the energy envelope.
LINES = {
    "def":      ("m81", 0.00, 2.86, "Noun ki definition yaad karne ki zaroorat nahi hai."),
    "bachpan":  ("m81", 3.34, 6.04, "Bas apne bachpan ka ek favourite game yaad kar lo."),
    "npat":     ("m81", 6.84, 8.32, "Name, place, animal, thing."),
    "concept":  ("m81", 8.86, 11.06, "Isi game se related hai hamara noun ka poora concept."),
    "answers":  ("m82", 0.00, 7.28, "Game mein kya likhte hain? Jaise name: Ria, place: Mumbai, animal: tiger, thing: pencil."),
    "notice":   ("m82", 7.94, 16.84, "Ab aap notice karo: Ria kisi person ka naam hai, Mumbai place, tiger animal, pencil thing."),
    "rule":     ("m82", 17.16, 22.04, "Kisi bhi place, person, animal aur thing ke naam ko hum noun kehte hain."),
    "naming":   ("m82", 22.54, 24.80, "In simple words, noun is a naming word."),
    "sent_in":  ("m83", 1.06, 3.06, "Ab iske sentences dekhte hain."),
    "ex1":      ("m83", 3.32, 5.36, "First, meri friend Ria hai."),
    "ex1_why":  ("m83", 5.82, 10.08, "Iss sentence mein Ria ek noun hai, kyunki Ria ek ladki ka naam hai."),
    "ex2":      ("m83", 10.60, 12.46, "Second, main Mumbai mein rehti hoon."),
    "ex2_is":   ("m83", 12.90, 15.04, "Iss sentence mein Mumbai ek noun hai."),
    "ex2_ask":  ("m83", 15.56, 15.94, "Bataiye kyun?"),
    "ex2_why":  ("m83", 16.96, 19.20, "Kyunki Mumbai ek place ka naam hai."),
    "ex3":      ("m83", 20.48, 21.92, "Mujhe tiger se dar lagta hai."),
    "ex3_why":  ("m83", 22.48, 26.44, "Iss sentence mein tiger ek noun hai, kyunki wo ek animal ka naam hai."),
    "ex4":      ("m83", 26.62, 27.74, "I have a pencil."),
    "ex4_why":  ("m83", 28.58, 31.42, "In this sentence, pencil is a noun because it is the name of something."),
    "clear":    ("m84", 0.00, 4.22, "Ab aapko in sentences se noun ka concept samajh aa raha hoga."),
    "types":    ("m84", 4.92, 9.72, "Lekin noun ke do aur types hote hain: special noun aur common noun."),
    "type_ex":  ("m85", 0.00, 6.52, "For example, my friend is Ria. Yahan Ria ek special noun hai, friend ek common noun hai."),
    "part2":    ("m85", 7.02, 9.70, "Yahi difference jaanne ke liye dekhiye hamara part 2,"),
    "part2_b":  ("m85", 11.58, 16.52, "jisme main aapko sikhaungi special noun aur common noun ka matlab aur kai saare examples."),
}

ALL = list(LINES)
VERSIONS = {
    # V1 full: everything, pauses tightened
    "v1_full": ALL,
    # V2 shorter: every noun explanation kept; cut the repeats (the notebook shows them) and the long part-2 pitch
    "v2_short": ["def", "bachpan", "npat", "answers", "rule", "naming", "ex1", "ex1_why", "ex2", "ex2_is", "ex2_why",
                 "ex3", "ex3_why", "ex4", "ex4_why", "types", "type_ex", "part2"],
    # V3 animated: the full explanation with an animated scene on each idea
    "v3_anim": ALL,
    # V4 shortest: cold open on the game, the rule, the naming word, follow for part 2 (text)
    "v4_shortest": ["npat", "def", "answers", "rule", "naming"],
}


def rms(take):
    return WORDS[take]["rms30"]


def words(take):
    return WORDS[take]["words"]


def bounds(lid):
    a, b = _bounds(lid)
    take = LINES[lid][0]
    same = [k for k in LINES if LINES[k][0] == take]
    i = same.index(lid)
    r, fr = rms(take), 0.03
    if i > 0:  # meets the previous line of the same take: cut both at the quietest frame between them
        pa, pb = _bounds(same[i - 1])
        if pb > a:
            a = _quietest(r, LINES[same[i - 1]][2] + 0.15, LINES[lid][1])
    if i + 1 < len(same):
        na, nb = _bounds(same[i + 1])
        if b > na:
            b = _quietest(r, LINES[lid][2] + 0.15, LINES[same[i + 1]][1])
    return round(a, 3), round(b, 3)


def _quietest(r, t0, t1, fr=0.03):
    k0, k1 = int(t0 / fr), max(int(t0 / fr) + 1, int(t1 / fr))
    k = min(range(k0, k1), key=lambda x: r[x])
    return k * fr + fr / 2


def _bounds(lid):
    """Measured (in, out) of a line in its raw take: start just before the first word's onset, end when her voice has
    decayed into silence; clamped so it never reaches into the neighbouring words (never inside a word)."""
    take, s0, s_last, _ = LINES[lid]
    r, ws = rms(take), words(take)
    fr = 0.03
    dur = WORDS[take]["dur"]
    i = int(s0 / fr)
    j = i
    while j > 0 and i - j < 12 and r[j] > SILENT_DB:
        j -= 1
    t_in = max(0.0, j * fr - 0.06)
    prev = [w for w in ws if w["s"] < s0 - 0.05]
    if prev:
        t_in = max(t_in, prev[-1]["e"] + 0.02)
    k = int(s_last / fr) + 3
    while k < len(r) - 5 and not all(x < SILENT_DB for x in r[k:k + 5]):
        k += 1
    t_out = min(dur, k * fr + 0.08)
    nxt = [w for w in ws if w["s"] > s_last + 0.05]
    if nxt:
        t_out = min(t_out, nxt[0]["s"] - 0.05)
    return round(t_in, 3), round(t_out, 3)


MAX_PAUSE, KEEP_PAUSE = 0.5, 0.3  # pauses inside a line longer than MAX_PAUSE shrink to KEEP_PAUSE (cut in the middle)


def pieces(lid):
    """The kept raw intervals of a line, after shrinking its long inner pauses."""
    take = LINES[lid][0]
    a, b = bounds(lid)
    r, fr = rms(take), 0.03
    out, cur, k = [], a, int(a / fr) + 1
    end = int(b / fr)
    while k < end:
        if r[k] < SILENT_DB:
            k2 = k
            while k2 < end and r[k2] < SILENT_DB:
                k2 += 1
            if (k2 - k) * fr > MAX_PAUSE and k2 < end:
                mid_a = k * fr + KEEP_PAUSE / 2
                mid_b = k2 * fr - KEEP_PAUSE / 2
                out.append((round(cur, 3), round(mid_a, 3)))
                cur = mid_b
            k = k2
        k += 1
    out.append((round(cur, 3), round(b, 3)))
    return out


def edl(version):
    """Segments on the output timeline: [{id, take, in, out, start, end}] (a line may give several segments)."""
    t, segs = 0.0, []
    for lid in VERSIONS[version]:
        for a, b in pieces(lid):
            segs.append({"id": lid, "take": LINES[lid][0], "in": a, "out": b, "start": round(t, 3), "end": round(t + b - a, 3)})
            t += b - a
        t += GAP
    return segs


def at(version, lid, raw_t):
    """Raw time inside a line -> output time in a version (None if the line isn't in it). A time inside a removed
    pause snaps to the next kept frame."""
    segs = [s for s in edl(version) if s["id"] == lid]
    for s in segs:
        if raw_t < s["in"]:
            return s["start"]
        if raw_t <= s["out"]:
            return round(s["start"] + raw_t - s["in"], 3)
    return segs[-1]["end"] if segs else None


def span(version, lid):
    segs = [s for s in edl(version) if s["id"] == lid]
    return (segs[0]["start"], segs[-1]["end"]) if segs else None


def word_t(version, lid, word, nth=0):
    """Output time of the nth occurrence of `word` (case-insensitive prefix match) within a line."""
    take, s0, s_last, _ = LINES[lid]
    hits = [w for w in words(take) if s0 - 0.05 <= w["s"] <= s_last + 0.05
            and w["w"].lower().strip(",.?!").startswith(word.lower())]
    if len(hits) <= nth:
        raise KeyError(f"{word!r} #{nth} not in {lid}")
    return at(version, lid, hits[nth]["s"])


if __name__ == "__main__":
    for lid in LINES:
        a, b = bounds(lid)
        kept = sum(y - x for x, y in pieces(lid))
        print(f"{lid:9} {LINES[lid][0]} {a:6.2f}-{b:6.2f} ({b - a:4.2f}s -> {kept:4.2f}s)  {LINES[lid][3]}")
    for v in VERSIONS:
        e = edl(v)
        print(f"{v:12} {len(e):2} lines, {e[-1]['end']:5.1f}s")
