"""Synthesise the WH Family sound effects the bundled library doesn't have -> assets/sfx/*.wav.

flip    : a light card flip (paper flick + soft low tap, ~0.15 s) for each tile turning over
shuffle : a soft card riffle (seven quick flicks, ~0.45 s) under the tile-shuffle transitions
Deterministic (fixed seed), so the build is reproducible.
"""

import pathlib
import subprocess

import numpy as np

SR = 48000
OUT = pathlib.Path(__file__).resolve().parent / "assets" / "sfx"
rng = np.random.default_rng(11)


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def flick(t, at, bright=1.0):
    """One paper flick: a band-passed noise burst with a fast attack and a ~15 ms decay."""
    tt = np.clip(t - at, 0, None)
    env = (t >= at) * np.minimum(1, tt / 0.0015) * np.exp(-tt / 0.015)
    n = rng.standard_normal(len(t)) * env
    return lowpass(n, 4200 * bright) - lowpass(n, 700)


def flip():
    t = t_axis(0.18)
    tap = 0.35 * np.sin(2 * np.pi * 210 * t) * np.exp(-t / 0.025)
    x = flick(t, 0.0) + 0.6 * flick(t, 0.045, 0.8) + tap
    return x * np.minimum(1, (t[-1] - t) / 0.02)


def shuffle():
    t = t_axis(0.5)
    x = sum((0.6 + 0.4 * np.sin(k)) * flick(t, 0.03 + k * 0.055, 0.9 + 0.03 * k) for k in range(7))
    return lowpass(x, 6000) * np.minimum(1, (t[-1] - t) / 0.04)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("flip", flip), ("shuffle", shuffle)]:
        x = fn()
        x = 0.9 * x / np.abs(x).max()
        st = np.stack([x, x], 1).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        str(OUT / f"{name}.wav")], input=st.tobytes(), check=True)
        print(OUT / f"{name}.wav", f"{len(x) / SR:.2f}s")


if __name__ == "__main__":
    main()
