"""Caption layers for Manisha 9 ("being: 3 uses"), two versions from the two style boards (user, 22 Nov: "give me both").

  a  "Gold Tabs" (board/):  big gold Playfair "being", three numbered tabs, ivory example cards on the wall above her
     head with the being-phrase on a gold pill, Hinglish meaning under it, formula chip, gold light sweeps.
  b  "Explainer Panel" (board_b/, from the user's reference reel): top progress bar (NO series title, user), one dark
     glass panel at chest height with concept widgets (branches, toggles, ID card, progress bar, stamp), the English
     sentence lighting word by word in yellow, a subtitle pill under the panel; recap + comment panel at the end
     (her picture blurs there, done in build.py).
Rendered natively at 2160x3840 (1080x1920 stage scaled 2x).

Usage: python3 -I overlay.py a|b   -> overlay/<v>/index.html
"""

import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cut as C  # noqa: E402
from keys import K  # noqa: E402


def t(key, d=0.0):
    tk, s = K[key]
    return round(C.T(tk, s) + d, 3)


SEC = {n: (C.take_start(tk), C.take_end(tk)) for n, tk in (("hook", 1), ("u1", 2), ("u2", 3), ("u3", 4), ("recap", 5), ("cta", 6))}
SEC["cta"] = (SEC["cta"][0], C.duration())
BLURIN = '{opacity: 0, y: 18, filter: "blur(10px)"}, {opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out"}'
POP = '{opacity: 0, scale: 0.4}, {opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)"}'


