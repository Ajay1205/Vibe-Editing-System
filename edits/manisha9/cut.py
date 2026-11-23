"""Manisha 9 ("being: 3 uses") rough cut: six single-line takes, cut straight from the raw iPhone HLG 4K files.

SEGS are (take, in, out) in source seconds, edges set from the audio energy (never inside a word). The only real
cut is her 3 s silence in take 4 before "For example" (kept 0.5 s). Learner pauses after each English line stay.
Each segment gets a shot size; neighbours alternate wide / mid so the cut between takes lands as a punch.
T(take, s) maps a source time to the output timeline (used for every caption and sound cue).

  python3 -I cut.py        -> build/voice_raw.wav + build/edl.json (picture is cut in build.py compose, in HDR)
"""

import json
import pathlib
import subprocess

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "footage" / "manisha9" / "raw"
BUILD = HERE / "build"
FPS = 30
SR = 48000
FACE = (0.50, 0.50)  # her face in the raw frame; it stays put at every zoom
ZOOM = {"wide": 1.0, "mid": 1.10}
TAIL = 1.2  # end hold after her last word (CTA readable)

SEGS = [  # (take, in, out, shot)
    (1, 0.33, 6.00, "mid"),     # hook: Being word ke teen different uses ... bahut hi simple hai
    (2, 0.27, 11.00, "wide"),   # use 1: behave ... you are being rude today ... aaj aap thoda rude behave kar rahe ho
    (3, 0.00, 15.15, "mid"),    # use 2: pehchaan ... being a teacher ... teacher hone ke naate ...
    (4, 0.00, 7.00, "wide"),    # use 3: kisi kaam ke hone ki baat ... being ye word use kar sakte ho
    (4, 9.60, 16.35, "mid"),    #        For example, the house is being painted ... ghar ko paint kiya ja raha hai
    (5, 0.56, 5.85, "wide"),    # recap: I hope ... clarity mil gayi ho
    (6, 0.00, 14.80, "mid"),    # CTA: confusing words ... comment kijiye ... next video ...
]


def frames(a, b):
    return round((b - a) * FPS)


def edl():
    out, t = [], 0.0
    for k, (tk, a, b, shot) in enumerate(SEGS):
        n = frames(a, b)
        out.append({"i": k, "take": tk, "in": a, "out": a + n / FPS, "start": t, "end": t + n / FPS, "n": n, "zoom": ZOOM[shot]})
        t += n / FPS
    return out


def duration():
    return edl()[-1]["end"] + TAIL


def T(take, s):
    """Source time in a take -> output time (the segment that contains it)."""
    for e in edl():
        if e["take"] == take and e["in"] - 1e-6 <= s <= e["out"] + 1e-6:
            return round(e["start"] + s - e["in"], 3)
    raise ValueError(f"take {take} @ {s} is cut out")


def take_end(take):
    return max(e["end"] for e in edl() if e["take"] == take)


def take_start(take):
    return min(e["start"] for e in edl() if e["take"] == take)


def voice():
    BUILD.mkdir(exist_ok=True)
    parts = []
    for e in edl():
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{e['in']:.3f}", "-i", str(RAW / f"take_{e['take']}.mov"),
                              "-t", f"{e['n'] / FPS:.4f}", "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        a = np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()
        want = int(round(e["n"] / FPS * SR))
        a = a[:want] if len(a) >= want else np.vstack([a, np.zeros((want - len(a), 2), np.float32)])
        f = int(0.006 * SR)
        a[:f] *= np.linspace(0, 1, f)[:, None]
        a[-f:] *= np.linspace(1, 0, f)[:, None]
        edge = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)  # noqa: E731
        print(f"  seg {e['i']} take {e['take']} {e['in']:6.2f}-{e['out']:6.2f} -> {e['start']:6.2f}-{e['end']:6.2f} "
              f"edge dB in {edge(a[:int(.06 * SR)]):6.1f} out {edge(a[-int(.06 * SR):]):6.1f}")
        parts.append(a)
    a = np.vstack(parts + [np.zeros((int(TAIL * SR), 2), np.float32)])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    str(BUILD / "voice_raw.wav")], input=a.tobytes(), check=True)
    json.dump(edl(), open(BUILD / "edl.json", "w"), indent=1)
    print(BUILD / "voice_raw.wav", f"{len(a) / SR:.2f}s")


if __name__ == "__main__":
    voice()
