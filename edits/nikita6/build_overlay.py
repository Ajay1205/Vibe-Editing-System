"""Caption layer for the Nikita 6 reel -- "The WH Family" (approved style board: edits/nikita6/board).

Cocoa / latte with one pastel colour per WH word; Baloo 2 for English, Quicksand for Hinglish.
  - hook: "The WH Family" title, seven locked "?" squircle tiles pop in on "7 words"; hearts on "family",
    a crown on every tile on "question leaders",
  - meanings: the tiles flip "?" -> Hindi word -> English word (Hindi kept small underneath) as she says them,
  - examples: a mini family bar (full words) lights the WH word, the Hindi question sits on the wall, the English
    question lands on a latte card with the WH word as its coloured chip, "QUESTION LEADER = FIRST WORD" below,
  - quiz: the card shows a blank "?" chip and asks for the answer in the comments,
  - save: bookmark + "Save karo!" + a recap strip of the seven words,
  - "tile shuffle" transitions: seven pastel squircle columns sweep up across the frame on section cuts.
Everything sits on the wall above her head (y 262-880 on the 1080x1920 stage).
Usage: python3 -I build_overlay.py [--preview]   (--preview = 1080p)
"""

import html
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "overlay"
CUES = json.load(open(HERE / "cues.json"))

COL = {"What": "--what", "When": "--when", "Where": "--where", "Why": "--why", "Who": "--who", "Which": "--which",
       "Whose": "--whose"}
BLUR_IN = '{{opacity: 0, y: 22, filter: "blur(10px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out", stagger: {st}}}'
POP = '{opacity: 0, scale: 0.4}, {opacity: 1, scale: 1, duration: 0.42, ease: "back.out(2.2)"}'


def words(text):
    return " ".join(f'<span class="w">{html.escape(w)}</span>' for w in text.split())


