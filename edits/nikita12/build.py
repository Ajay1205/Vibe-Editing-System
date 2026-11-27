"""Nikita 12 build (motivational), two versions: v1 Hinglish subtitles, v2 Hindi (Devanagari) subtitles.

  python3 -I cut.py ; python3 -I overlay.py
  npx hyperframes render overlay --format webm -o build/overlay_2160.webm   (proxy env vars)
  python3 -I build.py cues ; python3 -I mix.py ; python3 -I build.py compose [--crf N]   -> renders/nikita11_4k.mp4
Picture: the takes are variable frame rate (600/19 fps); cut from the raw 4K and resampled to a steady 30 fps; her colour
untouched (no grade: the Nikita 6 grade washed her skin out on this bright footage). H.264 CRF 15 (33 s reel).
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cut as C  # noqa: E402

HERE = C.HERE
# user, 27 Nov: "nikita is looking a bit dark, just adjust that too" -- a GENTLE midtone lift only (the Nikita 6 curve made
# her look "extremely white" in Nikita 11); compared side by side with the raw on her face before rendering
GRADE = "eq=gamma=1.10:saturation=1.03"


def cues():
    fx = []

    def add(n, at, lu):
        fx.append(dict(name=n, t=round(max(0.0, at), 3), gain=0.5, lu=lu))
    import overlay as O  # noqa: E402
    for k, ((t1, s1), end, _h, _e) in enumerate(O.BIG):
        if k:
            add("impact-bass-1", O.T(t1, s1, 0.1), -13)
    for e in C.edl()[1:]:
        add("whoosh-short", e["start"] - 0.1, -16)
    add("chime", C.duration() - C.TAIL - 0.3, -13)
    fx.sort(key=lambda x: x["t"])
    json.dump({"duration": round(C.duration(), 3), "sfx": fx}, open(HERE / "build" / "cues.json", "w"), indent=1)
    print(f"cues: {len(fx)} sfx")


def compose(v, crf=17):
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
    out = HERE / "renders" / f"nikita12_{v}_4k.mp4"
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-c:v", "libvpx-vp9", "-i", str(HERE / "build" / f"overlay_{v}_2160.webm"),
                    "-i", str(HERE / "build" / "mix.wav"), "-filter_complex", fc, "-map", "[v]", "-map", f"{k + 1}:a",
                    "-c:v", "libx265", "-preset", "medium", "-crf", str(crf), "-tag:v", "hvc1", "-pix_fmt", "yuv420p",
                    "-x265-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709:keyint=60:min-keyint=30:log-level=error",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{C.duration():.3f}", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    crf = int(sys.argv[sys.argv.index("--crf") + 1]) if "--crf" in sys.argv else 17
    {"cues": cues, "compose": lambda: compose(sys.argv[2], crf)}[sys.argv[1]]()
