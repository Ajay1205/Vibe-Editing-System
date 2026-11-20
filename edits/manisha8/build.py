"""Manisha 8 build: cues -> mix -> caption layer -> final composite, per version.

  python3 -I render_base.py <v> [--preview]          picture + voice from the raw 4K takes
  python3 -I build.py cues <v>                        sound-effect cues (+ the end hold for v4)
  M8_VERSION=<v> python3 -I mix.py                    voice + sfx -> build/<v>/mix.wav (-14 LUFS)
  python3 -I overlay.py <v> ; python3 -I build.py caps <v>     caption layer -> build/<v>/overlay_2160.webm
  python3 -I build.py compose <v> [--preview] [--crf N]
  python3 -I build.py all <v> [--preview]             everything above in order

Versions: v1_full, v2_short, v3_anim, v4_shortest (see lines.py). Scenes: anim/make_scenes.py.
"""

import json
import os
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lines as L  # noqa: E402
import scenes_plan as SP  # noqa: E402

BROLL = L.ROOT / "footage" / "manisha8" / "broll"
RENDERS = HERE / "renders"
ENV = dict(os.environ, NODE_USE_ENV_PROXY="1", NODE_EXTRA_CA_CERTS="/root/.ccr/ca-bundle.crt")


def bdir(v):
    d = HERE / "build" / v
    d.mkdir(parents=True, exist_ok=True)
    return d


def cues(v):
    W = lambda lid, w, n=0: L.word_t(v, lid, w, n)  # noqa: E731
    order = L.VERSIONS[v]
    sp = {lid: L.span(v, lid) for lid in order}
    fx = []  # (name, t, lu)

    def add(name, t, lu):
        if t is not None:
            fx.append((name, max(0.0, t), lu))
    if v == "v4_shortest":
        add("impact-bass-2", 0.0, -6)
        for h in ("name", "place", "animal", "thing"):
            add("pop", W("npat", h), -9)
    if "def" in order:
        add("whoosh-short", sp["def"][0], -12)
        add("impact-bass-1", W("def", "nahi") + 0.1, -5)
    nb_open = None
    for lid in order:
        if lid in ("npat", "answers") and lid in sp:
            if nb_open is None or nb_open != order[order.index(lid) - 1]:
                add("whoosh-short", sp[lid][0] - 0.08, -11)
        nb_open = lid if lid in ("npat", "concept", "answers", "notice", "rule") else None
    if "npat" in order and v != "v4_shortest":
        for h in ("name", "place", "animal", "thing"):
            add("pop", W("npat", h), -10)
    if "answers" in order:
        for w in ("ria", "mumbai", "tiger", "pencil"):
            add("click-soft" if v != "v4_shortest" else "whoosh-short", W("answers", w), -8)
    if "notice" in order:
        for w in ("person", "place", "animal", "thing"):
            add("pop", W("notice", w), -11)
    if "rule" in order:
        add("ping", W("rule", "noun"), -8)
    if "naming" in order:
        add("sparkle", W("naming", "naming"), -7)
    for sl, why, noun in (("ex1", "ex1_why", "ria"), ("ex2", "ex2_is", "mumbai"), ("ex3", "ex3_why", "tiger"), ("ex4", "ex4_why", "pencil")):
        if sl in order:
            add("pop", W(sl, noun), -8)
            add("ping", W(why, "noun"), -9)
    if "ex2_ask" in order:
        add("click", sp["ex2_ask"][0], -9)
    if "types" in order:
        add("pop", W("types", "special"), -9)
        add("pop", W("types", "common"), -9)
    if "type_ex" in order:
        add("ping", W("type_ex", "special"), -9)
        add("ping", W("type_ex", "common"), -9)
    if "part2" in order:
        add("chime", sp["part2"][0] + 0.1, -9)
    for b in SP.brolls(v):  # a soft whoosh into every animated scene
        if not b["key"].startswith("answers_"):
            add("whoosh-short", b["start"] - 0.06, -11)
    if v == "v4_shortest":
        add("chime", L.span(v, "naming")[1] + 0.4, -8)
    fx.sort(key=lambda x: x[1])
    # drop near-duplicates (two effects within 0.12 s: keep the first)
    kept = []
    for f in fx:
        if not kept or f[1] - kept[-1][1] > 0.12:
            kept.append(f)
    dur = L.edl(v)[-1]["end"] + SP.TAIL.get(v, 0.0)
    out = {"duration": round(dur, 3), "sfx": [{"name": n, "t": round(t, 3), "gain": 0.5, "lu": lu} for n, t, lu in kept]}
    json.dump(out, open(bdir(v) / "cues.json", "w"), indent=1)
    # end hold: pad her voice with silence so the mix runs to the end
    wav = bdir(v) / "voice_raw.wav"
    if wav.exists() and SP.TAIL.get(v):
        a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                                         capture_output=True, check=True).stdout, np.float32).reshape(-1, 2)
        want = int(round(dur * 48000))
        if len(a) < want:
            a = np.vstack([a, np.zeros((want - len(a), 2), np.float32)])
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", "48000", "-ac", "2", "-i", "-", str(wav)],
                           input=a.tobytes(), check=True)
    print(f"cues {v}: {len(kept)} sfx, {dur:.2f}s")


