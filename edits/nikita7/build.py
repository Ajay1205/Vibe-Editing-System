"""Nikita 7 -- "Feelings in English" (Hindi -> English feeling words), approved board: edits/nikita7/board (v3).

Steps: python3 -I build.py sfx | base [--4k] | mix | overlay [--4k] | compose [--4k]
  (overlay: then render overlay/ with HyperFrames to build/overlay_<res>.webm)
User rules for this reel: her video stays as shot -- full frame, no grade; the iPhone HDR (HLG) file only gets the
neutral HDR->SDR conversion that keeps her skin natural (the first try looked glossy and white). Words must be
readable, may sit over her. Riser: none at the start (she speaks from frame 1), soft 2 s tail under the question.
"""

import json
import pathlib
import re
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE.parents[1] / "footage" / "nikita7" / "raw"
BUILD = HERE / "build"
FPS = 30
K4 = "--4k" in sys.argv
RES = 2160 if K4 else 1080
TM = ("zscale=t=linear:npl=400,format=gbrpf32le,zscale=p=bt709,tonemap=reinhard:param=0.6:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")

# (clip, in, out) source seconds: the list take, then the comment question
CLIPS = [("7.1", 0.0, 22.30), ("7.2", 0.0, 3.90)]
# (Hindi, English, emoji, Hindi onset, English onset) in clip 7.1 -- onsets measured on the audio energy
WORDS = [
    ("चिढ़ाना", "Annoy", "😤", 0.05, 2.18),
    ("शर्मिंदा", "Embarrass", "😳", 3.10, 4.18),
    ("पछताना", "Regret", "😞", 5.17, 6.16),
    ("झिझकना", "Hesitate", "😬", 7.31, 8.27),
    ("घबरा जाना", "Panic", "😱", 9.22, 10.40),
    ("परेशान होना", "Frustrate", "😩", 11.42, 12.46),
    ("निराश", "Disappoint", "😔", 13.45, 14.39),
    ("बेचैन", "Restless", "😣", 15.38, 16.40),
    ("मनाना", "Convince", "🤝", 17.34, 18.34),
    ("राहत देना", "Relieve", "😌", 19.14, 19.98),
    ("हकदार", "Deserve", "🏆", 20.84, 21.60),
]
QUIZ = {"hi": "ईर्ष्या", "t": 0.20, "comment_t": 2.70}  # in clip 7.2


def starts():
    out, t = {}, 0.0
    for c, a, b in CLIPS:
        n = round((b - a) * FPS)
        out[c] = (t, a, n)
        t += n / FPS
    return out, t


START, DUR = starts()


def at(clip, src):
    t0, a, n = START[clip]
    return round(t0 + min(max(src - a, 0), n / FPS), 3)


# --------------------------------------------------------------------------------------------- picture
def base():
    BUILD.mkdir(exist_ok=True)
    w, h = (2160, 3840) if K4 else (1080, 1920)
    inputs, parts = [], []
    for i, (c, a, b) in enumerate(CLIPS):
        n = round((b - a) * FPS)
        inputs += ["-ss", f"{a:.3f}", "-t", f"{n / FPS + 0.2:.3f}", "-i", str(RAW / f"nikita_{c}.mov")]
        parts.append(f"[{i}:v]fps={FPS},{TM},scale={w}:{h}:flags=lanczos,trim=end_frame={n},setpts=PTS-STARTPTS[v{i}]")
    graph = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(CLIPS))) + f"concat=n={len(CLIPS)}:v=1:a=0[v]"
    out = BUILD / f"base_{RES}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-filter_complex", graph, "-map", "[v]",
                    "-c:v", "libx264", "-preset", "medium" if K4 else "veryfast", "-crf", "12" if K4 else "18",
                    "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    str(out)], check=True)
    print(out)


# --------------------------------------------------------------------------------------------- sound
SR = 48000
NOTES = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66, 1318.5, 1568.0, 1760.0, 2093.0]  # rising pentatonic


def marimba(f0):
    t = np.arange(int(0.45 * SR)) / SR
    x = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.16) + 0.18 * np.sin(2 * np.pi * 4 * f0 * t) * np.exp(-t / 0.03)
    x *= np.minimum(1, t / 0.003) * np.minimum(1, (t[-1] - t) / 0.05)
    return x.astype(np.float32)