def clip(id_, start, end, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


def bg(word):
    return f"background:var({COL[word]})"


def build(res=2160):
    OUT.mkdir(exist_ok=True)
    (OUT / "vendor").mkdir(exist_ok=True)
    shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", OUT / "vendor/gsap.min.js")
    # fonts/ (Baloo 2, Quicksand; Google Fonts, OFL) are kept in git with the overlay

    els, js = [], []
    dur = CUES["duration"]
    caps = CUES["captions"]

    # the mini family bar runs from the first example to the end of the quiz and lights the current WH word
    exs = [c for c in caps if c["type"] == "example"]
    quiz = next(c for c in caps if c["type"] == "quiz")
    fam = "".join(f'<i id="fb{j}" style="{bg(w)}">{w}</i>' for j, w in enumerate(exs[0]["words"]))
    els.append(clip("fambar", exs[0]["start"], quiz["end"], 6, f'<div class="fam" id="fam">{fam}</div>'))
    js.append(f'tl.fromTo("#fam", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.4, ease: "back.out(2)"}}, {exs[0]["start"] + 0.05});')
    for c in exs:
        js.append(f'tl.to("#fam i", {{opacity: 0.45, scale: 1, boxShadow: "0 0 0 0px #fff", duration: 0.15}}, {c["hi_t"]});'
                  f'tl.to("#fb{c["idx"]}", {{opacity: 1, scale: 1.16, boxShadow: "0 0 0 4px #fff", duration: 0.3, ease: "back.out(3)"}}, {c["en_t"] - 0.05});')
    js.append(f'tl.to("#fam i", {{opacity: 1, scale: 1, boxShadow: "0 0 0 0px #fff", duration: 0.2}}, {quiz["hi_t"] if "hi_t" in quiz else quiz["start"]});'
              f'tl.to("#fam i", {{y: -12, duration: 0.18, yoyo: true, repeat: 1, stagger: 0.07, ease: "sine.out"}}, {quiz["ask_t"]});'
              f'tl.to("#fam", {{opacity: 0, y: -30, duration: 0.25}}, {quiz["end"] - 0.25});')

    for i, c in enumerate(caps):
        s, e = c["start"], c["end"]
        cid = f"c{i}"
        if c["type"] == "family":
            tiles = "".join(f'<div class="t" style="{bg(w)}"><div class="en">?</div><div class="crown">👑</div></div>'
                            for w in c["words"])
            els.append(clip(cid, s, e, 1, f"""
              <div class="title" id="{cid}-t">{c['title']}</div>
              <div class="sub" id="{cid}-s">{words(c['sub'])}</div>
              <div class="grid" id="{cid}-g">{tiles}</div>
              <div class="heart hA">❤️</div><div class="heart hB">❤️</div><div class="heart hC">💛</div>
              <div class="pill" id="{cid}-r">{html.escape(c['rule'])}</div>
              <div class="pill dark" id="{cid}-l">{html.escape(c['label'])}</div>
              <div class="note" id="{cid}-l2">{html.escape(c['label2'])}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-t", {{opacity: 0, scale: 0.85, filter: "blur(12px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "power3.out"}}, 0.05);
              tl.fromTo("#{cid}-t b", {{rotation: -8, scale: 0.6}}, {{rotation: 0, scale: 1, duration: 0.5, ease: "back.out(3)"}}, 0.3);
              tl.fromTo("#{cid}-g .t", {{opacity: 0, scale: 0.3, y: 40}}, {{opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(2.2)", stagger: 0.08}}, {c['tiles_t']});
              tl.to("#{cid}-g .en", {{rotation: 10, duration: 0.5, yoyo: true, repeat: 5, ease: "sine.inOut", stagger: 0.1}}, {c['tiles_t'] + 0.7});
              tl.fromTo("#{cid}-s .w", {BLUR_IN.format(st=0.06)}, {c['sub_t']});
              tl.fromTo("#{cid}-r", {POP}, {c['rule_t']});
              tl.to("#{cid}-r", {{opacity: 0, y: -20, duration: 0.25}}, {c['family_t'] - 0.6});
              tl.fromTo("#{cid} .heart", {{opacity: 0, scale: 0.2, y: 40}}, {{opacity: 1, scale: 1, y: 0, duration: 0.45, stagger: 0.12, ease: "back.out(2.5)"}}, {c['family_t']});
              tl.to("#{cid} .heart", {{y: -14, duration: 0.9, yoyo: true, repeat: 5, stagger: 0.2, ease: "sine.inOut"}}, {c['family_t'] + 0.5});
              tl.to("#{cid}-s", {{opacity: 0, y: -16, duration: 0.25}}, {c['leaders_t'] - 0.3});
              tl.fromTo("#{cid}-g .crown", {{opacity: 0, y: 30, scale: 0.3}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(3)", stagger: 0.06}}, {c['leaders_t']});
              tl.fromTo("#{cid}-l", {POP}, {c['leaders_t'] + 0.1});
              tl.fromTo("#{cid}-l2 .w, #{cid}-l2", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.3}}, {c['start_t']});
              tl.to("#{cid} .layer > *", {{opacity: 0, duration: 0.2}}, {e - 0.2});""")
        elif c["type"] == "meanings":
            tiles = "".join(f"""<div class="t" id="{cid}-t{j}" style="{bg(t['en'])}">
                <div class="face fq"><div class="en">?</div></div>
                <div class="face fh"><div class="hib">{t['hi']}</div></div>
                <div class="face fe"><div class="en">{t['en']}</div><div class="hi">{t['hi']}</div></div></div>"""
                            for j, t in enumerate(c["tiles"]))
            els.append(clip(cid, s, e, 1, f"""
              <div class="title small" id="{cid}-h">Hindi → <b>English</b></div>
              <div class="grid mg" id="{cid}-g">{tiles}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-h", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}}, {s + 0.35});
              tl.fromTo("#{cid}-g .t", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)", stagger: 0.05}}, {s + 0.45});
              tl.set("#{cid} .fh, #{cid} .fe", {{opacity: 0}}, 0);""")
            for j, t in enumerate(c["tiles"]):
                tile = f"#{cid}-t{j}"
                for at_t, hide, show in [(t["hi_t"], ".fq", ".fh"), (t["en_t"] - 0.08, ".fh", ".fe")]:
                    js.append(f"""
              tl.to("{tile}", {{rotationY: 90, transformPerspective: 600, duration: 0.12, ease: "power2.in"}}, {at_t:.3f});
              tl.set("{tile} {hide}", {{opacity: 0}}, {at_t + 0.12:.3f});
              tl.set("{tile} {show}", {{opacity: 1}}, {at_t + 0.12:.3f});
              tl.to("{tile}", {{rotationY: 0, duration: 0.2, ease: "back.out(2)"}}, {at_t + 0.12:.3f});""")
                js.append(f'tl.to("{tile}", {{scale: 1.12, duration: 0.16, yoyo: true, repeat: 1}}, {t["en_t"] + 0.1:.3f});')
            js.append(f'tl.to("#{cid} .layer > *", {{opacity: 0, duration: 0.2}}, {e - 0.2});')
        elif c["type"] == "exintro":
            els.append(clip(cid, s, e, 1, f'<div class="title small" id="{cid}-t">{words(c["line"])}</div>'))
            js.append(f"""
              tl.fromTo("#{cid}-t .w", {BLUR_IN.format(st=0.08)}, {s + 0.3});
              tl.to("#{cid}-t", {{opacity: 0, y: -20, duration: 0.2}}, {e - 0.2});""")
        elif c["type"] == "example":
            wh, rest = c["en"].split(" ", 1)
            track = 2 + (c["n"] % 2)  # alternate tracks so the held card can overlap the next question
            lead = '<div class="lead">👑 QUESTION LEADER = FIRST WORD</div>'
            els.append(clip(cid, s, e, track, f"""
              <div class="hq" id="{cid}-hq"{' style="font-size:42px"' if len(c['hi']) > 28 else ''}>{words(chr(8220) + c['hi'] + chr(8221))}</div>
              <div class="ex" id="{cid}-x"><div class="card" id="{cid}-c"><div class="q"><span class="chip" style="{bg(wh)}">{wh}</span> {words(rest)}</div></div>
              {lead}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-hq .w", {BLUR_IN.format(st=0.06)}, {c['hi_t']});
              tl.fromTo("#{cid}-c", {{opacity: 0, scale: 0.5, y: 40}}, {{opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(1.9)"}}, {c['en_t'] - 0.1});
              tl.fromTo("#{cid}-c .chip", {{scale: 1.6, rotation: -10}}, {{scale: 1, rotation: 0, duration: 0.45, ease: "back.out(3)"}}, {c['en_t']});
              tl.fromTo("#{cid}-c .w", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.18, ease: "power2.out", stagger: 0.09}}, {c['en_t'] + 0.15});
              tl.fromTo("#{cid} .lead", {{opacity: 0, y: -10}}, {{opacity: 1, y: 0, duration: 0.3}}, {c['en_t'] + 0.5});""")
            if c["next"]:
                js.append(f'tl.to("#{cid}-hq", {{opacity: 0, y: -16, duration: 0.2}}, {c["next"] - 0.2});')
            js.append(f'tl.to("#{cid}-x", {{opacity: 0, y: -24, scale: 0.92, duration: 0.25, ease: "power2.in"}}, {e - 0.25});')
            if not c["next"]:
                js.append(f'tl.to("#{cid}-hq", {{opacity: 0, duration: 0.2}}, {e - 0.2});')
        elif c["type"] == "quiz":
            els.append(clip(cid, s, e, 4, f"""
              <div class="hq" id="{cid}-hq"{' style="font-size:42px"' if len(c['hi']) > 28 else ''}>{words(chr(8220) + c['hi'] + chr(8221))}</div>
              <div class="ex" id="{cid}-x"><div class="card" id="{cid}-c"><div class="q"><span class="chip blank">?</span> {words(c['en'])}</div></div>
              <div class="ask" id="{cid}-a">{html.escape(c['ask'])}</div></div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-hq .w", {BLUR_IN.format(st=0.06)}, {s + 0.05});
              tl.fromTo("#{cid}-c", {{opacity: 0, scale: 0.5, y: 40}}, {{opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(1.9)"}}, {s + 0.2});
              tl.to("#{cid}-c .blank", {{scale: 1.14, duration: 0.35, yoyo: true, repeat: 15, ease: "sine.inOut"}}, {s + 0.7});
              tl.fromTo("#{cid}-a", {POP}, {c['ask_t']});
              tl.to("#{cid}-a", {{rotation: 2, duration: 0.12, yoyo: true, repeat: 3}}, {c['ask_t'] + 0.5});
              tl.to("#{cid} .layer > *", {{opacity: 0, y: -24, duration: 0.25}}, {e - 0.25});""")
        elif c["type"] == "save":
            strip = "".join(f'<span style="{bg(w)}">{w}</span>' for w in c["words"])
            els.append(clip(cid, s, e, 1, f"""
              <div class="book" id="{cid}-b">🔖</div>
              <div class="save" id="{cid}-s">{c['line']}</div>
              <div class="mini" id="{cid}-m">{strip}</div>
              <div class="note" id="{cid}-n">{html.escape(c['sub'])}</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-b", {{opacity: 0, y: -60, rotation: -40}}, {{opacity: 1, y: 0, rotation: -8, duration: 0.5, ease: "back.out(2.4)"}}, {c['save_t'] - 0.15});
              tl.fromTo("#{cid}-s", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2.4)"}}, {c['save_t']});
              tl.to("#{cid}-b", {{y: -14, duration: 0.6, yoyo: true, repeat: 7, ease: "sine.inOut"}}, {c['save_t'] + 0.6});
              tl.fromTo("#{cid}-n", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.35}}, {c['save_t'] + 1.6});
              tl.to("#{cid}-n", {{opacity: 0, duration: 0.2}}, {c['strip_t'] - 0.4});
              tl.fromTo("#{cid}-m span", {{opacity: 0, y: 30, scale: 0.5}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2.6)", stagger: 0.08}}, {c['strip_t']});""")

    # tile shuffle: seven pastel squircle columns sweep up through the frame, centred on the cut
    cols = "".join(f'<div class="col" style="left:{j * 154 - 4}px;{bg(w)}"></div>' for j, w in enumerate(COL))
    for j, t in enumerate(CUES["shuffles"]):
        els.append(clip(f"sh{j}", t - 0.45, t + 0.45, 9, cols))
        js.append(f"""
              tl.fromTo("#sh{j} .col", {{y: 2100}}, {{y: -2300, duration: 0.8, ease: "power1.inOut", stagger: {{each: 0.035, from: "center"}}}}, {t - 0.45:.3f});""")
    for j, t in enumerate(CUES["flashes"]):
        els.append(clip(f"fl{j}", t - 0.15, t + 0.35, 9, '<div class="flash"></div>'))
        js.append(f"""
              tl.fromTo("#fl{j} .flash", {{opacity: 0}}, {{opacity: 0.55, duration: 0.14, ease: "power2.out"}}, {t - 0.15:.3f});
              tl.to("#fl{j} .flash", {{opacity: 0, duration: 0.32, ease: "power2.in"}}, {t:.3f});""")

    page = TEMPLATE.replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "".join(js))
    if res == 1080:
        page = (page.replace("width=2160, height=3840", "width=1080, height=1920")
                .replace("html, body { width: 2160px; height: 3840px;", "html, body { width: 1080px; height: 1920px;")
                .replace(".clip { width: 2160px; height: 3840px; }", ".clip { width: 1080px; height: 1920px; }")
                .replace("transform-origin: 0 0; transform: scale(2); }", "transform-origin: 0 0; transform: none; }")
                .replace('data-width="2160" data-height="3840"', 'data-width="1080" data-height="1920"'))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    if not (OUT / "hyperframes.json").exists():
        (OUT / "hyperframes.json").write_text('{"name":"nikita6-overlay"}')
    print(f"{OUT / 'index.html'}: {len(els)} clips, {dur:.2f}s at {res}p")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=2160, height=3840" />
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "Baloo"; src: url(fonts/baloo.woff2) format("woff2"); font-weight: 400 800; }
@font-face { font-family: "Quick"; src: url(fonts/quicksand.woff2) format("woff2"); font-weight: 300 700; }
:root { --cocoa: #4A2E22; --latte: #FFF4E6; --heart: #E8475A;
  --what: #FFB3C1; --when: #FFD58A; --where: #A8E0C4; --why: #B9C8FF; --who: #FFC2A1; --which: #D7B9FF; --whose: #A9DDF2;
  --sh: 0 2px 3px rgba(0,0,0,.5), 0 4px 16px rgba(0,0,0,.45), 0 0 2px rgba(0,0,0,.5); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 2160px; height: 3840px; overflow: hidden; background: transparent; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { width: 2160px; height: 3840px; }
.layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; transform: scale(2); }
.layer > div { position: absolute; }
.w { display: inline-block; }

.title { left: 80px; top: 280px; width: 920px; text-align: center; font: 800 92px/1 Baloo; color: var(--latte); text-shadow: var(--sh); }
.title b { display: inline-block; color: var(--heart); background: var(--latte); padding: 0 18px; border-radius: 22px; text-shadow: none; }
.title.small { top: 285px; font-size: 70px; }
.sub { left: 80px; top: 390px; width: 920px; text-align: center; font: 700 42px/1.2 Quick; color: #fff; text-shadow: var(--sh); }

.grid { left: 110px; top: 470px; width: 860px; display: flex; flex-wrap: wrap; justify-content: center; gap: 18px; }
.grid.mg { top: 400px; }
.t { position: relative; width: 190px; height: 150px; border-radius: 38px; display: flex; flex-direction: column; align-items: center;
  justify-content: center; box-shadow: 0 10px 22px rgba(0,0,0,.28), inset 0 -6px 0 rgba(0,0,0,.08); }
.t .en { display: inline-block; font: 800 54px/1 Baloo; color: var(--cocoa); }
.t > .en { font-size: 70px; opacity: .55; }
.t .hi { margin-top: 4px; font: 700 28px/1 Quick; color: rgba(74,46,34,.75); }
.t .hib { font: 700 44px/1 Quick; color: var(--cocoa); }
.face { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.fq .en { font-size: 70px; opacity: .55; }
.crown { position: absolute; left: 50%; top: -34px; margin-left: -24px; font-size: 44px; line-height: 1; opacity: 0;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,.3)); }
.heart { font-size: 46px; line-height: 1; filter: drop-shadow(0 4px 8px rgba(0,0,0,.25)); }
.hA { left: 36px; top: 440px; } .hB { left: 994px; top: 520px; font-size: 38px; }
.hC { left: 44px; top: 690px; font-size: 36px; }
.pill { left: 50%; top: 815px; transform: translateX(-50%); width: max-content; padding: 12px 26px; border-radius: 26px; background: var(--latte);
  color: var(--cocoa); font: 800 32px/1 Baloo; box-shadow: 0 8px 20px rgba(0,0,0,.28); white-space: nowrap; }
.pill.dark { background: var(--cocoa); color: var(--latte); letter-spacing: 1px; }
.note { left: 80px; top: 880px; width: 920px; text-align: center; font: 700 38px/1.2 Quick; color: #fff; text-shadow: var(--sh); }

/* examples */
.fam { left: 50%; top: 270px; transform: translateX(-50%); width: max-content; display: flex; gap: 8px; padding: 9px 12px; border-radius: 34px;
  background: rgba(74,46,34,.55); }
.fam i { display: inline-block; padding: 9px 12px; border-radius: 16px; font: 800 26px/1 Baloo; color: var(--cocoa); font-style: normal; opacity: .45; }
.hq { left: 30px; top: 382px; width: 1020px; text-align: center; white-space: nowrap; font: 700 48px/1.2 Quick; color: #fff; text-shadow: var(--sh); }
.ex { left: 90px; top: 470px; width: 900px; display: flex; flex-direction: column; align-items: center; gap: 18px; }
.card { width: 900px; padding: 30px 30px; border-radius: 40px; background: var(--latte); text-align: center;
  box-shadow: 0 18px 44px rgba(0,0,0,.32); border: 5px solid #fff; }
.card .q { font: 800 70px/1.12 Baloo; color: var(--cocoa); }
.chip { display: inline-block; padding: 0 18px; border-radius: 22px; }
.chip.blank { min-width: 150px; background: #fff; border: 5px dashed var(--heart); color: var(--heart); }
.lead { padding: 10px 24px; border-radius: 24px; background: var(--cocoa); color: var(--latte); font: 800 28px/1 Baloo; letter-spacing: 2px;
  white-space: nowrap; }
.ask { padding: 14px 28px; border-radius: 28px; background: var(--heart); color: #fff; font: 800 38px/1 Baloo; white-space: nowrap;
  box-shadow: 0 10px 24px rgba(0,0,0,.3); }

/* save */
.book { left: 50%; top: 300px; margin-left: -85px; font-size: 170px; line-height: 1; filter: drop-shadow(0 12px 24px rgba(0,0,0,.35)); }
.save { left: 80px; top: 500px; width: 920px; text-align: center; font: 800 110px/1 Baloo; color: var(--latte); text-shadow: var(--sh); }
.save b { color: var(--heart); }
.mini { left: 140px; top: 640px; width: 800px; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
.mini span { display: inline-block; padding: 10px 18px; border-radius: 22px; font: 800 34px/1 Baloo; color: var(--cocoa); box-shadow: 0 6px 14px rgba(0,0,0,.25); }

/* transitions */
.col { position: absolute; top: 0; width: 162px; height: 1920px; border-radius: 80px; box-shadow: 0 0 40px rgba(0,0,0,.15); }
.flash { position: absolute; inset: 0; width: 1080px; height: 1920px;
  background: radial-gradient(circle at 50% 35%, rgba(255,244,230,.95), rgba(255,194,161,.6) 45%, rgba(255,179,193,.25) 75%, rgba(255,179,193,0)); }
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
"""

if __name__ == "__main__":
    build(1080 if "--preview" in sys.argv else 2160)
