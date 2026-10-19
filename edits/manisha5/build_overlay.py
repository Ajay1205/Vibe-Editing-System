"""Caption layer for the Manisha 5 reel -- "Pep Talk" (approved style board: edits/manisha5/board).

A warm cheer-up look built from the footage (her navy top + the lamp): navy / cream / sunflower / apricot / rose.
Fraunces (soft serif) for English, Nunito for Hinglish and labels.
  - a MOOD meter at the top fills from 😔 to 🤩 as each sentence is taught,
  - hook: rain cloud turns into a sun on "cheer up",
  - each pep-talk sentence: "PEP TALK #n" tag, the Hinglish line on the wall (white italic, shadow, no panel),
    the English line in a cream speech bubble, the key word underlined by a hand-drawn stroke as she says it,
    plus its own motion graphic (sun rays / hearts / muscle / confetti),
  - "sunrise glow" transitions: a golden bloom with soft rays on every section change.
Everything sits on the wall above her head (y 262-800 on the 1080x1920 stage).
Usage: python3 -I build_overlay.py [--preview]   (--preview = 1080p)
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

UNDERLINE = ('<svg viewBox="0 0 100 20" preserveAspectRatio="none"><path pathLength="100" '
             'd="M2 12 C 25 4, 50 18, 75 8 S 96 10, 98 9"/></svg>')
BLUR_IN = '{{opacity: 0, y: 22, filter: "blur(10px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out", stagger: {st}}}'


def en_html(text):
    """English line -> word spans; **key** words get the hand-drawn underline."""
    out = []
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        for w in part.split():
            if i % 2:
                out.append(f'<span class="w k">{html.escape(w)}{UNDERLINE}</span>')
            else:
                out.append(f'<span class="w">{html.escape(w)}</span>')
    return " ".join(out)


def words(text):
    return " ".join(f'<span class="w">{w}</span>' for w in text.split())


def clip(id_, start, end, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


FX = {
    "sun": '<div class="rays" data-layout-allow-overlap></div><div class="stk fx-sun">☀️</div>',
    "hearts": ('<div class="heart hA">💛</div><div class="heart hB">🧡</div><div class="heart hC">💛</div>'
               '<div class="heart hD">🧡</div>'),
    "muscle": '<div class="stk fx-mus">💪</div>',
    "confetti": '<div class="stk fx-clap">👏</div>' + "".join(
        f'<div class="conf cf{j}"></div>' for j in range(14)),
}


def fx_js(cid, c):
    fx, s, k = c["fx"], c["hi_t"], c["key_t"]
    if fx == "sun":
        return f"""
          tl.fromTo("#{cid} .rays", {{opacity: 0, scale: 0.5, rotation: 0}}, {{opacity: 1, scale: 1, rotation: 30, duration: 1.2, ease: "power2.out"}}, {c['en_t']});
          tl.to("#{cid} .rays", {{rotation: 120, duration: {max(1, c['end'] - c['en_t']):.2f}, ease: "none"}}, {c['en_t'] + 1.2});
          tl.fromTo("#{cid} .fx-sun", {{opacity: 0, scale: 0.2, rotation: -90}}, {{opacity: 1, scale: 1, rotation: 0, duration: 0.6, ease: "back.out(2)"}}, {c['en_t'] + 0.1});"""
    if fx == "hearts":
        return f"""
          tl.fromTo("#{cid} .heart", {{opacity: 0, scale: 0.2, y: 40}}, {{opacity: 1, scale: 1, y: 0, duration: 0.45, stagger: 0.12, ease: "back.out(2.5)"}}, {c['en_t'] + 0.2});
          tl.to("#{cid} .heart", {{y: -18, duration: 1.1, yoyo: true, repeat: 6, stagger: 0.2, ease: "sine.inOut"}}, {c['en_t'] + 0.7});
          tl.to("#{cid} .heart", {{scale: 1.35, duration: 0.15, yoyo: true, repeat: 1, stagger: 0.05}}, {c.get('key2_t', k)});"""
    if fx == "muscle":
        return f"""
          tl.fromTo("#{cid} .fx-mus", {{opacity: 0, scale: 0.2, rotation: 30}}, {{opacity: 1, scale: 1, rotation: 0, duration: 0.45, ease: "back.out(3)"}}, {k - 0.1});
          tl.to("#{cid} .fx-mus", {{scale: 1.15, rotation: -8, duration: 0.25, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {k + 0.4});"""
    if fx == "confetti":
        return f"""
          tl.fromTo("#{cid} .fx-clap", {{opacity: 0, scale: 0.2}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(3)"}}, {k - 0.15});
          tl.to("#{cid} .fx-clap", {{rotation: 12, duration: 0.12, yoyo: true, repeat: 5}}, {k + 0.25});
          tl.fromTo("#{cid} .conf", {{opacity: 0, x: 0, y: 0, rotation: 0}}, {{opacity: 1, x: (i) => [-380,-300,-220,-140,-60,40,120,200,280,360,-330,-170,170,330][i], y: (i) => [-120,-200,-90,-240,-170,-230,-150,-250,-110,-190,40,70,60,30][i], rotation: (i) => i * 47, duration: 0.7, ease: "power3.out"}}, {k});
          tl.to("#{cid} .conf", {{y: "+=160", opacity: 0, rotation: "+=180", duration: 1.4, ease: "power1.in"}}, {k + 0.7});"""
    return ""


def build(res=2160):
    OUT.mkdir(exist_ok=True)
    (OUT / "vendor").mkdir(exist_ok=True)
    shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", OUT / "vendor/gsap.min.js")
    # fonts/ (Fraunces, Nunito; Google Fonts, OFL) are kept in git with the overlay

    els, js = [], []
    dur = CUES["duration"]

    # mood meter, whole video
    m = CUES["mood"]
    els.append(clip("mood", 0, dur, 7, f'<div class="mood" id="mood-b"><span class="face" id="mood-f">{m[0]["face"]}</span>'
                    '<span class="lbl">MOOD</span><span class="bar"><span class="fill" id="mood-x"></span></span></div>'))
    js.append(f'tl.fromTo("#mood-b", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.4, ease: "back.out(2)"}}, 0.05);')
    js.append(f'tl.set("#mood-x", {{width: "{m[0]["pct"]}%"}}, 0);')
    for p in m[1:]:
        js.append(f'tl.to("#mood-x", {{width: "{p["pct"]}%", duration: 0.6, ease: "power3.out"}}, {p["t"]:.3f});'
                  f'tl.set("#mood-f", {{textContent: "{p["face"]}"}}, {p["t"]:.3f});'
                  f'tl.fromTo("#mood-f", {{scale: 1.6}}, {{scale: 1, duration: 0.35, ease: "back.out(3)"}}, {p["t"]:.3f});')

    for i, c in enumerate(CUES["captions"]):
        s, e = c["start"], c["end"]
        cid = f"c{i}"
        if c["type"] == "hook":
            els.append(clip(cid, s, e, 1, f"""
              <div class="cloud" id="{cid}-cl">🌧️</div><div class="cloud sun" id="{cid}-sn">☀️</div>
              <div class="h1" id="{cid}-t">{c['title']}</div>
              <div class="h2" id="{cid}-s">{words(c['sub'])}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-cl", {{opacity: 0, y: -40}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power2.out"}}, {max(0.1, c['title_t'] - 0.5)});
              tl.to("#{cid}-cl", {{x: 10, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {c['title_t']});
              tl.fromTo("#{cid}-t", {{opacity: 0, scale: 0.85, filter: "blur(12px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "power3.out"}}, {c['title_t']});
              tl.to("#{cid}-cl", {{opacity: 0, scale: 0.4, duration: 0.3, ease: "power2.in"}}, {c['sun_t'] - 0.1});
              tl.fromTo("#{cid}-sn", {{opacity: 0, scale: 0.2, rotation: -120}}, {{opacity: 1, scale: 1, rotation: 0, duration: 0.6, ease: "back.out(2)"}}, {c['sun_t'] + 0.1});
              tl.to("#{cid}-sn", {{rotation: 40, duration: 3, ease: "none"}}, {c['sun_t'] + 0.7});
              tl.fromTo("#{cid}-s .w", {BLUR_IN.format(st=0.06)}, {c['sub_t']});
              tl.to(["#{cid}-t", "#{cid}-s", "#{cid}-sn"], {{opacity: 0, y: -30, duration: 0.25}}, {e - 0.25});""")
        elif c["type"] == "intro":
            els.append(clip(cid, s, e, 1, f"""
              <div class="h1 intro" id="{cid}-t">{c['line']}</div>
              <div class="chip" id="{cid}-s">{html.escape(c['sub'])}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-t", {{opacity: 0, y: 30, filter: "blur(12px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "power3.out"}}, {s + 0.25});
              tl.fromTo("#{cid}-s", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)"}}, {c['simple_t']});
              tl.to(["#{cid}-t", "#{cid}-s"], {{opacity: 0, y: -30, duration: 0.25}}, {e - 0.25});""")
        elif c["type"] == "pep":
            tag = f"PEP TALK #{c['n']}" + (f" · {c['tag']}" if c.get("tag") else "")
            two = "en2" in c
            els.append(clip(cid, s, e, 2, f"""
              {FX[c['fx']]}
              <div class="tag" id="{cid}-tag">{tag}</div>
              {f'<div class="tag" id="{cid}-tag2">PEP TALK #{c["n"]} · {c["tag2"]}</div>' if two else ""}
              <div class="bub" id="{cid}-b"><div class="en" id="{cid}-en">{en_html(c['en'])}</div></div>
              {f'<div class="bub" id="{cid}-b2"><div class="en" id="{cid}-en2">{en_html(c["en2"])}</div></div>' if two else ""}
              <div class="hi" id="{cid}-hi">{words(chr(8220) + html.escape(c['hi']) + chr(8221))}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-tag", {{opacity: 0, y: -14, scale: 0.8}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2.4)"}}, {c['hi_t']});
              tl.fromTo("#{cid}-hi .w", {BLUR_IN.format(st=0.07)}, {c['hi_t'] + 0.15});
              tl.fromTo("#{cid}-b", {{opacity: 0, scale: 0.4, y: 40, transformOrigin: "50% 100%"}}, {{opacity: 1, scale: 1, y: 0, duration: 0.42, ease: "back.out(1.9)"}}, {c['en_t'] - 0.08});
              tl.fromTo("#{cid}-en .w", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.18, ease: "power2.out", stagger: 0.09}}, {c['en_t']});
              tl.fromTo("#{cid}-en .k path", {{strokeDashoffset: 100}}, {{strokeDashoffset: 0, duration: 0.45, ease: "power2.out"}}, {c['key_t']});
              tl.to("#{cid}-b", {{scale: 1.04, duration: 0.18, yoyo: true, repeat: 1}}, {c['key_t']});
              {fx_js(cid, c)}""")
            if two:
                js.append(f"""
              tl.to("#{cid}-b", {{opacity: 0, scale: 0.85, y: -20, duration: 0.3, ease: "power2.in"}}, {c['up_t']});
              tl.to("#{cid}-tag", {{opacity: 0, duration: 0.2}}, {c['up_t']});
              tl.fromTo("#{cid}-tag2", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.6)"}}, {c['up_t'] + 0.2});
              tl.fromTo("#{cid}-b2", {{opacity: 0, scale: 0.4, y: 40, transformOrigin: "50% 100%"}}, {{opacity: 1, scale: 1, y: 0, duration: 0.42, ease: "back.out(1.9)"}}, {c['en2_t'] - 0.08});
              tl.fromTo("#{cid}-en2 .w", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.18, ease: "power2.out", stagger: 0.09}}, {c['en2_t']});
              tl.fromTo("#{cid}-en2 .k path", {{strokeDashoffset: 100}}, {{strokeDashoffset: 0, duration: 0.45, ease: "power2.out"}}, {c['key2_t']});""")
            js.append(f'tl.to("#{cid} .layer > *", {{opacity: 0, y: -30, duration: 0.26, ease: "power2.in"}}, {e - 0.26});')
        elif c["type"] == "better":
            els.append(clip(cid, s, e, 3, f"""
              <div class="h1 better" id="{cid}-t">{c['line']}</div>
              <div class="sparks" id="{cid}-sp">✨</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-t", {{opacity: 0, y: 30, filter: "blur(12px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "power3.out"}}, {s + 0.2});
              tl.fromTo("#{cid}-t em", {{color: "#FFF8EE"}}, {{color: "#FFC94A", duration: 0.3}}, {c['better_t']});
              tl.fromTo("#{cid}-sp", {{opacity: 0, scale: 0.2, rotation: -60}}, {{opacity: 1, scale: 1.2, rotation: 0, duration: 0.45, ease: "back.out(3)"}}, {c['better_t']});
              tl.to(["#{cid}-t", "#{cid}-sp"], {{opacity: 0, y: -30, duration: 0.25}}, {e - 0.25});""")
        elif c["type"] == "cta":
            els.append(clip(cid, s, e, 3, f"""
              <div class="cta-l" id="{cid}-l">{html.escape(c['line'])}</div>
              <div class="fbtn" id="{cid}-f">Follow</div>
              <div class="hand" id="{cid}-h">👆</div>
              <div class="daily" id="{cid}-d">{html.escape(c['daily'])}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-l", {{opacity: 0, y: -16}}, {{opacity: 1, y: 0, duration: 0.35}}, {s + 0.15});
              tl.fromTo("#{cid}-f", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)"}}, {s + 0.35});
              tl.fromTo("#{cid}-h", {{opacity: 0, x: 160, y: 120}}, {{opacity: 1, x: 0, y: 0, duration: 0.4, ease: "power2.out"}}, {c['tap'] - 0.5});
              tl.to("#{cid}-f", {{scale: 0.9, duration: 0.08, yoyo: true, repeat: 1}}, {c['tap']});
              tl.set("#{cid}-f", {{textContent: "Following ✓", backgroundColor: "#FFF8EE", color: "#1B2340"}}, {c['tap'] + 0.08});
              tl.to("#{cid}-h", {{opacity: 0, duration: 0.3}}, {c['tap'] + 0.6});
              tl.fromTo("#{cid}-d", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.35}}, {c['daily_t']});""")

    for j, f in enumerate(CUES["glows"]):
        els.append(clip(f"gl{j}", max(0, f - 0.3), f + 0.5, 9, '<div class="glow"></div><div class="grays"></div>'))
        js.append(f"""
              tl.fromTo("#gl{j} .glow", {{opacity: 0, scale: 0.5}}, {{opacity: 0.85, scale: 1.25, duration: 0.32, ease: "power2.out"}}, {max(0, f - 0.3)});
              tl.to("#gl{j} .glow", {{opacity: 0, scale: 1.6, duration: 0.4}}, {f + 0.05});
              tl.fromTo("#gl{j} .grays", {{opacity: 0, rotation: -20}}, {{opacity: 0.7, rotation: 10, duration: 0.35, ease: "power2.out"}}, {max(0, f - 0.25)});
              tl.to("#gl{j} .grays", {{opacity: 0, rotation: 30, duration: 0.35}}, {f + 0.1});""")

    page = TEMPLATE.replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "".join(js))
    if res == 1080:
        page = (page.replace("width=2160, height=3840", "width=1080, height=1920")
                .replace("html, body { width: 2160px; height: 3840px;", "html, body { width: 1080px; height: 1920px;")
                .replace(".clip { width: 2160px; height: 3840px; }", ".clip { width: 1080px; height: 1920px; }")
                .replace("transform-origin: 0 0; transform: scale(2); }", "transform-origin: 0 0; transform: none; }")
                .replace('data-width="2160" data-height="3840"', 'data-width="1080" data-height="1920"'))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    if not (OUT / "hyperframes.json").exists():
        (OUT / "hyperframes.json").write_text('{"name":"manisha5-overlay"}')
    print(f"{OUT / 'index.html'}: {len(els)} clips, {dur:.2f}s at {res}p")


CONF_COLORS = ["#FFC94A", "#FF7E9D", "#FF9E6B", "#FFF8EE"]
TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=2160, height=3840" />
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "Fraunces"; src: url(fonts/fraunces.woff2) format("woff2"); font-weight: 100 900; }
@font-face { font-family: "Fraunces"; src: url(fonts/fraunces-i.woff2) format("woff2"); font-weight: 100 900; font-style: italic; }
@font-face { font-family: "Nunito"; src: url(fonts/nunito.woff2) format("woff2"); font-weight: 100 900; }
@font-face { font-family: "Nunito"; src: url(fonts/nunito-i.woff2) format("woff2"); font-weight: 100 900; font-style: italic; }
:root { --navy: #1B2340; --cream: #FFF8EE; --sun: #FFC94A; --apricot: #FF9E6B; --rose: #FF7E9D;
  --sh: 0 2px 3px rgba(0,0,0,.55), 0 4px 16px rgba(0,0,0,.5), 0 0 2px rgba(0,0,0,.5); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 2160px; height: 3840px; overflow: hidden; background: transparent; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { width: 2160px; height: 3840px; }
.layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; transform: scale(2); }
.layer > div { position: absolute; }
.w { display: inline-block; }

.mood { left: 50%; top: 270px; transform: translateX(-50%); display: flex; align-items: center; gap: 16px; padding: 12px 22px 12px 16px;
  border-radius: 44px; background: rgba(27,35,64,.62); box-shadow: 0 8px 22px rgba(0,0,0,.25); }
.mood .face { display: inline-block; font-size: 48px; line-height: 1; }
.mood .lbl { font: 900 22px/1 Nunito; letter-spacing: 4px; color: var(--cream); }
.mood .bar { width: 300px; height: 18px; border-radius: 9px; background: rgba(255,255,255,.22); overflow: hidden; }
.mood .fill { display: block; width: 12%; height: 100%; border-radius: 9px; background: linear-gradient(90deg, var(--rose), var(--apricot), var(--sun)); }

.cloud { left: 50%; top: 380px; width: 180px; margin-left: -90px; text-align: center; font-size: 150px; line-height: 1;
  filter: drop-shadow(0 10px 20px rgba(0,0,0,.3)); }
.h1 { left: 80px; top: 560px; width: 920px; text-align: center; font: 800 96px/1.02 Fraunces; color: var(--cream); text-shadow: var(--sh); letter-spacing: -1px; }
.h1 em { font-style: italic; color: var(--sun); }
.h2 { left: 80px; top: 690px; width: 920px; text-align: center; font: 800 italic 46px/1.2 Nunito; color: #fff; text-shadow: var(--sh); }
.h1.intro { top: 430px; font-size: 84px; line-height: 1.06; }
.chip { left: 50%; top: 660px; transform: translateX(-50%); width: max-content; padding: 12px 28px; border-radius: 30px; background: var(--sun);
  color: var(--navy); font: 900 36px/1 Nunito; box-shadow: 0 8px 20px rgba(0,0,0,.28); }
.h1.better { top: 470px; font-size: 80px; line-height: 1.06; }
.sparks { left: 880px; top: 400px; font-size: 90px; }

.tag { left: 50%; top: 382px; transform: translateX(-50%); width: max-content; padding: 9px 22px; border-radius: 22px; background: var(--sun); color: var(--navy);
  font: 900 24px/1 Nunito; letter-spacing: 3px; white-space: nowrap; box-shadow: 0 6px 16px rgba(0,0,0,.25); }
.bub { left: 110px; top: 440px; width: 860px; padding: 34px 40px 40px; border-radius: 46px; background: var(--cream); text-align: center;
  box-shadow: 0 18px 44px rgba(0,0,0,.32), inset 0 0 0 4px rgba(255,201,74,.55); }
.bub:after { content: ""; position: absolute; left: 50%; bottom: -26px; width: 52px; height: 52px; margin-left: -26px; background: var(--cream);
  transform: rotate(45deg); border-radius: 8px; }
.en { position: relative; z-index: 1; font: 800 74px/1.08 Fraunces; color: var(--navy); letter-spacing: -1px; }
.k { position: relative; color: #C2410C; }
.k svg { position: absolute; left: -4%; bottom: -16px; width: 108%; height: 26px; overflow: visible; }
.k path { fill: none; stroke: var(--sun); stroke-width: 9; stroke-linecap: round; stroke-dasharray: 100; stroke-dashoffset: 100; }
.hi { left: 80px; top: 730px; width: 920px; text-align: center; font: 800 italic 54px/1.2 Nunito; color: #fff; text-shadow: var(--sh); }

.stk { font-size: 120px; line-height: 1; filter: drop-shadow(0 8px 16px rgba(0,0,0,.3)); }
.fx-sun { left: 850px; top: 270px; }
.rays { left: 690px; top: 140px; width: 420px; height: 420px; border-radius: 50%;
  background: repeating-conic-gradient(rgba(255,201,74,.38) 0 8deg, rgba(255,201,74,0) 8deg 22deg);
  -webkit-mask: radial-gradient(circle, #000 18%, transparent 68%); mask: radial-gradient(circle, #000 18%, transparent 68%); }
.heart { font-size: 58px; line-height: 1; }
.hA { left: 120px; top: 330px; } .hB { left: 900px; top: 350px; } .hC { left: 960px; top: 650px; font-size: 42px; }
.hD { left: 70px; top: 640px; font-size: 44px; }
.fx-mus { left: 870px; top: 280px; }
.fx-clap { left: 880px; top: 290px; }
.conf { left: 532px; top: 520px; width: 16px; height: 26px; border-radius: 4px; opacity: 0; }
%CONF%

.cta-l { left: 80px; top: 420px; width: 920px; text-align: center; font: 800 italic 50px/1.2 Nunito; color: #fff; text-shadow: var(--sh); }
.fbtn { left: 50%; top: 520px; transform: translateX(-50%); width: 420px; padding: 30px 0; border-radius: 60px; text-align: center;
  background: var(--sun); color: var(--navy); font: 900 56px/1 Nunito; box-shadow: 0 14px 34px rgba(0,0,0,.35); }
.hand { left: 640px; top: 600px; font-size: 110px; }
.daily { left: 80px; top: 690px; width: 920px; text-align: center; font: 800 64px/1.1 Fraunces; color: var(--cream); text-shadow: var(--sh); }

.glow { position: absolute; left: 180px; top: -300px; width: 1300px; height: 1300px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,250,232,.95), rgba(255,214,120,.7) 30%, rgba(255,170,90,.35) 55%, rgba(255,150,80,0) 72%); }
.grays { position: absolute; left: -200px; top: -500px; width: 2000px; height: 2000px; border-radius: 50%;
  background: repeating-conic-gradient(from 0deg at 62% 30%, rgba(255,225,150,.35) 0 4deg, rgba(255,225,150,0) 4deg 14deg); }
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%" data-width="2160" data-height="3840" data-fps="30">
%ELS%
</div>
<script>
  const tl = gsap.timeline({ paused: true });
  %JS%
  window.__timelines["main"] = tl;
</script>
</body></html>
""".replace("%CONF%", "\n".join(f".cf{j} {{ background: {CONF_COLORS[j % 4]}; }}" for j in range(14)))

if __name__ == "__main__":
    build(1080 if "--preview" in sys.argv else 2160)
