"""Generate the v2 caption layer: a kinetic, editorial style, different from v1 in every way.

v1 = warm cream/plum cards under her face. v2 = no cards: white words that blur in one by one,
electric-lime highlights, Poppins italic for the Hinglish lines, lime light-sweep transitions.
v2 keeps the raw framing, so every caption lives in the open wall ABOVE her head
(y 262-850 on the 1080x1920 stage, x 140-940), never on her face, and inside the Reels safe box.

Usage: python3 -I build_overlay_v2.py [--preview]   (--preview = 1080p for fast review)
"""

import html
import json
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "overlay_v2"
CUES = json.load(open(HERE / "cues.json"))

FONTS = {
    "brico-600.woff2": "@fontsource/bricolage-grotesque/files/bricolage-grotesque-latin-600-normal.woff2",
    "brico-700.woff2": "@fontsource/bricolage-grotesque/files/bricolage-grotesque-latin-700-normal.woff2",
    "brico-800.woff2": "@fontsource/bricolage-grotesque/files/bricolage-grotesque-latin-800-normal.woff2",
    "playfair-600i.woff2": "@fontsource/playfair-display/files/playfair-display-latin-600-italic.woff2",
    "playfair-700i.woff2": "@fontsource/playfair-display/files/playfair-display-latin-700-italic.woff2",
    "poppins-600i.woff2": "@fontsource/poppins/files/poppins-latin-600-italic.woff2",
}


def words(text, kw_cls="kw"):
    """Split into word spans for the blur-in; **keyword** spans get the lime marker."""
    out = []
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        for w in part.split():
            cls = f"w {kw_cls}" if i % 2 else "w"
            out.append(f'<span class="{cls}">{html.escape(w)}</span>')
    return " ".join(out)


