"""Manisha 7 -- "Pick One" grammar quiz (fill in the blank, 3 options, comment CTA). One take, ~10.6 s.

Approved style board: edits/manisha7/board (user, 19 Nov: A and B side by side, C centred below them).
Palette from the footage (window plants, warm wood, her beige top): forest #1F4D3A, mint #D6F0DF, cream #FFF8EE,
sunflower #FFC94A. Bricolage Grotesque (sentence, options), Plus Jakarta Sans (chip, letters), Caveat (comment line).
Everything sits in the lower half (y 1075-1550 on the 1080x1920 stage): her face fills the top half.
Video untouched (no grade, no zoom): the window light already looks good.

  python3 -I build.py cues               # cues.json (captions + sfx on the edit timeline)
  python3 -I build.py base [--preview]   # trimmed 4K (or 1080p) picture + voice_raw.wav
  python3 -I build.py overlay            # overlay/index.html (rendered natively at 2160x3840)
  python3 -I mix.py                       # voice + sfx -> build/mix.wav (-14 LUFS)
  npx hyperframes render overlay --format webm -o build/overlay_2160.webm   (proxy env vars, see CLAUDE.md)
  python3 -I build.py compose [--preview]
"""

import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "footage" / "manisha7" / "raw" / "manisha_7.mov"
BUILD = HERE / "build"
RENDERS = HERE / "renders"

# ------------------------------------------------------------------------------------------------ CONTENT
CUT_IN, CUT_OUT = 0.85, 11.40  # raw seconds: just before her first word / just after "batayiye", before the phone drops
SENTENCE = ("I have known him", "years.")  # the blank sits between the two parts
OPTIONS = [("A", "since", 3.90, 4.74), ("B", "for", 5.62, 6.74), ("C", "during", 7.60, 8.62)]  # tile in, word spoken (raw s)
Q_T, BLANK_T, CTA_T = 1.00, 2.40, 9.40  # sentence starts, the blank moment, "Sahi answers mujhe comment mein batayiye"
CHIP = "✏️ FILL IN THE BLANK"
CTA = "Comment karo — <i>A, B ya C?</i> 👇"
# ---------------------------------------------------------------------------------------------------------
DUR = round(CUT_OUT - CUT_IN, 3)


def e(t):
    """raw time -> edit time"""
    return round(t - CUT_IN, 3)


def cues():
    sfx = [{"name": "whoosh-short", "t": max(0.0, e(Q_T) - 0.1), "gain": 0.5, "lu": -10.0}]
    sfx += [{"name": "pop", "t": e(t_in), "gain": 0.5, "lu": -6.0} for _, _, t_in, _ in OPTIONS]
    sfx += [{"name": "ping", "t": e(CTA_T), "gain": 0.5, "lu": -8.0}]
    out = {"duration": DUR, "fps": 30, "cut_in": CUT_IN, "cut_out": CUT_OUT,
           "options": [{"letter": l, "word": w, "in": e(a), "hot": e(b)} for l, w, a, b in OPTIONS],
           "q_t": e(Q_T), "blank_t": e(BLANK_T), "cta_t": e(CTA_T), "sfx": sfx}
    json.dump(out, open(HERE / "cues.json", "w"), ensure_ascii=False, indent=1)
    print(f"cues.json: {DUR:.2f}s, {len(sfx)} sfx")


def base(preview=False):
    BUILD.mkdir(exist_ok=True)
    w, h = (1080, 1920) if preview else (2160, 3840)
    out = BUILD / f"base{'_preview' if preview else ''}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", "-ss", f"{CUT_IN}", "-to", f"{CUT_OUT}", "-i", str(RAW),
                    "-vf", f"fps=30,scale={w}:{h}:flags=lanczos,setsar=1", "-an",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "12" if not preview else "18", "-pix_fmt", "yuv420p",
                    str(out)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{CUT_IN}", "-to", f"{CUT_OUT}", "-i", str(RAW), "-vn",
                    "-ac", "2", "-ar", "48000", str(BUILD / "voice_raw.wav")], check=True)
    print(out)


OVERLAY = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: Brico; src: url(fonts/brico800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs600.woff2); font-weight: 600; }
@font-face { font-family: Cav; src: url(fonts/caveat700.woff2); font-weight: 700; }
:root { --forest: #1F4D3A; --mint: #D6F0DF; --cream: #FFF8EE; --sun: #FFC94A;
  --sh: 0 2px 3px rgba(0,0,0,.45), 0 6px 22px rgba(0,0,0,.45); }
html, body { margin: 0; background: transparent; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; }
.abs { position: absolute; }
.chip { left: 120px; top: 268px; padding: 12px 22px; border-radius: 30px; background: var(--forest); color: var(--mint);
  font: 800 30px/1 PJS; letter-spacing: 2px; box-shadow: 0 10px 24px rgba(0,0,0,.3); }
