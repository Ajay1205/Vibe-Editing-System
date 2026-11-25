"""Caption layer for Nikita 11 -- "Stop Saying OPEN" (board: edits/nikita11/board, simplified per the user:
"a little simple editing, don't strip it down to nothing" + bigger text).

Each mistake: the wrong phrase appears big above her head as she says it ("Open the TV"), gets a red strike + ❌ on
"you don't open..."; the right phrase lands on a white card at chest level with the verb on a green pill as she says
it ("Turn on the TV 📺"). Six progress dots at the top. Hook (frame 1): a big crossed-out OPEN + "6 galtiyan jo sab
karte hain". Quiz: "Open the tap 🚰" + "✅ ____ the tap" + "Answer comment karo" (answer never shown).
Rendered natively at 2160x3840.   Usage: python3 -I overlay.py -> overlay/index.html
"""

import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cut as C  # noqa: E402

# name, emoji, take, "Open the X" onset, "you don't open" onset, "you <verb>" onset, verb onset, verb, object
ITEMS = [
    ("TV", "📺", 1, 0.39, 1.86, 3.28, 3.54, "Turn on", "the TV"),
    ("AC", "❄️", 1, 4.98, 6.44, 8.00, 8.24, "Turn on", "the AC"),
    ("computer", "💻", 1, 9.72, 11.22, 12.70, 12.88, "Switch on", "the computer"),
    ("mobile", "📱", 2, 0.24, 1.58, 3.22, 3.40, "Unlock", "your mobile"),
    ("gift", "🎁", 2, 4.71, 5.96, 7.42, 7.68, "Unwrap", "the gift"),
    ("parcel", "📦", 3, 0.09, 1.40, 2.86, 3.20, "Unpack", "the parcel"),
]
QUIZ = {"now": 4.82, "open": 5.04, "how": 6.06, "comment": 8.02}  # take 3
READ_HOLD = 0.4
POP = '{opacity: 0, scale: 0.5}, {opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.4)"}'
IN = '{opacity: 0, y: 24}, {opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}'


def T(take, s, d=0.0):
    return round(C.T(take, s) + d, 3)


