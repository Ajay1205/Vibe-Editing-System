"""Picture + voice for one Manisha 8 version, cut straight from the raw 4K takes.

Each line has a shot size (wide / mid / close). Consecutive pieces never share a size, so every cut between two
lines (and inside a line where a long pause was shortened) lands as a punch-in or punch-out rather than a jump cut.
Her face sits at (0.50, 0.54) of the raw frame and stays there at every zoom, so the wall above her head is always
free for the notebook graphics. Zoom is done on the raw 4K pixels (Lanczos), one high-quality encode per piece.

Usage: python3 -I render_base.py <version> [--preview]     (preview = 1080x1920)
       -> build/<version>/base[_preview].mp4 + build/<version>/voice_raw.wav
"""

import json
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lines as L  # noqa: E402

FACE = (0.50, 0.54)
ZOOM = {"wide": 1.0, "mid": 1.14, "close": 1.30}
# shot per line: the notebook / list lines stay wide (they need the wall), the punchy lines go close
SHOT = {"def": "close", "bachpan": "mid", "npat": "close", "concept": "wide", "answers": "wide", "notice": "wide",
        "rule": "mid", "naming": "close", "sent_in": "mid", "ex1": "wide", "ex1_why": "mid", "ex2": "wide",
        "ex2_is": "mid", "ex2_ask": "close", "ex2_why": "mid", "ex3": "wide", "ex3_why": "mid", "ex4": "wide",
        "ex4_why": "mid", "clear": "mid", "types": "wide", "type_ex": "wide", "part2": "close", "part2_b": "mid"}
SR = 48000


def plan(version):
    """Segments with a zoom each; neighbours never share a zoom (inner cuts alternate +/-0.06)."""
    segs = L.edl(version)
    prev = None
    for s in segs:
        z = ZOOM[SHOT[L.parent(s["id"])]]
        if prev is not None and abs(z - prev) < 0.03:
            z = round(z + (0.07 if z < 1.25 else -0.07), 3)
        s["zoom"] = z
        prev = z
    return segs


def crop(z, w=2160, h=3840):
    cw, ch = w / z, h / z
    x0 = FACE[0] * w - FACE[0] * cw
    y0 = FACE[1] * h - FACE[1] * ch
    return int(round(cw / 2) * 2), int(round(ch / 2) * 2), int(round(x0)), int(round(y0))


def main(version, preview=False):
    out_dir = HERE / "build" / version
    parts = out_dir / ("parts_preview" if preview else "parts")
    parts.mkdir(parents=True, exist_ok=True)
    W, H = (1080, 1920) if preview else (2160, 3840)
    segs = plan(version)
    listing, voice = [], []
    for i, s in enumerate(segs):
        src = L.RAW / f"manisha_8.{s['take'][-1]}.mov"
        cw, ch, x0, y0 = crop(s["zoom"])
        n = round((s["out"] - s["in"]) * L.FPS)
        p = parts / f"p{i:03d}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['in']:.3f}", "-i", str(src), "-frames:v", str(n),
                        "-vf", f"fps={L.FPS},crop={cw}:{ch}:{x0}:{y0},scale={W}:{H}:flags=lanczos,setsar=1",
                        "-an", "-c:v", "libx264", "-preset", "fast" if not preview else "veryfast",
                        "-crf", "12" if not preview else "18", "-pix_fmt", "yuv420p", "-r", str(L.FPS), str(p)], check=True)
        listing.append(f"file '{p.name}'")
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{s['in']:.3f}", "-i", str(src), "-t", f"{n / L.FPS:.4f}",
                              "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()
        want = int(round(n / L.FPS * SR))
        a = a[:want] if len(a) >= want else np.vstack([a, np.zeros((want - len(a), 2), np.float32)])
        f = int(0.006 * SR)  # 6 ms fades: no clicks at the cuts
        a[:f] *= np.linspace(0, 1, f)[:, None]
        a[-f:] *= np.linspace(1, 0, f)[:, None]
        voice.append(a)
        print(f"  {i:2d} {s['id']:9} {s['take']} {s['in']:6.2f}-{s['out']:6.2f} z{s['zoom']:.2f}", flush=True)
    (parts / "list.txt").write_text("\n".join(listing) + "\n")
    base = out_dir / f"base{'_preview' if preview else ''}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(parts / "list.txt"),
                    "-c", "copy", str(base)], check=True)
    v = np.vstack(voice)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    str(out_dir / "voice_raw.wav")], input=v.tobytes(), check=True)
    json.dump(segs, open(out_dir / "edl.json", "w"), indent=1)
    for p in parts.glob("p*.mp4"):
        p.unlink()
    print(base, f"{len(v) / SR:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1], "--preview" in sys.argv)
