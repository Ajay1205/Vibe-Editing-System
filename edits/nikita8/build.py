"""Nikita 8 -- "Positive feelings in English". v2: the approved Nikita 7 list style (v1 translate-app card is kept as
build_v1_translate.py; the user wanted all 8 words to stay on screen to read and write down).

Steps: python3 -I build.py sfx | mix | overlay [--4k] | hdr [--4k]
  (overlay: then render overlay/ with HyperFrames to build/overlay_<res>.webm)
Same rules as Nikita 7: her iPhone HDR video passes through untouched (no grade, no zoom); only the caption layer is
converted into HLG, brighter and more saturated so it pops. Everything sits below her face, except the top tag.
  - a translate-app card on her chest: the Hindi types into the top box, "Translating..." dots wait in the answer box
    until she says the English word, then it lands big in blue; counter k/8,
  - her example as a final translation, then a "Save for later" recap of all 8 pairs and a Follow tap at the top.
"""

import pathlib
import re
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE.parents[1] / "footage" / "nikita8" / "raw" / "nikita_8.1.mov"
BUILD = HERE / "build"
FPS = 30
K4 = "--4k" in sys.argv
RES = 2160 if K4 else 1080
CLIP_IN, CLIP_OUT = 0.0, 35.0  # source seconds (she ends at 34.9)
DUR = round((CLIP_OUT - CLIP_IN) * FPS) / FPS

# (Hindi, English, emoji, Hindi onset, English onset) -- onsets measured on the audio energy
WORDS = [
    ("उत्साहित होना", "Excited", "🤩", 0.00, 2.48),
    ("प्रेरित करना", "Inspire", "💡", 3.10, 5.24),
    ("प्रोत्साहित करना", "Encourage", "💪", 6.45, 9.50),
    ("तारीफ करना", "Appreciate", "👏", 10.05, 11.74),
    ("आभारी होना", "Grateful", "🙏", 13.79, 14.96),
    ("गर्व महसूस करना", "Proud", "🦁", 17.00, 18.62),
    ("विश्वास करना", "Trust", "🤝", 19.75, 22.96),
    ("उम्मीद रखना", "Hope", "🌈", 23.55, 25.24),
]
EXAMPLE = {"hi": "मैं उम्मीद रखती हूँ कि आपने कुछ सीखा होगा", "hi_t": 26.20, "en_t": 28.40,
           "en": 'I <b>hope</b> you learnt something! 🙂'}
RECAP_T, FOLLOW_T, TAP_T = 30.70, 32.60, 33.95


# --------------------------------------------------------------------------------------------- sound
SR = 48000
NOTES = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66, 1318.5]


def marimba(f0):
    t = np.arange(int(0.45 * SR)) / SR
    x = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.16) + 0.18 * np.sin(2 * np.pi * 4 * f0 * t) * np.exp(-t / 0.03)
    x *= np.minimum(1, t / 0.003) * np.minimum(1, (t[-1] - t) / 0.05)
    return x.astype(np.float32)


def tick():
    """Soft key tap (typing the Hindi)."""
    rng = np.random.default_rng(5)
    t = np.arange(int(0.05 * SR)) / SR
    return (rng.standard_normal(len(t)) * np.exp(-t / 0.006) * 0.6 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.01)).astype(np.float32)


