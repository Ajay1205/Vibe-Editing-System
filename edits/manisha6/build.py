"""Manisha 6 -- spice names in English ("Kuch masalon ke naam English mein seekhte hain").

Steps: python3 -I build.py sfx | mix | overlay [--4k] | base [--4k] | compose [--4k]
  (overlay: then render overlay/ with HyperFrames to build/overlay_<res>.webm)
The approved Nikita 7 list style (every word stays on screen), with the user's spice photos as round tokens:
  - as she says the Hindi name, its photo pops in big on the wall above her head (viewers see it before the answer),
  - the English answer is blurred in its row until she says it, then pops out (yellow) and the big photo flies down
    into the row's thumbnail; rows sit below her face,
  - the last row is her comment question: नमक -> "? ? ?" + "Comment karo".
Video untouched (SDR iPhone footage this time: no grade, no zoom). Clip 1 starts at "kuch" (user: cut "aaj hum").
"""

import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE.parents[1] / "footage" / "manisha6" / "raw"
BUILD = HERE / "build"
FPS = 30
K4 = "--4k" in sys.argv
RES = 2160 if K4 else 1080

CLIPS = [("6.1", 0.43, 7.10), ("6.2", 0.50, 10.35)]  # source in/out (clip 1 from "kuch")
# (Hindi, English, image, clip, Hindi onset, English onset) -- onsets from the audio energy
WORDS = [
    ("जीरा", "Cumin", "cumin", "6.1", 2.82, 3.54),
    ("अजवाइन", "Carom Seeds", "ajwain", "6.1", 4.50, 5.40),
    ("लौंग", "Clove", "clove", "6.2", 0.60, 1.44),
    ("धनिया पाउडर", "Coriander Powder", "coriander", "6.2", 2.22, 3.24),
    ("दालचीनी", "Cinnamon", "cinnamon", "6.2", 4.56, 5.52),
]
QUIZ = {"hi": "नमक", "img": "salt", "clip": "6.2", "t": 6.36, "comment_t": 9.10}


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


# --------------------------------------------------------------------------------------------- sound
SR = 48000
NOTES = [523.25, 659.25, 783.99, 880.0, 1046.5]
SFX_LIB = pathlib.Path.home() / ".claude/skills/media-use/audio/assets/sfx"


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
    BUILD.mkdir(exist_ok=True)
    parts = []
    for c, a, b in CLIPS:
        n = round((b - a) * FPS) * SR // FPS
        x = decode(RAW / f"manisha_{c}.mov", a, (b - a) + 0.2)[:n]
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

    pop = decode(SFX_LIB / "pop.mp3")
    for k, w in enumerate(WORDS):
        place(pop, at(w[3], w[4]), -30)  # soft pop as the photo appears
        place(marimba(NOTES[k]), at(w[3], w[5]) - 0.02, -24)  # rising note on the answer
    place(pop, at(QUIZ["clip"], QUIZ["t"]), -30)
    place(marimba(1568.0) + 0.6 * marimba(2093.0), at(QUIZ["clip"], QUIZ["comment_t"]), -27)
    riser = decode(HERE.parents[1] / "assets" / "shared" / "riser_user.mp3")
    tail = riser[-2 * SR:].copy()
    tail[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    place(tail, DUR - 2.0, -22)
    for name, x in [("voice_raw", voice), ("sfx", bed)]:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        str(BUILD / f"{name}.wav")], input=x.astype(np.float32).tobytes(), check=True)
    print("voice + sfx", f"{len(voice) / SR:.2f}s")


