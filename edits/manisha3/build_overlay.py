"""Caption layer for the Manisha 3 reel -- "Chat Pop" style (new for this video).

A chat world for a WhatsApp-replies lesson: notification cards with typing dots and ticks that turn blue,
an outgoing "Hi" that gets left on seen, then each reply arrives ONE AT A TIME as a chat notification with the
English line inside and its Hinglish meaning outside, then swipes away before the next. Plus Jakarta Sans +
Caveat; mint / deep teal / cream with a hot-pink accent; bubble-burst transitions.

Everything sits in the wall above her head: y 262-770 on the 1080x1920 stage, x 140-940 (Reels safe box,
face never covered). Usage: python3 -I build_overlay.py [--preview]   (--preview = 1080p)
"""

import html
import json
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "overlay"
CUES = json.load(open(HERE / "cues.json"))

FONTS = {
    "jak-700.woff2": "@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-700-normal.woff2",
    "jak-800.woff2": "@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-800-normal.woff2",
    "jak-700i.woff2": "@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-700-italic.woff2",
    "jak-800i.woff2": "@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-800-italic.woff2",
    "caveat-700.woff2": "@fontsource/caveat/files/caveat-latin-700-normal.woff2",
}


def rich(text, cls):
    parts = re.split(r"\*\*(.+?)\*\*", html.escape(text))
    return "".join(f'<span class="{cls}">{p}</span>' if i % 2 else p for i, p in enumerate(parts))