def caps(v, res=2160):
    subprocess.run(["npx", "hyperframes", "render", str(HERE / "overlay" / v), "--format", "webm", "-o",
                    str(bdir(v) / f"overlay_{res}.webm"), "--quiet"], check=True, env=ENV, cwd=L.ROOT, stdout=subprocess.DEVNULL)
    print("caption layer", bdir(v) / f"overlay_{res}.webm")


def compose(v, preview=False, crf=15):
    RENDERS.mkdir(exist_ok=True)
    W, H = (1080, 1920) if preview else (2160, 3840)
    base = bdir(v.replace("v3_anim", "v1_full")) / f"base{'_preview' if preview else ''}.mp4"  # v3 shares v1's picture
    if not base.exists():
        base = bdir(v) / f"base{'_preview' if preview else ''}.mp4"
    dur = json.load(open(bdir(v) / "cues.json"))["duration"]
    tail = SP.TAIL.get(v, 0.0)
    br = SP.brolls(v)
    ins = ["-i", str(base), "-c:v", "libvpx-vp9", "-i", str(bdir(v) / "overlay_2160.webm"), "-i", str(bdir(v) / "mix.wav")]
    fc = [f"[0:v]fps=30,{'tpad=stop_mode=clone:stop_duration=' + str(tail) + ',' if tail else ''}format=yuv420p[b0]"]
    last = "b0"
    for k, b in enumerate(br):
        ins += ["-ss", f"{b['in']:.3f}", "-t", f"{b['end'] - b['start'] + 0.2:.3f}", "-i", str(BROLL / b["file"])]
        fc.append(f"[{3 + k}:v]fps=30,scale={W}:{H}:flags=lanczos,setsar=1,setpts=PTS-STARTPTS+{b['start']:.3f}/TB[r{k}];"
                  f"[{last}][r{k}]overlay=enable='between(t,{b['start']:.3f},{b['end'] - 0.001:.3f})':eof_action=pass[x{k}]")
        last = f"x{k}"
    off = "+".join(f"between(t,{b['start']:.3f},{b['end'] - 0.001:.3f})" for b in br)
    enable = f":enable='not({off})'" if off else ""
    fc.append(f"[1:v]{'scale=1080:1920:flags=lanczos,' if preview else ''}format=yuva420p[o];[{last}][o]overlay=0:0:format=yuv420{enable},format=yuv420p[v]")
    out = RENDERS / f"manisha8_{v}_{'preview_1080p' if preview else '4k'}{'' if preview or crf == 15 else f'_crf{crf}'}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "2:a",
                    "-t", f"{dur:.3f}", "-c:v", "libx264", *(["-preset", "veryfast", "-crf", "20"] if preview else
                                                            ["-preset", "medium", "-crf", str(crf), "-profile:v", "high", "-level", "5.2"]),
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out)], check=True)
    print(out)


def everything(v, preview=False):
    src = "v1_full" if v == "v3_anim" else v
    if not (bdir(src) / f"base{'_preview' if preview else ''}.mp4").exists():
        subprocess.run([sys.executable, "-I", str(HERE / "render_base.py"), src] + (["--preview"] if preview else []), check=True)
    if v == "v3_anim":
        import shutil
        shutil.copy(bdir("v1_full") / "voice_raw.wav", bdir(v) / "voice_raw.wav")
    cues(v)
    subprocess.run([sys.executable, "-I", str(HERE / "mix.py")], check=True, env=dict(os.environ, M8_VERSION=v))
    subprocess.run([sys.executable, "-I", str(HERE / "overlay.py"), v], check=True)
    caps(v)
    compose(v, preview)


if __name__ == "__main__":
    cmd, v = sys.argv[1], sys.argv[2]
    crf = int(sys.argv[sys.argv.index("--crf") + 1]) if "--crf" in sys.argv else 15
    {"cues": lambda: cues(v), "caps": lambda: caps(v), "compose": lambda: compose(v, "--preview" in sys.argv, crf),
     "all": lambda: everything(v, "--preview" in sys.argv)}[cmd]()
