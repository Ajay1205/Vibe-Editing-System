"""Caption layer for Nikita 9 -- "Office Chat" (approved board: edits/nikita9/board). Same layer for V1 and V2
(V2 cuts to animated scenes during the situations; build.py switches this layer off there).

Each situation = a yellow sticky note on the wall left of her head (Hinglish, handwritten, numbered 01/05 .. BONUS);
the English sentence types itself out word by word in a work-chat message at chest level, key phrases on an indigo
highlight, "Sent ✓✓" + a reaction; under it meaning chips (user: "very explanatory"). Hook: "darr" line, then a
message typed and struck out; intro: "5 OFFICE SENTENCES" + five mini notes; quiz: message box + "Comment karo".
Rendered natively at 2160x3840.   Usage: python3 -I overlay.py -> overlay/index.html
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


def T(x, d=0.0):
    return round(C.T(*x) + d, 3)


def t(key, d=0.0):
    return T(K[key], d)


def clip(id_, s, e, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{s:.3f}" data-duration="{max(0.05, e - s):.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


SENTENCES = [  # id, take, note label, note text, to, words with [key] markup, reaction, chips
    ("s1", 3, "01 / 05", "Boss ko task ka update dena hai 📋", "Manager",
     "I wanted to give you a [quick update] about the task.", "👍 1", ["<b>quick update</b> = chhota sa update"]),
    ("s2", 4, "02 / 05", "Kaam mein thoda delay ho raha hai 😬", "Manager",
     "There might be a [slight delay]. I will [keep you posted].", "👍 1",
     ["<b>slight</b> = thoda sa", "<b>keep you posted</b> = update deta rahunga"]),
    ("s3", 4, "03 / 05", "Doubt hai, help chahiye 🙋", "Teammate",
     "[Could you please] help me with this task?", "🙌 1", ["<b>Could you please…</b> = polite request 🙏"]),
    ("s4", 5, "04 / 05", "Task poora ho gaya ✅", "Manager",
     "I have [completed] the task.", "🎉 3", ["<b>completed</b> = poora kar liya"]),
    ("s5", 5, "05 / 05", "Bahut saare tasks… pehle kaunsa? 🤯", "Manager",
     "Which task should I [prioritize] first?", "👀 1", ["<b>prioritize</b> = pehle kya karna hai"]),
    ("s6", 6, "BONUS 🎁", "Mere paas ek idea hai 💡", "Team",
     "I have a [suggestion] that we could [consider].", "🔥 3 · 👏 2", ["<b>suggestion</b> = sujhaav", "<b>consider</b> = soch sakte hain"]),
]
READ_HOLD = 0.7
TIMES = {"s1": "10:42 AM", "s2": "11:15 AM", "s3": "12:03 PM", "s4": "4:30 PM", "s5": "9:20 AM", "s6": "11:05 AM"}


def words_html(sid, text):
    """Split into word spans; [..] marks a key phrase (indigo highlight)."""
    out, j, inkey = [], 0, False
    for w in text.split():
        start = w.startswith("[")
        end = "]" in w
        w = w.replace("[", "").replace("]", "")
        if start:
            out.append('<span class="k">')
            inkey = True
        out.append(f'<span class="w" id="{sid}w{j}">{w}</span>')
        j += 1
        if end:
            out.append("</span>")
            inkey = False
    html = " ".join(out).replace('<span class="k"> ', '<span class="k">').replace(" </span>", "</span>")
    return html, j


def build():
    els, js = [], []
    dur = C.duration()
    out_ = lambda sel, e, d=0.17: js.append(f'tl.to("{sel}", {{opacity: 0, y: -10, duration: {d - 0.01:.2f}, ease: "power2.in"}}, {e - d:.3f});')  # noqa: E731

    def note(id_, label, text, rot=-4, bonus=False, shown=False):
        return (f'<div class="note{" bonus" if bonus else ""}" id="{id_}" style="--r:{rot}deg{";opacity:1" if shown else ""}"><span class="n">{label}</span>'
                f'<div class="h">{text}</div></div>')

    def note_in(sel, at):
        js.append(f'tl.fromTo("{sel}", {{opacity: 0, y: -60, rotation: -14, scale: 1.15}}, {{opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.45, ease: "back.out(1.8)"}}, {at});')

    def note_out(sel, e):
        js.append(f'tl.to("{sel}", {{opacity: 0, y: 90, rotation: 12, duration: 0.25, ease: "power2.in"}}, {e - 0.26:.3f});')

    # ------------------------------------------------------------------ hook (take 1)
    e = C.take_end(1)
    hs = 'Office mein English bolne se <em>darr</em> lagta hai? 😰'
    els.append(clip("hk", 0, e, 1, f"""{note("hkn", "OFFICE MEETING", "Idea hai… par English ka darr 😶", shown=True)}
      <div class="tagc" id="hkt">💼 Corporate employees ke liye</div>
      <div class="pill" id="hk1">{hs}</div>
      <div class="label" id="hkl">💬 Team chat</div>
      <div class="typing" id="hkb"><span class="del" id="hkd">{"".join(f'<span id="hc{i}">{c}</span>' for i, c in enumerate("I think we sho"))}</span><span class="caret" id="hkc"></span><span class="send">➤</span></div>
      <div class="pill low" id="hk2">Idea hai, par <em>English</em> ke darr se chup rehte ho? 🤐</div>"""))
    js.append(f'tl.fromTo("#hkt", {POP}, {t("h_corporate", -0.1)});')
    js.append(f'tl.fromTo("#hk1 em", {{color: "#FFFFFF"}}, {{color: "#FFE45C", duration: 0.2}}, {t("h_darte", -0.05)});')
    js.append(f'tl.to("#hk1, #hkt", {{opacity: 0, y: -12, duration: 0.2}}, {t("h_opinions", -0.35)});')
    js.append(f'tl.fromTo("#hkl, #hkb", {BLURIN}, {t("h_opinions", -0.25)});')
    t0, t1 = t("h_opinions"), t("h_thoughts", 0.6)
    for i in range(14):
        js.append(f'tl.fromTo("#hc{i}", {{display: "none"}}, {{display: "inline", duration: 0.01}}, {t0 + (t1 - t0) * i / 14:.3f});')
    js.append(f'tl.fromTo("#hkd", {{textDecorationColor: "rgba(255,90,95,0)", color: "#16171B"}}, {{textDecorationColor: "rgba(255,90,95,1)", color: "#C8C9D0", duration: 0.25}}, {t("h_darr", -0.1)});')
    js.append(f'tl.to("#hkb", {{x: 10, duration: 0.05, yoyo: true, repeat: 5, ease: "none"}}, {t("h_darr", 0.1)});')
    js.append(f'tl.to("#hkd", {{opacity: 0, duration: 0.3}}, {t("h_share", -0.3)});')
    js.append(f'tl.fromTo("#hk2", {BLURIN}, {t("h_share", -0.2)});')
    out_("#hk .clip, #hkt, #hkl, #hkb, #hk2", e)
    note_out("#hkn", e)

    # ------------------------------------------------------------------ intro (take 2)
    s, e = C.take_start(2), C.take_end(2)
    minis = "".join(f'<div class="mini" id="mn{i}">0{i + 1}</div>' for i in range(5)) + '<div class="mini q" id="mn5">🎁</div>'
    els.append(clip("in", s, e, 2, f"""<div class="title" id="it"><em>5</em> OFFICE SENTENCES 💼</div>
      <div class="minis">{minis}</div><div class="conf" id="ic">Confidently bolo 💪</div>"""))
    js.append(f'tl.fromTo("#it", {{opacity: 0, scale: 1.4}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "power3.out"}}, {t("i_five", -0.1)});')
    for i in range(5):
        js.append(f'tl.fromTo("#mn{i}", {{opacity: 0, y: -50, rotation: {(-1) ** i * 12}}}, {{opacity: 1, y: 0, rotation: {(-1) ** i * 3}, duration: 0.35, ease: "back.out(2)"}}, {t("i_sentences", -0.2) + 0.12 * i:.3f});')
    js.append(f'tl.fromTo("#mn5", {{opacity: 0, scale: 0.3}}, {{opacity: 1, scale: 1, rotation: 6, duration: 0.4, ease: "back.out(3)"}}, {t("i_office"):.3f});')
    js.append(f'tl.fromTo("#ic", {BLURIN}, {t("i_conf", -0.1)});')
    out_("#in .layer > div", e)

    # ------------------------------------------------------------------ the six sentences
    for n, (sid, tk, label, ntext, to, text, react, chips) in enumerate(SENTENCES):
        s = C.T(*K[f"{sid}_sit"])
        nxt = C.T(*K[SENTENCES[n + 1][0] + "_sit"]) if n + 1 < len(SENTENCES) else C.take_start(7)
        e = nxt + READ_HOLD  # the card stays readable into the next situation (user: lines must not vanish)
        wh, nw = words_html(sid, text)
        ch = "".join(f'<span class="chip" id="{sid}c{i}">{c}</span>' for i, c in enumerate(chips))
        els.append(clip(sid, s, e, 3, f"""{note(f"{sid}n", label, ntext, rot=-4 if n % 2 else 3, bonus=sid == "s6")}
          <div class="chat" id="{sid}k"><div class="hd"><span class="av">You</span><b>You</b> → {to} · {TIMES[sid]}</div>
            <div class="msg">{wh}</div><div class="ft" id="{sid}f">Sent<i>✓✓</i></div></div>
          <div class="react" id="{sid}r">{react}</div>
          <div class="chips">{ch}</div>"""))
        note_in(f"#{sid}n", s + 0.08)
        ws = K[sid]
        assert len(ws) == nw, (sid, len(ws), nw)
        js.append(f'tl.fromTo("#{sid}k", {{opacity: 0, y: 40, scale: 0.95}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.6)"}}, {T(ws[0], -0.35)});')
        for j, w in enumerate(ws):
            js.append(f'tl.fromTo("#{sid}w{j}", {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: 0.18, ease: "power2.out"}}, {T(w, -0.06)});')
        js.append(f'tl.fromTo("#{sid}k .k", {{backgroundColor: "rgba(232,231,255,0)", color: "#16171B"}}, {{backgroundColor: "rgba(232,231,255,1)", color: "#5E5CE6", duration: 0.25}}, {T(ws[-1], 0.08)});')
        js.append(f'tl.fromTo("#{sid}f", {{opacity: 0}}, {{opacity: 1, duration: 0.2}}, {T(ws[-1], 0.15)});')
        js.append(f'tl.fromTo("#{sid}f i", {{color: "#B8BAC4"}}, {{color: "#34B7F1", duration: 0.2}}, {T(ws[-1], 0.35)});')
        js.append(f'tl.fromTo("#{sid}r", {{opacity: 0, scale: 0.3, y: 20}}, {{opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(3)"}}, {T(ws[-1], 0.3)});')
        for i in range(len(chips)):
            js.append(f'tl.fromTo("#{sid}c{i}", {BLURIN}, {T(ws[-1], 0.2 + 0.2 * i):.3f});')
        note_out(f"#{sid}n", nxt + 0.05)  # the old note peels off just before the next one lands
        out_(f"#{sid}k, #{sid}r, #{sid} .chips", e)

    # ------------------------------------------------------------------ quiz (take 7)
    s, e = C.take_start(7), dur
    els.append(clip("qz", s, e + 0.2, 4, f"""<div class="tagc big" id="q1">YOUR TURN ✍️</div>
      <div class="pill" id="q2">English mein <em>translate</em> karke comment karo 👇</div>
      {note("qn", "SITUATION 🧩", "Kal office nahi jaana, chhutti chahiye 🏖️", rot=3)}
      <div class="label" id="ql">💬 Message to Manager</div>
      <div class="typing" id="qb"><span style="color:#B5B6BE">Type in English…</span><span class="caret" id="qc"></span><span class="send on">➤</span></div>
      <div class="cta" id="qt">Comment karo 👇</div>"""))
    js.append(f'tl.fromTo("#q1", {POP}, {t("q_sit", -0.3)});')
    js.append(f'tl.fromTo("#q2", {BLURIN}, {t("q_comment", -0.6)});')
    js.append(f'tl.to("#q1, #q2", {{opacity: 0, y: -12, duration: 0.2}}, {t("q_kal", -0.45)});')
    note_in("#qn", t("q_kal", -0.3))
    js.append(f'tl.fromTo("#ql, #qb", {BLURIN}, {t("q_chhutti", -0.2)});')
    js.append(f'tl.fromTo("#qc", {{opacity: 1}}, {{opacity: 0, duration: 0.35, yoyo: true, repeat: 13, ease: "steps(1)"}}, {t("q_chhutti")});')
    js.append(f'tl.fromTo("#qt", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.4)"}}, {t("q_kaise", -0.1)});')
    js.append(f'tl.to("#qt", {{scale: 1.07, duration: 0.35, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {t("q_kaise", 0.5)});')

    out = HERE / "overlay"
    (out / "vendor").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    shutil.copy(C.ROOT / "node_modules/gsap/dist/gsap.min.js", out / "vendor/gsap.min.js")
    for f in (HERE / "board" / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "fonts" / f.name)
    (out / "hyperframes.json").write_text('{"name":"nikita9-overlay"}\n')
    page = TEMPLATE.replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "\n".join(js))
    (out / "index.html").write_text(page)
    print(out / "index.html", f"{len(els)} clips, {dur:.2f}s")


TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: Brico; src: url(fonts/brico800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs700.woff2); font-weight: 700; }
@font-face { font-family: PJS; src: url(fonts/pjs500.woff2); font-weight: 500; }
@font-face { font-family: Cav; src: url(fonts/cav700.woff2); font-weight: 700; }
:root { --ink: #16171B; --y: #FFE45C; --ind: #5E5CE6; --tick: #34B7F1; --grn: #2FBF71;
  --sh: 0 2px 3px rgba(0,0,0,.45), 0 8px 26px rgba(0,0,0,.4); }
html, body { margin: 0; background: transparent; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; }
.clip { position: absolute; inset: 0; } .layer { position: absolute; inset: 0; }
.layer > div { position: absolute; }
.w { display: inline-block; }
.note { left: 110px; top: 290px; width: 290px; min-height: 240px; box-sizing: border-box; padding: 22px 22px 26px; background: var(--y);
  transform: rotate(var(--r)); box-shadow: 0 18px 30px rgba(0,0,0,.3); border-radius: 4px 4px 22px 4px; opacity: 0; }
.note::before { content: ""; position: absolute; left: 95px; top: -16px; width: 100px; height: 32px; background: rgba(255,255,255,.55); transform: rotate(3deg); }
.note .n { display: inline-block; padding: 6px 12px; border-radius: 10px; background: var(--ink); color: var(--y); font: 800 22px/1 PJS; letter-spacing: 2px; }
.note .h { margin-top: 12px; font: 700 50px/1.02 Cav; color: var(--ink); }
.note.bonus .n { background: var(--ind); color: #fff; }
.chat { left: 90px; top: 1090px; width: 900px; box-sizing: border-box; padding: 22px 28px 20px; border-radius: 30px; background: #fff; box-shadow: 0 22px 50px rgba(0,0,0,.35); }
.hd { display: flex; align-items: center; gap: 14px; font: 700 24px/1 PJS; color: #8A8C96; }
.av { width: 46px; height: 46px; border-radius: 50%; background: var(--ind); color: #fff; font: 800 18px/46px PJS; text-align: center; }
.hd b { color: var(--ink); font-weight: 800; }
.msg { margin-top: 14px; font: 800 48px/1.2 PJS; color: var(--ink); }
.msg .k { padding: 0 6px 2px; border-radius: 12px; }
.ft { margin-top: 8px; text-align: right; font: 700 22px/1 PJS; color: #9A9CA6; }
.ft i { font-style: normal; font-weight: 800; letter-spacing: -4px; margin-left: 6px; }
.react { left: 760px; top: 1058px; padding: 8px 16px; border-radius: 26px; background: #fff; box-shadow: 0 8px 20px rgba(0,0,0,.25); font: 800 30px/1 PJS; color: var(--ink); }
.chips { left: 90px; top: 1430px; width: 900px; display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; }
.chip { display: inline-block; padding: 12px 20px; border-radius: 20px; background: rgba(22,23,27,.86); color: #fff; font: 700 34px/1 PJS; }
.chip b { color: var(--y); font-weight: 800; }
.label { left: 90px; top: 1030px; padding: 10px 18px; border-radius: 14px; background: rgba(22,23,27,.85); color: #fff; font: 700 26px/1 PJS; }
.typing { left: 90px; top: 1150px; width: 900px; height: 120px; box-sizing: border-box; padding: 0 30px; border-radius: 60px; background: #fff;
  display: flex; align-items: center; box-shadow: 0 22px 50px rgba(0,0,0,.35); font: 700 44px/1 PJS; color: var(--ink); }
.typing .del { text-decoration: line-through; text-decoration-thickness: 4px; white-space: pre; }
.caret { display: inline-block; width: 4px; height: 50px; background: var(--ind); margin-left: 6px; }
.send { margin-left: auto; width: 78px; height: 78px; border-radius: 50%; background: #D9DAE0; color: #fff; text-align: center; font: 800 38px/78px PJS; }
.send.on { background: var(--ind); }
.pill { left: 130px; top: 1150px; width: 820px; box-sizing: border-box; padding: 18px 24px; border-radius: 26px; background: rgba(22,23,27,.84);
  text-align: center; font: 800 50px/1.15 Brico; color: #fff; }
.pill em { font-style: normal; color: var(--y); }
.pill.low { top: 1300px; font-size: 46px; }
.tagc { left: 0; right: 0; margin: 0 auto; width: fit-content; top: 1060px; padding: 10px 20px; border-radius: 18px; background: var(--y); color: var(--ink); font: 800 28px/1 PJS; letter-spacing: 1px; }
.tagc.big { top: 1100px; font-size: 44px; padding: 16px 28px; background: var(--ind); color: #fff; }
.title { left: 0; top: 1120px; width: 1080px; text-align: center; font: 800 64px/1 Brico; color: #fff; text-shadow: var(--sh); }
.title em { font-style: normal; color: var(--y); }
.minis { left: 150px; top: 1240px; width: 780px; display: flex; gap: 18px; justify-content: center; }
.mini { width: 104px; height: 96px; border-radius: 4px 4px 14px 4px; background: var(--y); color: var(--ink); font: 800 34px/96px PJS; text-align: center;
  box-shadow: 0 10px 20px rgba(0,0,0,.3); }
.mini.q { background: var(--ind); color: #fff; font-size: 44px; }
.conf { left: 0; top: 1380px; width: 1080px; text-align: center; font: 700 72px/1 Cav; color: #fff; text-shadow: var(--sh); }
.cta { left: 0; top: 1310px; width: 1080px; text-align: center; font: 700 84px/1 Cav; color: #fff; text-shadow: var(--sh); }
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
