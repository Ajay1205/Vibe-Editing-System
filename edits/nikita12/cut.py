"""Nikita 12 (motivational: "galtiyon se mat daro") rough cut: the best take of each line from the raw 4K SDR files.

SEGS are (take, in, out, zoom), edges from the audio energy (never inside a word); neighbours alternate zoom
(1.00 / 1.08 around her face) so every cut is a punch. Her pause after each English sentence stays (reading time).
T(take, s) maps a source time to the output timeline. stage(x, y, seg) maps a raw-frame stage point through the zoom.
"""

import pathlib
import subprocess

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "footage" / "nikita12" / "raw"
BUILD = HERE / "build"
FPS = 30
SR = 48000
FACE = (0.50, 0.45)
TAIL = 1.5

SEGS = [  # (take, in, out, zoom) -- take 1 and take 4 are alternates (take 2 says "bolna"; takes 5+6 are clearer)
    (2, 0.00, 8.70, 1.00),   # hook: bachche itna jaldi kaise seekh jaate... hum adults nahi
    (3, 0.00, 5.60, 1.08),   # kyunki bachche nahi sochte ki galti ho gayi toh...
    (5, 0.00, 6.45, 1.00),   # bachche bina soche bolte... galat bhi
    (6, 0.05, 5.80, 1.08),   # unhi galtiyon se seekh jaate
    (7, 0.00, 9.35, 1.00),   # aur hum kya sochte: galti ho gayi toh? judge kar liya toh?
    (8, 0.00, 5.95, 1.08),   # jab tak ye soch dimaag se nahi nikaaloge... lifelong learner
    (9, 0.00, 25.60, 1.00),  # purpose + speed breakers / potholes + goal
]


def edl():
    out, t = [], 0.0
    for k, (tk, a, b, z) in enumerate(SEGS):
        n = round((b - a) * FPS)
        out.append({"i": k, "take": tk, "in": a, "out": a + n / FPS, "start": t, "end": t + n / FPS, "n": n, "zoom": z})
        t += n / FPS
    return out


def duration():
    return edl()[-1]["end"] + TAIL


def T(take, s):
    for e in edl():
        if e["take"] == take and e["in"] - 1e-6 <= s <= e["out"] + 1e-6:
            return round(e["start"] + s - e["in"], 3)
    raise ValueError(f"take {take} @ {s} is cut out")


def take_start(take):
    return min(e["start"] for e in edl() if e["take"] == take)


def take_end(take):
    return max(e["end"] for e in edl() if e["take"] == take)


def zoom_of(take):
    return [e["zoom"] for e in edl() if e["take"] == take][-1]


def stage(x, y, take):
    """A point measured on the unzoomed 1080x1920 frame -> where it lands in this take's zoomed picture."""
    z = zoom_of(take)
    cx, cy = FACE[0] * 1080, FACE[1] * 1920
    return round(cx + (x - cx) * z), round(cy + (y - cy) * z)


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
        db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)  # noqa: E731
        print(f"  seg {e['i']} take {e['take']} {e['in']:6.2f}-{e['out']:6.2f} -> {e['start']:6.2f}-{e['end']:6.2f} "
              f"edge dB in {db(a[:int(.06 * SR)]):6.1f} out {db(a[-int(.06 * SR):]):6.1f}")
        parts.append(a)
    a = np.vstack(parts + [np.zeros((int(TAIL * SR), 2), np.float32)])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    str(BUILD / "voice_raw.wav")], input=a.tobytes(), check=True)
    print(BUILD / "voice_raw.wav", f"{len(a) / SR:.2f}s")


if __name__ == "__main__":
    voice()