def clip(id_, s, e, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{s:.3f}" data-duration="{max(0.05, e - s):.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


def sweep(js, els, n, at, color):
    """Light sweep transition: a soft coloured band crossing the frame diagonally."""
    els.append(clip(f"sw{n}", at - 0.2, at + 0.45, 20, f'<div class="sweep" id="swb{n}" style="--c:{color}"></div>'))
    js.append(f'tl.fromTo("#swb{n}", {{x: -1500, opacity: 0.9}}, {{x: 1500, opacity: 0.9, duration: 0.55, ease: "power2.inOut"}}, {at - 0.18});')


def exit_(js, sel, e):
    js.append(f'tl.to("{sel}", {{opacity: 0, y: -10, duration: 0.16, ease: "power2.in"}}, {e - 0.17});')


# ====================================================================================================== version A
def build_a():
    els, js = [], []
    # ---------- hook
    s, e = SEC["hook"]
    els.append(clip("hk", 0, e, 1, """
      <div class="hk"><span class="big" id="hb">being</span><span id="h2" class="w">ke</span> <span id="h3" class="w gold">3</span> <span id="h4" class="w">alag USES</span></div>
      <div class="tabs"><div class="tb" id="tb1"><b>1</b><i>🎭</i></div><div class="tb" id="tb2"><b>2</b><i>🪪</i></div><div class="tb" id="tb3"><b>3</b><i>🏗️</i></div></div>
      <div class="easy" id="ez">Trust me, very easy 😌</div>"""))
    js.append('tl.fromTo("#hb", {opacity: 1, scale: 1.12}, {opacity: 1, scale: 1, duration: 0.5, ease: "power3.out"}, 0);')
    js.append(f'tl.fromTo("#h2", {BLURIN}, {t("teen", -0.3)});tl.fromTo("#h3", {POP}, {t("teen")});tl.fromTo("#h4", {BLURIN}, {t("uses", -0.25)});')
    for i in range(3):
        js.append(f'tl.fromTo("#tb{i + 1}", {{opacity: 0, y: 40, scale: 0.7}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2)"}}, {t("uses", 0.15 + 0.18 * i)});')
    js.append(f'tl.fromTo("#ez", {BLURIN}, {t("trust")});')
    exit_(js, "#hk .layer > div", e)
    # ---------- three uses
    uses = [
        ("u1", 1, "BEHAVIOUR", "🎭", "Jab koi <b>alag behave</b> kare", "u1_jab",
         [("You", "u1_you"), ("are", "u1_are"), ("[being", "u1_being"), ("rude]", "u1_rude"), ("today.", "u1_today")],
         "= Aaj tum thoda <b>rude behave</b> kar rahe ho", "u1_matlab", None),
        ("u2", 2, "PEHCHAAN", "🪪", "Jab apni <b>pehchaan</b> batani ho", "u2_jab",
         [("[Being", "u2_Being"), ("a", "u2_a"), ("teacher,]", "u2_teacher"), ("I", "u2_I"), ("understand", "u2_understand"),
          ("my", "u2_my"), ("students", "u2_students"), ("very", "u2_very"), ("well.", "u2_well")],
         "= <b>Teacher hone ke naate</b>, main bachchon ko<br>bahut achhe se samajhti hoon", "u2_iska", None),
        ("u3", 3, "KAAM HO RAHA HAI", "🏗️", "Jab kisi <b>kaam ke hone</b> ki baat ho", "u3_jab",
         [("The", "u3_the"), ("house", "u3_house"), ("is", "u3_is"), ("[being", "u3_being"), ("painted.]", "u3_painted")],
         "= Ghar ko <b>paint kiya ja raha hai</b>", "u3_iska", "is / are + being + V3"),
    ]
    for n, (sid, k, name, icon, rule, rule_k, words, hi, hi_k, pat) in enumerate(uses):
        s, e = SEC[sid]
        sweep(js, els, n, s, "rgba(255,182,39,.55)")
        sen, inpill, wid = [], False, 0
        for j, (w, key) in enumerate(words):
            if w.startswith("["):
                sen.append('<span class="hl" id="%shl">' % sid)
                inpill = True
                w = w[1:]
            end = w.endswith("]")
            w = w.rstrip("]")
            core = '<span class="being">being</span>' if w.lower() == "being" else w
            if w == "Being":
                core = '<span class="being">Being</span>'
            sen.append(f'<span class="w" id="{sid}w{j}">{core}</span>')
            if end:
                sen.append("</span>")
                inpill = False
        sent = " ".join(sen).replace('<span class="hl" id="%shl"> ' % sid, '<span class="hl" id="%shl">' % sid).replace(" </span>", "</span>")
        small = {"u2": " sm", "u3": " sm3"}.get(sid, "")
        els.append(clip(sid, s, e, 2, f"""
          <div class="chip" id="{sid}c">USE {k}/3 · {name}</div><div class="icon" id="{sid}i">{icon}</div>
          <div class="rule" id="{sid}r">{rule}</div>
          <div class="card{small}" id="{sid}k"><div class="en">{sent}</div><div class="hi" id="{sid}h">{hi}</div></div>
          {f'<div class="pat" id="{sid}p"><span>{pat}</span></div>' if pat else ''}"""))
        js.append(f'tl.fromTo("#{sid}c", {{opacity: 0, x: -60}}, {{opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}}, {s + 0.05});')
        js.append(f'tl.fromTo("#{sid}i", {{opacity: 0, scale: 0.3, rotation: -20}}, {{opacity: 1, scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2.6)"}}, {s + 0.2});')
        js.append(f'tl.fromTo("#{sid}r", {BLURIN}, {t(rule_k, -0.1)});')
        t0 = t(words[0][1], -0.25)
        js.append(f'tl.fromTo("#{sid}k", {{opacity: 0, y: 30, scale: 0.94}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.8)"}}, {t0});')
        for j, (w, key) in enumerate(words):
            js.append(f'tl.fromTo("#{sid}w{j}", {{opacity: 0, y: 14, filter: "blur(8px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.25, ease: "power3.out"}}, {t(key, -0.08)});')
        first_pill = next(key for w, key in words if w.endswith("]"))  # light the pill once the whole phrase is said
        js.append(f'tl.fromTo("#{sid}hl", {{backgroundColor: "rgba(255,182,39,0)"}}, {{backgroundColor: "rgba(255,182,39,1)", duration: 0.25}}, {t(first_pill)});')
        js.append(f'tl.fromTo("#{sid}hl .being", {{color: "#FFB627"}}, {{color: "#1E1B24", duration: 0.25}}, {t(first_pill)});')
        js.append(f'tl.fromTo("#{sid}h", {BLURIN}, {t(hi_k, -0.05)});')
        if pat:
            js.append(f'tl.fromTo("#{sid}p span", {POP}, {t("u3_painted", 0.6)});')
        exit_(js, f"#{sid} .layer > div", e)
    # ---------- recap
    s, e = SEC["recap"]
    sweep(js, els, 3, s, "rgba(255,182,39,.55)")
    els.append(clip("rc", s, e, 3, """
      <div class="rch"><span class="being">being</span> ke 3 uses</div>
      <div class="tabs rt"><div class="tb wide" id="rt1"><b>1</b><i>🎭</i><u>Behaviour</u></div><div class="tb wide" id="rt2"><b>2</b><i>🪪</i><u>Pehchaan</u></div><div class="tb wide" id="rt3"><b>3</b><i>🏗️</i><u>Kaam ho raha</u></div></div>
      <div class="easy rce" id="rcl">Clarity mil gayi? ✅</div>"""))
    js.append(f'tl.fromTo("#rc .rch", {BLURIN}, {s + 0.05});')
    for i in range(3):
        js.append(f'tl.fromTo("#rt{i + 1}", {{opacity: 0, y: 40, scale: 0.7}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2)"}}, {s + 0.3 + 0.2 * i});')
    js.append(f'tl.fromTo("#rcl", {BLURIN}, {t("r_clarity", -0.1)});')
    exit_(js, "#rc .layer > div", e)
    # ---------- CTA
    s, e = SEC["cta"]
    sweep(js, els, 4, s, "rgba(255,107,107,.45)")
    els.append(clip("ct", s, e, 4, """
      <div class="cq" id="cq">Kaunsa English word<br><em>confuse</em> karta hai? 🤔</div>
      <div class="box" id="bx">💬<b id="bxt">Comment karo...</b><span class="caret" id="cr"></span></div><div class="send" id="sd">➤</div>
      <div class="nxt" id="nx">Next video mein uska explanation 👀</div>"""))
    js.append(f'tl.fromTo("#cq", {BLURIN}, {t("c_confusing", -0.35)});')
    js.append(f'tl.fromTo("#bx", {{opacity: 0, y: 30, scale: 0.9}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2)"}}, {t("c_comment", -0.15)});')
    js.append(f'tl.fromTo("#sd", {POP}, {t("c_comment", 0.15)});')
    js.append(f'tl.to("#sd", {{scale: 1.15, duration: 0.3, yoyo: true, repeat: 9, ease: "sine.inOut"}}, {t("c_comment", 0.6)});')
    js.append(f'tl.fromTo("#cr", {{opacity: 1}}, {{opacity: 0, duration: 0.3, yoyo: true, repeat: 21, ease: "steps(1)"}}, {t("c_comment")});')
    js.append(f'tl.fromTo("#nx", {BLURIN}, {t("c_next", -0.1)});')
    return els, js, TPL_A


# ====================================================================================================== version B
def build_b():
    els, js = [], []
    dur = C.duration()
    # ---------- top progress bar (persistent, no series title)
    labels = [("hook", "BEING · 3 USES"), ("u1", "USE 1 / 3"), ("u2", "USE 2 / 3"), ("u3", "USE 3 / 3"), ("recap", "RECAP"), ("cta", "COMMENT 👇")]
    lab = "".join(f'<div class="d" id="bl{i}">{x}</div>' for i, (_, x) in enumerate(labels))
    els.append(clip("bar", 0, dur, 1, f'<div class="bar">{lab}<div class="seg"><i><b id="sg1"></b></i><i><b id="sg2"></b></i><i><b id="sg3"></b></i></div></div>'))
    for i, (sid, _) in enumerate(labels[1:], 1):
        s = SEC[sid][0]
        js.append(f'tl.to("#bl{i - 1}", {{opacity: 0, y: -8, duration: 0.15}}, {s - 0.1});'
                  f'tl.fromTo("#bl{i}", {{opacity: 0, y: 8}}, {{opacity: 1, y: 0, duration: 0.25}}, {s + 0.05});')
        if i <= 3:
            js.append(f'tl.to("#sg{i}", {{scaleX: 1, duration: 0.5, ease: "power2.out"}}, {s + 0.1});')
    # ---------- panel background (persistent; its size eases between sections)
    els.append(clip("pan", 0, dur, 2, '<div class="pan" id="pb"></div>'))
    js.append(f'tl.to("#pb", {{top: 1100, height: 300, duration: 0.35, ease: "power3.inOut"}}, {SEC["recap"][0] - 0.05});')
    js.append(f'tl.to("#pb", {{top: 1045, height: 445, duration: 0.35, ease: "power3.inOut"}}, {SEC["cta"][0] + 0.05});')

    def sub(id_, s, e, html, first=False):
        els.append(clip(id_, s, e, 9, f'<div class="sub"><span id="{id_}s">{html}</span></div>'))
        if not first:
            js.append(f'tl.fromTo("#{id_}s", {{opacity: 0, y: 14, scale: 0.96}}, {{opacity: 1, y: 0, scale: 1, duration: 0.22, ease: "power3.out"}}, {s});')
        js.append(f'tl.to("#{id_}s", {{opacity: 0, duration: 0.12}}, {e - 0.12});')

    def content(id_, s, e, inner, first=False):
        els.append(clip(id_, s, e, 3, f'<div class="pc" id="{id_}p">{inner}</div>'))
        if not first:
            js.append(f'tl.fromTo("#{id_}p", {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}}, {s + 0.02});')
        js.append(f'tl.to("#{id_}p", {{opacity: 0, y: -14, duration: 0.15, ease: "power2.in"}}, {e - 0.16});')

    def sentence(id_, words, top, size=56):
        spans = []
        for j, (w, key, cls) in enumerate(words):
            br = w.endswith("<br>")
            w = w.replace("<br>", "")
            spans.append(f'<span class="w {cls}" id="{id_}w{j}">{w}</span>' + ("<br>" if br else ""))
        return f'<div class="sen" style="top:{top}px;font-size:{size}px">{" ".join(spans)}</div>'

    def light(id_, words):
        for j, (w, key, cls) in enumerate(words):
            col = "#FFC83D" if "y" in cls.split() else "#FFFFFF"
            js.append(f'tl.fromTo("#{id_}w{j}", {{color: "rgba(255,255,255,0.32)"}}, {{color: "{col}", duration: 0.18}}, {t(key, -0.04)});')

    # ---------- hook
    s, e = SEC["hook"]
    content("bh", 0, e, """<div class="lab">1 word · 3 uses</div><div class="big" id="bhb">being</div>
      <svg width="900" height="370" style="left:0;top:0;stroke:#5AA9FF;stroke-width:4"><path id="br1" d="M350 180 L150 235"/><path id="br2" d="M450 185 L450 235"/><path id="br3" d="M550 180 L750 235"/></svg>
      <div class="node" id="nd1" style="left:125px;top:228px">1</div><div class="node" id="nd2" style="left:425px;top:228px">2</div><div class="node" id="nd3" style="left:725px;top:228px">3</div>
      <div class="nl" id="nl1" style="left:20px;top:295px">behave</div><div class="nl" id="nl2" style="left:320px;top:295px">pehchaan</div><div class="nl" id="nl3" style="left:620px;top:295px">kaam ho raha</div>""", first=True)
    js.append('tl.fromTo("#bhb", {scale: 1.15}, {scale: 1, duration: 0.5, ease: "power3.out"}, 0);')
    for i in range(3):
        at = t("teen", 0.05 + 0.12 * i)
        js.append(f'tl.fromTo("#br{i + 1}", {{strokeDasharray: 220, strokeDashoffset: 220}}, {{strokeDashoffset: 0, duration: 0.3, ease: "power2.out"}}, {at});')
        js.append(f'tl.fromTo("#nd{i + 1}", {POP}, {at + 0.2});')
        js.append(f'tl.fromTo("#nl{i + 1}", {BLURIN}, {t("uses", 0.1 + 0.15 * i)});')
    sub("bs0", 0, t("trust", -0.05), 'Being ke <span class="y">3 alag uses</span>', first=True)
    sub("bs1", t("trust", -0.05), e, 'Trust me, <span class="y">bahut simple</span> hai 😌')
    # ---------- use 1
    s, e = SEC["u1"]
    w1 = [("You", "u1_you", ""), ("are", "u1_are", ""), ('<span class="ring" id="rg">being</span>', "u1_being", "y"), ("rude", "u1_rude", "y"), ("today.", "u1_today", "")]
    content("b1", s, e, f"""<div class="lab">USE 1 · behave</div>
      <svg width="120" height="120" style="left:40px;top:84px" viewBox="0 0 120 120"><circle cx="60" cy="60" r="44"/><path d="M42 50 l10 4 M78 50 l-10 4"/><path d="M42 84 q18 -14 36 0"/></svg>
      <div class="row1" id="b1r1"><span class="tl m">usually</span><span class="tg" id="tg1"></span><span class="tl m">polite 🙂</span></div>
      <div class="row1" id="b1r2" style="top:158px"><span class="tl">aaj</span><span class="tg" id="tg2"><i></i></span><span class="tl y" id="b1rude">rude 😤</span></div>
      {sentence("b1", w1, 262)}""")
    js.append(f'tl.fromTo("#b1r1", {BLURIN}, {t("u1_jab")});tl.fromTo("#b1r2", {BLURIN}, {t("u1_alag")});tl.set("#b1rude", {{opacity: 0.3}}, {s});')
    js.append(f'tl.to("#tg2", {{backgroundColor: "#5AA9FF", duration: 0.2}}, {t("u1_rude")});tl.to("#tg2 i", {{x: 40, duration: 0.2, ease: "power2.out"}}, {t("u1_rude")});tl.to("#b1rude", {{opacity: 1, duration: 0.15}}, {t("u1_rude")});tl.fromTo("#b1rude", {{scale: 1}}, {{scale: 1.18, duration: 0.18, yoyo: true, repeat: 1}}, {t("u1_rude")});')
    light("b1", w1)
    js.append(f'tl.fromTo("#rg", {{outlineColor: "rgba(255,77,77,0)"}}, {{outlineColor: "rgba(255,77,77,1)", duration: 0.25}}, {t("u1_being", 0.1)});')
    sub("b1s0", s + 0.1, t("u1_you", -0.1), 'Jab koi <span class="y">alag behave</span> kare')
    sub("b1s1", t("u1_you", -0.1), t("u1_matlab", -0.05), 'For example 👇')
    sub("b1s2", t("u1_matlab", -0.05), e, '= Aaj tum thoda <span class="y">rude behave</span> kar rahe ho')
    # ---------- use 2
    s, e = SEC["u2"]
    w2 = [("Being", "u2_Being", "y"), ("a", "u2_a", "y"), ("teacher,", "u2_teacher", "y"), ("I", "u2_I", ""), ("understand", "u2_understand", ""),
          ("my", "u2_my", ""), ("students", "u2_students", ""), ("very", "u2_very", ""), ("well.", "u2_well", "")]
    content("b2", s, e, f"""<div class="lab">USE 2 · pehchaan</div>
      <svg width="120" height="120" style="left:40px;top:84px" viewBox="0 0 120 120"><rect x="14" y="22" width="92" height="76" rx="12"/><circle cx="42" cy="54" r="11"/><path d="M26 84 q16 -18 32 0"/><path d="M70 50 h24 M70 66 h18"/></svg>
      <div class="idc" id="b2id"><span class="m">I am</span> <span class="slot" id="b2slot"><span id="b2q">?</span><span id="b2a" class="y">a teacher</span></span> <span class="tick" id="b2tk">✓</span></div>
      {sentence("b2", w2, 200, 48)}""")
    js.append(f'tl.fromTo("#b2id", {BLURIN}, {t("u2_pehchaan")});')
    js.append(f'tl.set("#b2a", {{display: "none"}}, 0);tl.set("#b2q", {{display: "none"}}, {t("u2_teacher")});tl.set("#b2a", {{display: "inline"}}, {t("u2_teacher")});'
              f'tl.fromTo("#b2slot", {{borderColor: "rgba(255,255,255,.4)"}}, {{borderColor: "rgba(255,200,61,.9)", duration: 0.2}}, {t("u2_teacher")});'
              f'tl.fromTo("#b2slot", {{scale: 0.7}}, {{scale: 1, duration: 0.3, ease: "back.out(2.4)"}}, {t("u2_teacher")});'
              f'tl.fromTo("#b2tk", {POP}, {t("u2_teacher", 0.3)});')
    light("b2", w2)
    sub("b2s0", s + 0.1, t("u2_Being", -0.15), 'Jab apni <span class="y">pehchaan</span> batani ho')
    sub("b2s1", t("u2_Being", -0.15), t("u2_iska", -0.05), 'For example 👇')
    sub("b2s2", t("u2_iska", -0.05), e, '= <span class="y">Teacher hone ke naate</span>, main bachchon ko<br>bahut achhe se samajhti hoon')
    # ---------- use 3
    s, e = SEC["u3"]
    w3 = [("The", "u3_the", ""), ("house", "u3_house", ""), ("is", "u3_is", "y"), ("being", "u3_being", "y"), ("painted.", "u3_painted", "y")]
    content("b3", s, e, f"""<div class="lab">USE 3 · kaam ho raha hai</div>
      <svg width="130" height="120" style="left:40px;top:84px" viewBox="0 0 130 120"><path d="M14 58 L62 18 L110 58"/><path d="M26 50 V106 H98 V50"/><path d="M52 106 V76 H72 V106"/></svg>
      <div class="tl m" style="left:200px;top:96px" id="b3pl">painting…</div><div class="tl b" style="left:700px;top:96px" id="b3pc">ho raha hai…</div>
      <div class="pb" style="left:200px;top:146px;width:640px"><i id="b3bar"></i></div>
      <div class="stamp" id="b3st" style="left:500px;top:186px">is / are + being + V3</div>
      {sentence("b3", w3, 284)}""")
    js.append(f'tl.fromTo("#b3pl, #b3pc", {BLURIN}, {t("u3_kaam")});')
    p1, p2 = t("u3_hone"), t("u3_painted", 0.6)
    seg3_end = C.edl()[3]["end"]
    js.append(f'tl.fromTo("#b3bar", {{width: "0%"}}, {{width: "38%", duration: {seg3_end - p1:.2f}, ease: "none"}}, {p1});')
    js.append(f'tl.to("#b3bar", {{width: "100%", duration: {p2 - t("u3_the"):.2f}, ease: "power1.inOut"}}, {t("u3_the")});')
    js.append(f'tl.fromTo("#b3pc", {{color: "#5AA9FF"}}, {{color: "#FFC83D", duration: 0.2}}, {t("u3_being")});')
    light("b3", w3)
    js.append(f'tl.fromTo("#b3st", {{opacity: 0, scale: 2, rotation: -20}}, {{opacity: 1, scale: 1, rotation: -7, duration: 0.25, ease: "power3.in"}}, {t("u3_painted", 0.55)});')
    sub("b3s0", s + 0.1, t("u3_the", -0.15), 'Jab kisi <span class="y">kaam ke hone</span> ki baat ho')
    sub("b3s1", t("u3_the", -0.15), t("u3_iska", -0.05), 'For example 👇')
    sub("b3s2", t("u3_iska", -0.05), e, '= Ghar ko <span class="y">paint kiya ja raha hai</span>')
    # ---------- recap + CTA (one content block: rows stay, comment part joins at the CTA)
    s, e = SEC["recap"][0], dur
    rows = [("behave", 'You are <span class="y">being rude</span>.'), ("pehchaan", '<span class="y">Being a teacher</span>, I…'),
            ("kaam", 'The house is <span class="y">being painted</span>.')]
    rr = "".join(f'<div class="row" id="rr{i}" style="top:{84 + 62 * i}px"><span class="n">{i + 1}</span><span class="m">{a} →</span><span>{b}</span></div>'
                 for i, (a, b) in enumerate(rows))
    typed_html = "".join(f'<span id="brt{k}">{c if c != " " else "&nbsp;"}</span>' for k, c in enumerate("“Since” vs “For”"))
    content("br", s, e + 0.5, f"""<div class="lab">RECAP</div>{rr}
      <div class="tl" id="brq" style="left:40px;top:292px"><span class="y">Comment</span> karo: kaunsa word confuse karta hai?</div>
      <div class="box" id="brb" style="top:340px"><b id="brt">{typed_html}</b><span class="caret" id="brc"></span></div>""")
    for i in range(3):
        js.append(f'tl.fromTo("#rr{i}", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.3, ease: "power3.out"}}, {s + 0.25 + 0.25 * i});')
    cs = SEC["cta"][0]
    js.append(f'tl.fromTo("#br .pc", {{top: 1100}}, {{top: 1045, duration: 0.35, ease: "power3.inOut"}}, {cs + 0.05});')
    js.append(f'tl.fromTo("#brq", {BLURIN}, {t("c_confusing", -0.2)});')
    js.append(f'tl.fromTo("#brb", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}}, {t("c_comment", -0.15)});')
    typed = "“Since” vs “For”"
    for k in range(len(typed)):
        js.append(f'tl.fromTo("#brt{k}", {{display: "none"}}, {{display: "inline", duration: 0.01}}, {t("c_comment", 0.2 + 0.06 * k):.3f});')
    js.append(f'tl.fromTo("#brc", {{opacity: 1}}, {{opacity: 0, duration: 0.3, yoyo: true, repeat: 21, ease: "steps(1)"}}, {t("c_comment")});')
    sub("brs0", s + 0.1, cs, 'I hope <span class="y">clarity</span> mil gayi ✅')
    sub("brs1", cs + 0.05, t("c_comment", -0.1), 'Bahut saare English words <span class="y">confusing</span> hote hain 🤯')
    sub("brs2", t("c_comment", -0.1), t("c_next", -0.1), '<span class="y">Comment</span> karo 👇')
    sub("brs3", t("c_next", -0.1), dur + 0.2, 'Next video mein <span class="y">uska explanation</span> 👀')
    return els, js, TPL_B


def write(v):
    els, js, tpl = {"a": build_a, "b": build_b}[v]()
    out = HERE / "overlay" / v
    (out / "vendor").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    shutil.copy(C.ROOT / "node_modules/gsap/dist/gsap.min.js", out / "vendor/gsap.min.js")
    for f in list((HERE / "board" / "fonts").glob("*.woff2")) + list((HERE / "board_b" / "fonts").glob("*.woff2")):
        shutil.copy(f, out / "fonts" / f.name)
    (out / "hyperframes.json").write_text('{"name":"manisha9-overlay-%s"}\n' % v)
    dur = C.duration()
    page = (HEAD + tpl + BODY).replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "\n".join(js))
    (out / "index.html").write_text(page)
    print(out / "index.html", f"{len(els)} clips, {dur:.2f}s")


HEAD = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: PF; src: url(fonts/pf900.woff2); font-weight: 900; }
@font-face { font-family: PF; src: url(fonts/pf900i.woff2); font-weight: 900; font-style: italic; }
@font-face { font-family: Pop; src: url(fonts/pop500.woff2); font-weight: 500; }
@font-face { font-family: Pop; src: url(fonts/pop600.woff2); font-weight: 600; }
@font-face { font-family: Pop; src: url(fonts/pop700.woff2); font-weight: 700; }
@font-face { font-family: Pop; src: url(fonts/pop800.woff2); font-weight: 800; }
@font-face { font-family: Pop; src: url(fonts/pop600i.woff2); font-weight: 600; font-style: italic; }
html, body { margin: 0; background: transparent; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; }
.clip { position: absolute; inset: 0; } .layer { position: absolute; inset: 0; }
.layer > div { position: absolute; }
.w { display: inline-block; }
"""
TPL_A = """
:root { --ink: #1E1B24; --ivory: #FFF8EC; --gold: #FFB627; --coral: #FF6B6B; --sky: #7EC8E3;
  --sh: 0 2px 3px rgba(0,0,0,.45), 0 8px 26px rgba(0,0,0,.4); }
