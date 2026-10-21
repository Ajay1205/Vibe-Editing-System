"""Synthesise the WH Family sound effects the bundled library doesn't have -> assets/sfx/*.wav.

note0..note6 : soft marimba notes (C major pentatonic, rising), one per WH tile -- replaces the paper-flick
               "flip" and "shuffle" sounds (user note: the tile sound was annoying)
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


NOTES = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66]


def marimba(f0):
    """Warm wooden mallet note: fundamental + quiet 4x partial, fast attack, ~0.25 s decay, rounded top."""
    t = t_axis(0.45)
    x = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.16) + 0.18 * np.sin(2 * np.pi * 4 * f0 * t) * np.exp(-t / 0.03)
    x *= np.minimum(1, t / 0.003)
    return lowpass(x, 3500) * np.minimum(1, (t[-1] - t) / 0.05)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [(f"note{k}", lambda f=f: marimba(f)) for k, f in enumerate(NOTES)]:
        x = fn()
        x = 0.9 * x / np.abs(x).max()
        st = np.stack([x, x], 1).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        str(OUT / f"{name}.wav")], input=st.tobytes(), check=True)
        print(OUT / f"{name}.wav", f"{len(x) / SR:.2f}s")


if __name__ == "__main__":
    main()
