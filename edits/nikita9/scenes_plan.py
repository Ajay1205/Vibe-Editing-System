"""V2: where the picture cuts to an animated scene (anim/<name> -> footage/nikita9/broll/<name>.mp4).
Each scene plays during her Hindi situation and ends just before her English sentence, so she is always on screen
(with the chat card) when she says the sentence. The caption layer is off during a scene; scenes carry their own text."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cut as C  # noqa: E402
from keys import K  # noqa: E402

WIN = {  # scene: (start (take, s), end (take, s) or sentence key -> 0.12 s before its first word)
    "hook": ((1, 6.55), (1, 10.95)),
    "update": ((3, 1.20), "s1"),
    "delay": ((4, 1.10), "s2"),
    "help": ((4, 10.30), "s3"),
    "done": ((5, 0.70), "s4"),
    "priority": ((5, 8.20), "s5"),
    "idea": ((6, 2.60), "s6"),
    "leave": ((7, 6.90), (7, 11.30)),
}


def brolls():
    out = []
    for name, (a, b) in WIN.items():
        s = C.T(*a)
        e = C.T(*K[b][0]) - 0.12 if isinstance(b, str) else C.T(*b)
        out.append({"key": name, "file": f"{name}.mp4", "start": round(s, 3), "end": round(e, 3), "dur": round(e - s, 3)})
    return out


if __name__ == "__main__":
    for b in brolls():
        print(b)