.being { font: italic 900 1.08em/1 PF; color: var(--gold); }
.gold { color: var(--gold); }
.hk { left: 0; top: 280px; width: 1080px; text-align: center; font: 800 76px/1.05 Pop; color: #fff; text-shadow: var(--sh); }
.hk .big { display: block; font: italic 900 190px/1 PF; color: var(--gold); margin-bottom: 4px; -webkit-text-stroke: 5px var(--ink); paint-order: stroke fill;
  text-shadow: 0 6px 24px rgba(0,0,0,.45); }
.hk .gold { color: var(--gold); background: rgba(30,27,36,.88); padding: 0 16px; border-radius: 14px; text-shadow: none; }
.tabs { left: 150px; top: 590px; width: 780px; display: flex; justify-content: center; gap: 26px; }
.tb { width: 220px; height: 150px; border-radius: 28px; background: var(--ivory); box-shadow: 0 16px 34px rgba(0,0,0,.3); text-align: center; }
.tb b { display: block; margin-top: 14px; font: italic 900 70px/1 PF; color: var(--ink); }
.tb i { display: block; font: normal 46px/1.2 sans-serif; }
.tb.wide { width: 250px; height: 200px; } .tb u { display: block; margin-top: 6px; text-decoration: none; font: 800 28px/1 Pop; color: var(--coral); }
.rt { left: 90px; width: 900px; top: 400px; }
.rch .being { -webkit-text-stroke: 4px var(--ink); paint-order: stroke fill; }
.rch { left: 0; top: 290px; width: 1080px; text-align: center; font: 800 64px/1.1 Pop; color: #fff; text-shadow: var(--sh); }
.easy { left: 0; top: 770px; width: 1080px; text-align: center; font: italic 600 46px/1 Pop; color: #fff; text-shadow: var(--sh); }
.rce { top: 640px; }
.chip { left: 120px; top: 270px; padding: 12px 22px; border-radius: 30px; background: var(--ink); color: var(--gold); font: 800 30px/1 Pop; letter-spacing: 2px; }
.icon { left: 820px; top: 250px; font: 90px/1 sans-serif; }
.rule { left: 0; top: 350px; width: 1080px; text-align: center; font: 600 44px/1.2 Pop; color: #fff; text-shadow: var(--sh); }
.rule b { color: var(--gold); font-weight: 800; background: rgba(30,27,36,.88); padding: 0 12px 2px; border-radius: 12px; text-shadow: none; }
.card { left: 90px; top: 450px; width: 900px; box-sizing: border-box; padding: 30px 30px; border-radius: 36px; background: var(--ivory); text-align: center; box-shadow: 0 18px 40px rgba(0,0,0,.3); }
.en { font: 800 64px/1.15 Pop; color: var(--ink); }
.card.sm .en { font-size: 50px; } .card.sm .hi { font-size: 35px; } .card.sm3 .en { font-size: 56px; }
.hl { display: inline-block; padding: 0 14px; border-radius: 14px; background: rgba(255,182,39,0); }
.hl .being { color: var(--gold); }
.hi { margin-top: 14px; font: italic 600 38px/1.25 Pop; color: #6B5E55; }
.hi b { color: var(--coral); font-style: normal; font-weight: 800; }
.pat { left: 0; top: 660px; width: 1080px; text-align: center; }
.pat span { display: inline-block; padding: 14px 26px; border-radius: 30px; background: var(--sky); color: var(--ink); font: 800 36px/1 Pop; box-shadow: 0 10px 24px rgba(0,0,0,.25); }
.cq { left: 0; top: 300px; width: 1080px; text-align: center; font: 800 70px/1.1 Pop; color: #fff; text-shadow: var(--sh); }
.cq em { font-style: normal; color: var(--gold); background: rgba(30,27,36,.88); padding: 0 14px 4px; border-radius: 14px; text-shadow: none; }
.box { left: 140px; top: 500px; width: 800px; height: 120px; box-sizing: border-box; border-radius: 60px; background: #fff; box-shadow: 0 16px 34px rgba(0,0,0,.3);
  display: flex; align-items: center; padding: 0 40px; font: 600 44px/1 Pop; color: #9A8F86; }
.box b { color: var(--ink); font-weight: 600; margin-left: 12px; }
.caret { display: inline-block; width: 4px; height: 46px; background: var(--coral); margin-left: 6px; }
.send { left: 836px; top: 515px; width: 90px; height: 90px; border-radius: 50%; background: var(--coral); color: #fff; text-align: center; font: 800 48px/90px Pop; }
.nxt { left: 0; top: 680px; width: 1080px; text-align: center; font: italic 600 46px/1.2 Pop; color: #fff; text-shadow: var(--sh); }
.sweep { left: -400px; top: -200px; width: 700px; height: 2400px; transform: rotate(18deg);
  background: linear-gradient(90deg, transparent, var(--c), rgba(255,240,200,.65), var(--c), transparent); filter: blur(30px); mix-blend-mode: screen; }
"""
TPL_B = """
:root { --glass: rgba(22,22,28,.82); --y: #FFC83D; --b: #5AA9FF; --mut: rgba(255,255,255,.45); }
#stage { font-family: Pop; color: #fff; }
.y { color: var(--y); } .b { color: var(--b); } .m { color: var(--mut); }
.bar { left: 70px; top: 255px; width: 940px; height: 74px; border-radius: 18px; background: var(--glass); }
.bar .d { position: absolute; left: 26px; top: 12px; font: 800 28px/1 Pop; color: var(--y); letter-spacing: 1.5px; opacity: 0; } #bl0 { opacity: 1; }
.bar .seg { position: absolute; left: 26px; right: 26px; bottom: 14px; display: flex; gap: 10px; }
.bar .seg i { flex: 1; height: 6px; border-radius: 3px; background: rgba(255,255,255,.18); overflow: hidden; }
.bar .seg b { display: block; height: 100%; background: var(--y); transform-origin: 0 50%; transform: scaleX(0); }
.pan { left: 90px; top: 1100px; width: 900px; height: 370px; border-radius: 34px; background: var(--glass); box-shadow: 0 20px 50px rgba(0,0,0,.35); }
.pc { left: 90px; top: 1100px; width: 900px; height: 370px; }
#br .pc { height: 445px; }
.pc > * { position: absolute; }
.lab { left: 30px; top: 24px; padding: 7px 16px; border-radius: 12px; border: 2px solid rgba(90,169,255,.55); background: rgba(90,169,255,.12); color: var(--b); font: 700 24px/1 Pop; }
.sub { left: 0; top: 1490px; width: 1080px; text-align: center; }
.sub > span { display: inline-block; max-width: 900px; padding: 12px 24px; border-radius: 16px; background: rgba(22,22,28,.80); font: 700 36px/1.2 Pop; }
.sen { left: 0; width: 900px; text-align: center; font: 800 56px/1.15 Pop; color: rgba(255,255,255,.32); }
svg { fill: none; stroke: #fff; stroke-width: 5; stroke-linecap: round; stroke-linejoin: round; }
.big { left: 0; width: 900px; top: 70px; text-align: center; font: 800 112px/1 Pop; color: var(--y); }
.node { width: 50px; height: 50px; border-radius: 50%; background: var(--b); color: #0E1A2A; text-align: center; font: 800 28px/50px Pop; }
.nl { width: 260px; text-align: center; font: 700 30px/1.1 Pop; }
.row1 { left: 200px; top: 96px; display: flex; align-items: center; gap: 22px; }
.tl { font: 700 30px/1 Pop; }
.row1 .tl:first-child { width: 120px; }
.tg { position: relative; width: 84px; height: 44px; border-radius: 22px; background: rgba(255,255,255,.2); display: inline-block; }
.tg::after { content: ""; position: absolute; left: 5px; top: 5px; width: 34px; height: 34px; border-radius: 50%; background: #fff; }
#tg2 { background: rgba(255,255,255,.2); } #tg2::after { display: none; }
#tg2 i { position: absolute; left: 5px; top: 5px; width: 34px; height: 34px; border-radius: 50%; background: #fff; }
.ring { display: inline-block; padding: 0 10px; border-radius: 40px; outline: 4px solid rgba(255,77,77,0); outline-offset: -2px; }
.idc { left: 200px; top: 100px; font: 700 34px/1 Pop; display: flex; align-items: center; gap: 14px; }
.slot { display: inline-block; min-width: 70px; padding: 8px 18px; border: 3px dashed rgba(255,255,255,.4); border-radius: 14px; text-align: center; }
.tick { display: inline-block; width: 40px; height: 40px; border-radius: 50%; background: #3BD16F; color: #0E1A2A; font: 800 26px/40px Pop; text-align: center; }
.pb { height: 14px; border-radius: 7px; background: rgba(255,255,255,.16); overflow: hidden; }
.pb i { display: block; height: 100%; width: 0%; border-radius: 7px; background: var(--b); }
.stamp { padding: 8px 18px; border: 5px solid var(--y); border-radius: 14px; color: var(--y); font: 800 34px/1 Pop; transform: rotate(-7deg); background: rgba(22,22,28,.6); }
.row { left: 40px; width: 820px; display: flex; align-items: center; gap: 18px; font: 700 34px/1 Pop; }
.row .n { width: 44px; height: 44px; border-radius: 50%; background: var(--b); color: #0E1A2A; font: 800 26px/44px Pop; text-align: center; }
.box { left: 40px; width: 820px; height: 78px; border-radius: 39px; background: rgba(255,255,255,.1); border: 2px solid rgba(255,255,255,.25);
  font: 500 32px/78px Pop; padding-left: 30px; box-sizing: border-box; color: var(--mut); }
.box b { color: #fff; font-weight: 700; } .caret { display: inline-block; width: 3px; height: 34px; background: var(--y); vertical-align: -6px; margin-left: 4px; }
"""
BODY = """</style></head><body>
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
    write(sys.argv[1])
