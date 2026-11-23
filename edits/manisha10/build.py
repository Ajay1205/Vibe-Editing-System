"""Manisha 10 build ("Tag It", prepositions).

  python3 -I cut.py                  voice + edl
  python3 -I build.py cues           sound-effect cues -> build/cues.json
  python3 -I mix.py                  -> build/mix.wav (-14 LUFS)
  python3 -I overlay.py; python3 -I build.py caps      caption layer -> build/overlay_2160.webm
  python3 -I build.py compose [--crf N]                -> renders/manisha10_4k.mp4
  python3 -I build.py all

Picture: SDR, cut and zoomed from the raw 4K (Lanczos) in one pass. User, 23 Nov: "make her look a little better,
just the video" -> the Nikita 6 grade (brighter warm midtones) + a touch of saturation and crispness on HER picture only,
applied before the caption layer, so caption colours stay exactly as designed. H.264 CRF 15.
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cut as C  # noqa: E402
from keys import K  # noqa: E402

HERE = C.HERE
ENV = dict(os.environ, NODE_USE_ENV_PROXY="1", NODE_EXTRA_CA_CERTS="/root/.ccr/ca-bundle.crt")
GRADE = ("curves=master='0/0 0.2/0.30 0.5/0.66 0.8/0.89 1/1',eq=contrast=1.03:saturation=1.06,"
         "colorbalance=rm=-0.03:bm=0.03,unsharp=5:5:0.3:5:5:0")


def t(key, d=0.0):
    tk, s = K[key]
    return round(C.T(tk, s) + d, 3)


def cues():
    fx = []

    def add(n, at, lu):
        fx.append((n, max(0.0, at), lu))
    for w in ("in", "under", "at"):
        add("pop", t(w, -0.03), -10)
    add("impact-bass-1", t("prepositions"), -9)
    for tk in range(2, 8):
        add("whoosh-short", C.take_start(tk) - 0.12, -12)
    for k in ("on_t", "in_t", "under_t", "at_t"):
        add("pop", t(k, -0.05), -9)
    for k in ("lamp", "table", "box", "in_s1", "pen", "napkin"):
        add("click-soft", t(k, -0.05), -9)
    for k, w in (("on_s0", "on_s3"), ("in_s0", "in_s3"), ("un_s0", "un_s3"), ("a1_0", "a1_4"), ("a2_0", "a2_3")):
        add("pop", t(k, -0.3), -12)
        add("ping", t(w), -12)
    add("click", t("baje", -0.55), -10)
    add("pop", t("gandhi1", 0.15), -10)
    add("whoosh-short", t("q0", -0.35), -13)
    add("pop", t("qprep", 0.1), -12)
    add("ping", t("comment", -0.1), -10)
    add("chime", C.duration() - 1.0, -14)
    fx.sort(key=lambda x: x[1])
    kept = []
    for f in fx:
        if not kept or f[1] - kept[-1][1] > 0.12:
            kept.append(f)
    json.dump({"duration": round(C.duration(), 3), "sfx": [{"name": n, "t": round(a, 3), "gain": 0.5, "lu": lu} for n, a, lu in kept]},
              open(HERE / "build" / "cues.json", "w"), indent=1)
    print(f"cues: {len(kept)} sfx")


def caps():
    subprocess.run(["npx", "hyperframes", "render", str(HERE / "overlay"), "--format", "webm", "-o",
                    str(HERE / "build" / "overlay_2160.webm"), "--quiet"], check=True, env=ENV, cwd=C.ROOT, stdout=subprocess.DEVNULL)
    print("caption layer done")


def compose(crf=15):
    W, H = 2160, 3840
    inputs, parts = [], []
    for i, e in enumerate(C.edl()):
        z = e["zoom"]
        cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
        x0, y0 = int(round(C.FACE[0] * W - C.FACE[0] * cw)), int(round(C.FACE[1] * H - C.FACE[1] * ch))
        inputs += ["-ss", f"{e['in']:.3f}", "-t", f"{e['n'] / C.FPS + 0.3:.3f}", "-i", str(C.RAW / f"take_{e['take']}.mov")]
        crop = f"crop={cw}:{ch}:{x0}:{y0},scale={W}:{H}:flags=lanczos," if z != 1.0 else ""
        parts.append(f"[{i}:v]fps={C.FPS},{crop}setsar=1,format=yuv420p,trim=end_frame={e['n']},setpts=PTS-STARTPTS[v{i}]")
    k = len(C.edl())
    graph = (";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(k)) +
             f"concat=n={k}:v=1:a=0,tpad=stop_mode=clone:stop_duration={C.TAIL},{GRADE},format=yuv420p[b];"
             f"[{k}:v]format=yuva420p[o];[b][o]overlay=0:0:format=yuv420,format=yuv420p[v]")
    out = HERE / "renders" / f"manisha10_4k{'' if crf == 15 else f'_crf{crf}'}.mp4"
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-c:v", "libvpx-vp9", "-i", str(HERE / "build" / "overlay_2160.webm"),
                    "-i", str(HERE / "build" / "mix.wav"), "-filter_complex", graph, "-map", "[v]", "-map", f"{k + 1}:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-profile:v", "high", "-level", "5.2",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{C.duration():.3f}", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    crf = int(sys.argv[sys.argv.index("--crf") + 1]) if "--crf" in sys.argv else 15
    if cmd == "all":
        cues(); subprocess.run([sys.executable, "-I", str(HERE / "mix.py")], check=True); caps(); compose(crf)  # noqa: E702
    else:
        {"cues": cues, "caps": caps, "compose": lambda: compose(crf)}[cmd]()
