"""Caption layer for Manisha 10 -- "Tag It" (approved board: edits/manisha10/board).

Prepositions taught on the real props on her desk: AR corner brackets + name tags land on the lamp, table, box, mic,
pen and napkin as she names them; big word + handwritten Hinglish meaning + mini icon; sentence card with the
preposition on an amber pill (lights when she says it); ON · IN · UNDER · AT strip on top; AT gets a clock that turns to
5 and a map pin for Gandhinagar; quiz card with a pulsing blank, options A-D and "Comment karo" (answer never shown).
Rendered natively at 2160x3840.   Usage: python3 -I overlay.py  -> overlay/index.html
"""

import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cut as C  # noqa: E402
from keys import K  # noqa: E402

BLURIN = '{opacity: 0, y: 18, filter: "blur(10px)"}, {opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out"}'
POP = '{opacity: 0, scale: 0.4}, {opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)"}'


def t(key, d=0.0):
    tk, s = K[key]
    return round(C.T(tk, s) + d, 3)


def clip(id_, s, e, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{s:.3f}" data-duration="{max(0.05, e - s):.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


ICON = {k: f'<svg width="170" height="150" viewBox="-25 -25 170 150"><use href="#i-{k}" width="120" height="100"/></svg>' for k in ("on", "in", "under", "at")}


def build():
    els, js = [], []
    dur = C.duration()
    ex = lambda sel, e: js.append(f'tl.to("{sel}", {{opacity: 0, y: -10, duration: 0.16, ease: "power2.in"}}, {e - 0.17});')  # noqa: E731

    # ---------------------------------------------------------------- hook: 4 tiles, then "= PREPOSITIONS"
    hook_end = C.take_end(1)
    tiles = "".join(f'<div class="tile" id="tl{i}"><b>{w.upper()}</b>{ICON[w].replace("170", "120", 1).replace("150", "100", 1)}</div>'
                    for i, w in enumerate(("on", "in", "under", "at")))
    els.append(clip("hk", 0, hook_end, 1, f'<div class="tiles">{tiles}</div><div class="prep"><span id="pp">= PREPOSITIONS 📍</span></div>'))
    for i, w in enumerate(("on", "in", "under", "at")):
        if i == 0:
            continue  # the first tile is on screen from frame 1 (hook)
        at = t(w, -0.05)
        js.append(f'tl.fromTo("#tl{i}", {{opacity: 0, y: -80, scale: 0.6, rotation: {(-1) ** i * 8}}}, {{opacity: 1, y: 0, scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2)"}}, {at});')
    js.append(f'tl.fromTo("#pp", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.6)"}}, {t("prepositions")});')
    js.append(f'tl.to("#hk .tile", {{y: -60, scale: 0.4, opacity: 0, duration: 0.3, ease: "power2.in", stagger: 0.05}}, {hook_end - 0.3});')
    js.append(f'tl.to("#pp", {{opacity: 0, duration: 0.15}}, {hook_end - 0.15});')

    # ---------------------------------------------------------------- top strip (intro -> AT)
    s0, s1 = C.take_start(2), C.take_start(7)
    els.append(clip("strip", s0, s1, 2, '<div class="tabs">' + "".join(f'<span id="tb{i}">{w}<em class="ck" id="ck{i}"> ✓</em></span>' for i, w in enumerate(("ON", "IN", "UNDER", "AT"))) + '</div>'))
    js.append(f'tl.fromTo("#strip .tabs span", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out", stagger: 0.08}}, {s0 + 0.05});')
    for i, tk in enumerate((3, 4, 5, 6)):
        st, en = C.take_start(tk), C.take_end(tk)
        js.append(f'tl.to("#tb{i}", {{backgroundColor: "#FFB547", color: "#1E1C1A", scale: 1.06, duration: 0.25}}, {st + 0.05});')
        if tk != 6:
            js.append(f'tl.to("#tb{i}", {{backgroundColor: "rgba(30,28,26,.8)", color: "#A8D5B5", scale: 1, duration: 0.25}}, {en - 0.05});'
                      f'tl.fromTo("#ck{i}", {{display: "none"}}, {{display: "inline", duration: 0.01}}, {en - 0.05});')
    ex("#strip .tabs", s1)

    # ---------------------------------------------------------------- intro line
    s, e = C.take_start(2), C.take_end(2)
    els.append(clip("intro", s, e, 3, '<div class="hand" id="it">Aaj: <b>matlab</b> + <b>examples</b> 👇</div>'))
    js.append(f'tl.fromTo("#it", {BLURIN}, {t("aaj", -0.1)});')
    ex("#it", e)

    # ---------------------------------------------------------------- ON / IN / UNDER
    def bracket(id_, take, x, y, w, h, sage=False):
        x0, y0 = C.stage(x, y, take)
        x1, y1 = C.stage(x + w, y + h, take)
        return f'<div class="brk{" sg" if sage else ""}" id="{id_}" style="left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px"><i></i><i></i><i></i><i></i></div>'

    def tag(id_, take, x, y, text, sage=False):
        x0, y0 = C.stage(x, y, take)
        return f'<div class="tag{" sg" if sage else ""}" id="{id_}" style="left:{x0}px;top:{y0}px">{text}</div>'

    def land_bracket(sel, at):
        js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: 1.25}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "power3.out"}}, {at});')
        js.append(f'tl.fromTo("{sel} i", {{opacity: 1}}, {{opacity: 0.55, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {at + 0.4});')

    def sentence(id_, words, pill_idx, extra=""):
        sp = []
        for j, w in enumerate(words):
            cls = ' class="w pill"' if j == pill_idx else ' class="w"'
            sp.append(f'<span{cls} id="{id_}w{j}">{w}</span>')
        return f'<div class="card" id="{id_}"{extra}>{" ".join(sp)}</div>'

    def sentence_js(id_, keys, pill_idx):
        js.append(f'tl.fromTo("#{id_}", {{opacity: 0, y: 30, scale: 0.94}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.8)"}}, {t(keys[0], -0.3)});')
        for j, k in enumerate(keys):
            js.append(f'tl.fromTo("#{id_}w{j}", {{opacity: 0, y: 14, filter: "blur(8px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.25, ease: "power3.out"}}, {t(k, -0.08)});')
        js.append(f'tl.fromTo("#{id_}w{pill_idx}", {{backgroundColor: "rgba(255,181,71,0)"}}, {{backgroundColor: "rgba(255,181,71,1)", duration: 0.2}}, {t(keys[pill_idx])});')
        js.append(f'tl.fromTo("#{id_}w{pill_idx}", {{scale: 1}}, {{scale: 1.15, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out"}}, {t(keys[pill_idx])});')

    sections = [
        # id, take, WORD, meaning, meaning key, mean left, icon, sentence words, pill idx, key prefix, tags
        ("on", 3, "ON", "= upar ⬆️", "on_upar", 400, "on", ["The", "lamp", "is", "on", "the", "table."], 3, "on_s",
         [("b", (590, 1140, 470, 750), False, "lamp"), ("t", (620, 1075), False, "LAMP", "lamp"), ("ln", None, True, "table"), ("t", (150, 1500), True, "TABLE", "table")]),
        ("in", 4, "IN", "= andar 📦", "in_andar", 330, "in", ["The", "mic", "is", "in", "the", "box."], 3, "in_s",
         [("b", (405, 1625, 310, 240), True, "box"), ("t", (430, 1560), True, "BOX", "box"), ("t", (600, 1560), False, "MIC ↘", "in_s1")]),
        ("un", 5, "UNDER", "= neeche ⬇️", "under_neeche", 700, None, ["The", "pen", "is", "under", "the", "napkin."], 3, "un_s",
         [("b", (320, 1735, 250, 90), False, "pen"), ("t", (330, 1655), False, "PEN", "pen"), ("b", (540, 1670, 480, 240), True, "napkin"), ("t", (700, 1590), True, "NAPKIN", "napkin")]),
    ]
    for sid, tk, word, mean, mk, ml, icon, words, pidx, kp, tags in sections:
        s, e = C.take_start(tk), C.take_end(tk)
        inner = [f'<div class="big" id="{sid}B">{word}</div>', f'<div class="mean" id="{sid}M" style="left:{ml}px">{mean}</div>']
        if icon:
            inner.append(f'<div class="ico" id="{sid}I" style="left:780px;top:340px">{ICON[icon]}</div>')
        inner.append(sentence(f"{sid}C", words, pidx))
        tj = []
        for n, tg in enumerate(tags):
            kind = tg[0]
            if kind == "b":
                x, y, w, h = tg[1]
                inner.append(bracket(f"{sid}b{n}", tk, x, y, w, h, tg[2]))
                tj.append((f"#{sid}b{n}", tg[3], "b"))
            elif kind == "t":
                inner.append(tag(f"{sid}t{n}", tk, tg[1][0], tg[1][1], tg[3], tg[2]))
                tj.append((f"#{sid}t{n}", tg[4], "t"))
            else:  # table line
                x0, y0 = C.stage(150, 1568, tk)
                inner.append(f'<div class="lead" id="{sid}l{n}" style="left:{x0}px;top:{y0}px;width:900px;background:#A8D5B5"></div>')
                tj.append((f"#{sid}l{n}", tg[3], "l"))
        els.append(clip(sid, s, e, 4, "".join(inner)))
        tw = K[f"{sid if sid != 'un' else 'under'}_t"]
        js.append(f'tl.fromTo("#{sid}B", {{opacity: 0, scale: 1.8, y: -20}}, {{opacity: 1, scale: 1, y: 0, duration: 0.35, ease: "power3.out"}}, {round(C.T(*tw) - 0.05, 3)});')
        js.append(f'tl.fromTo("#{sid}M", {BLURIN}, {t(mk, -0.1)});')
        if icon:
            js.append(f'tl.fromTo("#{sid}I", {POP}, {t(mk, 0.1)});')
        for sel, k, kind in tj:
            at = t(k, -0.05)
            if kind == "b":
                land_bracket(sel, at)
            elif kind == "t":
                js.append(f'tl.fromTo("{sel}", {{opacity: 0, y: 16, scale: 0.7}}, {{opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2.4)"}}, {at + 0.1});')
            else:
                js.append(f'tl.fromTo("{sel}", {{scaleX: 0, opacity: 1}}, {{scaleX: 1, opacity: 1, duration: 0.45, ease: "power3.out"}}, {at});')
        sentence_js(f"{sid}C", [f"{kp}{j}" for j in range(len(words))], pidx)
        ex(f"#{sid} .layer > div", e)

    # ---------------------------------------------------------------- AT
    s, e = C.take_start(6), C.take_end(6)
    clock = ('<svg width="128" height="128" viewBox="0 0 150 150"><circle cx="75" cy="75" r="62" fill="#fff" stroke="#1E1C1A" stroke-width="7"/>'
             + "".join(f'<line x1="75" y1="20" x2="75" y2="30" stroke="#1E1C1A" stroke-width="5" transform="rotate({a} 75 75)"/>' for a in range(0, 360, 30))
             + '<line id="hh" x1="75" y1="75" x2="75" y2="45" stroke="#1E1C1A" stroke-width="8" stroke-linecap="round"/>'
             '<line id="mh" x1="75" y1="75" x2="75" y2="28" stroke="#FF6B57" stroke-width="5" stroke-linecap="round"/><circle cx="75" cy="75" r="6" fill="#1E1C1A"/></svg>')
    pin = ('<svg width="92" height="110" viewBox="0 0 110 130"><path d="M55 124 C24 84 16 70 16 52 a39 39 0 0 1 78 0 c0 18 -8 32 -39 72z" fill="#FF6B57" stroke="#1E1C1A" stroke-width="6"/>'
           '<circle cx="55" cy="52" r="14" fill="#fff"/></svg>')
    a1 = ["I", "will", "meet", "you", "at", "5 PM."]
    a2 = ["We", "will", "meet", "at", "Gandhinagar", "today."]
    els.append(clip("at", s, e, 4, f"""<div class="big" id="atB">AT</div>
      <div class="mean sm" id="atM1" style="left:330px;top:350px">= time ⏰</div><div class="mean sm" id="atM2" style="left:330px;top:430px">/ jagah 📍</div>
      <div class="ico wide" id="atW" style="left:760px;top:335px"><div class="clk" id="clk">{clock}<div class="lbl" id="clkL">5 PM</div></div>
        <div class="pin" id="pin">{pin}<div class="lbl" id="pinL">Gandhinagar</div></div></div>
      {sentence("atC1", a1, 4)}{sentence("atC2", a2, 3, ' style="font-size:52px"')}"""))
    js.append(f'tl.fromTo("#atB", {{opacity: 0, scale: 1.8, y: -20}}, {{opacity: 1, scale: 1, y: 0, duration: 0.35, ease: "power3.out"}}, {t("at_t", -0.05)});')
    js.append(f'tl.fromTo("#atM1", {BLURIN}, {t("at_time", -0.1)});tl.fromTo("#atM2", {BLURIN}, {t("at_place", -0.1)});')
    js.append(f'tl.fromTo("#atW", {POP}, {t("at_time")});tl.set("#pin", {{opacity: 0}}, {s});tl.set("#clkL", {{opacity: 0}}, {s});')
    js.append(f'tl.fromTo("#hh", {{rotation: 0, svgOrigin: "75 75"}}, {{rotation: 150, svgOrigin: "75 75", duration: 0.7, ease: "power3.inOut"}}, {t("baje", -0.6)});')
    js.append(f'tl.fromTo("#mh", {{rotation: 0, svgOrigin: "75 75"}}, {{rotation: 720, svgOrigin: "75 75", duration: 0.7, ease: "power3.inOut"}}, {t("baje", -0.6)});')
    js.append(f'tl.fromTo("#clkL", {POP}, {t("baje", 0.1)});')
    js.append(f'tl.to("#clk", {{opacity: 0, scale: 0.6, duration: 0.2}}, {t("gandhi1", -0.25)});')
    js.append(f'tl.fromTo("#pin", {{opacity: 0, y: -120}}, {{opacity: 1, y: 0, duration: 0.45, ease: "bounce.out"}}, {t("gandhi1", -0.1)});')
    sentence_js("atC1", [f"a1_{j}" for j in range(6)], 4)
    js.append(f'tl.to("#atC1", {{opacity: 0, y: -10, duration: 0.15}}, {t("gandhi1", -0.3)});')
    sentence_js("atC2", [f"a2_{j}" for j in range(6)], 3)
    ex("#at .layer > div", e)

    # ---------------------------------------------------------------- quiz
    s, e = C.take_start(7), dur
    qw = ["The", "keys", "are", '<span class="blank" id="qb"></span>', "the", "table."]
    els.append(clip("qz", s, e + 0.2, 5, f"""<div class="qchip" id="qc">QUIZ TIME 🧠</div>
      {sentence("qC", qw, -1, ' style="top:350px;font-size:52px"')}
      <div class="hand q" id="qh">Sahi preposition kaunsa? 🤔</div>
      <div class="opts" id="qo"><span><em>A</em>on</span><span><em>B</em>in</span><span><em>C</em>under</span><span><em>D</em>at</span></div>
      <div class="cta" id="qct">Comment karo 👇</div>"""))
    js.append(f'tl.fromTo("#qc", {{opacity: 0, x: -60}}, {{opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}}, {s + 0.05});')
    js.append(f'tl.fromTo("#qC", {{opacity: 0, y: 30, scale: 0.94}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.8)"}}, {t("q0", -0.3)});')
    for j in range(6):
        js.append(f'tl.fromTo("#qCw{j}", {{opacity: 0, y: 14, filter: "blur(8px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.25, ease: "power3.out"}}, {t(f"q{j}", -0.08)});')
    js.append(f'tl.fromTo("#qb", {{scale: 1}}, {{scale: 1.08, duration: 0.45, yoyo: true, repeat: 15, ease: "sine.inOut"}}, {t("q3", 0.3)});')
    js.append(f'tl.fromTo("#qh", {BLURIN}, {t("sahi", -0.1)});')
    js.append(f'tl.fromTo("#qo span", {{opacity: 0, y: 24, scale: 0.7}}, {{opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2.4)", stagger: 0.12}}, {t("qprep", 0.1)});')
    js.append(f'tl.fromTo("#qct", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.4)"}}, {t("comment", -0.1)});')
    js.append(f'tl.to("#qct", {{scale: 1.07, duration: 0.35, yoyo: true, repeat: 5, ease: "sine.inOut"}}, {t("comment", 0.4)});')

    out = HERE / "overlay"
    (out / "vendor").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    shutil.copy(C.ROOT / "node_modules/gsap/dist/gsap.min.js", out / "vendor/gsap.min.js")
    for f in (HERE / "board" / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "fonts" / f.name)
    (out / "hyperframes.json").write_text('{"name":"manisha10-overlay"}\n')
    page = TEMPLATE.replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "\n".join(js))
    (out / "index.html").write_text(page)
    print(out / "index.html", f"{len(els)} clips, {dur:.2f}s")


TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: Brico; src: url(fonts/brico800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs600.woff2); font-weight: 600; }
@font-face { font-family: Cav; src: url(fonts/cav700.woff2); font-weight: 700; }
:root { --ink: #1E1C1A; --cream: #FFF6E6; --amb: #FFB547; --sage: #A8D5B5; --tom: #FF6B57;
  --sh: 0 2px 3px rgba(0,0,0,.4), 0 8px 26px rgba(0,0,0,.35); }
html, body { margin: 0; background: transparent; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; }
.clip { position: absolute; inset: 0; } .layer { position: absolute; inset: 0; }
.layer > div { position: absolute; }
.w { display: inline-block; }
.tabs { left: 150px; top: 262px; width: 780px; display: flex; gap: 12px; }
.ck { font-style: normal; display: none; }
.tabs span { flex: 1; height: 54px; border-radius: 27px; background: rgba(30,28,26,.55); color: rgba(255,246,230,.7);
  font: 800 26px/54px PJS; letter-spacing: 2px; text-align: center; display: block; }
.tiles { left: 110px; top: 350px; width: 860px; display: flex; gap: 20px; }
.tile { flex: 1; height: 220px; border-radius: 30px; background: var(--cream); box-shadow: 0 16px 34px rgba(0,0,0,.25); text-align: center; }
.tile b { display: block; margin-top: 16px; font: 800 52px/1 Brico; color: var(--ink); }
.tile svg { margin-top: 10px; }
.prep { left: 0; top: 610px; width: 1080px; text-align: center; }
.prep span { display: inline-block; padding: 14px 30px; border-radius: 40px; background: var(--tom); color: #fff; font: 800 46px/1 Brico; box-shadow: 0 12px 26px rgba(0,0,0,.25); }
.hand { left: 0; top: 380px; width: 1080px; text-align: center; font: 700 84px/1.1 Cav; color: #fff; text-shadow: var(--sh); }
.hand b { color: var(--amb); font-weight: 700; background: rgba(30,28,26,.85); padding: 0 16px 6px; border-radius: 16px; text-shadow: none; }
.hand.q { top: 470px; font-size: 64px; }
.big { left: 130px; top: 340px; font: 800 150px/1 Brico; color: var(--amb); -webkit-text-stroke: 6px var(--ink); paint-order: stroke fill;
  text-shadow: 0 10px 26px rgba(0,0,0,.3); }
.mean { top: 380px; font: 700 76px/1 Cav; color: #fff; text-shadow: var(--sh); white-space: nowrap; }
.mean.sm { font-size: 64px; }
.ico { width: 170px; height: 150px; border-radius: 26px; background: var(--cream); box-shadow: 0 14px 30px rgba(0,0,0,.25); }
.ico.wide { width: 210px; height: 190px; }
.clk, .pin { position: absolute; left: 0; top: 0; width: 210px; height: 190px; text-align: center; }
.clk svg { margin-top: 10px; } .pin svg { margin-top: 12px; }
.lbl { position: absolute; left: 0; width: 210px; bottom: 6px; font: 800 26px/1 PJS; color: var(--ink); }
#clkL { left: 30px; width: 150px; bottom: 12px; padding: 7px 0; border-radius: 14px; background: var(--amb); }
#pinL { left: 8px; width: 194px; bottom: 12px; padding: 7px 0; border-radius: 14px; background: var(--tom); color: #fff; font-size: 23px; }
.card { left: 110px; top: 545px; width: 860px; box-sizing: border-box; padding: 24px 28px; border-radius: 30px; background: var(--cream);
  text-align: center; font: 800 56px/1.12 Brico; color: var(--ink); box-shadow: 0 18px 40px rgba(0,0,0,.28); }
.pill { padding: 0 16px 4px; border-radius: 16px; background: rgba(255,181,71,0); }
.brk i { position: absolute; width: 46px; height: 46px; border: 7px solid var(--amb); }
.brk i:nth-child(1) { left: 0; top: 0; border-right: 0; border-bottom: 0; border-radius: 14px 0 0 0; }
.brk i:nth-child(2) { right: 0; top: 0; border-left: 0; border-bottom: 0; border-radius: 0 14px 0 0; }
.brk i:nth-child(3) { left: 0; bottom: 0; border-right: 0; border-top: 0; border-radius: 0 0 0 14px; }
.brk i:nth-child(4) { right: 0; bottom: 0; border-left: 0; border-top: 0; border-radius: 0 0 14px 0; }
.brk.sg i { border-color: var(--sage); }
.tag { padding: 10px 18px; border-radius: 14px; background: var(--ink); color: var(--amb); font: 800 28px/1 PJS; letter-spacing: 2px; box-shadow: 0 8px 20px rgba(0,0,0,.3); }
.tag.sg { color: var(--sage); }
.tag::before { content: ""; display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: currentColor; margin-right: 10px; vertical-align: 2px; }
.lead { height: 4px; transform-origin: 0 50%; border-radius: 2px; }
.qchip { left: 110px; top: 262px; padding: 12px 22px; border-radius: 30px; background: var(--tom); color: #fff; font: 800 28px/1 PJS; letter-spacing: 2px; }
.blank { display: inline-block; width: 170px; height: 56px; vertical-align: -8px; border-radius: 16px; border: 5px dashed var(--tom); background: rgba(255,107,87,.12); }
.opts { left: 110px; top: 580px; width: 860px; display: flex; gap: 16px; justify-content: center; }
.opts span { display: inline-block; padding: 16px 26px; border-radius: 30px; background: rgba(30,28,26,.85); color: var(--cream); font: 800 38px/1 Brico; box-shadow: 0 10px 24px rgba(0,0,0,.25); }
.opts span em { font-style: normal; color: var(--amb); margin-right: 10px; font: 800 26px/1 PJS; }
.cta { left: 0; top: 690px; width: 1080px; text-align: center; font: 700 80px/1 Cav; color: #fff; text-shadow: var(--sh); }
</style></head><body>
<svg width="0" height="0" style="position:absolute"><defs>
 <symbol id="i-on" viewBox="0 0 120 100"><circle cx="60" cy="34" r="16" fill="#FFB547" stroke="#1E1C1A" stroke-width="5"/><path d="M14 52 H106 M26 52 V92 M94 52 V92" stroke="#1E1C1A" stroke-width="8" stroke-linecap="round" fill="none"/></symbol>
 <symbol id="i-in" viewBox="0 0 120 100"><rect x="22" y="30" width="76" height="60" rx="8" fill="rgba(168,213,181,.45)" stroke="#1E1C1A" stroke-width="7"/><circle cx="60" cy="62" r="16" fill="#FFB547" stroke="#1E1C1A" stroke-width="5"/></symbol>
 <symbol id="i-under" viewBox="0 0 120 100"><path d="M14 22 H106 M26 22 V92 M94 22 V92" stroke="#1E1C1A" stroke-width="8" stroke-linecap="round" fill="none"/><circle cx="60" cy="74" r="16" fill="#FFB547" stroke="#1E1C1A" stroke-width="5"/></symbol>
 <symbol id="i-at" viewBox="0 0 120 100"><circle cx="40" cy="52" r="28" fill="#fff" stroke="#1E1C1A" stroke-width="6"/><path d="M40 52 V34 M40 52 H54" stroke="#1E1C1A" stroke-width="6" stroke-linecap="round"/><path d="M92 86 C76 64 74 56 74 46 a18 18 0 0 1 36 0 c0 10 -2 18 -18 40z" fill="#FF6B57" stroke="#1E1C1A" stroke-width="5"/><circle cx="92" cy="46" r="6" fill="#fff"/></symbol>
</defs></svg>
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
