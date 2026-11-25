"""Nikita 11 build ("Stop Saying OPEN").

  python3 -I cut.py ; python3 -I overlay.py
  npx hyperframes render overlay --format webm -o build/overlay_2160.webm   (proxy env vars)
  python3 -I build.py cues ; python3 -I mix.py ; python3 -I build.py compose [--crf N]   -> renders/nikita11_4k.mp4
Picture: the takes are variable frame rate (600/19 fps); cut from the raw 4K and resampled to a steady 30 fps; the
Nikita 6 grade on her picture only (captions untouched). H.264 CRF 15 (33 s reel).
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cut as C  # noqa: E402
import overlay as O  # noqa: E402

HERE = C.HERE
GRADE = ("curves=master='0/0 0.2/0.30 0.5/0.66 0.8/0.89 1/1',eq=contrast=1.03:saturation=1.04,"
         "colorbalance=rm=-0.03:bm=0.03")


def cues():
    fx = []

    def add(n, at, lu):
        fx.append(dict(name=n, t=round(max(0.0, at), 3), gain=0.5, lu=lu))
    add("impact-bass-1", 0.0, -12)
    for k, (name, emo, tk, o, dn, r, v, verb, obj) in enumerate(O.ITEMS):
        add("whoosh-short", O.T(tk, o, -0.15), -15)
        add("error", O.T(tk, dn, -0.05), -17)       # soft buzz on "you don't open..."
        add("pop", O.T(tk, r, -0.25), -12)          # the right card lands
        add("ping", O.T(tk, v, -0.04), -12)         # the verb turns green
    add("whoosh-short", O.T(3, O.QUIZ["now"], -0.2), -14)
    add("pop", O.T(3, O.QUIZ["open"], -0.08), -12)
    add("click", O.T(3, O.QUIZ["how"], -0.1), -12)
    add("ping", O.T(3, O.QUIZ["comment"], -0.1), -11)
    fx.sort(key=lambda x: x["t"])
    kept = []
    for f in fx:
        if not kept or f["t"] - kept[-1]["t"] > 0.12:
            kept.append(f)
    json.dump({"duration": round(C.duration(), 3), "sfx": kept}, open(HERE / "build" / "cues.json", "w"), indent=1)
    print(f"cues: {len(kept)} sfx")


def compose(crf=15):
    W, H = 2160, 3840
    inputs, parts = [], []
    segs = C.edl()
    for i, e in enumerate(segs):
        z = e["zoom"]
        cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
        x0, y0 = int(round(C.FACE[0] * W - C.FACE[0] * cw)), int(round(C.FACE[1] * H - C.FACE[1] * ch))
        inputs += ["-ss", f"{e['in']:.3f}", "-t", f"{e['n'] / C.FPS + 0.3:.3f}", "-i", str(C.RAW / f"take_{e['take']}.mov")]
        crop = f"crop={cw}:{ch}:{x0}:{y0},scale={W}:{H}:flags=lanczos," if z != 1.0 else ""
        parts.append(f"[{i}:v]fps={C.FPS},{crop}setsar=1,format=yuv420p,trim=end_frame={e['n']},setpts=PTS-STARTPTS[v{i}]")
    k = len(segs)
    fc = (";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(k)) +
          f"concat=n={k}:v=1:a=0,tpad=stop_mode=clone:stop_duration={C.TAIL},{GRADE},format=yuv420p[b];"
          f"[{k}:v]format=yuva420p[o];[b][o]overlay=0:0:format=yuv420,format=yuv420p[v]")
    out = HERE / "renders" / f"nikita11_4k{'' if crf == 15 else f'_crf{crf}'}.mp4"
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-c:v", "libvpx-vp9", "-i", str(HERE / "build" / "overlay_2160.webm"),
                    "-i", str(HERE / "build" / "mix.wav"), "-filter_complex", fc, "-map", "[v]", "-map", f"{k + 1}:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-profile:v", "high", "-level", "5.2",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{C.duration():.3f}", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    crf = int(sys.argv[sys.argv.index("--crf") + 1]) if "--crf" in sys.argv else 15
    {"cues": cues, "compose": lambda: compose(crf)}[sys.argv[1]]()