def clip(id_, s, e, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{s:.3f}" data-duration="{max(0.05, e - s):.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


def build():
    els, js = [], []
    dur = C.duration()
    quiz_s = T(3, QUIZ["now"], -0.15)

    # hook (frame 1): crossed-out OPEN + "6 galtiyan" at chest level until the first right card
    he = T(1, ITEMS[0][5], -0.25)
    els.append(clip("hk", 0, he, 1, '<div class="bigo" id="bo"><span>OPEN</span></div><div class="pill" id="gp">6 galtiyan jo <em>sab</em> karte hain 👇</div>'))
    js.append('tl.fromTo("#bo span", {scale: 1.1}, {scale: 1, duration: 0.5, ease: "power3.out"}, 0);')
    js.append(f'tl.to("#bo, #gp", {{opacity: 0, y: 20, duration: 0.2}}, {he - 0.2:.3f});')

    # progress dots (whole lesson)
    els.append(clip("dots", 0, quiz_s, 2, '<div class="dots">' + "".join(f'<i id="d{k}"></i>' for k in range(6)) + '</div>'))
    for k, it in enumerate(ITEMS):
        js.append(f'tl.to("#d{k}", {{backgroundColor: "#FFD43B", width: 70, duration: 0.25}}, {T(it[2], it[3], -0.05)});')
        js.append(f'tl.to("#d{k}", {{backgroundColor: "#1FBF6A", width: 52, duration: 0.25}}, {T(it[2], it[6]):.3f});')
    js.append(f'tl.to("#dots .dots", {{opacity: 0, duration: 0.2}}, {quiz_s - 0.2:.3f});')

    for k, (name, emo, tk, o, dn, r, v, verb, obj) in enumerate(ITEMS):
        s = T(tk, o, -0.08)
        nxt = T(ITEMS[k + 1][2], ITEMS[k + 1][3], -0.08) if k + 1 < len(ITEMS) else quiz_s
        e = nxt + READ_HOLD
        long_ = len(obj) > 8
        els.append(clip(f"i{k}", s, e, 3, f"""
          <div class="wrong{' long' if long_ else ''}" id="w{k}"><span class="xm" id="x{k}">❌</span> <span class="o" id="o{k}">Open</span> {obj.replace("your", "the")}</div>
          <div class="right{' long' if long_ else ''}" id="r{k}"><small>✅ SAY THIS</small><span class="v" id="v{k}">{verb}</span> {obj}&nbsp;{emo}</div>"""))
        js.append(f'tl.fromTo("#w{k}", {POP}, {s:.3f});')
        js.append(f'tl.set("#x{k}", {{opacity: 0}}, {s:.3f});')
        js.append(f'tl.fromTo("#x{k}", {{opacity: 0, scale: 2}}, {{opacity: 1, scale: 1, duration: 0.25, ease: "power3.in"}}, {T(tk, dn, -0.05):.3f});')
        js.append(f'tl.fromTo("#o{k}", {{"--s": 0, color: "#FFFFFF"}}, {{"--s": 1, color: "#FFC4C4", duration: 0.3, ease: "power2.out"}}, {T(tk, dn, -0.05):.3f});')
        js.append(f'tl.fromTo("#r{k}", {{opacity: 0, y: 40, scale: 0.94}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.8)"}}, {T(tk, r, -0.25):.3f});')
        js.append(f'tl.fromTo("#v{k}", {{backgroundColor: "rgba(31,191,106,0)", color: "#111216"}}, {{backgroundColor: "rgba(31,191,106,1)", color: "#FFFFFF", duration: 0.2}}, {T(tk, v, -0.04):.3f});')
        js.append(f'tl.fromTo("#v{k}", {{scale: 1}}, {{scale: 1.12, duration: 0.15, yoyo: true, repeat: 1}}, {T(tk, v, -0.04):.3f});')
        js.append(f'tl.to("#w{k}, #r{k}", {{opacity: 0, y: -12, duration: 0.18}}, {e - 0.19:.3f});')

    # quiz
    q = {k: T(3, v) for k, v in QUIZ.items()}
    els.append(clip("qz", quiz_s, dur + 0.1, 4, """<div class="turn" id="qt">YOUR TURN ✍️</div>
      <div class="wrong" id="qw" style="top:410px"><span class="xm">❌</span> <span class="o struck">Open</span> the tap 🚰</div>
      <div class="q" id="qc">✅ <span class="b" id="qb"></span> the tap</div><div class="pill cta" id="qa">Answer <em>comment</em> karo 👇</div>"""))
    js.append(f'tl.fromTo("#qt", {POP}, {quiz_s + 0.05:.3f});')
    js.append(f'tl.fromTo("#qw", {POP}, {q["open"] - 0.08:.3f});')
    js.append(f'tl.fromTo("#qc", {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: 0.35, ease: "back.out(1.8)"}}, {q["how"] - 0.1:.3f});')
    js.append(f'tl.fromTo("#qb", {{scale: 1}}, {{scale: 1.08, duration: 0.4, yoyo: true, repeat: 9, ease: "sine.inOut"}}, {q["how"] + 0.3:.3f});')
    js.append(f'tl.fromTo("#qa", {POP}, {q["comment"] - 0.1:.3f});')

    out = HERE / "overlay"
    (out / "vendor").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    shutil.copy(C.ROOT / "node_modules/gsap/dist/gsap.min.js", out / "vendor/gsap.min.js")
    for f in (HERE / "board" / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "fonts" / f.name)
    (out / "hyperframes.json").write_text('{"name":"nikita11-overlay"}\n')
    page = TEMPLATE.replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "\n".join(js))
    (out / "index.html").write_text(page)
    print(out / "index.html", f"{len(els)} clips, {dur:.2f}s")


TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: Anton; src: url(fonts/anton.woff2); }
@font-face { font-family: Brico; src: url(fonts/brico800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs700.woff2); font-weight: 700; }
:root { --ink: #111216; --red: #FF4D4D; --grn: #1FBF6A; --y: #FFD43B; --sh: 0 2px 3px rgba(0,0,0,.45), 0 8px 26px rgba(0,0,0,.4); }
html, body { margin: 0; background: transparent; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; }
.clip { position: absolute; inset: 0; } .layer { position: absolute; inset: 0; }
.layer > div { position: absolute; }
.dots { left: 0; top: 268px; width: 1080px; display: flex; justify-content: center; gap: 12px; }
.dots i { width: 52px; height: 14px; border-radius: 7px; background: rgba(17,18,22,.35); }
.wrong { left: 0; top: 330px; width: 1080px; text-align: center; font: 800 88px/1.05 Brico; color: #fff; text-shadow: var(--sh); }
.wrong.long { font-size: 74px; }
.wrong .o { position: relative; display: inline-block; --s: 0; }
.wrong .o::after { content: ""; position: absolute; left: -8px; right: -8px; top: 50%; height: 10px; border-radius: 5px; background: var(--red);
  transform: rotate(-6deg) scaleX(var(--s)); transform-origin: 0 50%; }
.wrong .o.struck { color: #FFC4C4; --s: 1; }
.xm { display: inline-block; }
.right { left: 110px; top: 1130px; width: 860px; box-sizing: border-box; text-align: center; padding: 28px; border-radius: 30px; background: #fff;
  box-shadow: 0 20px 44px rgba(0,0,0,.3); font: 800 76px/1.1 Brico; color: var(--ink); }
.right.long { font-size: 54px; left: 90px; width: 900px; padding: 28px 20px; }
.right small { display: block; font: 800 30px/1 PJS; letter-spacing: 3px; color: var(--grn); margin-bottom: 12px; }
.right .v { display: inline-block; padding: 0 14px 4px; border-radius: 16px; }
.bigo { left: 0; top: 1060px; width: 1080px; text-align: center; font: 400 220px/1 Anton; color: #fff; letter-spacing: 6px; text-shadow: var(--sh); }
.bigo span { position: relative; display: inline-block; }
.bigo span::after { content: ""; position: absolute; left: -20px; right: -20px; top: 48%; height: 22px; border-radius: 11px; background: var(--red); transform: rotate(-8deg); }
.pill { left: 0; right: 0; margin: 0 auto; width: fit-content; top: 1310px; padding: 14px 26px; border-radius: 22px; background: rgba(17,18,22,.85);
  font: 800 56px/1.2 Brico; color: #fff; }
.pill em { font-style: normal; color: var(--y); }
.pill.cta { top: 1320px; font-size: 60px; }
.turn { left: 0; top: 300px; width: 1080px; text-align: center; font: 800 60px/1 Brico; color: #fff; text-shadow: var(--sh); }
.q { left: 110px; top: 1120px; width: 860px; box-sizing: border-box; padding: 28px; border-radius: 30px; background: #fff; text-align: center; font: 800 76px/1.1 Brico;
  color: var(--ink); box-shadow: 0 20px 44px rgba(0,0,0,.3); }
.q .b { display: inline-block; width: 210px; height: 76px; vertical-align: -10px; border-radius: 16px; border: 5px dashed var(--grn); background: rgba(31,191,106,.12); }
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%" data-width="2160" data-height="3840" data-fps="30"><div id="stage">
%ELS%
</div></div>
<script>
  const tl = gsap.timeline({ paused: true });
  %JS%
  window.__timelines["main"] = tl;
</script></body></html>
"""

if __name__ == "__main__":
    build()
