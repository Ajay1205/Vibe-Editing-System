"""Synthesise the restaurant sound effects the bundled library doesn't have -> assets/sfx/*.wav.

kaching : small, soft cash-register "cha-ching" for the bill (drawer click + two light coin rings, ~0.7 s)
stamp   : rubber stamp slammed on paper (low thud + paper slap)
neon    : neon sign switching on (two quick flickers, then a short buzzing hum)
Deterministic (fixed seed), so the build is reproducible.
"""

import pathlib
import subprocess

import numpy as np

SR = 48000
OUT = pathlib.Path(__file__).resolve().parent / "assets" / "sfx"
rng = np.random.default_rng(7)


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


def kaching():
    """Short and soft on purpose (user note: the long bell ring was unbearable): mellow coin rings, no ring-out."""
    t = t_axis(0.75)
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.006)
    click = lowpass(click, 5000) - lowpass(click, 900)
    thunk = 0.5 * np.sin(2 * np.pi * 160 * t) * np.exp(-t / 0.03)
    x = click + thunk
    for start, f0, amp in [(0.085, 1568.0, 0.55), (0.165, 1975.5, 0.42)]:
        tt = np.clip(t - start, 0, None)
        on = (t >= start) * np.minimum(1, tt / 0.002)
        ring = sum(a * np.exp(-tt / d) * np.sin(2 * np.pi * f0 * r * tt)
                   for r, a, d in [(1.0, 1.0, 0.16), (2.0, 0.3, 0.08), (2.76, 0.25, 0.05)])
        x = x + amp * on * ring
    x = lowpass(x, 7000)
    return x * np.minimum(1, (t[-1] - t) / 0.05)


def stamp():
    t = t_axis(0.5)
    thud = np.sin(2 * np.pi * (95 - 40 * t) * t) * np.exp(-t / 0.09)
    slap = rng.standard_normal(len(t)) * np.exp(-t / 0.012)
    slap = lowpass(slap, 2500)
    return thud + 0.9 * slap


def neon():
    t = t_axis(1.1)
    buzz = np.sign(np.sin(2 * np.pi * 100 * t)) + 0.5 * np.sin(2 * np.pi * 200 * t)
    buzz = lowpass(buzz, 2500) + 0.15 * (rng.standard_normal(len(t)) - lowpass(rng.standard_normal(len(t)), 4000))
    gate = np.zeros_like(t)
    for a, b in [(0.0, 0.06), (0.14, 0.19), (0.30, 1.1)]:
        gate[(t >= a) & (t < b)] = 1
    gate = lowpass(gate, 300)
    tail = np.minimum(1, (t[-1] - t) / 0.4)
    clicks = np.zeros_like(t)
    for a in (0.0, 0.14, 0.30):
        i = int(a * SR)
        clicks[i:i + 200] += rng.standard_normal(200) * np.exp(-np.arange(200) / 40)
    return 0.6 * buzz * gate * tail + clicks


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("kaching", kaching), ("stamp", stamp), ("neon", neon)]:
        x = fn()
        x = 0.9 * x / np.abs(x).max()
        st = np.stack([x, x], 1).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        str(OUT / f"{name}.wav")], input=st.tobytes(), check=True)
        print(OUT / f"{name}.wav", f"{len(x) / SR:.2f}s")


if __name__ == "__main__":
    main()
