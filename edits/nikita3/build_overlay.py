"""Generate the HyperFrames caption/graphics layer (transparent 4K) from cues.json.

The layer is shared by both versions; it is rendered once as WebM with alpha and
composited over each base video. Layout is authored on a 1080x1920 stage scaled 2x,
and every text block stays inside the Instagram Reels safe box: 120 px in from each side,
below the top 250 px and above the bottom 320 px (the 840x1350 centre area).
"""

import html
import json
import pathlib
import re
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "overlay"
CUES = json.load(open(HERE / "cues.json"))

FONTS = {
    "anton.woff2": "@fontsource/anton/files/anton-latin-400-normal.woff2",
    "poppins-600i.woff2": "@fontsource/poppins/files/poppins-latin-600-italic.woff2",
    "poppins-700.woff2": "@fontsource/poppins/files/poppins-latin-700-normal.woff2",
    "poppins-800.woff2": "@fontsource/poppins/files/poppins-latin-800-normal.woff2",
    "caveat-700.woff2": "@fontsource/caveat/files/caveat-latin-700-normal.woff2",
}


def rich(text, cls="hl"):
    """**word** -> highlighted span."""
    parts = re.split(r"\*\*(.+?)\*\*", html.escape(text))
    return "".join(f'<span class="{cls}">{p}</span>' if i % 2 else p for i, p in enumerate(parts))


def clip(id_, start, end, track, inner, extra=""):
    return (f'<div id="{id_}" class="clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
            f'data-track-index="{track}"{extra}><div class="layer">{inner}</div></div>')


