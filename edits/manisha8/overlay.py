"""Caption + graphics layer for a Manisha 8 version -- "NPAT Notebook" style (approved board: edits/manisha8/board).

Palette from the footage: deep teal #17423C, mint #CFEADF, paper #FFF9EE, pencil yellow #FFC94A, margin red #E8475A.
Anton (hook), Bricolage Grotesque (sentences), Caveat (handwriting), Plus Jakarta Sans (chips / tags).
All graphics live on the wall above her head (y 262-840 on the 1080x1920 stage); rendered natively at 2160x3840.

Hooks: A "Ratta? No!" (slashed textbook definition + stamp) on the `def` line; C (shortest version) a text hook on the
first frame over her cold open "Name, place, animal, thing".
Cutaway lines (animated scenes, version 3 and 4) get no captions here: each scene carries its own text.

Usage: python3 -I overlay.py <version> [--res 1080|2160]   -> overlay/<version>/index.html
"""

import html
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lines as L  # noqa: E402
import scenes_plan as SP  # noqa: E402

NB_LINES = ["npat", "concept", "answers", "notice", "rule"]
EXAMPLES = [  # (sentence line, its explanation lines, noun, Hinglish sentence, English, label, reason)
    ("ex1", ["ex1_why"], "Ria", "Meri friend Ria hai.", "My friend is Ria.", "👤 PERSON = NOUN", "kyunki Ria ek ladki ka <b>naam</b> hai"),
    ("ex2", ["ex2_is", "ex2_ask", "ex2_why"], "Mumbai", "Main Mumbai mein rehti hoon.", "I live in Mumbai.", "📍 PLACE = NOUN",
     "kyunki Mumbai ek jagah ka <b>naam</b> hai"),
    ("ex3", ["ex3_why"], "tiger", "Mujhe tiger se dar lagta hai.", "I am scared of tigers.", "🐯 ANIMAL = NOUN",
     "kyunki tiger ek animal ka <b>naam</b> hai"),
    ("ex4", ["ex4_why"], "pencil", "I have a pencil.", "", "✏️ THING = NOUN", "kyunki pencil ek cheez ka <b>naam</b> hai"),
]
COLS = [("NAME", "Ria", "PERSON", "ria", "person"), ("PLACE", "Mumbai", "PLACE", "mumbai", "place"),
        ("ANIMAL", "Tiger", "ANIMAL", "tiger", "animal"), ("THING", "Pencil", "THING", "pencil", "thing")]

BLUR = '{opacity: 0, y: 24, filter: "blur(10px)"}, {opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out", stagger: %s}'
POP = '{opacity: 0, scale: 0.4}, {opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)"}'


def words(text, hl=None):
    out = []
    for w in text.split():
        core = w.strip(".,?!")
        if hl and core.lower() == hl.lower():
            out.append(f'<span class="w"><span class="hl">{core}</span>{w[len(core):]}</span>')
        else:
            out.append(f'<span class="w">{w}</span>')
    return " ".join(out)