def clip(id_, start, end, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


TICKS = '<span class="ticks">✓✓</span>'


def build(res=2160):
    OUT.mkdir(exist_ok=True)
    (OUT / "fonts").mkdir(exist_ok=True)
    (OUT / "vendor").mkdir(exist_ok=True)
    for dst, src in FONTS.items():
        shutil.copy(ROOT / "node_modules" / src, OUT / "fonts" / dst)
    shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", OUT / "vendor/gsap.min.js")

    els, js = [], []
    for i, c in enumerate(CUES["captions"]):
        s, e = c["start"], c["end"]
        cid = f"c{i}"
        if c["type"] == "hook":
            b = c["beats"]
            els.append(clip(cid, s, e, 1, f"""
              <div class="scene" id="{cid}-a">
                <div class="notif" id="{cid}-n">
                  <div class="avatar">B</div>
                  <div class="n-body"><div class="n-name">Boss <span>now</span></div>
                  <div class="n-text">Hi! Are you free to talk? 🙂</div></div>
                </div>
                <div class="bubble out" id="{cid}-hi">Hi 👋 {TICKS}</div>
                <div class="note" id="{cid}-nr">…aur phir? English khatam 😶</div>
              </div>
              <div class="scene" id="{cid}-b">
                <div class="chip-app" id="{cid}-chip">💬 WhatsApp pe</div>
                <div class="headline" id="{cid}-h">Smart English <span class="hl-pink">Replies</span></div>
                <div class="subline" id="{cid}-t">aaj hi vocabulary mein add karo ✅</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-n", {{y: -160, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.5, ease: "back.out(1.6)"}}, {b['notif']});
              tl.fromTo("#{cid}-hi", {{scale: 0.3, opacity: 0, transformOrigin: "100% 100%"}}, {{scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.2)"}}, {b['hi']});
              tl.to("#{cid}-hi .ticks", {{color: "#34B7F1", duration: 0.15}}, {b['seen']});
              tl.fromTo("#{cid}-nr", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.3}}, {b['noreply']});
              tl.to("#{cid}-hi", {{x: 12, duration: 0.06, yoyo: true, repeat: 5}}, {b['noreply'] + 0.3});
              tl.to("#{cid}-a", {{y: -120, opacity: 0, duration: 0.3, ease: "power2.in"}}, {b['swap'] - 0.3});
              tl.fromTo("#{cid}-chip", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.3}}, {b['swap']});
              tl.fromTo("#{cid}-h", {{opacity: 0, scale: 0.7}}, {{opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.8)"}}, {b['swap'] + 0.1});
              tl.fromTo("#{cid}-h .hl-pink", {{backgroundSize: "0% 100%"}}, {{backgroundSize: "100% 100%", duration: 0.35}}, {b['swap'] + 0.5});
              tl.fromTo("#{cid}-t", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.35}}, {b['today']});
              tl.to("#{cid}-b", {{y: -100, opacity: 0, duration: 0.28, ease: "power2.in"}}, {e - 0.3});""")
        elif c["type"] == "reply":
            els.append(clip(cid, s, e, 2, f"""
              <div class="card" id="{cid}-card">
                <div class="c-head"><span class="c-icon">💬</span><b>Reply {c['n']}/4</b><span class="c-time">now</span></div>
                <div class="typing" id="{cid}-dots"><i></i><i></i><i></i></div>
                <div class="c-en" id="{cid}-en">{rich(c['en'], 'hl-en')} <span class="c-emoji">{c['emoji']}</span></div>
                {TICKS.replace('class="ticks"', f'class="ticks c-ticks" id="{cid}-tk"')}
              </div>
              <div class="mean" id="{cid}-m">
                <div class="m-label">matlab 👇</div>
                <div class="m-text">{rich(c['hi'], 'hl-hi')}</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-card", {{y: -180, opacity: 0, scale: 0.9}}, {{y: 0, opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.5)"}}, {s});
              tl.fromTo("#{cid}-dots i", {{y: 0}}, {{y: -10, duration: 0.18, yoyo: true, repeat: 3, stagger: 0.08}}, {s + 0.1});
              tl.to("#{cid}-dots", {{opacity: 0, height: 0, duration: 0.12}}, {c['en_t'] - 0.12});
              tl.fromTo("#{cid}-en", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}}, {c['en_t']});
              tl.fromTo("#{cid}-en .hl-en", {{backgroundSize: "0% 40%"}}, {{backgroundSize: "100% 40%", duration: 0.35}}, {c['en_t'] + 0.35});
              tl.to("#{cid}-tk", {{color: "#34B7F1", duration: 0.15}}, {c['seen']});
              tl.fromTo("#{cid}-m", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.35, ease: "back.out(1.6)"}}, {c['hi_t']});
              tl.fromTo("#{cid}-m .hl-hi", {{backgroundSize: "0% 100%"}}, {{backgroundSize: "100% 100%", duration: 0.3}}, {c['hi_t'] + 0.3});
              tl.to("#{cid}-card", {{y: -200, opacity: 0, duration: 0.3, ease: "power2.in"}}, {e - 0.32});
              tl.to("#{cid}-m", {{y: 40, opacity: 0, duration: 0.25, ease: "power2.in"}}, {e - 0.3});""")
        elif c["type"] == "challenge":
            els.append(clip(cid, s, e, 3, f"""
              <div class="ch-head" id="{cid}-h">Your Turn! 🎯</div>
              <div class="ch-sub" id="{cid}-s">Is Hindi sentence ka <b>English translation</b> comment karo</div>
              <div class="bubble in" id="{cid}-q">Main pahunchne wali hoon 🏃‍♀️</div>
              <div class="inputbar" id="{cid}-ib"><span class="ph">Type your answer<i class="cursor">|</i></span>
                <span class="send" id="{cid}-btn">Comment 👇</span></div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-h", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)"}}, {s});
              tl.fromTo("#{cid}-s", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.35}}, {s + 0.35});
              tl.fromTo("#{cid}-q", {{opacity: 0, x: -80, scale: 0.8, transformOrigin: "0% 100%"}}, {{opacity: 1, x: 0, scale: 1, duration: 0.4, ease: "back.out(1.8)"}}, {c['q_t']});
              tl.fromTo("#{cid}-ib", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.35, ease: "power2.out"}}, {c['box_t']});
              tl.fromTo("#{cid} .cursor", {{opacity: 1}}, {{opacity: 0, duration: 0.25, yoyo: true, repeat: 7}}, {c['box_t']});
              tl.to("#{cid}-btn", {{scale: 0.88, duration: 0.08, yoyo: true, repeat: 1}}, {c['tap']});
              tl.to("#{cid}-btn", {{scale: 1.08, duration: 0.3, yoyo: true, repeat: 1, ease: "sine.inOut"}}, {c['tap'] + 0.25});""")

    for j, f in enumerate(CUES["flashes"]):
        els.append(clip(f"tr{j}", max(0, f - 0.15), f + 0.65, 9,
                        '<div class="burst"></div><div class="mini m1">💬</div><div class="mini m2">✓✓</div><div class="mini m3">💬</div>'))
        js.append(f"""
              tl.fromTo("#tr{j} .burst", {{scale: 0, opacity: 0.85}}, {{scale: 3.2, opacity: 0, duration: 0.55, ease: "power2.out"}}, {max(0, f - 0.15)});
              tl.fromTo("#tr{j} .mini", {{y: 60, opacity: 0}}, {{y: -140, opacity: 1, duration: 0.45, stagger: 0.05, ease: "power2.out"}}, {max(0, f - 0.12)});
              tl.to("#tr{j} .mini", {{opacity: 0, duration: 0.15}}, {f + 0.45});""")

    dur = CUES["duration"]
    page = TEMPLATE.replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "".join(js))
    if res == 1080:
        page = (page.replace("width=2160, height=3840", "width=1080, height=1920")
                .replace("html, body { width: 2160px; height: 3840px;", "html, body { width: 1080px; height: 1920px;")
                .replace(".clip { width: 2160px; height: 3840px; }", ".clip { width: 1080px; height: 1920px; }")
                .replace("transform-origin: 0 0; transform: scale(2); }", "transform-origin: 0 0; transform: none; }")
                .replace('data-width="2160" data-height="3840"', 'data-width="1080" data-height="1920"'))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    if not (OUT / "hyperframes.json").exists():
        (OUT / "hyperframes.json").write_text('{"name":"manisha3-overlay"}')
    print(f"{OUT / 'index.html'}: {len(els)} clips, {dur:.2f}s at {res}p")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=2160, height=3840" />
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "Jak"; src: url(fonts/jak-700.woff2) format("woff2"); font-weight: 700; }
@font-face { font-family: "Jak"; src: url(fonts/jak-800.woff2) format("woff2"); font-weight: 800; }
@font-face { font-family: "Jak"; src: url(fonts/jak-700i.woff2) format("woff2"); font-weight: 700; font-style: italic; }
@font-face { font-family: "Jak"; src: url(fonts/jak-800i.woff2) format("woff2"); font-weight: 800; font-style: italic; }
@font-face { font-family: "Caveat"; src: url(fonts/caveat-700.woff2) format("woff2"); font-weight: 700; }
:root { --mint: #D9FDD3; --green: #25C26E; --teal: #0B3B36; --cream: #FFF8EC; --pink: #FF4D8D; --ink: #0E2A28; --blue: #34B7F1; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 2160px; height: 3840px; overflow: hidden; background: transparent; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { width: 2160px; height: 3840px; }
.layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; transform: scale(2); }
.layer > div { position: absolute; }
.scene { left: 140px; top: 280px; width: 800px; height: 480px; }
.scene > div { position: absolute; }

/* hook */
.notif { left: 0; top: 0; width: 800px; height: 128px; display: flex; align-items: center; gap: 20px; padding: 0 28px;
  background: rgba(255,248,236,.97); border-radius: 30px; box-shadow: 0 16px 40px rgba(0,0,0,.3); }
.avatar { width: 76px; height: 76px; border-radius: 38px; background: var(--teal); color: #fff; font: 800 38px/76px Jak; text-align: center; flex: none; }
.n-name { font: 800 30px/1.2 Jak; color: var(--ink); }
.n-name span { font: 700 22px/1 Jak; color: #7d8b88; margin-left: 10px; }
.n-text { font: 700 36px/1.25 Jak; color: #2f4743; }
.bubble { font: 800 58px/1.2 Jak; padding: 22px 34px; border-radius: 34px; box-shadow: 0 12px 30px rgba(0,0,0,.28); width: max-content; max-width: 800px; }
.bubble.out { right: 0; top: 168px; background: var(--mint); color: var(--ink); border-bottom-right-radius: 8px; }
.bubble.in { left: 140px; top: 520px; background: var(--cream); color: var(--ink); border-bottom-left-radius: 8px; font-size: 50px; white-space: nowrap; }
.ticks { font: 800 30px/1 Jak; color: #8a9a97; margin-left: 10px; letter-spacing: -6px; }
.note { right: 0; top: 300px; width: 800px; text-align: right; font: 700 54px/1.1 Caveat; color: #FFD3E2; text-shadow: 0 3px 12px rgba(0,0,0,.6); }
.chip-app { left: 0; top: 0; width: max-content; padding: 12px 24px; border-radius: 30px; background: var(--green); color: #fff; font: 800 32px/1 Jak; }
.headline { left: 0; top: 74px; width: 800px; font: 800 104px/1.04 Jak; color: #fff; letter-spacing: -3px; text-shadow: 0 6px 24px rgba(0,0,0,.45); }
.hl-pink { padding: 0 10px; border-radius: 16px; background-image: linear-gradient(var(--pink), var(--pink)); background-repeat: no-repeat; background-size: 0% 100%; }
.subline { left: 0; top: 330px; width: 800px; font: 700 italic 46px/1.25 Jak; color: var(--cream); text-shadow: 0 3px 14px rgba(0,0,0,.6); }

/* reply card (one at a time) */
.card { left: 140px; top: 280px; width: 800px; padding: 22px 32px 26px; border-radius: 34px; background: rgba(255,248,236,.97);
  box-shadow: 0 18px 44px rgba(0,0,0,.32); border-top: 10px solid var(--green); }
.c-head { display: flex; align-items: center; gap: 12px; font: 700 26px/1 Jak; color: #6f7e7b; margin-bottom: 14px; }
.c-head b { font-weight: 800; color: var(--teal); letter-spacing: 1px; }
.c-icon { width: 44px; height: 44px; border-radius: 22px; background: var(--green); text-align: center; font-size: 24px; line-height: 44px; }
.c-time { margin-left: auto; }
.typing { height: 40px; display: flex; gap: 10px; align-items: center; padding-left: 4px; overflow: hidden; }
.typing i { width: 16px; height: 16px; border-radius: 8px; background: #9fb1ad; display: block; }
.c-en { font: 800 60px/1.18 Jak; color: var(--ink); letter-spacing: -1px; }
.c-emoji { font-size: 50px; }
.hl-en { background-image: linear-gradient(rgba(255,77,141,.45), rgba(255,77,141,.45)); background-repeat: no-repeat;
  background-position: 0 88%; background-size: 0% 40%; }
.c-ticks { position: absolute; right: 30px; bottom: 18px; }
.mean { left: 140px; top: 578px; width: 800px; }
.m-label { font: 700 46px/1 Caveat; color: #FFD3E2; text-shadow: 0 3px 12px rgba(0,0,0,.6); margin-bottom: 8px; }
.m-text { font: 800 italic 52px/1.25 Jak; color: #fff; text-shadow: 0 4px 18px rgba(0,0,0,.6); }
.hl-hi { padding: 0 10px; border-radius: 12px; color: #fff; text-shadow: none; background-image: linear-gradient(var(--pink), var(--pink));
  background-repeat: no-repeat; background-size: 0% 100%; }

/* challenge */
.ch-head { left: 140px; top: 280px; width: 800px; font: 800 96px/1 Jak; color: var(--pink); letter-spacing: -2px;
  text-shadow: 0 6px 24px rgba(0,0,0,.4); }
.ch-sub { left: 140px; top: 396px; width: 800px; font: 700 italic 40px/1.3 Jak; color: var(--cream); text-shadow: 0 3px 14px rgba(0,0,0,.6); }
.ch-sub b { color: #FFD3E2; }
.inputbar { left: 140px; top: 660px; width: 800px; height: 100px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 14px 0 32px; border-radius: 50px; background: rgba(255,248,236,.97); box-shadow: 0 12px 30px rgba(0,0,0,.3); }
.ph { font: 700 36px/1 Jak; color: #8a9a97; }
.cursor { font-style: normal; color: var(--ink); margin-left: 4px; }
.send { padding: 18px 30px; border-radius: 40px; background: var(--green); color: #fff; font: 800 36px/1 Jak; }

/* transition: chat bubble burst */
.burst { position: absolute; left: 390px; top: 420px; width: 300px; height: 300px; border-radius: 150px;
  background: radial-gradient(circle, rgba(217,253,211,.95), rgba(37,194,110,.55) 60%, rgba(37,194,110,0) 72%); }
.mini { position: absolute; font: 800 54px/1 Jak; color: #fff; text-shadow: 0 4px 14px rgba(0,0,0,.4); }
.m1 { left: 300px; top: 640px; } .m2 { left: 520px; top: 680px; color: var(--blue); } .m3 { left: 720px; top: 640px; }
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%" data-width="2160" data-height="3840" data-fps="30">
%ELS%
</div>
<script>
  const tl = gsap.timeline({ paused: true });
  %JS%
  window.__timelines["main"] = tl;
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build(1080 if "--preview" in sys.argv else 2160)