def decode(path, start=None, dur=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", f"{start:.3f}", "-t", f"{dur:.3f}"] if start is not None else [])
    pcm = subprocess.run(cmd + ["-i", str(path), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).copy()


def sfx():
    """Voice cut + effect bed (effects levelled by peak, well under her voice)."""
    BUILD.mkdir(exist_ok=True)
    parts = []
    for c, a, b in CLIPS:
        n = round((b - a) * FPS) * SR // FPS
        x = decode(RAW / f"nikita_{c}.mov", a, (b - a) + 0.2)[:n]
        x = np.pad(x, (0, n - len(x)))
        f = int(0.006 * SR)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        parts.append(x)
    voice = np.concatenate(parts)
    bed = np.zeros_like(voice)

    def place(s, t, peak_db):
        s = s / (np.abs(s).max() + 1e-9) * 10 ** (peak_db / 20)
        i = int(t * SR)
        j = min(len(bed), i + len(s))
        bed[i:j] += s[:j - i]

    for k, w in enumerate(WORDS):
        place(marimba(NOTES[k]), at("7.1", w[4]) - 0.02, -24)
    place(marimba(2349.3) + marimba(1760.0) * 0.6, at("7.2", QUIZ["t"]) + 0.1, -26)  # soft two-note "ping" on the question
    riser = decode(HERE.parents[1] / "assets" / "shared" / "riser_user.mp3")
    tail = riser[-2 * SR:].copy()  # its last 2 s, under the question, ending with the video
    tail[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    place(tail, DUR - 2.0, -22)
    for name, x in [("voice_raw", voice), ("sfx", bed)]:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        str(BUILD / f"{name}.wav")], input=x.astype(np.float32).tobytes(), check=True)
    print("voice + sfx", f"{len(voice) / SR:.2f}s")


VOICE = ("highpass=f=80,afftdn=nr=8:nf=-45,acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
         "loudnorm=I=-14:TP=-2:LRA=7")


def mix():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(BUILD / "voice_raw.wav"), "-i", str(BUILD / "sfx.wav"),
                    "-filter_complex", f"[0]{VOICE},aresample=48000[v];[v][1]amix=inputs=2:duration=first:normalize=0,"
                    "alimiter=limit=0.7:attack=2:release=50:level=disabled,aformat=channel_layouts=stereo[o]",
                    "-map", "[o]", "-ar", "48000", "-c:a", "pcm_s16le", str(BUILD / "mix.wav")], check=True)
    log = subprocess.run(["ffmpeg", "-i", str(BUILD / "mix.wav"), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    print(" ".join(log[log.rfind("Summary:"):].split())[:160])


# --------------------------------------------------------------------------------------------- captions
def overlay():
    board = (HERE / "board" / "index.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", board, re.S).group(1)
    rows = "".join(f'<div class="row" id="r{k}"><span class="hi"><span>{hi}</span></span><span class="ar">→</span>'
                   f'<span class="en hid">{en}</span><span class="emo">{emo}</span></div>'
                   for k, (hi, en, emo, _, _) in enumerate(WORDS))
    rows += (f'<div class="row" id="rq"><span class="hi"><span>{QUIZ["hi"]}</span></span><span class="ar">→</span>'
             '<span class="en q">? ? ?</span><span class="emo">🤔</span></div>')
    els = (f'<div id="main" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="1"><div class="p">'
           '<div class="ttl">Feelings <i>in English</i></div><div class="cnt"><b id="cn">00</b> / 11</div>'
           f'<div class="list">{rows}</div><div class="save" id="gs">Guess before I say it! 👀</div>'
           '<div class="cmt" id="cm"><span>💬 Comment karo 👇</span></div></div></div>')
    js = ['tl.set("#main .emo, #rq .en, #rq .emo, #cm", {opacity: 0}, 0);',
          'tl.fromTo("#main .ttl, #main .cnt", {opacity: 0, y: -20}, {opacity: 1, y: 0, duration: 0.35}, 0);',
          'tl.fromTo("#main .row", {opacity: 0, x: -40}, {opacity: 1, x: 0, duration: 0.3, stagger: 0.03, ease: "power3.out"}, 0.05);',
          'tl.fromTo("#gs", {opacity: 0, scale: 0.8}, {opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)"}, 0.3);',
          f'tl.to("#gs", {{opacity: 0, duration: 0.25}}, {at("7.1", WORDS[0][4]) - 0.1});']
    for k, (hi, en, emo, ht, et) in enumerate(WORDS):
        h, e = at("7.1", ht), at("7.1", et)
        r = f"#r{k}"
        if k:
            js.append(f'tl.set("#r{k - 1}", {{attr: {{class: "row"}}}}, {h});')
        js.append(f'tl.set("{r}", {{attr: {{class: "row on"}}}}, {h});'
                  f'tl.fromTo("{r} .hi > span", {{scale: 1.25}}, {{scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false}}, {h});'
                  f'tl.to("{r} .en", {{filter: "blur(0px)", opacity: 1, duration: 0.18}}, {e - 0.04});'
                  f'tl.fromTo("{r} .en", {{scale: 1.35}}, {{scale: 1, duration: 0.35, ease: "back.out(2.6)", transformOrigin: "0% 50%", immediateRender: false}}, {e - 0.04});'
                  f'tl.fromTo("{r} .emo", {{opacity: 0, scale: 0.2, rotation: -30}}, {{opacity: 1, scale: 1, rotation: 0, duration: 0.35, ease: "back.out(3)", immediateRender: false}}, {e + 0.05});'
                  f'tl.set("#cn", {{textContent: "{k + 1:02d}"}}, {e});'
                  f'tl.fromTo("#main .cnt", {{scale: 1.25}}, {{scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false}}, {e});')
        nxt = at("7.1", WORDS[k + 1][3]) if k + 1 < len(WORDS) else at("7.2", 0)
        js.append(f'tl.to("{r} .emo", {{opacity: 0, scale: 0.5, duration: 0.15}}, {nxt - 0.15});')
    q = at("7.2", QUIZ["t"])
    js += [f'tl.set("#r{len(WORDS) - 1}", {{attr: {{class: "row"}}}}, {q});',
           f'tl.set("#rq", {{attr: {{class: "row on"}}}}, {q});',
           f'tl.fromTo("#rq .en", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(3)", transformOrigin: "0% 50%"}}, {q + 0.15});',
           f'tl.to("#rq .en", {{scale: 1.12, duration: 0.3, yoyo: true, repeat: 7, ease: "sine.inOut", transformOrigin: "0% 50%"}}, {q + 0.6});',
           f'tl.fromTo("#rq .emo", {{opacity: 0, scale: 0.2}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(3)"}}, {q + 0.3});',
           f'tl.fromTo("#cm", {{opacity: 0, y: 30, scale: 0.7}}, {{opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(2.4)"}}, {at("7.2", QUIZ["comment_t"])});']
    page = PAGE.replace("%CSS%", css).replace("%DUR%", f"{DUR:.3f}").replace("%ELS%", els).replace("%JS%", "\n  ".join(js))
    if K4:
        page = (page.replace("width=1080, height=1920", "width=2160, height=3840")
                .replace("html, body { width: 1080px; height: 1920px;", "html, body { width: 2160px; height: 3840px;")
                .replace("#root { position: relative; width: 1080px; height: 1920px; }",
                         "#root { position: relative; width: 1080px; height: 1920px; zoom: 2; }")
                .replace('data-width="1080" data-height="1920"', 'data-width="2160" data-height="3840"'))
    out = HERE / "overlay"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    print(out / "index.html", f"{DUR:.2f}s", RES)


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="gsap.min.js"></script>
<style>%CSS%
html, body { background: transparent !important; }
#root { position: relative; width: 1080px; height: 1920px; }
.clip { position: absolute; inset: 0; width: 1080px; height: 1920px; }
.row .en { display: inline-block; }
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%" data-width="1080" data-height="1920" data-fps="30">
%ELS%
</div>
<script>
  const tl = gsap.timeline({ paused: true });
  %JS%
  window.__timelines["main"] = tl;
</script>
</body></html>
"""


# --------------------------------------------------------------------------------------------- final
def compose():
    out = HERE / "renders" / (f"nikita7_final_4k.mp4" if K4 else "nikita7_v1_preview_1080p.mp4")
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", "-i", str(BUILD / f"base_{RES}.mp4"),
                    "-c:v", "libvpx-vp9", "-i", str(BUILD / f"overlay_{RES}.webm"), "-i", str(BUILD / "mix.wav"),
                    "-filter_complex", "[1:v]format=yuva420p[o];[0:v][o]overlay=0:0:format=yuv420,format=yuv420p[v]",
                    "-map", "[v]", "-map", "2:a", "-c:v", "libx264",
                    *(["-preset", "medium", "-crf", "15", "-profile:v", "high", "-level", "5.2"] if K4 else
                      ["-preset", "veryfast", "-crf", "20"]),
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-t", f"{DUR:.3f}", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    {"base": base, "sfx": sfx, "mix": mix, "overlay": overlay, "compose": compose}[sys.argv[1]]()
