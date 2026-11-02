"""Nikita 8 -- "Positive feelings in English" in the TRANSLATE-APP style (user picked it for reach; options board:
edits/nikita8/board/options.html, option A).

Steps: python3 -I build.py sfx | mix | overlay [--4k] | hdr [--4k]
  (overlay: then render overlay/ with HyperFrames to build/overlay_<res>.webm)
Same rules as Nikita 7: her iPhone HDR video passes through untouched (no grade, no zoom); only the caption layer is
converted into HLG, brighter and more saturated so it pops. Everything sits below her face, except the top tag.
  - a translate-app card on her chest: the Hindi types into the top box, "Translating..." dots wait in the answer box
    until she says the English word, then it lands big in blue; counter k/8,
  - her example as a final translation, then a "Save for later" recap of all 8 pairs and a Follow tap at the top.
"""

import pathlib
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
        for j in range(3):  # three soft key taps while the Hindi types in
            place(tick(), w[3] + 0.05 + 0.09 * j, -34)
        place(marimba(NOTES[k]), w[4] - 0.02, -24)
    place(marimba(1568.0) + 0.6 * marimba(2093.0), EXAMPLE["en_t"], -25)
    place(marimba(1046.5), RECAP_T + 0.1, -28)
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
def overlay():
    recap = "".join(f'<div class="rr"><span class="rh">{hi}</span><span class="ra">→</span><span class="re">{en} {emo}</span></div>'
                    for hi, en, emo, _, _ in WORDS)
    els = (f'<div id="main" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="1">'
           '<div class="tag" id="tag">Positive feelings <b>in English</b> ✨</div>'
           '<div class="fol" id="fol"><span id="fb">Follow</span> for daily English ✨</div><div class="hand" id="hand">👆</div>'
           '<div class="cnt" id="cnt"><span id="cn">1</span> / 8</div>'
           '<div class="tr" id="tr"><div class="bar"><span>Hindi</span><span class="sw">⇄</span><span class="on">English</span></div>'
           '<div class="src"><span class="st" id="st"></span><span class="ico">🔊</span></div>'
           '<div class="dst"><span class="dw" id="dw"></span><span class="dots" id="dots">Translating<i>.</i><i>.</i><i>.</i></span>'
           '<span class="ico" id="spk">🔊</span></div></div>'
           f'<div class="rec" id="rec"><div class="rt">📌 Save for later</div>{recap}</div></div>')
    js = ['tl.set("#fol, #hand, #rec, #dots", {opacity: 0}, 0);',
          'tl.fromTo("#tag", {opacity: 0, y: -20}, {opacity: 1, y: 0, duration: 0.35}, 0);',
          'tl.fromTo("#tr", {opacity: 0, y: 60, scale: 0.9}, {opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.8)"}, 0);',
          'tl.fromTo("#cnt", {opacity: 0}, {opacity: 1, duration: 0.3}, 0.2);']

    def word_in(hi, t, en_t, en_html, k):
        # type the Hindi (clip reveal), wait with dots, land the English
        out = [f'tl.set("#st", {{textContent: "{hi}"}}, {t:.3f});',
               f'tl.set("#dw", {{innerHTML: "", opacity: 0}}, {t:.3f});',
               f'tl.fromTo("#st", {{clipPath: "inset(0 100% 0 0)"}}, {{clipPath: "inset(0 0% 0 0)", duration: 0.45, ease: "none"}}, {t:.3f});',
               f'tl.to("#dots", {{opacity: 1, duration: 0.15}}, {t + 0.45:.3f});',
               f'tl.to("#dots", {{opacity: 0, duration: 0.08}}, {en_t - 0.08:.3f});',
               f'tl.set("#dw", {{innerHTML: \'{en_html}\'}}, {en_t - 0.04:.3f});',
               f'tl.fromTo("#dw", {{opacity: 0, scale: 1.3}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.6)", transformOrigin: "0% 50%", immediateRender: false}}, {en_t - 0.04:.3f});',
               f'tl.fromTo("#spk", {{scale: 1.5}}, {{scale: 1, duration: 0.4, ease: "back.out(3)", immediateRender: false}}, {en_t:.3f});']
        if k is not None:
            out += [f'tl.set("#cn", {{textContent: "{k + 1}"}}, {t:.3f});',
                    f'tl.fromTo("#cnt", {{scale: 1.3}}, {{scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false}}, {t:.3f});']
        return out

    for k, (hi, en, emo, ht, et) in enumerate(WORDS):
        js += word_in(hi, max(ht, 0.05), et, f'{en} <em>{emo}</em>', k)
    js += [f'tl.to("#cnt", {{opacity: 0, duration: 0.2}}, {EXAMPLE["hi_t"]:.3f});',
           f'tl.set("#tr", {{attr: {{class: "tr ex"}}}}, {EXAMPLE["hi_t"]:.3f});']
    js += word_in(EXAMPLE["hi"], EXAMPLE["hi_t"], EXAMPLE["en_t"], EXAMPLE["en"], None)
    js += [f'tl.to("#tr", {{opacity: 0, y: 40, duration: 0.3, ease: "power2.in"}}, {RECAP_T - 0.3:.3f});',
           f'tl.fromTo("#rec", {{opacity: 0, y: 60, scale: 0.92}}, {{opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.8)"}}, {RECAP_T:.3f});',
           f'tl.fromTo("#rec .rr", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.25, stagger: 0.07, immediateRender: false}}, {RECAP_T + 0.2:.3f});',
           f'tl.to("#tag", {{opacity: 0, duration: 0.2}}, {FOLLOW_T - 0.2:.3f});',
           f'tl.fromTo("#fol", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)"}}, {FOLLOW_T:.3f});',
           f'tl.fromTo("#hand", {{opacity: 0, x: 120, y: 120}}, {{opacity: 1, x: 0, y: 0, duration: 0.4, ease: "power2.out"}}, {TAP_T - 0.5:.3f});',
           f'tl.to("#fb", {{scale: 0.88, duration: 0.08, yoyo: true, repeat: 1}}, {TAP_T:.3f});',
           f'tl.set("#fb", {{textContent: "Following ✓"}}, {TAP_T + 0.1:.3f});',
           f'tl.to("#hand", {{opacity: 0, duration: 0.3}}, {TAP_T + 0.5:.3f});']
    page = PAGE.replace("%DUR%", f"{DUR:.3f}").replace("%ELS%", els).replace("%JS%", "\n  ".join(js))
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
<style>
@font-face { font-family: "Inter"; src: url(fonts/inter.woff2) format("woff2"); font-weight: 100 900; }
@font-face { font-family: "Mukta"; src: url(fonts/mukta-800-devanagari.woff2) format("woff2"); font-weight: 800; unicode-range: U+0900-097F, U+200C-200D, U+25CC; }
@font-face { font-family: "Mukta"; src: url(fonts/mukta-800-latin.woff2) format("woff2"); font-weight: 800; }
:root { --blue: #1A73E8; --ink: #202124; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: transparent; }
#root { position: relative; width: 1080px; height: 1920px; }
.clip { position: absolute; inset: 0; width: 1080px; height: 1920px; }
.clip > div { position: absolute; }
.tag, .fol { left: 50%; top: 262px; transform: translateX(-50%); padding: 14px 30px; border-radius: 44px; background: #fff; color: var(--ink);
  font: 800 38px/1 Inter; white-space: nowrap; box-shadow: 0 8px 24px rgba(0,0,0,.2); }
.tag b { color: var(--blue); }
.fol #fb { display: inline-block; padding: 8px 20px; margin-right: 8px; border-radius: 26px; background: var(--blue); color: #fff; }
.hand { left: 330px; top: 300px; font-size: 90px; }
.cnt { right: 100px; top: 1012px; padding: 8px 20px; border-radius: 22px; background: var(--blue); color: #fff; font: 800 30px/1 Inter; }
.tr { left: 100px; top: 1062px; width: 880px; border-radius: 34px; background: #fff; overflow: hidden; box-shadow: 0 24px 60px rgba(0,0,0,.3); }
.tr .bar { display: flex; align-items: center; justify-content: space-between; padding: 22px 34px; border-bottom: 2px solid #eceff1;
  font: 700 30px/1 Inter; color: #5f6368; }
.tr .bar .sw { color: var(--blue); font-size: 36px; }
.tr .bar .on { color: var(--blue); }
.tr .src { padding: 24px 34px 18px; min-height: 120px; display: flex; justify-content: space-between; align-items: center; gap: 20px; }
.tr .st { font: 800 60px/1.3 Mukta; color: var(--ink); white-space: nowrap; }
.tr .dst { position: relative; padding: 24px 34px 28px; min-height: 146px; background: #E8F0FE; display: flex; justify-content: space-between; align-items: center; gap: 20px; }
.tr .dw { display: inline-block; font: 800 96px/1 Inter; color: var(--blue); letter-spacing: -3px; white-space: nowrap; }
.tr .dw em { font-style: normal; font-size: 74px; letter-spacing: 0; }
.tr .dots { position: absolute; left: 34px; top: 54px; font: 700 38px/1 Inter; color: #5f6368; }
.ico { font-size: 44px; opacity: .75; flex: none; }
.tr.ex .st { font-size: 44px; white-space: normal; line-height: 1.3; }
.tr.ex .dw { font-size: 58px; letter-spacing: -1.5px; white-space: normal; line-height: 1.12; }
.tr.ex .dw b { padding: 0 12px; border-radius: 12px; background: var(--blue); color: #fff; }
.rec { left: 100px; top: 1000px; width: 880px; padding: 26px 36px 22px; border-radius: 34px; background: #fff; box-shadow: 0 24px 60px rgba(0,0,0,.3); }
.rec .rt { font: 800 36px/1 Inter; color: var(--ink); margin-bottom: 12px; }
.rec .rr { display: flex; align-items: center; height: 62px; border-top: 2px solid #eceff1; }
.rec .rh { width: 330px; font: 800 36px/1.3 Mukta; color: #5f6368; white-space: nowrap; }
.rec .ra { width: 50px; color: var(--blue); font: 800 32px/1 Inter; }
.rec .re { font: 800 42px/1 Inter; color: var(--blue); letter-spacing: -1px; white-space: nowrap; }
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
    out = HERE / "renders" / ("nikita8_final_4k_HDR.mp4" if K4 else "nikita8_v1_preview_1080p_HDR.mp4")
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