def decode(path, start=None, dur=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", f"{start:.3f}", "-t", f"{dur:.3f}"] if start is not None else [])
    pcm = subprocess.run(cmd + ["-i", str(path), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).copy()


def sfx():
    BUILD.mkdir(exist_ok=True)
    n = int(DUR * SR)
    voice = decode(RAW, CLIP_IN, DUR + 0.1)[:n]
    voice = np.pad(voice, (0, n - len(voice)))
    voice[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    bed = np.zeros_like(voice)

    def place(s, t, peak_db):
        s = s / (np.abs(s).max() + 1e-9) * 10 ** (peak_db / 20)
        i = int(t * SR)
        j = min(n, i + len(s))
        bed[i:j] += s[:j - i]

    for k, w in enumerate(WORDS):
        place(marimba(NOTES[k]), w[4] - 0.02, -24)
    place(marimba(1568.0) + 0.6 * marimba(2093.0), EXAMPLE["en_t"], -25)
    place(tick() * 2, TAP_T, -24)
    riser = decode(HERE.parents[1] / "assets" / "shared" / "riser_user.mp3")
    tail = riser[-2 * SR:].copy()
    tail[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    place(tail, DUR - 2.0, -22)
    for name, x in [("voice_raw", voice), ("sfx", bed)]:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        str(BUILD / f"{name}.wav")], input=x.astype(np.float32).tobytes(), check=True)
    print("voice + sfx", f"{n / SR:.2f}s")


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
# v2 (user: the translate card didn't stay on screen -- with 8 words people want to read and write them down):
# the approved Nikita 7 "Feelings in English" list, every row staying on screen; her example + Follow tap below it.
N7_BOARD = HERE.parent / "nikita7" / "board" / "index.html"
EXTRA_CSS = """
.list { top: 372px; }
.row { height: 112px; }
.hi > span { font-size: 50px; }
.en { font-size: 80px; }
.save { top: 1300px; }
.exl { left: 0; top: 1296px; width: 1080px; text-align: center; }
.exl .eh { display: inline-block; padding: 2px 18px 0; border-radius: 16px; background: #fff; color: var(--plum); font: 800 40px/1.3 Mukta;
  box-shadow: 0 6px 16px rgba(42,21,51,.28); }
.exl .ee { display: block; margin-top: 10px; font: 900 64px/1.05 Serif; color: #fff; letter-spacing: -1px;
  -webkit-text-stroke: 11px var(--plum); paint-order: stroke fill; text-shadow: 0 6px 16px rgba(42,21,51,.35); }
.exl .ee b { color: #FFE14D; }
.fol { left: 0; top: 1490px; width: 1080px; text-align: center; }
.fol span { display: inline-block; padding: 14px 34px; border-radius: 40px; background: var(--coral); color: #fff; font: 800 40px/1 Outfit;
  box-shadow: 0 8px 20px rgba(255,90,95,.4); }
.hand { left: 640px; top: 1510px; font-size: 90px; }
"""


def overlay():
    board = N7_BOARD.read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", board, re.S).group(1) + EXTRA_CSS
    rows = "".join(f'<div class="row" id="r{k}"><span class="hi"><span>{hi}</span></span><span class="ar">→</span>'
                   f'<span class="en hid">{en}</span><span class="emo">{emo}</span></div>'
                   for k, (hi, en, emo, _, _) in enumerate(WORDS))
    els = (f'<div id="main" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="1"><div class="p">'
           '<div class="ttl">Positive <i>Feelings</i> ✨</div><div class="cnt"><b id="cn">00</b> / 08</div>'
           f'<div class="list">{rows}</div><div class="save" id="gs">Guess before I say it! 👀</div>'
           '<div class="exl" id="ex"><span class="eh">जैसे कि…</span>'
           '<span class="ee">I <b>hope</b> you learnt something! 🙂</span></div>'
           '<div class="fol" id="fol"><span id="fb">👉 Follow for daily English</span></div><div class="hand" id="hand">👆</div>'
           '</div></div>')
    js = ['tl.set("#main .emo, #ex, #ex .ee, #fol, #hand", {opacity: 0}, 0);',
          'tl.fromTo("#main .ttl, #main .cnt", {opacity: 0, y: -20}, {opacity: 1, y: 0, duration: 0.35}, 0);',
          'tl.fromTo("#main .row", {opacity: 0, x: -40}, {opacity: 1, x: 0, duration: 0.3, stagger: 0.03, ease: "power3.out"}, 0.05);',
          'tl.fromTo("#gs", {opacity: 0, scale: 0.8}, {opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)"}, 0.3);',
          f'tl.to("#gs", {{opacity: 0, duration: 0.25}}, {WORDS[0][4] - 0.1:.3f});']
    for k, (hi, en, emo, ht, et) in enumerate(WORDS):
        h, e, r = max(ht, 0.05), et, f"#r{k}"
        if k:
            js.append(f'tl.set("#r{k - 1}", {{attr: {{class: "row"}}}}, {h:.3f});')
        js.append(f'tl.set("{r}", {{attr: {{class: "row on"}}}}, {h:.3f});'
                  f'tl.fromTo("{r} .hi > span", {{scale: 1.25}}, {{scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false}}, {h:.3f});'
                  f'tl.to("{r} .en", {{filter: "blur(0px)", opacity: 1, duration: 0.18}}, {e - 0.04:.3f});'
                  f'tl.fromTo("{r} .en", {{scale: 1.35}}, {{scale: 1, duration: 0.35, ease: "back.out(2.6)", transformOrigin: "0% 50%", immediateRender: false}}, {e - 0.04:.3f});'
                  f'tl.fromTo("{r} .emo", {{opacity: 0, scale: 0.2, rotation: -30}}, {{opacity: 1, scale: 1, rotation: 0, duration: 0.35, ease: "back.out(3)", immediateRender: false}}, {e + 0.05:.3f});'
                  f'tl.set("#cn", {{textContent: "0{k + 1}"}}, {e:.3f});'
                  f'tl.fromTo("#main .cnt", {{scale: 1.25}}, {{scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false}}, {e:.3f});')
        nxt = WORDS[k + 1][3] if k + 1 < len(WORDS) else EXAMPLE["hi_t"]
        js.append(f'tl.to("{r} .emo", {{opacity: 0, scale: 0.5, duration: 0.15}}, {nxt - 0.15:.3f});')
    x = EXAMPLE["hi_t"]
    js += [f'tl.set("#r{len(WORDS) - 1}", {{attr: {{class: "row"}}}}, {x:.3f});',
           f'tl.fromTo("#ex", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.35, ease: "back.out(2)", immediateRender: false}}, {x:.3f});',
           f'tl.fromTo("#ex .ee", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.6)", immediateRender: false}}, {EXAMPLE["en_t"]:.3f});',
           f'tl.fromTo("#ex .ee b", {{scale: 1.4}}, {{scale: 1, duration: 0.4, ease: "back.out(3)", immediateRender: false}}, {EXAMPLE["en_t"] + 0.3:.3f});',
           f'tl.fromTo("#fol", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)", immediateRender: false}}, {FOLLOW_T:.3f});',
           f'tl.fromTo("#hand", {{opacity: 0, x: 120, y: 120}}, {{opacity: 1, x: 0, y: 0, duration: 0.4, ease: "power2.out", immediateRender: false}}, {TAP_T - 0.5:.3f});',
           f'tl.to("#fb", {{scale: 0.9, duration: 0.08, yoyo: true, repeat: 1}}, {TAP_T:.3f});',
           f'tl.set("#fb", {{textContent: "Following ✓", backgroundColor: "#2A1533"}}, {TAP_T + 0.1:.3f});',
           f'tl.to("#hand", {{opacity: 0, duration: 0.3}}, {TAP_T + 0.5:.3f});']
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


# --------------------------------------------------------------------------------------------- final (HDR)
def hdr():
    """Her iPhone HLG video untouched (trimmed, scaled); captions converted into HLG / BT.2020, colour and alpha
    separately, +1.8 stops and more saturated so they pop (Nikita 7 learning)."""
    w, h = (2160, 3840) if K4 else (1080, 1920)
    n = round(DUR * FPS)
    graph = (f"[0:v]fps={FPS},scale={w}:{h}:flags=lanczos,format=yuv420p10le,trim=end_frame={n},setpts=PTS-STARTPTS[b];"
             "[1:v]format=yuva420p,split[c][a];[a]alphaextract,format=gray10le[al];"
             "[c]format=yuv420p,eq=saturation=1.5,zscale=tin=bt709:pin=bt709:min=bt709:rin=tv:t=linear:p=bt709:m=gbr:npl=203,"
             "format=gbrpf32le,exposure=exposure=1.8,zscale=tin=linear:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:"
             "m=bt2020nc:r=tv:npl=203,format=yuv444p10le[cc];[cc][al]alphamerge[o];"
             "[b][o]overlay=0:0:format=yuv444p10,format=yuv420p10le[v]")
    out = HERE / "renders" / ("nikita8_final_4k_HDR.mp4" if K4 else "nikita8_v2_preview_1080p_HDR.mp4")
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", "-ss", f"{CLIP_IN:.3f}", "-t", f"{DUR + 0.2:.3f}", "-i", str(RAW),
                    "-c:v", "libvpx-vp9", "-i", str(BUILD / f"overlay_{RES}.webm"), "-i", str(BUILD / "mix.wav"),
                    "-filter_complex", graph, "-map", "[v]", "-map", "2:a", "-c:v", "libx265",
                    "-preset", "medium" if K4 else "fast", "-crf", "16" if K4 else "20", "-tag:v", "hvc1",
                    "-x265-params", "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error",
                    "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc",
                    "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-t", f"{DUR:.3f}", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    {"sfx": sfx, "mix": mix, "overlay": overlay, "hdr": hdr}[sys.argv[1]]()