VOICE = ("highpass=f=80,afftdn=nr=8:nf=-45,acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
         "loudnorm=I=-13.1:TP=-2:LRA=7,volume=1.4dB")


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
    rows = "".join(f'<div class="row" id="r{k}"><img class="th" src="img/tok_{img}.png"/><span class="hi"><span>{hi}</span></span>'
                   f'<span class="ar">→</span><span class="en hid">{en}</span></div>'
                   for k, (hi, en, img, _, _, _) in enumerate(WORDS))
    rows += (f'<div class="row" id="rq"><img class="th" src="img/tok_{QUIZ["img"]}.png"/><span class="hi"><span>{QUIZ["hi"]}</span></span>'
             '<span class="ar">→</span><span class="en q">? ? ?</span></div>')
    bigs = "".join(f'<img class="big" id="b{k}" src="img/tok_{w[2]}.png"/>' for k, w in enumerate(WORDS))
    bigs += f'<img class="big" id="bq" src="img/tok_{QUIZ["img"]}.png"/><div class="qm" id="qm">?</div>'
    els = (f'<div id="main" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="1">'
           '<div class="ttl">मसालों के नाम <i>in English</i> 🌶️</div>'
           f'{bigs}<div class="guess" id="gs">Guess before I say it! 👀</div>'
           f'<div class="list">{rows}</div><div class="cmt" id="cm"><span>💬 Comment karo 👇</span></div></div>')
    js = ['tl.set("#main .big, #qm, #rq .en, #cm", {opacity: 0}, 0);',
          'tl.fromTo("#main .ttl", {opacity: 0, y: -20}, {opacity: 1, y: 0, duration: 0.35}, 0);',
          'tl.fromTo("#main .row", {opacity: 0, x: -40}, {opacity: 1, x: 0, duration: 0.3, stagger: 0.04, ease: "power3.out"}, 0.05);',
          'tl.fromTo("#gs", {opacity: 0, scale: 0.8}, {opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)"}, 0.3);',
          f'tl.to("#gs", {{opacity: 0, duration: 0.2}}, {at(WORDS[0][3], WORDS[0][4]) - 0.2:.3f});']

    def fly(big, row, t):
        # the big photo shrinks and flies into its row thumbnail
        return (f'tl.to("{big}", {{x: () => {{ const a = document.querySelector("{big}").getBoundingClientRect(), '
                f'b = document.querySelector("{row} .th").getBoundingClientRect(); return b.left + b.width / 2 - (a.left + a.width / 2); }}, '
                f'y: () => {{ const a = document.querySelector("{big}").getBoundingClientRect(), '
                f'b = document.querySelector("{row} .th").getBoundingClientRect(); return b.top + b.height / 2 - (a.top + a.height / 2); }}, '
                f'scale: 0.22, opacity: 0, duration: 0.45, ease: "power2.in"}}, {t:.3f});'
                f'tl.fromTo("{row} .th", {{scale: 0.4}}, {{scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false}}, {t + 0.4:.3f});')

    for k, (hi, en, img, c, ht, et) in enumerate(WORDS):
        h, e, r, b = at(c, ht), at(c, et), f"#r{k}", f"#b{k}"
        if k:
            js.append(f'tl.set("#r{k - 1}", {{attr: {{class: "row"}}}}, {h:.3f});')
        js.append(f'tl.set("{r}", {{attr: {{class: "row on"}}}}, {h:.3f});'
                  f'tl.fromTo("{b}", {{opacity: 0, scale: 0.3, rotation: -25}}, {{opacity: 1, scale: 1, rotation: -4, duration: 0.45, ease: "back.out(2.2)", immediateRender: false}}, {h:.3f});'
                  f'tl.fromTo("{r} .hi > span", {{scale: 1.25}}, {{scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false}}, {h:.3f});'
                  f'tl.to("{r} .en", {{filter: "blur(0px)", opacity: 1, duration: 0.18}}, {e - 0.04:.3f});'
                  f'tl.fromTo("{r} .en", {{scale: 1.35}}, {{scale: 1, duration: 0.35, ease: "back.out(2.6)", transformOrigin: "0% 50%", immediateRender: false}}, {e - 0.04:.3f});')
        nxt = at(WORDS[k + 1][3], WORDS[k + 1][4]) if k + 1 < len(WORDS) else at(QUIZ["clip"], QUIZ["t"])
        js.append(fly(b, r, max(e + 0.5, nxt - 0.5)))
    q = at(QUIZ["clip"], QUIZ["t"])
    js += [f'tl.set("#r{len(WORDS) - 1}", {{attr: {{class: "row"}}}}, {q:.3f});',
           f'tl.set("#rq", {{attr: {{class: "row on"}}}}, {q:.3f});',
           f'tl.fromTo("#bq", {{opacity: 0, scale: 0.3, rotation: -25}}, {{opacity: 1, scale: 1, rotation: -4, duration: 0.45, ease: "back.out(2.2)", immediateRender: false}}, {q:.3f});',
           f'tl.fromTo("#qm", {{opacity: 0, scale: 0.2}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(3)", immediateRender: false}}, {q + 0.35:.3f});',
           f'tl.to("#qm", {{rotation: 12, duration: 0.25, yoyo: true, repeat: 9, ease: "sine.inOut"}}, {q + 0.8:.3f});',
           f'tl.fromTo("#rq .en", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(3)", transformOrigin: "0% 50%", immediateRender: false}}, {q + 0.2:.3f});',
           f'tl.to("#rq .en", {{scale: 1.12, duration: 0.3, yoyo: true, repeat: 7, ease: "sine.inOut", transformOrigin: "0% 50%"}}, {q + 0.7:.3f});',
           f'tl.fromTo("#cm", {{opacity: 0, y: 20, scale: 0.7}}, {{opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(2.4)", immediateRender: false}}, {at(QUIZ["clip"], QUIZ["comment_t"]):.3f});']
    page = PAGE.replace("%DUR%", f"{DUR:.3f}").replace("%ELS%", els).replace("%JS%", "\n  ".join(js))
    if K4:
        page = (page.replace("width=1080, height=1920", "width=2160, height=3840")
                .replace("html, body { width: 1080px; height: 1920px;", "html, body { width: 2160px; height: 3840px;")
                .replace("#root { position: relative; width: 1080px; height: 1920px; }",
                         "#root { position: relative; width: 1080px; height: 1920px; zoom: 2; }")
                .replace('data-width="1080" data-height="1920"', 'data-width="2160" data-height="3840"'))
    (HERE / "overlay" / "index.html").write_text(page, encoding="utf-8")
    print(HERE / "overlay" / "index.html", f"{DUR:.2f}s", RES)


