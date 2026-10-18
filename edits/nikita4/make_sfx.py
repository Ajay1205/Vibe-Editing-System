"""Synthesise the restaurant sound effects the bundled library doesn't have -> assets/sfx/*.wav.

bell    : desk service bell "ding" (struck metal: inharmonic partials, slight beating, long ring)
printer : receipt printer feeding paper (fast thermal-head chatter + motor hum, ~0.9 s)
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


def bell():
    t = t_axis(2.2)
    f0 = 2093.0
    parts = [(1.0, 1.0, 1.6), (1.0021, 0.6, 1.5), (2.76, 0.45, 0.8), (5.40, 0.22, 0.35), (8.93, 0.08, 0.15),
             (0.52, 0.10, 0.9)]
    x = sum(a * np.exp(-t / d) * np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6.3)) for r, a, d in parts)
    strike = rng.standard_normal(len(t)) * np.exp(-t / 0.002) * 0.6
    x = x + strike - lowpass(strike, 3000)
    x *= np.minimum(1, t / 0.0015)
    return x


def printer():
    t = t_axis(0.95)
    chatter = rng.standard_normal(len(t))
    chatter = chatter - lowpass(chatter, 1800)
    gate = (np.sin(2 * np.pi * 38 * t) > 0.15).astype(float)  # head steps
    gate = lowpass(gate, 400)
    hum = 0.25 * np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5
    hum = lowpass(hum, 900)
    env = np.minimum(1, t / 0.03) * np.minimum(1, (t[-1] - t) / 0.06)
    tear = np.zeros_like(t)
    return (0.5 * chatter * gate + hum) * env + tear


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
    for name, fn in [("bell", bell), ("printer", printer), ("stamp", stamp), ("neon", neon)]:
        x = fn()
        x = 0.9 * x / np.abs(x).max()
        st = np.stack([x, x], 1).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        str(OUT / f"{name}.wav")], input=st.tobytes(), check=True)
        print(OUT / f"{name}.wav", f"{len(x) / SR:.2f}s")


if __name__ == "__main__":
    main()