def build():
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
              <div class="hook">
                <div class="hook-num" id="{cid}-num">3</div>
                <div class="hook-words" id="{cid}-words"><span>English</span><span>Words</span></div>
                <div class="chip chip-cream" id="{cid}-sub">for your vocabulary 📚</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-num", {{scale: 2.6, rotation: -14, opacity: 0}}, {{scale: 1, rotation: -6, opacity: 1, duration: 0.42, ease: "back.out(2.2)"}}, {b['num']});
              tl.fromTo("#{cid}-words span", {{yPercent: 110, opacity: 0}}, {{yPercent: 0, opacity: 1, duration: 0.38, stagger: 0.09, ease: "power3.out"}}, {b['words']});
              tl.fromTo("#{cid}-sub", {{y: 30, opacity: 0, scale: 0.8}}, {{y: 0, opacity: 1, scale: 1, duration: 0.32, ease: "back.out(2)"}}, {b['sub']});
              tl.to("#{cid} .hook", {{y: -40, opacity: 0, duration: 0.22, ease: "power2.in"}}, {e - 0.24});""")
        elif c["type"] == "promise":
            l1, l2 = c["lines"]
            els.append(clip(cid, s, e, 1, f"""
              <div class="promise">
                <div class="pill pill-a" id="{cid}-a">✨ {l1['text']}</div>
                <div class="plus" id="{cid}-p">+</div>
                <div class="pill pill-b" id="{cid}-b">💪 {l2['text']}</div>
                <div class="promise-sub" id="{cid}-s">English</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-a", {{x: -260, opacity: 0, rotation: -8}}, {{x: 0, opacity: 1, rotation: -3, duration: 0.4, ease: "back.out(1.8)"}}, {l1['t']});
              tl.fromTo("#{cid}-s", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3}}, {l1['t'] + 0.15});
              tl.fromTo("#{cid}-p", {{scale: 0}}, {{scale: 1, duration: 0.25, ease: "back.out(3)"}}, {l2['t'] - 0.12});
              tl.fromTo("#{cid}-b", {{x: 260, opacity: 0, rotation: 8}}, {{x: 0, opacity: 1, rotation: 3, duration: 0.4, ease: "back.out(1.8)"}}, {l2['t']});
              tl.to("#{cid} .promise", {{scale: 0.9, opacity: 0, duration: 0.2}}, {e - 0.22});""")
        elif c["type"] == "title":
            word = c["word"].upper()
            letters = "".join(f"<span>{ch}</span>" for ch in word)
            els.append(clip(cid, s, e, 2, f"""
              <div class="title" id="{cid}-t">
                <div class="title-badge" id="{cid}-badge">WORD {c['num']} <i>/ 03</i></div>
                <div class="title-word" id="{cid}-w">{letters}</div>
                <svg class="swoosh" viewBox="0 0 600 40" preserveAspectRatio="none"><path id="{cid}-sw" d="M8 28 C 160 6, 420 6, 592 22" /></svg>
                <div class="meaning" id="{cid}-m"><b>Matlab</b> {html.escape(c['meaning'])}</div>
              </div>
              <div class="dock" id="{cid}-d"><b>{c['num']}</b> {word} <span>= {html.escape(c['meaning'])}</span></div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-badge", {{y: -30, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.25, ease: "power2.out"}}, {s - 0.05});
              tl.fromTo("#{cid}-w span", {{yPercent: 120, rotation: 12, opacity: 0}}, {{yPercent: 0, rotation: 0, opacity: 1, duration: 0.42, stagger: 0.035, ease: "back.out(2.4)"}}, {s});
              tl.fromTo("#{cid}-sw", {{strokeDashoffset: 640}}, {{strokeDashoffset: 0, duration: 0.45, ease: "power2.out"}}, {s + 0.3});
              tl.fromTo("#{cid}-m", {{scale: 0.6, opacity: 0, y: 20}}, {{scale: 1, opacity: 1, y: 0, duration: 0.35, ease: "back.out(2.2)"}}, {c['meaning_t']});
              tl.to("#{cid}-t", {{y: -60, scale: 0.55, opacity: 0, duration: 0.35, ease: "power3.in"}}, {c['dock'] - 0.35});
              tl.fromTo("#{cid}-d", {{x: -120, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.35, ease: "power3.out"}}, {c['dock'] - 0.05});
              tl.to("#{cid}-d", {{x: -80, opacity: 0, duration: 0.25, ease: "power2.in"}}, {e - 0.28});""")
        elif c["type"] == "example":
            els.append(clip(cid, s, e, 3, f"""
              <div class="ex" id="{cid}-x">
                <div class="ex-card" id="{cid}-card">
                  <div class="ex-emoji" id="{cid}-em">{c['emoji']}</div>
                  <div class="ex-label">EXAMPLE</div>
                  <div class="ex-en">{rich(c['en'])}</div>
                  <div class="ex-hi" id="{cid}-hi">{html.escape(c['hi'])}</div>
                </div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-card", {{y: 120, scale: 0.7, rotation: -4, opacity: 0}}, {{y: 0, scale: 1, rotation: -1, opacity: 1, duration: 0.42, ease: "back.out(1.7)"}}, {s});
              tl.fromTo("#{cid}-em", {{scale: 0, rotation: -40}}, {{scale: 1, rotation: 8, duration: 0.4, ease: "back.out(3)"}}, {s + 0.2});
              tl.fromTo("#{cid} .hl", {{backgroundSize: "0% 42%"}}, {{backgroundSize: "100% 42%", duration: 0.4, ease: "power2.out"}}, {s + 0.45});
              tl.fromTo("#{cid}-hi", {{y: -30, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.3, ease: "power2.out"}}, {c['hi_t']});
              tl.to("#{cid}-x", {{y: 80, opacity: 0, duration: 0.25, ease: "power2.in"}}, {e - 0.27});""")
        elif c["type"] == "tip":
            lines = "".join(f'<div class="tip-line" id="{cid}-l{j}">{rich(l["text"], "hl-dark")}</div>'
                            for j, l in enumerate(c["lines"]))
            els.append(clip(cid, s, e, 3, f"""
              <div class="tip" id="{cid}-x">
                <div class="tip-head" id="{cid}-h">💡 Yaad rakhiye</div>
                <div class="tip-panel" id="{cid}-p">{lines}</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-h", {{scale: 0.5, opacity: 0, rotation: -6}}, {{scale: 1, opacity: 1, rotation: -3, duration: 0.35, ease: "back.out(2.5)"}}, {s});
              tl.fromTo("#{cid}-p", {{scaleY: 0, opacity: 0}}, {{scaleY: 1, opacity: 1, duration: 0.3, ease: "power3.out"}}, {c['lines'][0]['t'] - 0.15});""")
            for j, l in enumerate(c["lines"]):
                js.append(f"""
              tl.fromTo("#{cid}-l{j}", {{x: -40, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.3, ease: "power2.out"}}, {l['t']});""")
            js.append(f"""
              tl.to("#{cid}-x", {{y: 60, opacity: 0, duration: 0.25, ease: "power2.in"}}, {e - 0.27});""")
        elif c["type"] == "recap":
            rows = [("Actually", "Asal mein"), ("Instead", "Iske bajaye"), ("Finally", "Aakhirkaar")]
            body = "".join(f'<div class="rc-row" id="{cid}-r{j}"><span class="rc-n">0{j + 1}</span>'
                           f'<span class="rc-w">{w}</span><span class="rc-a">→</span><span class="rc-m">{m}</span></div>'
                           for j, (w, m) in enumerate(rows))
            els.append(clip(cid, s, e, 3, f"""
              <div class="recap" id="{cid}-x">
                <div class="rc-head" id="{cid}-h">Daily conversation mein use karo 🗣️</div>
                {body}
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-h", {{y: -30, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.3, ease: "power2.out"}}, {s});
              tl.fromTo("#{cid} .rc-row", {{x: 200, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.35, stagger: 0.32, ease: "back.out(1.6)"}}, {c['rows_t']});
              tl.to("#{cid}-x", {{scale: 0.92, opacity: 0, duration: 0.22, ease: "power2.in"}}, {e - 0.24});""")
        elif c["type"] == "boost":
            els.append(clip(cid, s, e, 3, f"""
              <div class="boost" id="{cid}-x"><div class="b1">Better +</div><div class="b2">Confident English 🚀</div></div>"""))
            js.append(f"""
              tl.fromTo("#{cid} .b1", {{scale: 0.4, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)"}}, {s});
              tl.fromTo("#{cid} .b2", {{scale: 0.4, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)"}}, {c['confident']});
              tl.to("#{cid}-x", {{opacity: 0, duration: 0.18}}, {e - 0.2});""")
        elif c["type"] == "cta":
            els.append(clip(cid, s, e, 3, f"""
              <div class="cta" id="{cid}-x">
                <div class="cta-line">aise aur videos ke liye</div>
                <div class="btn btn-follow" id="{cid}-f">➕ Follow</div>
                <div class="btn btn-comment" id="{cid}-c">💬 Comment</div>
                <div class="hand" id="{cid}-hand">👆</div>
              </div>"""))
            f, cm = max(c["follow"], s + 0.5), max(c["comment"], s + 1.1)
            js.append(f"""
              tl.fromTo("#{cid} .cta-line", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3}}, {s});
              tl.fromTo("#{cid}-f", {{scale: 0, rotation: -10}}, {{scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2.5)"}}, {s + 0.1});
              tl.fromTo("#{cid}-c", {{scale: 0, rotation: 10}}, {{scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2.5)"}}, {s + 0.25});
              tl.fromTo("#{cid}-hand", {{x: 520, y: 260, opacity: 0}}, {{x: 300, y: 70, opacity: 1, duration: 0.35, ease: "power2.out"}}, {f - 0.4});
              tl.to("#{cid}-f", {{scale: 0.88, duration: 0.08, yoyo: true, repeat: 1}}, {f});
              tl.set("#{cid}-f", {{backgroundColor: "#4A1530", color: "#FFF7EC"}}, {f + 0.08});
              tl.set("#{cid}-f", {{textContent: "✓ Following"}}, {f + 0.08});
              tl.to("#{cid}-hand", {{x: 560, y: 70, duration: 0.3, ease: "power2.inOut"}}, {cm - 0.32});
              tl.to("#{cid}-c", {{scale: 0.88, duration: 0.08, yoyo: true, repeat: 1}}, {cm});
              tl.to("#{cid}-hand", {{opacity: 0, duration: 0.3}}, {cm + 0.6});""")

    for j, f in enumerate(CUES["flashes"]):
        els.append(clip(f"fl{j}", max(0, f - 0.12), f + 0.4, 9, '<div class="flash"></div>'))
        js.append(f"""
              tl.fromTo("#fl{j} .flash", {{opacity: 0}}, {{opacity: 0.9, duration: 0.1, ease: "power1.in"}}, {max(0, f - 0.12)});
              tl.to("#fl{j} .flash", {{opacity: 0, duration: 0.32, ease: "power2.out"}}, {f});""")

    dur = CUES["duration"]
    page = TEMPLATE.replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "".join(js))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"{OUT / 'index.html'}: {len(els)} clips, {dur:.2f}s")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=2160, height=3840" />
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "Anton"; src: url(fonts/anton.woff2) format("woff2"); font-weight: 400; }
@font-face { font-family: "Poppins"; src: url(fonts/poppins-700.woff2) format("woff2"); font-weight: 700; }
@font-face { font-family: "Poppins"; src: url(fonts/poppins-800.woff2) format("woff2"); font-weight: 800; }
@font-face { font-family: "Poppins"; src: url(fonts/poppins-600i.woff2) format("woff2"); font-weight: 600; font-style: italic; }
@font-face { font-family: "Caveat"; src: url(fonts/caveat-700.woff2) format("woff2"); font-weight: 700; }
:root { --cream: #FFF7EC; --plum: #4A1530; --berry: #9B2C5C; --amber: #FFB547; --ink: #22101A; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 2160px; height: 3840px; overflow: hidden; background: transparent; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { width: 2160px; height: 3840px; }
.layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; transform: scale(2); }
.layer > div { position: absolute; }

/* hook */
.hook { left: 140px; top: 270px; width: 800px; height: 560px; }
.hook-num { position: absolute; left: 0; top: 0; width: 300px; height: 380px; font: 400 380px/1 Anton; color: var(--amber);
  text-shadow: 0 10px 0 var(--plum), 0 18px 40px rgba(0,0,0,.35); }
.hook-words { position: absolute; left: 240px; top: 70px; width: 560px; height: 300px; font: 400 140px/1.02 Anton; color: var(--cream);
  text-transform: uppercase; overflow: hidden; text-shadow: 0 6px 0 var(--plum), 0 14px 30px rgba(0,0,0,.35); }
.hook-words span { display: block; }
.chip { display: block; font: 800 40px/1 Poppins; padding: 22px 34px; border-radius: 60px; box-shadow: 0 10px 30px rgba(0,0,0,.25); }
.chip-cream { position: absolute; left: 240px; top: 410px; width: max-content; background: var(--cream); color: var(--plum); }

/* promise */
.promise { left: 140px; top: 1190px; width: 800px; height: 420px; }
.pill { position: absolute; width: max-content; font: 800 74px/1 Poppins; padding: 26px 46px; border-radius: 80px;
  box-shadow: 0 14px 36px rgba(0,0,0,.3); }
.pill-a { left: 0; top: 0; background: var(--amber); color: var(--plum); }
.pill-b { right: 0; top: 170px; background: var(--plum); color: var(--cream); }
.plus { position: absolute; left: 355px; top: 100px; width: 90px; height: 90px; font: 400 90px/90px Anton; color: var(--cream);
  text-align: center; text-shadow: 0 6px 18px rgba(0,0,0,.4); }
.promise-sub { position: absolute; left: 0; top: 330px; width: 800px; text-align: center; font: 700 italic 64px/1 Caveat;
  color: var(--cream); text-shadow: 0 4px 14px rgba(0,0,0,.55); }

/* word title */
.title { left: 140px; top: 268px; width: 800px; height: 470px; transform-origin: 0 0; }
.title-badge { position: absolute; left: 6px; top: 0; width: max-content; font: 800 34px/1 Poppins; letter-spacing: 6px; color: var(--plum);
  background: var(--amber); padding: 14px 24px; border-radius: 14px; }
.title-badge i { font-style: normal; opacity: .55; }
.title-word { position: absolute; left: 0; top: 60px; width: 800px; height: 240px; font: 400 205px/1.05 Anton; color: var(--cream);
  letter-spacing: 4px; overflow: hidden; white-space: nowrap; text-shadow: 0 8px 0 var(--plum), 0 20px 50px rgba(0,0,0,.4); }
.title-word span { display: inline-block; }
.swoosh { position: absolute; left: 0; top: 300px; width: 640px; height: 46px; overflow: visible; }
.swoosh path { fill: none; stroke: var(--amber); stroke-width: 14; stroke-linecap: round; stroke-dasharray: 640; }
.meaning { position: absolute; left: 0; top: 370px; width: max-content; max-width: 800px; font: 800 50px/1.1 Poppins; color: var(--cream);
  background: var(--berry); padding: 20px 34px; border-radius: 22px; box-shadow: 0 12px 30px rgba(0,0,0,.3); }
.meaning b { color: var(--amber); font-weight: 800; margin-right: 10px; }
.dock { left: 140px; top: 268px; width: max-content; font: 400 52px/1 Anton; letter-spacing: 2px; color: var(--cream);
  background: rgba(34,16,26,.78); padding: 16px 26px 16px 18px; border-radius: 18px; border-left: 10px solid var(--amber); }
.dock b { color: var(--amber); font-weight: 400; margin-right: 8px; }
.dock span { font: 700 34px/1 Poppins; color: var(--cream); opacity: .85; margin-left: 8px; }

/* example */
.ex { left: 140px; top: 1160px; width: 800px; height: 420px; }
.ex-card { position: absolute; left: 0; top: 0; width: 800px; background: var(--cream); border-radius: 40px; padding: 64px 40px 34px;
  box-shadow: 0 22px 50px rgba(0,0,0,.35); border-bottom: 10px solid var(--amber); }
.ex-emoji { position: absolute; right: 20px; top: -54px; width: 128px; height: 128px; border-radius: 64px; background: var(--amber);
  font-size: 70px; line-height: 128px; text-align: center; box-shadow: 0 10px 24px rgba(0,0,0,.3); }
.ex-label { position: absolute; left: 40px; top: 26px; width: 300px; font: 800 26px/1 Poppins; letter-spacing: 8px; color: var(--berry); }
.ex-en { width: 720px; font: 800 56px/1.2 Poppins; color: var(--plum); }
.hl { background-image: linear-gradient(var(--amber), var(--amber)); background-repeat: no-repeat; background-position: 0 88%;
  background-size: 0% 42%; padding: 0 4px; }
.ex-hi { width: 720px; margin-top: 18px; padding-top: 16px; border-top: 3px dashed rgba(155,44,92,.35);
  font: 600 italic 40px/1.3 Poppins; color: var(--berry); }

/* tip */
.tip { left: 140px; top: 1175px; width: 800px; height: 520px; }
.tip-head { position: absolute; left: 0; top: 0; width: max-content; font: 800 46px/1 Poppins; color: var(--plum); background: var(--amber);
  padding: 20px 32px; border-radius: 20px; box-shadow: 0 10px 26px rgba(0,0,0,.3); }
.tip-panel { position: absolute; left: 0; top: 112px; width: 800px; background: rgba(34,16,26,.82); border-radius: 34px; padding: 34px 42px;
  transform-origin: 50% 0; }
.tip-line { font: 800 48px/1.25 Poppins; color: var(--cream); margin: 6px 0; }
.hl-dark { color: var(--amber); }

/* recap */
.recap { left: 140px; top: 1150px; width: 800px; height: 560px; }
.rc-head { position: absolute; left: 0; top: 0; width: 800px; font: 700 italic 64px/1 Caveat; color: var(--cream);
  text-shadow: 0 4px 14px rgba(0,0,0,.6); }
.rc-row { position: relative; top: 80px; display: flex; align-items: center; width: 800px; height: 104px; margin-bottom: 12px;
  background: var(--cream); border-radius: 30px; padding: 0 34px; box-shadow: 0 14px 30px rgba(0,0,0,.3); }
.rc-n { font: 400 54px/1 Anton; color: var(--berry); width: 90px; }
.rc-w { font: 800 52px/1 Poppins; color: var(--plum); width: 270px; }
.rc-a { font: 800 50px/1 Poppins; color: var(--amber); width: 70px; }
.rc-m { font: 700 46px/1 Poppins; color: var(--berry); }

/* boost */
.boost { left: 140px; top: 1200px; width: 800px; height: 300px; text-align: center; }
.b1 { font: 400 120px/1.05 Anton; color: var(--amber); text-shadow: 0 6px 0 var(--plum), 0 14px 30px rgba(0,0,0,.4); }
.b2 { font: 800 70px/1.2 Poppins; color: var(--cream); text-shadow: 0 6px 22px rgba(0,0,0,.55); }

/* cta */
.cta { left: 140px; top: 1200px; width: 800px; height: 420px; }
.cta-line { position: absolute; left: 0; top: 0; width: 800px; text-align: center; font: 700 italic 66px/1 Caveat; color: var(--cream);
  text-shadow: 0 4px 14px rgba(0,0,0,.6); }
.btn { position: absolute; top: 110px; width: 370px; height: 130px; border-radius: 70px; font: 800 54px/130px Poppins; text-align: center;
  box-shadow: 0 16px 36px rgba(0,0,0,.35); }
.btn-follow { left: 15px; background: var(--amber); color: var(--plum); }
.btn-comment { left: 415px; background: var(--cream); color: var(--plum); }
.hand { position: absolute; left: 0; top: 0; width: 140px; height: 140px; font-size: 120px; line-height: 140px; }

.flash { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
  background: radial-gradient(circle at 50% 45%, #FFFDF8 0%, #FFE7C2 60%, #FFD39A 100%); }
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
    build()