PAGE = r"""<!doctype html>
<html lang="hi"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="gsap.min.js"></script>
<style>
@font-face { font-family: "Serif"; src: url(fonts/fraunces.woff2) format("woff2"); font-weight: 100 900; }
@font-face { font-family: "Outfit"; src: url(fonts/outfit.woff2) format("woff2"); font-weight: 100 900; }
@font-face { font-family: "Mukta"; src: url(fonts/mukta-800-devanagari.woff2) format("woff2"); font-weight: 800; unicode-range: U+0900-097F, U+200C-200D, U+25CC; }
@font-face { font-family: "Mukta"; src: url(fonts/mukta-800-latin.woff2) format("woff2"); font-weight: 800; }
:root { --plum: #2A1533; --coral: #FF5A5F; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: transparent; }
#root { position: relative; width: 1080px; height: 1920px; }
.clip { position: absolute; inset: 0; width: 1080px; height: 1920px; }
.clip > * { position: absolute; }
.ttl { left: 0; top: 262px; width: 1080px; text-align: center; font: 800 54px/1.25 Mukta; color: #fff;
  -webkit-text-stroke: 10px var(--plum); paint-order: stroke fill; }
.ttl i { font: 900 italic 54px/1 Serif; color: #FFE14D; font-style: normal; }
.guess { left: 0; top: 540px; width: 1080px; text-align: center; font: 800 46px/1 Outfit; color: #fff;
  -webkit-text-stroke: 9px var(--plum); paint-order: stroke fill; }
.big { left: 365px; top: 370px; width: 350px; height: 350px; border-radius: 50%; border: 10px solid #fff;
  box-shadow: 0 18px 40px rgba(42,21,51,.4); }
.qm { left: 640px; top: 350px; width: 110px; height: 110px; border-radius: 50%; background: var(--coral); color: #fff; border: 6px solid #fff;
  font: 900 76px/96px Serif; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,.3); }
.list { left: 0; top: 1066px; width: 1080px; }
.row { position: relative; height: 88px; display: flex; align-items: center; white-space: nowrap; padding-left: 100px; }
.th { width: 74px; height: 74px; border-radius: 50%; border: 4px solid #fff; flex: none; box-shadow: 0 4px 10px rgba(42,21,51,.35); }
.hi { flex: none; margin-left: 14px; }
.hi > span { display: inline-block; padding: 2px 16px 0; border-radius: 14px; background: #fff; color: var(--plum); font: 800 40px/1.3 Mukta;
  box-shadow: 0 5px 14px rgba(42,21,51,.28); }
.ar { flex: none; width: 48px; text-align: center; font: 900 40px/1 Outfit; color: #fff; -webkit-text-stroke: 7px var(--plum); paint-order: stroke fill; }
.en { display: inline-block; font: 900 58px/1 Serif; color: #fff; letter-spacing: -1px;
  -webkit-text-stroke: 11px var(--plum); paint-order: stroke fill; text-shadow: 0 6px 16px rgba(42,21,51,.35); }
.en.hid { filter: blur(11px); opacity: .55; }
.row.on .hi > span { background: var(--coral); color: #fff; }
.row.on .en { color: #FFE14D; }
.q { color: var(--coral) !important; letter-spacing: 8px; }
.cmt { left: 0; top: 740px; width: 1080px; text-align: center; }
.cmt span { display: inline-block; padding: 12px 28px; border-radius: 34px; background: var(--coral); color: #fff; font: 800 38px/1 Outfit;
  box-shadow: 0 8px 20px rgba(255,90,95,.4); }
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


# --------------------------------------------------------------------------------------------- picture + final
def base():
    BUILD.mkdir(exist_ok=True)
    w, h = (2160, 3840) if K4 else (1080, 1920)
    inputs, parts = [], []
    for i, (c, a, b) in enumerate(CLIPS):
        n = round((b - a) * FPS)
        inputs += ["-ss", f"{a:.3f}", "-t", f"{n / FPS + 0.2:.3f}", "-i", str(RAW / f"manisha_{c}.mov")]
        parts.append(f"[{i}:v]fps={FPS},scale={w}:{h}:flags=lanczos,trim=end_frame={n},setpts=PTS-STARTPTS[v{i}]")
    graph = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(CLIPS))) + f"concat=n={len(CLIPS)}:v=1:a=0,format=yuv420p[v]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[v]", "-c:v", "libx264",
                    "-preset", "medium" if K4 else "veryfast", "-crf", "12" if K4 else "18", "-color_primaries", "bt709",
                    "-color_trc", "bt709", "-colorspace", "bt709", str(BUILD / f"base_{RES}.mp4")], check=True)
    print(BUILD / f"base_{RES}.mp4")


def compose():
    out = HERE / "renders" / ("manisha6_final_4k.mp4" if K4 else "manisha6_v1_preview_1080p.mp4")
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(BUILD / f"base_{RES}.mp4"), "-c:v", "libvpx-vp9",
                    "-i", str(BUILD / f"overlay_{RES}.webm"), "-i", str(BUILD / "mix.wav"),
                    "-filter_complex", "[1:v]format=yuva420p[o];[0:v][o]overlay=0:0:format=yuv420,format=yuv420p[v]",
                    "-map", "[v]", "-map", "2:a", "-c:v", "libx264",
                    *(["-preset", "medium", "-crf", "15", "-profile:v", "high", "-level", "5.2"] if K4 else
                      ["-preset", "veryfast", "-crf", "20"]),
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-t", f"{DUR:.3f}", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    {"sfx": sfx, "mix": mix, "overlay": overlay, "base": base, "compose": compose}[sys.argv[1]]()
