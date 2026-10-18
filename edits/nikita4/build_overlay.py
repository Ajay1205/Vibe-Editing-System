"""Caption layer for the Nikita 4 reel -- v3 "Close & Bold" (the Situation Series template look).

Rebuilt after the user found the menu/ticket version (build_overlay_v2_menu.py) boring: the picture now cuts
between medium and close shots (render_base.py), and the captions sit big and bold at CHEST level, right under
her face, like the reference reels -- never on her face, never on an empty wall far away.
  - top: the series question title ("Restaurant mein / English kaise bolein?") with progress dots,
  - each situation: a big emoji sticker pops beside her head, "SITUATION n" tag, the Hindi need in big white
    words with a heavy shadow (no panel), then the English line slams in on a warm-white card (espresso text,
    key words in burnt sienna on a peach marker, a small "✓ polite" tag),
  - hook: word-by-word captions, a red ✗ stamp on "ratta", neon "Restaurant English" sign,
  - recap: "Save karo 📌" stack of the five lines; CTA: comment bar with floating idea chips.
Outfit (all text) + Pacifico (neon). Warm white #FFFBF4 / espresso #2A1E18 / burnt sienna #A4471F / peach #F5D3BC
(user: bright red/yellow/green looked cheap; 'please' in green was jarring).

Stage 1080x1920 (scaled x2 for 4K). Caption zone: x 120-960, y 1100-1600 (chest; Reels bottom 320 px kept free),
banner at y 262. Usage: python3 -I build_overlay.py [--preview]   (--preview = 1080p)
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

STICKER = {"table": "🍽️", "menu": "📖", "spoon": "🥄", "water": "🥛", "bill": "🧾"}


def sticker(icon):
    return STICKER.get(icon, icon)


def words_html(text, key_cls="key"):
    """Line -> word spans; **key** words grouped under one pill; 'please' marked."""
    out = []
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        ws = [f'<span class="w{" pl" if w.lower().startswith("please") else ""}">{html.escape(w)}</span>'
              for w in part.split()]
        if not ws:
            continue
        lead = " " if part[:1] == " " else ""
        trail = " " if part[-1:] == " " else ""
        inner = " ".join(ws)
        out.append(f'{lead}<span class="{key_cls}">{inner}</span>{trail}' if i % 2 else f"{lead}{inner}{trail}")
    return "".join(out).strip()


def rich(text, cls):
    parts = re.split(r"\*\*(.+?)\*\*", html.escape(text))
    return "".join(f'<span class="{cls}">{p}</span>' if i % 2 else p for i, p in enumerate(parts))


def marks(text):
    return text.replace("<m>", '<span class="hl">').replace("</m>", "</span>")


def clip(id_, start, end, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


def blur_in(sel, t, total):
    """Words blur and rise in one by one over `total` seconds."""
    return (f'tl.fromTo("{sel}", {{opacity: 0, y: 26, filter: "blur(10px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", '
            f'duration: 0.28, ease: "power3.out", stagger: {{amount: {max(0.1, total):.2f}}}}}, {t:.3f});')


def build(res=2160):
    OUT.mkdir(exist_ok=True)
    (OUT / "vendor").mkdir(exist_ok=True)
    shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", OUT / "vendor/gsap.min.js")
    # fonts/ (Outfit, Pacifico; Google Fonts, OFL) are kept in git with the overlay

    els, js = [], []
    caps = CUES["captions"]
    sits = [c for c in caps if c["type"] == "situation"]
    n_sit = len(sits)
    for i, c in enumerate(caps):
        s, e = c["start"], c["end"]
        cid = f"c{i}"
        if c["type"] == "hook":
            lines = c["lines"]
            parts = []
            for k, ln in enumerate(lines):
                sub = f'<div class="h-sub" id="{cid}-s{k}">{words_html(ln["sub"])}</div>' if "sub" in ln else ""
                x = f'<div class="xstamp" id="{cid}-x{k}" data-layout-allow-overlap>✗</div>' if "x_t" in ln else ""
                parts.append(f'<div class="h-blk" id="{cid}-l{k}"><div class="h-line">{words_html(ln["text"], "hk")}</div>{sub}{x}</div>')
            els.append(clip(cid, s, e, 1, "".join(parts) + f"""
              <div class="neon" id="{cid}-neon"><div class="n-a">{c['neon']}</div><div class="n-b">{c['neon_sub']}</div></div>"""))
            ends = [ln["t"] for ln in lines[1:]] + [c["neon_t"]]
            for k, ln in enumerate(lines):
                n_words = len(re.sub(r"\*\*", "", ln["text"]).split())
                js.append(blur_in(f"#{cid}-l{k} .h-line .w", ln["t"], min(0.6, 0.12 * n_words)))
                js.append(f'tl.fromTo("#{cid}-l{k} .hk", {{backgroundSize: "0% 100%"}}, {{backgroundSize: "100% 100%", duration: 0.3}}, {ln["t"] + 0.35:.3f});')
                if "sub" in ln:
                    js.append(blur_in(f"#{cid}-s{k} .w", ln["sub_t"], 0.5))
                if "x_t" in ln:
                    js.append(f'tl.fromTo("#{cid}-x{k}", {{opacity: 0, scale: 3, rotation: -30}}, {{opacity: 1, scale: 1, rotation: -12, duration: 0.2, ease: "power4.in"}}, {ln["x_t"] - 0.2:.3f});')
                    js.append(f'tl.to("#{cid}-l{k} .h-line", {{x: 9, duration: 0.05, yoyo: true, repeat: 5}}, {ln["x_t"]:.3f});')
                js.append(f'tl.to("#{cid}-l{k}", {{opacity: 0, y: -30, scale: 0.9, duration: 0.22, ease: "power2.in"}}, {ends[k] - 0.22:.3f});')
            nt = c["neon_t"]
            js.append(f"""
              tl.set("#{cid}-neon", {{opacity: 0}}, 0);
              tl.set("#{cid}-neon", {{opacity: 1}}, {nt});
              tl.set("#{cid}-neon", {{opacity: 0.15}}, {nt + 0.07});
              tl.set("#{cid}-neon", {{opacity: 1}}, {nt + 0.14});
              tl.set("#{cid}-neon", {{opacity: 0.25}}, {nt + 0.2});
              tl.set("#{cid}-neon", {{opacity: 1}}, {nt + 0.32});
              tl.fromTo("#{cid}-neon .n-b", {{opacity: 0.2}}, {{opacity: 1, duration: 0.3}}, {nt + 0.32});
              tl.fromTo("#{cid}-neon", {{scale: 0.92}}, {{scale: 1.04, duration: {max(0.5, e - nt - 0.3):.2f}, ease: "none"}}, {nt});
              tl.to("#{cid}-neon", {{opacity: 0, scale: 1.15, duration: 0.25, ease: "power2.in"}}, {e - 0.25});""")
        elif c["type"] == "situation":
            n = c["n"]
            n_hi = len(c["hi"].split())
            els.append(clip(cid, s, e, 2, f"""
              <div class="stk" id="{cid}-stk" data-layout-allow-overlap>{sticker(c['icon'])}</div>
              <div class="sit" id="{cid}-all">
                <div class="tag" id="{cid}-tag">SITUATION {n}</div>
                <div class="hi" id="{cid}-hi">{words_html(c['hi'])}</div>
                <div class="card" id="{cid}-card">
                  <div class="en" id="{cid}-en">{words_html(c['en'])}</div>
                  <div class="pol" id="{cid}-po" data-layout-allow-overlap>✓ polite</div>
                </div>
              </div>"""))
            hi_t, en_t, key, pl = c["hi_t"], c["en_t"], c["key"], c["pl"]
            js.append(f"""
              tl.fromTo("#{cid}-all", {{x: {300 if n > 1 else 0}, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.3, ease: "power3.out"}}, {s});
              tl.fromTo("#{cid}-tag", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)"}}, {hi_t});
              {blur_in(f"#{cid}-hi .w", hi_t + 0.1, min(1.2, 0.16 * n_hi))}
              tl.fromTo("#{cid}-stk", {{opacity: 0, scale: 0.2, rotation: -60}}, {{opacity: 1, scale: 1, rotation: 10, duration: 0.5, ease: "back.out(2.2)"}}, {hi_t + 0.2});
              tl.to("#{cid}-stk", {{rotation: -8, y: -10, duration: 0.9, yoyo: true, repeat: {max(1, int((e - hi_t) / 0.9) - 2)}, ease: "sine.inOut"}}, {hi_t + 0.7});
              tl.to("#{cid}-hi", {{scale: 0.9, opacity: 0.9, y: -8, duration: 0.25, ease: "power2.out"}}, {en_t - 0.1});
              tl.fromTo("#{cid}-card", {{opacity: 0, scale: 0.5, rotation: -6}}, {{opacity: 1, scale: 1, rotation: -1.5, duration: 0.32, ease: "back.out(2.2)"}}, {en_t - 0.08});
              tl.fromTo("#{cid}-en .w", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.16, ease: "power2.out", stagger: {{amount: {max(0.15, pl - en_t - 0.1):.2f}}}}}, {en_t - 0.04});
              tl.fromTo("#{cid}-en .key", {{backgroundSize: "0% 100%"}}, {{backgroundSize: "100% 100%", duration: 0.22, ease: "power2.out"}}, {key});
              tl.to("#{cid}-en .key", {{scale: 1.08, duration: 0.14, yoyo: true, repeat: 1}}, {key + 0.22});
              tl.fromTo("#{cid}-po", {{opacity: 0, scale: 2.2, rotation: 25}}, {{opacity: 1, scale: 1, rotation: 8, duration: 0.2, ease: "power4.in"}}, {pl + 0.15});
              tl.to("#{cid}-card", {{scale: 1.04, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 1}}, {pl + 0.5});
              tl.to("#{cid}-all", {{x: -380, opacity: 0, duration: 0.26, ease: "power2.in"}}, {e - 0.26});
              tl.to("#{cid}-stk", {{scale: 0, rotation: 90, duration: 0.25, ease: "back.in(2)"}}, {e - 0.26});""")
            if c["icon"] == "bill":
                els.append(clip(f"{cid}m", key - 0.05, key + 1.4, 5, "".join(
                    f'<div class="money m{j}">{ch}</div>' for j, ch in enumerate("💸💰💸🪙"))))
                js.append(f"""
              tl.fromTo("#{cid}m .money", {{opacity: 0, y: 0, scale: 0.3}}, {{opacity: 1, y: -120, scale: 1, duration: 0.6, stagger: 0.08, ease: "power2.out"}}, {key - 0.05});
              tl.to("#{cid}m .money", {{opacity: 0, y: -200, duration: 0.4, stagger: 0.08}}, {key + 0.75});""")
        elif c["type"] == "recap":
            items = "".join(f'<div class="r-item"><span class="r-n">{k + 1}</span><span class="r-t">{rich(t, "r-k")}</span></div>'
                            for k, t in enumerate(c["items"]))
            els.append(clip(cid, s, e, 3, f"""
              <div class="r-head" id="{cid}-h">{c['title']}</div>
              <div class="r-list" id="{cid}-l">{items}</div>
              <div class="r-foot" id="{cid}-say">{c['say']}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-h", {{opacity: 0, scale: 0.5, rotation: -6}}, {{opacity: 1, scale: 1, rotation: -2, duration: 0.4, ease: "back.out(2.4)"}}, {s + 0.05});
              tl.fromTo("#{cid}-l .r-item", {{opacity: 0, x: 120}}, {{opacity: 1, x: 0, duration: 0.3, stagger: 0.28, ease: "back.out(1.6)"}}, {s + 0.35});
              tl.fromTo("#{cid}-say", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.35}}, {c['say_t']});
              tl.to("#{cid}-l .r-item", {{opacity: 0, x: -120, duration: 0.22, stagger: 0.04, ease: "power2.in"}}, {e - 0.35});
              tl.to(["#{cid}-h", "#{cid}-say"], {{opacity: 0, duration: 0.2}}, {e - 0.25});""")
        elif c["type"] == "cta":
            chips = "".join(f'<span class="idea">{t}</span>' for t in c["ideas"])
            els.append(clip(cid, s, e, 4, f"""
              <div class="cta-h" id="{cid}-h">{marks(c['head'])}</div>
              <div class="ideas" id="{cid}-i">{chips}</div>
              <div class="cbar" id="{cid}-cb"><span class="ph">{c['bar']}<i class="cursor">|</i></span>
                <span class="send" id="{cid}-btn">💬 Comment</span></div>
              <div class="burst" id="{cid}-bu">❤️</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-h", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)"}}, {s + 0.1});
              tl.fromTo("#{cid}-h .hl", {{backgroundSize: "0% 100%"}}, {{backgroundSize: "100% 100%", duration: 0.3}}, {c['more']});
              tl.fromTo("#{cid}-cb", {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: 0.4, ease: "back.out(1.6)"}}, {c['comment']});
              tl.fromTo("#{cid} .cursor", {{opacity: 1}}, {{opacity: 0, duration: 0.25, yoyo: true, repeat: 15}}, {c['comment']});
              tl.fromTo("#{cid}-i .idea", {{opacity: 0, y: 50, scale: 0.5}}, {{opacity: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.18, ease: "back.out(2.2)"}}, {c['ideas_t']});
              tl.to("#{cid}-i .idea", {{y: -8, duration: 0.9, yoyo: true, repeat: 5, stagger: 0.15, ease: "sine.inOut"}}, {c['ideas_t'] + 1.3});
              tl.to("#{cid}-btn", {{scale: 0.84, duration: 0.08, yoyo: true, repeat: 1}}, {c['tap']});
              tl.fromTo("#{cid}-bu", {{opacity: 0, scale: 0.3, y: 0}}, {{opacity: 1, scale: 1.4, y: -90, duration: 0.45, ease: "back.out(2)"}}, {c['tap'] + 0.05});
              tl.to("#{cid}-bu", {{opacity: 0, duration: 0.3}}, {c['tap'] + 0.6});""")

    # series banner with progress dots, from the first situation to the end
    b0 = sits[0]["start"]
    dots = "".join(f'<i id="bd{k}"></i>' for k in range(n_sit))
    els.append(clip("ban", b0, CUES["duration"], 6, f'<div class="banner" id="ban-b"><span>{marks(CUES["series"])}</span><span class="bdots">{dots}</span></div>'))
    js.append(f'tl.fromTo("#ban-b", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.35, ease: "back.out(2)"}}, {b0 + 0.1});')
    for k, c in enumerate(sits):
        js.append(f'tl.to("#bd{k}", {{backgroundColor: "#F5D3BC", scale: 1.3, duration: 0.2}}, {c["hi_t"]});')

    # light sweep (like Nikita 3's, in this palette): a soft warm streak glides across the frame between
    # situations and at section changes; the camera moves themselves glide, so no flashes on cut-ins
    sweeps = sorted(set(CUES["flashes"] + [c["start"] for c in sits[1:]]))
    for j, f in enumerate(sweeps):
        big = f in CUES["flashes"]
        els.append(clip(f"sw{j}", max(0, f - 0.3), f + 0.45, 9, '<div class="sweep"></div><div class="bloom"></div>'))
        js.append(f"""
              tl.fromTo("#sw{j} .sweep", {{xPercent: -110, opacity: 0}}, {{xPercent: 110, opacity: {0.9 if big else 0.7}, duration: 0.6, ease: "power2.inOut"}}, {max(0, f - 0.3)});
              tl.to("#sw{j} .sweep", {{opacity: 0, duration: 0.18}}, {f + 0.12});
              tl.fromTo("#sw{j} .bloom", {{opacity: 0, scale: 0.7}}, {{opacity: {0.55 if big else 0.3}, scale: 1.25, duration: 0.25, ease: "power2.out"}}, {max(0, f - 0.12)});
              tl.to("#sw{j} .bloom", {{opacity: 0, duration: 0.3}}, {f + 0.13});""")

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
        (OUT / "hyperframes.json").write_text('{"name":"nikita4-overlay"}')
    print(f"{OUT / 'index.html'}: {len(els)} clips, {dur:.2f}s at {res}p")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=2160, height=3840" />
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "Outfit"; src: url(fonts/outfit.woff2) format("woff2"); font-weight: 100 900; }
@font-face { font-family: "Pacifico"; src: url(fonts/pacifico-400.woff2) format("woff2"); }
:root { --card: #FFFBF4; --ink: #2A1E18; --accent: #A4471F; --peach: #F5D3BC; --muted: #8A7468;
  --shadow: 0 3px 3px rgba(0,0,0,.7), 0 4px 14px rgba(0,0,0,.65), 0 8px 34px rgba(0,0,0,.5), 0 0 2px rgba(0,0,0,.6); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 2160px; height: 3840px; overflow: hidden; background: transparent; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { width: 2160px; height: 3840px; }
.layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; transform: scale(2); }
.layer > div { position: absolute; }
.w { display: inline-block; }

/* hook: chest captions */
.h-blk { left: 120px; top: 1170px; width: 840px; text-align: center; }
.h-line { font: 900 92px/1.08 Outfit; color: #fff; letter-spacing: -2px; text-shadow: var(--shadow); }
.hk { display: inline-block; padding: 0 14px; border-radius: 18px; color: var(--ink); text-shadow: none;
  background-image: linear-gradient(var(--peach), var(--peach)); background-repeat: no-repeat; background-size: 0% 100%; }
.hk .w { text-shadow: none; }
.h-sub { margin-top: 18px; font: 800 58px/1.15 Outfit; color: #fff; text-shadow: var(--shadow); }
.xstamp { position: absolute; right: -10px; top: -110px; width: 120px; height: 120px; border-radius: 60px; background: var(--accent); color: #fff;
  font: 900 84px/108px Outfit; text-align: center; box-shadow: 0 10px 26px rgba(0,0,0,.45); border: 6px solid #fff; }
.neon { left: 120px; top: 1130px; width: 840px; text-align: center; }
.n-a { font: 400 140px/1.25 Pacifico; color: #FFE9E2;
  text-shadow: 0 0 6px #fff, 0 0 16px #F3B08A, 0 0 34px #E08A5C, 0 0 60px #C8653A, 0 0 90px #A4471F; }
.n-b { margin-top: 4px; font: 900 74px/1 Outfit; letter-spacing: 16px; color: #FFF6D6;
  text-shadow: 0 0 6px #fff, 0 0 16px #FFC94D, 0 0 34px #F4B63F, 0 0 64px #F4A53F; }

/* banner */
/* series title (user chose option B: a question title rather than a label pill) */
.banner { left: 50%; top: 262px; transform: translateX(-50%); width: 840px; display: flex; flex-direction: column; align-items: center; gap: 14px;
  color: #FFFBF4; text-align: center; }
.banner > span:first-child { font: 900 64px/1.05 Outfit; letter-spacing: -1px;
  text-shadow: 0 3px 3px rgba(0,0,0,.6), 0 4px 14px rgba(0,0,0,.55), 0 8px 34px rgba(0,0,0,.45); }
.banner .hl { color: var(--ink); padding: 0 14px; border-radius: 14px; background: var(--peach); text-shadow: none; }
.bdots { display: flex; gap: 10px; }
.bdots i { width: 16px; height: 16px; border-radius: 8px; background: rgba(255,255,255,.45); display: block; box-shadow: 0 2px 6px rgba(0,0,0,.4); }

/* situation */
.stk { left: 790px; top: 560px; font-size: 130px; line-height: 1;
  filter: drop-shadow(0 0 0 #fff) drop-shadow(3px 0 0 #fff) drop-shadow(-3px 0 0 #fff) drop-shadow(0 3px 0 #fff) drop-shadow(0 -3px 0 #fff) drop-shadow(0 10px 16px rgba(0,0,0,.45)); }
.sit { left: 120px; top: 1110px; width: 840px; height: 490px; }
.sit > div { position: absolute; }
.tag { left: 50%; top: 0; transform: translateX(-50%); width: max-content; padding: 10px 22px; border-radius: 12px; background: var(--ink);
  color: var(--peach); font: 800 28px/1 Outfit; letter-spacing: 4px; box-shadow: 0 6px 16px rgba(0,0,0,.35); }
.hi { left: 0; top: 60px; width: 840px; text-align: center; font: 800 64px/1.1 Outfit; color: #fff; text-shadow: var(--shadow);
  transform-origin: 50% 0; }
.card { left: 10px; top: 222px; width: 820px; padding: 26px 30px 30px; border-radius: 28px; background: var(--card); text-align: center;
  box-shadow: 0 16px 40px rgba(0,0,0,.35); }
.en { font: 800 70px/1.1 Outfit; color: var(--ink); letter-spacing: -1.5px; }
.en .key { display: inline-block; padding: 0 10px; border-radius: 12px; color: var(--accent);
  background-image: linear-gradient(var(--peach), var(--peach)); background-repeat: no-repeat; background-position: 0 85%; background-size: 0% 100%; }
.en .pl { color: var(--ink); }
.pol { position: absolute; right: -14px; top: -30px; padding: 8px 16px; border-radius: 14px; background: var(--ink); color: var(--peach);
  font: 800 30px/1 Outfit; box-shadow: 0 6px 14px rgba(0,0,0,.3); }
.money { top: 1350px; font-size: 90px; }
.m0 { left: 150px; } .m1 { left: 330px; } .m2 { left: 690px; } .m3 { left: 840px; }

/* recap */
.r-head { left: 50%; top: 1060px; transform: translateX(-50%); width: max-content; padding: 12px 30px; border-radius: 18px; background: var(--ink);
  color: var(--card); font: 900 56px/1 Outfit; box-shadow: 0 10px 26px rgba(0,0,0,.4); }
.r-list { left: 120px; top: 1150px; width: 840px; }
.r-item { display: flex; align-items: center; gap: 16px; margin-bottom: 10px; padding: 11px 22px; border-radius: 20px; background: var(--card);
  box-shadow: 0 8px 20px rgba(0,0,0,.35); }
.r-n { flex: none; width: 46px; height: 46px; border-radius: 23px; background: var(--peach); color: var(--accent); font: 900 28px/46px Outfit; text-align: center; }
.r-t { font: 700 38px/1.12 Outfit; color: var(--ink); }
.r-k { color: var(--accent); font-weight: 800; }
.r-foot { left: 120px; top: 1540px; width: 840px; text-align: center; font: 800 40px/1.1 Outfit; color: #fff; text-shadow: var(--shadow); }

/* CTA */
.cta-h { left: 120px; top: 1100px; width: 840px; text-align: center; font: 900 84px/1.06 Outfit; color: #fff; letter-spacing: -2px; text-shadow: var(--shadow); }
.cta-h .hl { padding: 0 12px; border-radius: 16px; color: var(--ink); text-shadow: none;
  background-image: linear-gradient(var(--peach), var(--peach)); background-repeat: no-repeat; background-size: 0% 100%; }
.ideas { left: 120px; top: 1300px; width: 840px; display: flex; flex-wrap: wrap; justify-content: center; gap: 14px; }
.idea { display: inline-block; padding: 14px 24px; border-radius: 30px; background: var(--card); color: var(--ink); font: 800 36px/1 Outfit;
  box-shadow: 0 8px 20px rgba(0,0,0,.3); }
.cbar { left: 120px; top: 1480px; width: 840px; height: 104px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 14px 0 32px; border-radius: 52px; background: var(--card); box-shadow: 0 10px 24px rgba(0,0,0,.32); }
.ph { font: 600 34px/1 Outfit; color: #8a7f74; }
.cursor { font-style: normal; color: #222; margin-left: 4px; }
.send { padding: 20px 28px; border-radius: 40px; background: var(--ink); color: var(--card); font: 800 34px/1 Outfit; }
.burst { left: 820px; top: 1420px; font-size: 70px; }

/* transitions: warm light sweep (peach-gold streak) + soft bloom */
.sweep { position: absolute; left: -200px; top: -400px; width: 1480px; height: 2720px; transform: rotate(18deg);
  background: linear-gradient(90deg, rgba(255,214,170,0) 30%, rgba(255,226,190,.55) 44%, rgba(255,248,236,.95) 50%, rgba(255,226,190,.55) 56%, rgba(255,214,170,0) 70%); }
.bloom { position: absolute; left: -300px; top: 300px; width: 1680px; height: 1500px; border-radius: 50%;
  background: radial-gradient(ellipse at 50% 50%, rgba(255,250,240,.9), rgba(245,211,188,.55) 40%, rgba(245,211,188,0) 72%); }
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