def clip(id_, start, end, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


BLUR_IN = '{{opacity: 0, y: 34, filter: "blur(14px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.38, stagger: {st}, ease: "power3.out"}}'
BLUR_OUT = '{opacity: 0, y: -40, filter: "blur(12px)", duration: 0.28, ease: "power2.in"}'


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
              <div class="hook" id="{cid}-x">
                <div class="hook-num" id="{cid}-n">3</div>
                <div class="hook-words" id="{cid}-w"><span class="w">English</span> <span class="w">Words</span></div>
                <div class="serif hook-sub" id="{cid}-s">for your vocabulary</div>
                <div class="teaser" id="{cid}-tz"><span>🔒 #1 ???</span><span>🔒 #2 ???</span><span>🔒 #3 ???</span></div>
                <div class="hin hook-today" id="{cid}-td">aaj se hi use karna start karo ✓</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-n", {{scale: 0.2, opacity: 0, filter: "blur(20px)"}}, {{scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out"}}, {b['num']});
              tl.fromTo("#{cid}-w .w", {BLUR_IN.format(st=0.12)}, {b['words']});
              tl.fromTo("#{cid}-s", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.35, ease: "power2.out"}}, {b['sub']});
              tl.fromTo("#{cid}-tz span", {BLUR_IN.format(st=0.18)}, {b['teaser']});
              tl.to("#{cid}-tz span", {{backgroundColor: "rgba(215,255,63,1)", color: "#10131F", duration: 0.2, stagger: 0.35}}, {b['teaser'] + 0.9});
              tl.fromTo("#{cid}-td", {{opacity: 0, y: 20, filter: "blur(10px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "power3.out"}}, {b['today']});
              tl.to("#{cid}-n", {{scale: 1.08, duration: 0.6, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {b['teaser']});
              tl.to("#{cid}-x", {BLUR_OUT}, {e - 0.3});""")
        elif c["type"] == "promise":
            l1, l2 = c["lines"]
            els.append(clip(cid, s, e, 1, f"""
              <div class="promise" id="{cid}-x">
                <div class="pr-1" id="{cid}-a">{l1['text']} <span class="serif amp">&amp;</span></div>
                <div class="pr-2" id="{cid}-b">{l2['text']}</div>
                <div class="serif pr-sub" id="{cid}-s">English ✦</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-a", {{opacity: 0, x: -80, filter: "blur(12px)"}}, {{opacity: 1, x: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out"}}, {l1['t']});
              tl.fromTo("#{cid}-b", {{opacity: 0, x: 80, filter: "blur(12px)"}}, {{opacity: 1, x: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out"}}, {l2['t']});
              tl.fromTo("#{cid}-s", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {l2['t'] + 0.2});
              tl.to("#{cid}-x", {BLUR_OUT}, {e - 0.3});""")
        elif c["type"] == "title":
            n = int(c["num"])
            dots = "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(3))
            letters = "".join(f"<span>{ch}</span>" for ch in c["word"])
            els.append(clip(cid, s, e, 2, f"""
              <div class="title" id="{cid}-t">
                <div class="t-meta" id="{cid}-meta"><span class="dots">{dots}</span> WORD {n} OF 3</div>
                <div class="t-word" id="{cid}-w">{letters}</div>
                <div class="t-bar" id="{cid}-bar"></div>
                <div class="hin t-mean" id="{cid}-m">“{html.escape(c['meaning'])}”</div>
              </div>
              <div class="dock" id="{cid}-d"><b>{n}/3</b> {c['word']} <span class="hin">{html.escape(c['meaning'])}</span></div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-meta", {{opacity: 0, y: -16}}, {{opacity: 1, y: 0, duration: 0.3}}, {s - 0.05});
              tl.fromTo("#{cid}-w span", {{yPercent: 100, opacity: 0, filter: "blur(10px)"}}, {{yPercent: 0, opacity: 1, filter: "blur(0px)", duration: 0.45, stagger: 0.04, ease: "expo.out"}}, {s});
              tl.fromTo("#{cid}-bar", {{scaleX: 0}}, {{scaleX: 1, duration: 0.5, ease: "expo.out"}}, {s + 0.3});
              tl.fromTo("#{cid}-m", {{opacity: 0, y: 24, filter: "blur(10px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "power3.out"}}, {c['meaning_t']});
              tl.to("#{cid}-t", {BLUR_OUT}, {c['dock'] - 0.3});
              tl.fromTo("#{cid}-d", {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: 0.35, ease: "expo.out"}}, {c['dock'] - 0.05});
              tl.to("#{cid}-d", {{opacity: 0, x: -30, duration: 0.25}}, {e - 0.28});""")
        elif c["type"] == "example":
            els.append(clip(cid, s, e, 3, f"""
              <div class="ex" id="{cid}-x">
                <div class="ex-label">EXAMPLE <span>{c['emoji']}</span></div>
                <div class="ex-en" id="{cid}-en">{words(c['en'])}</div>
                <div class="hin ex-hi" id="{cid}-hi">{html.escape(c['hi'])}</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid} .ex-label", {{opacity: 0, x: -20}}, {{opacity: 1, x: 0, duration: 0.3}}, {s});
              tl.fromTo("#{cid}-en .w", {BLUR_IN.format(st=0.07)}, {s + 0.05});
              tl.fromTo("#{cid} .kw", {{backgroundSize: "0% 100%", color: "#FFFFFF"}}, {{backgroundSize: "100% 100%", color: "#10131F", duration: 0.3, ease: "power2.out"}}, {max(c['word_t'], s + 0.4)});
              tl.fromTo("#{cid}-hi", {{opacity: 0, y: 20, filter: "blur(10px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "power3.out"}}, {c['hi_t']});
              tl.to("#{cid}-x", {BLUR_OUT}, {e - 0.3});""")
        elif c["type"] == "tip":
            lines = "".join(f'<div class="tip-line" id="{cid}-l{j}">{words(l["text"], "kw-text")}</div>'
                            for j, l in enumerate(c["lines"]))
            els.append(clip(cid, s, e, 3, f"""
              <div class="tip" id="{cid}-x">
                <div class="tip-head" id="{cid}-h">💡 Yaad rakhiye</div>
                {lines}
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-h", {{opacity: 0, scale: 0.7}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)"}}, {s});""")
            for j, l in enumerate(c["lines"]):
                js.append(f"""
              tl.fromTo("#{cid}-l{j} .w", {BLUR_IN.format(st=0.05)}, {l['t']});""")
            js.append(f"""
              tl.to("#{cid}-x", {BLUR_OUT}, {e - 0.3});""")
        elif c["type"] == "recap":
            rows = [("Actually", "Asal mein"), ("Instead", "Iske bajaye"), ("Finally", "Aakhirkaar")]
            body = "".join(f'<div class="rc-row"><b>0{j + 1}</b><span class="rc-w">{w}</span>'
                           f'<span class="hin rc-m">{m}</span></div>' for j, (w, m) in enumerate(rows))
            els.append(clip(cid, s, e, 3, f"""
              <div class="recap" id="{cid}-x">
                <div class="hin rc-head">Daily conversation mein use karo</div>
                {body}
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid} .rc-head", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.35}}, {s});
              tl.fromTo("#{cid} .rc-row", {{opacity: 0, x: -60, filter: "blur(10px)"}}, {{opacity: 1, x: 0, filter: "blur(0px)", duration: 0.4, stagger: 0.32, ease: "expo.out"}}, {c['rows_t']});
              tl.to("#{cid}-x", {BLUR_OUT}, {e - 0.3});""")
        elif c["type"] == "boost":
            els.append(clip(cid, s, e, 3, f"""
              <div class="boost" id="{cid}-x"><div class="b1">Better</div><div class="b2">Confident</div><div class="serif b3">English</div></div>"""))
            js.append(f"""
              tl.fromTo("#{cid} .b1", {{opacity: 0, scale: 1.6, filter: "blur(16px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out"}}, {s});
              tl.fromTo("#{cid} .b2", {{opacity: 0, scale: 1.6, filter: "blur(16px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out"}}, {c['confident']});
              tl.fromTo("#{cid} .b3", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {c['confident'] + 0.2});
              tl.to("#{cid}-x", {BLUR_OUT}, {e - 0.25});""")
        elif c["type"] == "cta":
            f, cm = max(c["follow"], s + 0.5), max(c["comment"], s + 1.1)
            els.append(clip(cid, s, e, 3, f"""
              <div class="cta" id="{cid}-x">
                <div class="hin cta-line">aise aur videos ke liye</div>
                <div class="btn btn-f" id="{cid}-f">Follow</div>
                <div class="btn btn-c" id="{cid}-c">Comment</div>
                <div class="hand" id="{cid}-hand">👆</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid} .cta-line", {{opacity: 0, y: -16}}, {{opacity: 1, y: 0, duration: 0.3}}, {s});
              tl.fromTo("#{cid} .btn", {{opacity: 0, y: 40, filter: "blur(10px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, stagger: 0.12, ease: "expo.out"}}, {s + 0.1});
              tl.fromTo("#{cid}-hand", {{x: 520, y: 330, opacity: 0}}, {{x: 300, y: 170, opacity: 1, duration: 0.35, ease: "power2.out"}}, {f - 0.4});
              tl.to("#{cid}-f", {{scale: 0.9, duration: 0.08, yoyo: true, repeat: 1}}, {f});
              tl.set("#{cid}-f", {{textContent: "Following ✓", backgroundColor: "#FFFFFF"}}, {f + 0.08});
              tl.to("#{cid}-hand", {{x: 600, y: 170, duration: 0.3, ease: "power2.inOut"}}, {cm - 0.32});
              tl.to("#{cid}-c", {{scale: 0.9, duration: 0.08, yoyo: true, repeat: 1}}, {cm});
              tl.set("#{cid}-c", {{backgroundColor: "#D7FF3F", color: "#10131F", borderColor: "#D7FF3F"}}, {cm + 0.08});
              tl.to("#{cid}-hand", {{opacity: 0, duration: 0.3}}, {cm + 0.6});""")

    for j, f in enumerate(CUES["flashes"]):
        els.append(clip(f"tr{j}", max(0, f - 0.2), f + 0.35, 9, '<div class="sweep"></div><div class="veil"></div>'))
        js.append(f"""
              tl.fromTo("#tr{j} .sweep", {{xPercent: -160}}, {{xPercent: 160, duration: 0.5, ease: "power2.inOut"}}, {max(0, f - 0.2)});
              tl.fromTo("#tr{j} .veil", {{opacity: 0}}, {{opacity: 0.35, duration: 0.15, yoyo: true, repeat: 1}}, {max(0, f - 0.12)});""")

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
        (OUT / "hyperframes.json").write_text('{"name":"nikita3-overlay-v2"}')
    print(f"{OUT / 'index.html'}: {len(els)} clips, {dur:.2f}s at {res}p")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=2160, height=3840" />
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "Brico"; src: url(fonts/brico-600.woff2) format("woff2"); font-weight: 600; }
@font-face { font-family: "Brico"; src: url(fonts/brico-700.woff2) format("woff2"); font-weight: 700; }
@font-face { font-family: "Brico"; src: url(fonts/brico-800.woff2) format("woff2"); font-weight: 800; }
@font-face { font-family: "Playfair"; src: url(fonts/playfair-600i.woff2) format("woff2"); font-weight: 600; font-style: italic; }
@font-face { font-family: "Playfair"; src: url(fonts/playfair-700i.woff2) format("woff2"); font-weight: 700; font-style: italic; }
@font-face { font-family: "PoppinsI"; src: url(fonts/poppins-600i.woff2) format("woff2"); font-weight: 600; font-style: italic; }
:root { --lime: #D7FF3F; --coral: #FF7A59; --peach: #FFE2CF; --ink: #10131F; --glass: rgba(12,15,28,.55); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 2160px; height: 3840px; overflow: hidden; background: transparent; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { width: 2160px; height: 3840px; }
.layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; transform: scale(2); }
.layer > div { position: absolute; }
.serif { font-family: Playfair; font-style: italic; font-weight: 600; }
.hin { font-family: PoppinsI; font-style: italic; font-weight: 600; letter-spacing: 0; }  /* Hinglish lines: readable italic */
.w { display: inline-block; }
.shadow, .hook-words, .pr-1, .pr-2, .t-word, .ex-en, .tip-line, .b1, .b2 { text-shadow: 0 4px 18px rgba(0,0,0,.55), 0 1px 3px rgba(0,0,0,.6); }

/* hook */
.hook { left: 140px; top: 290px; width: 800px; height: 540px; }
.teaser { position: absolute; left: 0; top: 352px; width: 800px; display: flex; gap: 16px; }
.teaser span { display: inline-block; padding: 14px 26px; border-radius: 40px; font: 800 44px/1 Brico; color: #fff;
  background: var(--glass); border: 3px solid var(--lime); }
.hook-today { position: absolute; left: 4px; top: 452px; width: 800px; font-size: 40px; color: var(--peach);
  text-shadow: 0 3px 14px rgba(0,0,0,.6); }
.hook-num { position: absolute; left: 0; top: 0; width: 200px; height: 300px; font: 800 300px/1 Brico; color: var(--lime);
  text-shadow: 0 0 40px rgba(215,255,63,.45), 0 6px 20px rgba(0,0,0,.4); }
.hook-words { position: absolute; left: 200px; top: 34px; width: 600px; font: 800 104px/1 Brico; color: #fff; letter-spacing: -2px; }
.hook-sub { position: absolute; left: 204px; top: 262px; width: 600px; font-size: 46px; color: var(--peach); text-shadow: 0 3px 14px rgba(0,0,0,.6); }

/* promise */
.promise { left: 140px; top: 360px; width: 800px; height: 420px; text-align: center; }
.pr-1 { font: 800 118px/1.05 Brico; color: #fff; letter-spacing: -2px; }
.pr-1 .amp { font-size: 96px; color: var(--coral); }
.pr-2 { font: 800 118px/1.05 Brico; color: var(--lime); letter-spacing: -2px; text-shadow: 0 0 36px rgba(215,255,63,.45), 0 4px 16px rgba(0,0,0,.5); }
.pr-sub { margin-top: 10px; font-size: 52px; color: var(--peach); text-shadow: 0 3px 14px rgba(0,0,0,.6); }

/* title */
.title { left: 140px; top: 300px; width: 800px; height: 420px; }
.t-meta { position: absolute; left: 4px; top: 0; width: 600px; font: 700 28px/1 Brico; letter-spacing: 7px; color: var(--lime);
  text-shadow: 0 2px 10px rgba(0,0,0,.6); }
.dots { display: inline-block; margin-right: 10px; }
.dots i { display: inline-block; width: 16px; height: 16px; border-radius: 8px; margin-right: 6px; border: 3px solid var(--lime); }
.dots i.on { background: var(--lime); }
.t-word { position: absolute; left: 0; top: 46px; width: 800px; height: 190px; overflow: hidden; font: 800 172px/1.08 Brico; color: #fff;
  letter-spacing: -4px; white-space: nowrap; }
.t-word span { display: inline-block; }
.t-bar { position: absolute; left: 6px; top: 246px; width: 440px; height: 14px; border-radius: 7px; background: var(--lime);
  transform-origin: 0 50%; box-shadow: 0 0 24px rgba(215,255,63,.6); }
.t-mean { position: absolute; left: 4px; top: 286px; width: 800px; font-size: 58px; line-height: 1.15; color: var(--peach);
  text-shadow: 0 3px 16px rgba(0,0,0,.6); }
.dock { left: 140px; top: 268px; width: max-content; padding: 12px 24px; border-radius: 40px; background: var(--glass);
  border: 2px solid rgba(215,255,63,.6); font: 700 34px/1 Brico; color: #fff; }
.dock b { color: var(--lime); margin-right: 6px; }
.dock span { margin-left: 8px; font-size: 28px; color: var(--peach); }

/* example */
.ex { left: 140px; top: 360px; width: 800px; padding: 30px 36px 34px; border-radius: 36px;
  background: linear-gradient(180deg, rgba(12,15,28,.62), rgba(12,15,28,.38)); border-left: 8px solid var(--lime); }
.ex-label { font: 700 26px/1 Brico; letter-spacing: 8px; color: var(--lime); margin-bottom: 18px; }
.ex-label span { letter-spacing: 0; font-size: 34px; margin-left: 6px; }
.ex-en { font: 800 64px/1.18 Brico; color: #fff; letter-spacing: -1px; }
.kw { padding: 0 8px; border-radius: 10px; background-image: linear-gradient(var(--lime), var(--lime)); background-repeat: no-repeat;
  background-size: 0% 100%; text-shadow: none; }
.ex-hi { margin-top: 20px; font-size: 40px; line-height: 1.3; color: var(--peach); }

/* tip */
.tip { left: 140px; top: 360px; width: 800px; padding: 30px 36px; border-radius: 36px;
  background: linear-gradient(180deg, rgba(12,15,28,.62), rgba(12,15,28,.38)); }
.tip-head { display: inline-block; font: 800 40px/1 Brico; color: var(--ink); background: var(--coral); padding: 14px 24px;
  border-radius: 40px; margin-bottom: 22px; }
.tip-line { font: 700 54px/1.25 Brico; color: #fff; margin: 4px 0; }
.kw-text { color: var(--lime); }

/* recap */
.recap { left: 140px; top: 340px; width: 800px; height: 480px; }
.rc-head { font-size: 42px; color: var(--peach); margin-bottom: 12px; text-shadow: 0 3px 14px rgba(0,0,0,.6); }
.rc-row { display: flex; align-items: baseline; width: 800px; height: 100px; margin-bottom: 10px; padding: 0 30px; border-radius: 28px;
  background: var(--glass); border-left: 8px solid var(--lime); }
.rc-row b { font: 800 42px/100px Brico; color: var(--lime); width: 80px; }
.rc-w { font: 800 56px/100px Brico; color: #fff; width: 300px; }
.rc-m { font-size: 40px; color: var(--peach); }

/* boost */
.boost { left: 140px; top: 360px; width: 800px; height: 440px; text-align: center; }
.b1 { font: 800 150px/1 Brico; color: #fff; letter-spacing: -4px; }
.b2 { font: 800 150px/1.05 Brico; color: var(--lime); letter-spacing: -4px; text-shadow: 0 0 40px rgba(215,255,63,.5), 0 4px 16px rgba(0,0,0,.5); }
.b3 { font-size: 60px; color: var(--peach); text-shadow: 0 3px 14px rgba(0,0,0,.6); }

/* cta */
.cta { left: 140px; top: 380px; width: 800px; height: 380px; }
.cta-line { position: absolute; left: 0; top: 0; width: 800px; text-align: center; font-size: 48px; color: var(--peach);
  text-shadow: 0 3px 14px rgba(0,0,0,.6); }
.btn { position: absolute; top: 120px; width: 360px; height: 126px; border-radius: 63px; font: 800 52px/120px Brico; text-align: center; }
.btn-f { left: 20px; background: var(--lime); color: var(--ink); border: 3px solid var(--lime); }
.btn-c { left: 420px; background: var(--glass); color: #fff; border: 3px solid #fff; }
.hand { position: absolute; left: 0; top: 0; width: 140px; height: 140px; font-size: 120px; line-height: 140px; }

/* transitions: a lime light sweep with a soft veil */
.sweep { position: absolute; left: 0; top: -200px; width: 700px; height: 2400px; transform: rotate(18deg);
  background: linear-gradient(90deg, rgba(215,255,63,0), rgba(215,255,63,.85) 45%, rgba(255,255,255,.95) 50%, rgba(215,255,63,.85) 55%, rgba(215,255,63,0)); }
.veil { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; background: #fff; }
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