.q { left: 60px; top: 1075px; width: 960px; white-space: nowrap; text-align: center; font: 800 58px/1.1 Brico; color: #fff; text-shadow: var(--sh); }
.blank { display: inline-block; width: 200px; height: 62px; vertical-align: -10px; border-radius: 20px; border: 6px dashed var(--sun);
  background: rgba(255,201,74,.18); }
.opts { left: 120px; top: 1190px; width: 840px; display: grid; grid-template-columns: 400px 400px; column-gap: 40px; row-gap: 22px; }
.o { display: flex; align-items: center; gap: 22px; height: 104px; padding: 0 26px; border-radius: 52px; background: rgba(255,248,238,.95);
  box-shadow: 0 14px 30px rgba(0,0,0,.28); font: 800 54px/1 Brico; color: var(--forest); }
.o b { flex: none; width: 70px; height: 70px; border-radius: 50%; background: var(--forest); color: var(--mint); font: 800 38px/70px PJS; text-align: center; }
#oC { grid-column: 1 / span 2; justify-self: center; width: 400px; }
.cta { left: 0; top: 1462px; width: 1080px; text-align: center; font: 700 76px/1 Cav; color: #fff; text-shadow: var(--sh); }
.cta i { font-style: normal; color: var(--sun); }
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%" data-width="2160" data-height="3840" data-fps="30"><div id="stage">
  <div class="abs chip" id="chip">%CHIP%</div>
  <div class="abs q" id="q">%S1% <span class="blank" id="bl"></span> %S2%</div>
  <div class="abs opts">%OPTS%</div>
  <div class="abs cta" id="cta">%CTA%</div>
</div></div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#chip", {opacity: 0, y: -16}, {opacity: 1, y: 0, duration: 0.35, ease: "power2.out"}, 0.0);
  tl.fromTo("#q", {opacity: 0, y: 30, filter: "blur(10px)"}, {opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "power3.out"}, %Q%);
  tl.to("#bl", {scale: 1.07, duration: 0.3, yoyo: true, repeat: 5, ease: "sine.inOut"}, %BL%);
  %JS%
  tl.fromTo("#cta", {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, %CTA_T%);
  tl.to(".o", {scale: 1.04, duration: 0.25, yoyo: true, repeat: 3, stagger: 0.12, ease: "sine.inOut"}, %CTA_T% + 0.2);
  window.__timelines["main"] = tl;
</script></body></html>
"""


def overlay():
    c = json.load(open(HERE / "cues.json"))
    out = HERE / "overlay"
    (out / "vendor").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", out / "vendor/gsap.min.js")
    for f in (HERE / "board" / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "fonts" / f.name)
    opts = "".join(f'<div class="o" id="o{o["letter"]}"><b>{o["letter"]}</b>{o["word"]}</div>' for o in c["options"])
    entry = {"A": "{opacity: 0, x: -60}", "B": "{opacity: 0, x: 60}", "C": "{opacity: 0, y: 40}"}
    js = []
    ops = c["options"]
    for k, o in enumerate(ops):
        js.append(f'tl.fromTo("#o{o["letter"]}", {entry.get(o["letter"], "{opacity: 0, y: 40}")}, '
                  f'{{opacity: 1, x: 0, y: 0, duration: 0.4, ease: "back.out(1.6)"}}, {o["in"]});')
        off = ops[k + 1]["in"] if k + 1 < len(ops) else c["cta_t"] - 0.1
        js.append(f'tl.to("#o{o["letter"]}", {{backgroundColor: "#FFC94A", scale: 1.05, duration: 0.18, ease: "power2.out"}}, {o["hot"]});')
        js.append(f'tl.to("#o{o["letter"]}", {{backgroundColor: "rgba(255,248,238,.95)", scale: 1, duration: 0.2}}, {off});')
    page = (OVERLAY.replace("%DUR%", f"{c['duration']:.3f}").replace("%CHIP%", CHIP).replace("%S1%", SENTENCE[0])
            .replace("%S2%", SENTENCE[1]).replace("%OPTS%", opts).replace("%CTA%", CTA).replace("%JS%", "\n  ".join(js))
            .replace("%Q%", str(c["q_t"])).replace("%BL%", str(c["blank_t"])).replace("%CTA_T%", str(c["cta_t"])))
    (out / "index.html").write_text(page)
    print(out / "index.html")


def compose(preview=False):
    RENDERS.mkdir(exist_ok=True)
    out = RENDERS / f"manisha7_{'preview_1080p' if preview else '4k'}.mp4"
    scale = "scale=1080:1920:flags=lanczos," if preview else ""
    subprocess.run([
        "ffmpeg", "-v", "error", "-stats", "-y",
        "-i", str(BUILD / f"base{'_preview' if preview else ''}.mp4"),
        "-c:v", "libvpx-vp9", "-i", str(BUILD / "overlay_2160.webm"),
        "-i", str(BUILD / "mix.wav"),
        "-filter_complex", f"[1:v]{scale}format=yuva420p[o];[0:v]format=yuv420p[b];[b][o]overlay=0:0:format=yuv420,format=yuv420p[v]",
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", *(["-preset", "veryfast", "-crf", "20"] if preview else
                             ["-preset", "medium", "-crf", "15", "-profile:v", "high", "-level", "5.2"]),
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    {"cues": cues, "base": lambda: base("--preview" in sys.argv), "overlay": overlay,
     "compose": lambda: compose("--preview" in sys.argv)}[sys.argv[1]]()
