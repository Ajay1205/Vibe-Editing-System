"""Where each Manisha 8 version cuts away to an animated scene (anim/<scene> -> footage/manisha8/broll/<scene>.mp4).

V3 (animated): one scene per idea, on the line that introduces it; her voice carries on underneath.
V4 (shortest): quick flashes on each game answer (Ria, Mumbai, tiger, pencil) and the naming-word card as the
ending, held TAIL seconds with the follow CTA built into that scene.
While a scene is up the caption layer is switched off (compose.py), so every scene carries its own text.
"""

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lines as L  # noqa: E402

TAIL = {"v4_shortest": 1.6}  # seconds held after her last word (scene + CTA)

V3 = {  # line id: (scene, in-point inside the scene, end: None = whole line | (line, word) = cut back on that word)
    "bachpan": ("game", 0.0, None),
    "naming": ("naming", 0.0, None),
    "ex1": ("ria_s", 0.0, None),
    "ex2": ("mumbai_s", 0.0, None),
    "ex3": ("tiger_s", 0.0, None),
    "ex4": ("pencil_s", 0.0, None),
    "type_ex": ("proper", 0.0, ("type_ex", "yaha")),
    "part2": ("part2", 0.0, None),
}
V4_FLASH = [("ria", "place"), ("mumbai", "animal"), ("tiger", "thing"), ("pencil", None)]  # answer word -> until next word


def brolls(version):
    """[{key, file, in, start, end}] on the output timeline."""
    out = []
    if version == "v3_anim":
        for lid, (scene, sin, until) in V3.items():
            sp = L.span(version, lid)
            if not sp:
                continue
            end = sp[1] if until is None else L.word_t(version, until[0], until[1]) - 0.06
            out.append({"key": lid, "file": f"{scene}.mp4", "in": sin, "start": sp[0], "end": round(end, 3)})
    if version == "v4_shortest":
        for word, nxt in V4_FLASH:
            t = L.word_t(version, "answers", word) - 0.04
            e = (L.word_t(version, "answers", nxt) - 0.06) if nxt else L.span(version, "answers")[1]
            out.append({"key": f"answers_{word}", "file": f"{word}_w.mp4", "in": 0.95, "start": round(t, 3), "end": round(e, 3)})
        sp = L.span(version, "naming")
        out.append({"key": "naming", "file": "naming_end.mp4", "in": 0.0, "start": sp[0], "end": round(sp[1] + TAIL[version], 3)})
    return out


def cutaways(version):
    """{line id: (start, end)} for lines whose picture is (at least partly) a scene."""
    return {b["key"]: (b["start"], b["end"]) for b in brolls(version) if b["key"] in L.LINES}


def cut_end(version, lid):
    return cutaways(version)[lid][1]


if __name__ == "__main__":
    for v in ("v3_anim", "v4_shortest"):
        for b in brolls(v):
            print(v, b)