def clip(id_, start, end, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{start:.3f}" data-duration="{max(0.05, end - start):.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


def build(version, res=2160):
    segs = L.edl(version)
    order = L.VERSIONS[version]
    cut = SP.cutaways(version)  # {line id: (start, end)} picture is a scene there
    dur = segs[-1]["end"] + SP.TAIL.get(version, 0.0)
    span = {lid: L.span(version, lid) for lid in order}
    W = lambda lid, w, n=0: L.word_t(version, lid, w, n)  # noqa: E731
    els, js = [], []

    # ---------------------------------------------------------------- hook C (shortest): text hook from frame 1
    if version == "v4_shortest":
        s, e = span["npat"]
        els.append(clip("hookc", 0.0, e + 0.1, 8, '<div class="hc" id="hc">Bachpan ka <em>YE</em> game =<br>poori <em>NOUN</em> grammar 🤯</div>'))
        js.append('tl.fromTo("#hc", {opacity: 1, scale: 1.06}, {opacity: 1, scale: 1, duration: 0.35, ease: "power3.out"}, 0);  // frame 1 fully readable (it is the hook)')
        for j, (head, *_r) in enumerate(COLS):
            t = W("npat", head.lower())
            els.append(clip(f"hw{j}", t, e + 0.1, 7, f'<div class="hw" style="top:{560 + j * 70}px">{head}</div>'))
            js.append(f'tl.fromTo("#hw{j} .hw", {{opacity: 0, x: {-120 if j % 2 else 120}, scale: 1.4}}, '
                      f'{{opacity: 1, x: 0, scale: 1, duration: 0.25, ease: "power3.out"}}, {t});')

    # ---------------------------------------------------------------- hook A: "Ratta? No!"
    if "def" in order:
        s, e = span["def"]
        t_nahi, t_yaad = W("def", "nahi"), W("def", "yaad")
        e = e + 0.6  # hold the hook a beat into the next line
        els.append(clip("hook", s, e, 1, """
          <div class="def" id="dc">“A noun is a word used to identify any of a class of people, places, or things...”</div>
          <div class="slash" id="sl"></div><div class="nope" id="np">RATTA? NO!</div>
          <div class="h1" id="h1"><span class="l1">Noun ki definition</span><br><em class="l2">yaad mat karo</em></div>"""))
        js.append(f"""
          tl.fromTo("#h1 .l1", {{opacity: 0, y: -40, scale: 1.3}}, {{opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "power3.out"}}, {s + 0.02});
          tl.fromTo("#dc", {{opacity: 0, y: 40, rotation: 2}}, {{opacity: 1, y: 0, rotation: -3, duration: 0.4, ease: "power3.out"}}, {s + 0.35});
          tl.fromTo("#sl", {{scaleX: 0, transformOrigin: "0% 50%"}}, {{scaleX: 1, duration: 0.18, ease: "power2.in"}}, {t_nahi - 0.05});
          tl.fromTo("#np", {{opacity: 0, scale: 2.2, rotation: 25}}, {{opacity: 1, scale: 1, rotation: 10, duration: 0.22, ease: "power3.in"}}, {t_nahi + 0.1});
          tl.fromTo("#h1 .l2", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)"}}, {t_yaad});
          tl.fromTo("#hook .layer", {{x: 0}}, {{x: 10, duration: 0.04, yoyo: true, repeat: 5, ease: "none"}}, {t_nahi + 0.3});
          tl.to("#hook .layer > *", {{opacity: 0, duration: 0.15}}, {e - 0.15});""")

    # ---------------------------------------------------------------- bachpan
    if "bachpan" in order and "bachpan" not in cut:
        s, e = span["bachpan"]
        s0 = s
        s = s + (0.6 if "def" in order and order.index("def") + 1 == order.index("bachpan") else 0)
        els.append(clip("bp", s, e, 3, '<div class="hand" id="bpt">Bas bachpan ka <b>favourite game</b><br>yaad karo 🎮</div>'))
        js.append(f'tl.fromTo("#bpt", {{opacity: 0, y: 24, rotation: -2}}, {{opacity: 1, y: 0, rotation: -2, duration: 0.35, ease: "power3.out"}}, {s + 0.05});'
                  f'tl.fromTo("#bpt b", {{color: "#FFFFFF"}}, {{color: "#FFC94A", duration: 0.2}}, {W("bachpan", "favourite")});'
                  f'tl.to("#bpt", {{opacity: 0, duration: 0.15}}, {e - 0.15});')

    # ---------------------------------------------------------------- notebook runs
    runs, cur = [], []
    for lid in order:
        if lid in NB_LINES and not (version == "v4_shortest" and lid == "npat"):
            cur.append(lid)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    seen = set()
    for r, run in enumerate(runs):
        s, e = span[run[0]][0], span[run[-1]][1]
        cid = f"nb{r}"
        cols = "".join(f'<div class="col"><div class="hd" id="{cid}h{j}">{h}</div><div class="en" id="{cid}e{j}">{en}</div>'
                       f'<div class="tag" id="{cid}t{j}">{tg}</div></div>' for j, (h, en, tg, _, _) in enumerate(COLS))
        els.append(clip(cid, s, e, 2, f'<div class="nb" id="{cid}n"><div class="margin"></div><div class="cols">{cols}</div></div>'
                                       f'<div class="eq" id="{cid}q"></div>'))
        js.append(f'tl.fromTo("#{cid}n", {{opacity: 0, y: -60, rotation: -4, scale: 0.9}}, {{opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.4, ease: "back.out(1.7)"}}, {s});')
        # headers
        if "npat" in run:
            for j, (h, *_r) in enumerate(COLS):
                js.append(f'tl.fromTo("#{cid}h{j}", {POP}, {W("npat", h.lower())});')
        else:
            js.append(f'tl.fromTo("#{cid} .hd", {POP.replace("duration: 0.4", "duration: 0.3")}, {s + 0.1});')
        # entries
        if "answers" in run:
            for j, (*_x, key, _t) in enumerate(COLS):
                t = W("answers", key)
                js.append(f'tl.fromTo("#{cid}e{j}", {{opacity: 0, scale: 1.5, rotation: -8}}, {{opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "power3.out"}}, {t});')
            seen.add("answers")
        elif "answers" in seen:
            js.append(f'tl.set("#{cid} .en", {{opacity: 1}}, {s});')
        else:
            js.append(f'tl.set("#{cid} .en", {{opacity: 0}}, {s});')
        # tags (PERSON / PLACE / ...)
        tag_line = "notice" if "notice" in run else ("rule" if "rule" in run and "tags" not in seen else None)
        if tag_line:
            for j, (*_x, word) in enumerate(COLS):
                t = W(tag_line, word)
                js.append(f'tl.fromTo("#{cid}t{j}", {POP}, {t});')
            seen.add("tags")
        elif "tags" in seen:
            js.append(f'tl.set("#{cid} .tag", {{opacity: 1}}, {s});')
        else:
            js.append(f'tl.set("#{cid} .tag", {{opacity: 0}}, {s});')
        if "concept" in run:
            t0, t1 = span["concept"]
            js.append(f'tl.call(() => document.querySelector("#{cid}q").innerHTML = "= Noun ka <b>poora concept</b> ✨", null, {t0});'
                      f'tl.fromTo("#{cid}q", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3}}, {t0 + 0.05});'
                      f'tl.to("#{cid}q", {{opacity: 0, duration: 0.15}}, {t1 - 0.15});')
        if "rule" in run:
            t0, t1 = span["rule"]
            js.append(f'tl.call(() => document.querySelector("#{cid}q").innerHTML = "Inka <b>NAAM</b> = <b>NOUN</b> ✏️", null, {t0});'
                      f'tl.fromTo("#{cid}q", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3}}, {W("rule", "noun")});'
                      f'tl.to("#{cid} .en", {{scale: 1.12, color: "#E8475A", duration: 0.2, yoyo: true, repeat: 1, stagger: 0.08}}, {W("rule", "noun")});')
        js.append(f'tl.to("#{cid} .layer > *", {{opacity: 0, y: -20, duration: 0.2}}, {e - 0.2});')

    # ---------------------------------------------------------------- naming word
    if "naming" in order and "naming" not in cut:
        s, e = span["naming"]
        els.append(clip("nm", s, e + (SP.TAIL.get(version, 0.0) if order[-1] == "naming" else 0), 3,
                        '<div class="big" id="nmt">NOUN =<br><em>NAMING WORD</em></div><div class="tagicon" id="nmi">🏷️</div>'))
        js.append(f'tl.fromTo("#nmt", {{opacity: 0, scale: 1.4}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "power3.out"}}, {W("naming", "noun")});'
                  f'tl.fromTo("#nmi", {{opacity: 0, rotation: -60, scale: 0.3}}, {{opacity: 1, rotation: 12, scale: 1, duration: 0.45, ease: "back.out(2.5)"}}, {W("naming", "naming")});'
                  f'tl.to("#nmi", {{rotation: -8, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {W("naming", "naming") + 0.45});')

    # ---------------------------------------------------------------- sentences intro
    if "sent_in" in order:
        s, e = span["sent_in"]
        els.append(clip("si", s, e, 3, '<div class="chipbig" id="sit">Ab <b>SENTENCES</b> ✍️</div>'))
        js.append(f'tl.fromTo("#sit", {POP}, {s + 0.05});tl.to("#sit", {{opacity: 0, duration: 0.15}}, {e - 0.15});')

    # ---------------------------------------------------------------- examples
    for k, (sl, why, noun, hi, en, label, reason) in enumerate(EXAMPLES):
        if sl not in order:
            continue
        s = span[sl][0]
        e = span[[w for w in why if w in order][-1]][1]
        cid = f"ex{k}"
        hi_html = words(hi, noun)
        els.append(clip(cid, s, e, 4, f"""
          <div class="chip" id="{cid}c">EXAMPLE {k + 1}/4</div>
          <div class="lab" id="{cid}l">{label}</div>
          <div class="sb"><div class="s2" id="{cid}s">{hi_html}</div>
          {f'<div class="eng2" id="{cid}g">{html.escape(en)}</div>' if en else ''}</div>
          <div class="why" id="{cid}y">{reason}</div>"""))
        t_noun = W(sl, noun.lower())
        if sl in cut:  # the scene carried the sentence: on the cut back everything is already there
            js.append(f'tl.set("#{cid}c, #{cid}s .w, #{cid}g", {{opacity: 1}}, {s});'
                      f'tl.call(() => document.querySelector("#{cid}s .hl").classList.add("on"), null, {s});')
        else:
            js.append(f'tl.fromTo("#{cid}c", {POP}, {s + 0.02});'
                      f'tl.fromTo("#{cid}s .w", {BLUR % "0.06"}, {s + 0.08});'
                      f'tl.call(() => document.querySelector("#{cid}s .hl").classList.add("on"), null, {t_noun});'
                      f'tl.fromTo("#{cid}s .hl", {{scale: 1}}, {{scale: 1.1, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out"}}, {t_noun});')
            if en:
                js.append(f'tl.fromTo("#{cid}g", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {t_noun + 0.3});')
        first_why = [w for w in why if w in order][0]
        noun_lines = [w for w in why if w in order and w != "ex2_ask"]
        t_lab = W(noun_lines[0], "noun")
        js.append(f'tl.fromTo("#{cid}l", {{opacity: 0, scale: 0.4, rotation: -12}}, {{opacity: 1, scale: 1, rotation: -4, duration: 0.4, ease: "back.out(2.6)"}}, {t_lab});')
        reason_line = noun_lines[-1]
        t_why = W(reason_line, "becau") if reason_line == "ex4_why" else W(reason_line, "ky")
        js.append(f'tl.fromTo("#{cid}y", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.35, ease: "power3.out"}}, {t_why});')
        if "ex2_ask" in why and "ex2_ask" in order:
            a0, a1 = span["ex2_ask"]
            els.append(clip("ask", a0, a1 + 0.1, 6, '<div class="ask" id="askt">Bataiye <b>kyun?</b> 🤔</div>'))
            js.append(f'tl.fromTo("#askt", {{opacity: 0, scale: 0.3, rotation: -10}}, {{opacity: 1, scale: 1, rotation: -4, duration: 0.3, ease: "back.out(3)"}}, {a0});')
        js.append(f'tl.to("#{cid} .layer > *", {{opacity: 0, duration: 0.15}}, {e - 0.15});')

    # ---------------------------------------------------------------- types
    if "clear" in order:
        s, e = span["clear"]
        els.append(clip("cl", s, e, 3, '<div class="hand" id="clt">Concept <b>clear?</b> ✅</div>'))
        js.append(f'tl.fromTo("#clt", {POP}, {W("clear", "concept")});tl.to("#clt", {{opacity: 0, duration: 0.15}}, {e - 0.15});')
    if "types" in order:
        s, e = span["types"]
        els.append(clip("ty", s, e, 3, '<div class="tt" id="tyt">NOUN ke <em>2 TYPES</em></div>'
                                       '<div class="pills"><div class="pl pr" id="typ">PROPER noun</div><div class="pl co" id="tyc">COMMON noun</div></div>'))
        js.append(f'tl.fromTo("#tyt", {POP}, {W("types", "types")});'
                  f'tl.fromTo("#typ", {{opacity: 0, x: -80}}, {{opacity: 1, x: 0, duration: 0.35, ease: "back.out(2)"}}, {W("types", "special")});'
                  f'tl.fromTo("#tyc", {{opacity: 0, x: 80}}, {{opacity: 1, x: 0, duration: 0.35, ease: "back.out(2)"}}, {W("types", "common")});'
                  f'tl.to("#ty .layer > *", {{opacity: 0, duration: 0.15}}, {e - 0.15});')
    if "type_ex" in order:
        s, e = span["type_ex"]
        els.append(clip("te", s, e, 3, """
          <div class="s" id="tes">My <span class="hl co2" id="tef">friend</span> is <span class="hl" id="ter">Ria.</span></div>
          <div class="tagrow"><div class="pl pr" id="tep">Ria → PROPER</div><div class="pl co" id="tec">friend → COMMON</div></div>"""))
        t0 = s if "type_ex" not in cut else SP.cut_end(version, "type_ex")
        js.append(f'tl.fromTo("#tes", {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: 0.3}}, {t0});'
                  f'tl.fromTo("#tep", {POP}, {W("type_ex", "special")});tl.call(() => document.querySelector("#ter").classList.add("on"), null, {W("type_ex", "special")});tl.fromTo("#ter", {{scale: 1}}, {{scale: 1.12, duration: 0.2, yoyo: true, repeat: 1}}, {W("type_ex", "special")});'
                  f'tl.fromTo("#tec", {POP}, {W("type_ex", "common")});tl.to("#tef", {{backgroundColor: "rgba(207,234,223,1)", color: "#17423C", textShadow: "none", duration: 0.25}}, {W("type_ex", "common")});'
                  f'tl.to("#te .layer > *", {{opacity: 0, duration: 0.15}}, {e - 0.15});')

    # ---------------------------------------------------------------- part 2 / follow CTA
    if "part2" in order:
        s = span["part2"][0]
        e = span["part2_b"][1] if "part2_b" in order else span["part2"][1]
        if order[-1] in ("part2", "part2_b"):
            e = dur  # keep the card up through the end hold
        if "part2" in cut:
            s = SP.cut_end(version, "part2")
        els.append(clip("p2", s, e, 5, """
          <div class="p2card" id="p2c"><div class="p2k">PART 2 👉</div><div class="p2t">Proper vs Common Noun</div></div>
          <div class="follow" id="p2f">Follow karo 🔔 taaki miss na ho</div>"""))
        js.append(f'tl.fromTo("#p2c", {{opacity: 0, y: -40, scale: 0.9}}, {{opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(2)"}}, {s + 0.05});'
                  f'tl.fromTo("#p2f", {POP}, {s + 0.6});tl.to("#p2f", {{scale: 1.06, duration: 0.3, yoyo: true, repeat: 7, ease: "sine.inOut"}}, {s + 1.1});')
    out = HERE / "overlay" / version
    (out / "vendor").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    shutil.copy(L.ROOT / "node_modules/gsap/dist/gsap.min.js", out / "vendor/gsap.min.js")
    for f in (HERE / "board" / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "fonts" / f.name)
    (out / "hyperframes.json").write_text('{"name":"manisha8-overlay-%s"}\n' % version)
    page = TEMPLATE.replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "\n".join(js))
    (out / "index.html").write_text(page)
    json.dump({"duration": dur}, open(out / "meta.json", "w"))
    print(out / "index.html", f"{len(els)} clips, {dur:.2f}s")


TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: Anton; src: url(fonts/anton.woff2); }
@font-face { font-family: Brico; src: url(fonts/brico800.woff2); font-weight: 800; }
@font-face { font-family: Cav; src: url(fonts/caveat700.woff2); font-weight: 700; }
@font-face { font-family: PJS; src: url(fonts/pjs800.woff2); font-weight: 800; }
:root { --teal: #17423C; --mint: #CFEADF; --paper: #FFF9EE; --pen: #FFC94A; --red: #E8475A; --ink: #23324A;
  --sh: 0 2px 3px rgba(0,0,0,.45), 0 8px 26px rgba(0,0,0,.45); }
