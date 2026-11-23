"""Manisha 9 build ("being: 3 uses"), versions a (Gold Tabs) and b (Explainer Panel).

  python3 -I cut.py                   voice + edl (shared)
  python3 -I build.py cues <v>        sound-effect cues -> build/<v>/cues.json (+ voice_raw.wav copy)
  M9_VERSION=<v> python3 -I mix.py    -> build/<v>/mix.wav
  python3 -I overlay.py <v>; python3 -I build.py caps <v>      caption layer -> build/<v>/overlay_2160.webm
  python3 -I build.py compose <v>     final 4K HDR master -> renders/manisha9_<v>_4k_HDR.mp4
  python3 -I build.py all <v>

Picture: iPhone HLG passes through in HDR (as Nikita 7: SDR conversions made skin look glossy). Each segment is cut
and zoomed from the raw 4K (Lanczos) in 10-bit; only the caption layer is converted from SDR into HLG (colour and
alpha separately, +1.8 stops so white reads white next to her wall). Version b blurs her picture behind the comment
panel from just before "comment kijiye" (blur ramps in over 0.3 s).
"""

import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cut as C  # noqa: E402
from keys import K  # noqa: E402

HERE = C.HERE
ENV = dict(os.environ, NODE_USE_ENV_PROXY="1", NODE_EXTRA_CA_CERTS="/root/.ccr/ca-bundle.crt")
FPS = C.FPS


def t(key, d=0.0):
    tk, s = K[key]
    return round(C.T(tk, s) + d, 3)


def bdir(v):
    d = HERE / "build" / v
    d.mkdir(parents=True, exist_ok=True)
    return d


def blur_at():
    return t("c_comment", -0.2)


def cues(v):
    fx = []

    def add(n, at, lu):
        fx.append((n, max(0.0, at), lu))
    starts = {tk: C.take_start(tk) for tk in range(2, 7)}
    add("impact-bass-1", 0.0, -9)
    if v == "a":
        for i in range(3):
            add("pop", t("uses", 0.15 + 0.18 * i), -11)
    else:
        for i in range(3):
            add("click-soft", t("teen", 0.25 + 0.12 * i), -10)
    for tk in range(2, 7):
        add("whoosh-short", starts[tk] - 0.12, -12)
    # example lands
    for k in ("u1_you", "u2_Being", "u3_the"):
        add("pop", t(k, -0.25 if v == "a" else -0.05), -10)
    if v == "a":
        add("ping", t("u1_rude"), -11)
        add("ping", t("u2_teacher"), -11)
        add("ping", t("u3_painted"), -11)
        add("pop", t("u3_painted", 0.6), -10)
    else:
        add("click-soft", t("u1_rude"), -8)
        add("ping", t("u2_teacher"), -11)
        add("impact-bass-2", t("u3_painted", 0.75), -12)
    add("chime", C.take_start(5) + 0.15, -11)
    add("click", t("c_comment", -0.1), -9)
    add("ping", t("c_next", -0.05), -12)
    fx.sort(key=lambda x: x[1])
    kept = []
    for f in fx:
        if not kept or f[1] - kept[-1][1] > 0.12:
            kept.append(f)
    json.dump({"duration": round(C.duration(), 3), "sfx": [{"name": n, "t": round(a, 3), "gain": 0.5, "lu": lu} for n, a, lu in kept]},
              open(bdir(v) / "cues.json", "w"), indent=1)
    shutil.copy(HERE / "build" / "voice_raw.wav", bdir(v) / "voice_raw.wav")
    print(f"cues {v}: {len(kept)} sfx")


def caps(v):
    subprocess.run(["npx", "hyperframes", "render", str(HERE / "overlay" / v), "--format", "webm", "-o",
                    str(bdir(v) / "overlay_2160.webm"), "--quiet"], check=True, env=ENV, cwd=C.ROOT, stdout=subprocess.DEVNULL)
    print("caption layer", bdir(v) / "overlay_2160.webm")


def compose(v, crf=16):
    W, H = 2160, 3840
    segs = C.edl()
    inputs, parts = [], []
    for i, e in enumerate(segs):
        z = e["zoom"]
        cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
        x0, y0 = int(round(C.FACE[0] * W - C.FACE[0] * cw)), int(round(C.FACE[1] * H - C.FACE[1] * ch))
        inputs += ["-ss", f"{e['in']:.3f}", "-t", f"{e['n'] / FPS + 0.3:.3f}", "-i", str(C.RAW / f"take_{e['take']}.mov")]
        parts.append(f"[{i}:v]fps={FPS},crop={cw}:{ch}:{x0}:{y0},scale={W}:{H}:flags=lanczos,format=yuv420p10le,"
                     f"trim=end_frame={e['n']},setpts=PTS-STARTPTS[v{i}]")
    k = len(segs)
    dur = C.duration()
    base = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=0,tpad=stop_mode=clone:stop_duration={C.TAIL}"
    if v == "b":
        b0 = blur_at()
        base += "".join(f",gblur=sigma={sg}:enable='gte(t,{b0 + d:.3f})'" for sg, d in ((10, 0.0), (14, 0.1), (24, 0.2)))
    graph = (base + "[b];"
             f"[{k}:v]format=yuva420p,split[c][a];[a]alphaextract,format=gray10le[al];"
             "[c]format=yuv420p,eq=saturation=1.5,zscale=tin=bt709:pin=bt709:min=bt709:rin=tv:t=linear:p=bt709:m=gbr:npl=203,"
             "format=gbrpf32le,exposure=exposure=1.8,zscale=tin=linear:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:"
             "m=bt2020nc:r=tv:npl=203,format=yuv444p10le[cc];[cc][al]alphamerge[o];[b][o]overlay=0:0:format=yuv444p10,format=yuv420p10le[v]")
    out = HERE / "renders" / f"manisha9_{v}_4k_HDR.mp4"
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-c:v", "libvpx-vp9", "-i", str(bdir(v) / "overlay_2160.webm"),
                    "-i", str(bdir(v) / "mix.wav"), "-filter_complex", graph, "-map", "[v]", "-map", f"{k + 1}:a",
                    "-c:v", "libx265", "-preset", "medium", "-crf", str(crf), "-tag:v", "hvc1",
                    "-x265-params", "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:open-gop=0:keyint=60:min-keyint=30:log-level=error",
                    "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{dur:.3f}", str(out)], check=True)
    print(out)


def everything(v):
    cues(v)
    subprocess.run([sys.executable, "-I", str(HERE / "mix.py")], check=True, env=dict(os.environ, M9_VERSION=v))
    subprocess.run([sys.executable, "-I", str(HERE / "overlay.py"), v], check=True)
    caps(v)
    compose(v)


if __name__ == "__main__":
    cmd, v = sys.argv[1], sys.argv[2]
    {"cues": lambda: cues(v), "caps": lambda: caps(v), "compose": lambda: compose(v), "all": lambda: everything(v)}[cmd]()
