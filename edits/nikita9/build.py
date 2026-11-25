"""Nikita 9 build ("Office Chat"), two versions (user, 25 Nov: "very explanatory" + "version 2 with animations
related EXACTLY to those sentences"):
  v1  her picture + caption layer (sticky notes, typed chat messages, meaning chips)
  v2  v1 + animated scenes (anim/make_scenes.py) during each situation, hard cuts, caption layer off during a scene

  python3 -I cut.py                      voice + edl
  python3 -I overlay.py ; npx hyperframes render overlay --format webm -o build/overlay_2160.webm
  python3 -I anim/make_scenes.py render  scenes -> footage/nikita9/broll/
  python3 -I build.py cues <v> ; N9_VERSION=<v> python3 -I mix.py
  python3 -I build.py compose <v> [--crf N] [--h264]     -> renders/nikita9_<v>_4k.mp4 (HEVC CRF 17 by default: ~80 s reel)
  python3 -I build.py all <v>
Picture: the Nikita 6 grade on HER picture only (before scenes and captions), so graphic colours never change.
"""

import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cut as C  # noqa: E402
import scenes_plan as SP  # noqa: E402
from keys import K  # noqa: E402

HERE = C.HERE
BROLL = C.ROOT / "footage" / "nikita9" / "broll"
GRADE = ("curves=master='0/0 0.2/0.30 0.5/0.66 0.8/0.89 1/1',eq=contrast=1.03:saturation=1.04,"
         "colorbalance=rm=-0.03:bm=0.03")


def T(x, d=0.0):
    return round(C.T(*x) + d, 3)


def t(key, d=0.0):
    return T(K[key], d)


def bdir(v):
    d = HERE / "build" / v
    d.mkdir(parents=True, exist_ok=True)
    return d


def cues(v):
    fx = []

    def add(n, at, lu, **kw):
        fx.append(dict(name=n, t=round(max(0.0, at), 3), gain=0.5, lu=lu, **kw))
    scenes = SP.brolls() if v == "v2" else []
    if v == "v1":  # the typed-then-deleted message in the hook
        add("typing", t("h_opinions"), -16, **{"from": 0.0, "dur": 1.5})
        add("error", t("h_darr", -0.05), -15)
    add("pop", t("h_corporate", -0.1), -12)
    add("whoosh-short", C.take_start(2) - 0.1, -13)
    add("pop", t("i_five", -0.1), -10)
    for i in range(5):
        add("click-soft", t("i_sentences", -0.2) + 0.12 * i, -12)
    add("sparkle", t("i_office"), -12)
    for sid in ("s1", "s2", "s3", "s4", "s5", "s6"):
        ws = K[sid]
        add("whoosh-short", t(f"{sid}_sit", 0.02), -14)
        add("pop", T(ws[0], -0.35), -12)
        add("click-soft", T(ws[-1], 0.15), -11)
        add("chime" if sid == "s6" else "ping", T(ws[-1], 0.3), -12)
    add("whoosh-short", C.take_start(7) + t("q_sit", -0.3) - C.take_start(7), -13)
    add("pop", t("q_sit", -0.3), -11)
    add("click", t("q_chhutti", -0.2), -11)
    add("ping", t("q_kaise", -0.1), -10)
    for b in scenes:  # into each scene and back to her
        add("whoosh-short", b["start"] - 0.06, -12)
        add("whoosh-short", b["end"] - 0.04, -15)
    if v == "v2":
        hk = [b for b in scenes if b["key"] == "hook"][0]
        add("click", hk["start"] + (hk["dur"] + 0.2) * 0.55 + 0.35, -12)  # the lock lands on her mic
    fx.sort(key=lambda x: x["t"])
    kept = []
    for f in fx:
        if not kept or f["t"] - kept[-1]["t"] > 0.12:
            kept.append(f)
    json.dump({"duration": round(C.duration(), 3), "sfx": kept}, open(bdir(v) / "cues.json", "w"), indent=1)
    shutil.copy(HERE / "build" / "voice_raw.wav", bdir(v) / "voice_raw.wav")
    print(f"cues {v}: {len(kept)} sfx")


def compose(v, crf=17, h264=False):
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
    fc = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=0,tpad=stop_mode=clone:stop_duration={C.TAIL},{GRADE},format=yuv420p[b0]"
    inputs += ["-c:v", "libvpx-vp9", "-i", str(HERE / "build" / "overlay_2160.webm"), "-i", str(bdir(v) / "mix.wav")]
    n_ov, n_mix = k, k + 1
    last = "b0"
    br = SP.brolls() if v == "v2" else []
    for j, b in enumerate(br):
        inputs += ["-t", f"{b['dur'] + 0.2:.3f}", "-i", str(BROLL / b["file"])]
        idx = k + 2 + j
        fc += (f";[{idx}:v]fps={C.FPS},scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p,setpts=PTS-STARTPTS+{b['start']:.3f}/TB[r{j}];"
               f"[{last}][r{j}]overlay=enable='between(t,{b['start']:.3f},{b['end'] - 0.001:.3f})':eof_action=pass[x{j}]")
        last = f"x{j}"
    off = "+".join(f"between(t,{b['start']:.3f},{b['end'] - 0.001:.3f})" for b in br)
    en = f":enable='not({off})'" if off else ""
    fc += f";[{n_ov}:v]format=yuva420p[o];[{last}][o]overlay=0:0:format=yuv420{en},format=yuv420p[v]"
    tag = "" if (crf == 17 and not h264) else f"_{'h264' if h264 else 'hevc'}_crf{crf}"
    out = HERE / "renders" / f"nikita9_{v}_4k{tag}.mp4"
    out.parent.mkdir(exist_ok=True)
    venc = (["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-profile:v", "high", "-level", "5.2"] if h264 else
            ["-c:v", "libx265", "-preset", "medium", "-crf", str(crf), "-tag:v", "hvc1", "-pix_fmt", "yuv420p",
             "-x265-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709:keyint=60:min-keyint=30:log-level=error"])
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", f"{n_mix}:a", *venc,
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{C.duration():.3f}", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    cmd, v = sys.argv[1], sys.argv[2]
    crf = int(sys.argv[sys.argv.index("--crf") + 1]) if "--crf" in sys.argv else 17
    h264 = "--h264" in sys.argv
    if cmd in ("cues", "all"):
        cues(v)
    if cmd == "all":
        subprocess.run([sys.executable, "-I", str(HERE / "mix.py")], check=True, env=dict(os.environ, N9_VERSION=v))
    if cmd in ("compose", "all"):
        compose(v, crf, h264)