html, body { margin: 0; background: transparent; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; }
.clip { position: absolute; inset: 0; } .layer { position: absolute; inset: 0; }
.layer > div { position: absolute; }
.w { display: inline-block; }
/* hook A */
.h1 { left: 0; top: 290px; width: 1080px; text-align: center; font: 400 104px/1.02 Anton; color: #fff; text-shadow: var(--sh); text-transform: uppercase; }
.h1 span, .h1 em { display: inline-block; } .h1 em { font-style: normal; color: var(--pen); }
.def { left: 150px; top: 590px; width: 780px; padding: 24px 30px; border-radius: 18px; background: rgba(255,249,238,.95); transform: rotate(-3deg);
  font: 800 32px/1.25 Brico; color: #6B6B6B; box-shadow: 0 16px 34px rgba(0,0,0,.3); }
.slash { left: 130px; top: 670px; width: 820px; height: 14px; border-radius: 7px; background: var(--red); transform: rotate(-9deg); }
.nope { left: 680px; top: 540px; padding: 8px 20px; border-radius: 14px; border: 6px solid var(--red); color: var(--red); font: 400 54px/1 Anton;
  transform: rotate(10deg); background: rgba(255,249,238,.95); }
/* hook C */
.hc { left: 0; top: 280px; width: 1080px; text-align: center; font: 400 92px/1.05 Anton; color: #fff; text-shadow: var(--sh); text-transform: uppercase; }
.hc em { font-style: normal; color: var(--pen); }
.hw { left: 0; width: 1080px; text-align: center; font: 800 58px/1 PJS; letter-spacing: 6px; color: var(--teal); }
.hw { -webkit-text-stroke: 0; text-shadow: 0 0 0 transparent; }
.hw { color: #fff; text-shadow: var(--sh); }
/* handwriting lines */
.hand { left: 0; top: 380px; width: 1080px; text-align: center; font: 700 82px/1.1 Cav; color: #fff; text-shadow: var(--sh); }
.hand b { color: var(--pen); font-weight: 700; }
/* notebook */
.nb { left: 110px; top: 270px; width: 860px; height: 470px; border-radius: 22px; background: var(--paper); box-shadow: 0 20px 44px rgba(0,0,0,.32); overflow: hidden;
  background-image: repeating-linear-gradient(180deg, transparent 0 69px, #CFE0EE 69px 72px); }
.margin { position: absolute; left: 70px; top: 0; width: 4px; height: 470px; background: var(--red); opacity: .7; }
.cols { position: absolute; left: 74px; top: 0; width: 786px; height: 470px; display: grid; grid-template-columns: repeat(4, 1fr); }
.col { border-left: 3px solid #B8C9D8; } .col:first-child { border-left: none; }
.hd { height: 96px; display: flex; align-items: center; justify-content: center; font: 800 32px/1 PJS; letter-spacing: 1px; color: var(--teal);
  background: var(--mint); border-bottom: 4px solid var(--teal); }
.en { height: 150px; display: flex; align-items: center; justify-content: center; font: 700 64px/1 Cav; color: var(--ink); }
.tag { margin: 22px auto 0; width: 150px; padding: 10px 0; border-radius: 30px; background: var(--teal); color: var(--pen); text-align: center;
  font: 800 26px/1 PJS; letter-spacing: 2px; }
.eq { left: 0; top: 770px; width: 1080px; text-align: center; font: 800 56px/1 Brico; color: #fff; text-shadow: var(--sh); }
.eq b { color: var(--pen); }
/* naming word */
.big { left: 0; top: 330px; width: 1080px; text-align: center; font: 400 120px/1.02 Anton; color: #fff; text-shadow: var(--sh); }
.big em { font-style: normal; color: var(--pen); }
.tagicon { left: 760px; top: 260px; font: 120px/1 sans-serif; transform-origin: 30% 10%; }
.chipbig { left: 0; top: 420px; width: 1080px; text-align: center; }
.chipbig, .chip, .lab { font: 800 34px/1 PJS; letter-spacing: 2px; }
#sit { display: inline-block; left: 310px; width: auto; padding: 18px 34px; border-radius: 40px; background: var(--teal); color: var(--mint); font-size: 48px; }
#sit b { color: var(--pen); }
/* examples */
.chip { left: 120px; top: 280px; padding: 12px 22px; border-radius: 30px; background: var(--teal); color: var(--mint); font-size: 28px; }
.lab { left: 560px; top: 370px; padding: 12px 22px; border-radius: 30px; background: var(--pen); color: var(--teal); box-shadow: 0 10px 24px rgba(0,0,0,.3); }
.s { left: 40px; top: 470px; width: 1000px; text-align: center; font: 800 70px/1.15 Brico; color: #fff; text-shadow: var(--sh); }
.hl { display: inline-block; color: #fff; padding: 0 14px; border-radius: 16px; background: rgba(255,201,74,0); text-shadow: var(--sh); }
.hl.on { color: var(--ink); background: rgba(255,201,74,1); text-shadow: none; }
.co2 { color: #fff; text-shadow: var(--sh); }
.sb { left: 40px; top: 460px; width: 1000px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.s2 { width: 1000px; text-align: center; font: 800 64px/1.12 Brico; color: #fff; text-shadow: var(--sh); }
.eng2 { font: 800 36px/1 PJS; color: var(--mint); text-shadow: var(--sh); letter-spacing: 1px; }
.eng { left: 0; top: 570px; width: 1080px; text-align: center; font: 800 38px/1 PJS; color: var(--mint); text-shadow: var(--sh); letter-spacing: 1px; }
.why { left: 0; top: 660px; width: 1080px; text-align: center; font: 700 64px/1 Cav; color: #fff; text-shadow: var(--sh); }
.why b { color: var(--pen); font-weight: 700; }
.ask { left: 0; top: 740px; width: 1080px; text-align: center; font: 700 96px/1 Cav; color: #fff; text-shadow: var(--sh); }
.ask b { color: var(--pen); font-weight: 700; }
/* types */
.tt { left: 0; top: 330px; width: 1080px; text-align: center; font: 400 110px/1 Anton; color: #fff; text-shadow: var(--sh); text-transform: uppercase; }
.tt em { font-style: normal; color: var(--pen); }
.pills, .tagrow { left: 120px; top: 500px; width: 840px; display: flex; justify-content: center; gap: 30px; }
.tagrow { top: 600px; }
.pl { padding: 18px 30px; border-radius: 40px; font: 800 40px/1 PJS; box-shadow: 0 12px 26px rgba(0,0,0,.3); }
.pr { background: var(--pen); color: var(--teal); } .co { background: var(--mint); color: var(--teal); }
#tes { top: 440px; }
/* part 2 */
.p2card { left: 160px; top: 320px; width: 760px; padding: 34px; border-radius: 36px; background: var(--teal); text-align: center; box-shadow: 0 20px 44px rgba(0,0,0,.35); }
.p2k { font: 400 96px/1 Anton; color: var(--pen); } .p2t { margin-top: 16px; font: 800 48px/1.1 Brico; color: var(--paper); }
.follow { left: 0; top: 640px; width: 1080px; text-align: center; font: 700 70px/1 Cav; color: #fff; text-shadow: var(--sh); }
.follow b { color: var(--pen); font-weight: 700; } .follow.end { top: 700px; }
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
    build(sys.argv[1])
