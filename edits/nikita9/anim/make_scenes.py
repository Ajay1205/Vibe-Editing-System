"""Animated scenes for Nikita 9 V2 (user: "animations related EXACTLY to those sentences she says").
Grown-up flat editorial style (CLAUDE.md, Nikita 6 cutaways): office UI objects, no cartoon characters, calm power3
motion, few emoji; the reel's palette (ink, sticky yellow #FFE45C, indigo #5E5CE6, tick blue, green). Text at the top
(y 300-600, the Hinglish situation), the visual below (y 680-1600). Durations come from scenes_plan.WIN.

  python3 -I anim/make_scenes.py            write anim/<name>/
  python3 -I anim/make_scenes.py render     -> footage/nikita9/broll/<name>.mp4 (native 2160x3840)
"""

import pathlib
import shutil
import subprocess
import sys
import os

HERE = pathlib.Path(__file__).resolve().parent
EDIT = HERE.parent
sys.path.insert(0, str(EDIT))
import cut as C  # noqa: E402
import scenes_plan as SP  # noqa: E402

OUT = C.ROOT / "footage" / "nikita9" / "broll"
ENV = dict(os.environ, NODE_USE_ENV_PROXY="1", NODE_EXTRA_CA_CERTS="/root/.ccr/ca-bundle.crt")

HEAD = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: Brico; src: url(fonts/brico800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs800.woff2); font-weight: 800; }
@font-face { font-family: PJS; src: url(fonts/pjs700.woff2); font-weight: 700; }
@font-face { font-family: PJS; src: url(fonts/pjs500.woff2); font-weight: 500; }
@font-face { font-family: Cav; src: url(fonts/cav700.woff2); font-weight: 700; }
:root { --ink: #16171B; --y: #FFE45C; --ind: #5E5CE6; --tick: #34B7F1; --grn: #2FBF71; --red: #FF5A5F; --mut: #8A8C96; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #101116; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; background: #101116; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; overflow: hidden;
  background: radial-gradient(ellipse at 50% 62%, #2A2A52 0%, #1A1A30 48%, #101116 100%); font-family: PJS; color: #fff; }
#cam { position: absolute; inset: 0; transform-origin: 50% 60%; }
.abs { position: absolute; }
.top { left: 60px; top: 300px; width: 960px; text-align: center; font: 800 70px/1.12 Brico; color: #fff; }
.top em { font-style: normal; display: inline-block; padding: 0 14px; border-radius: 14px; background: var(--y); color: var(--ink); }
.top2 { left: 60px; top: 470px; width: 960px; text-align: center; font: 700 56px/1.1 Cav; color: var(--y); }
.card { border-radius: 30px; background: #fff; color: var(--ink); box-shadow: 0 34px 80px rgba(0,0,0,.5); }
.lbl { font: 800 24px/1 PJS; letter-spacing: 2px; color: var(--mut); }
.pill { display: inline-block; padding: 10px 18px; border-radius: 18px; font: 800 28px/1 PJS; }
%CSS%
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%" data-width="2160" data-height="3840" data-fps="30">
<div id="stage"><div id="cam">
%BODY%
</div></div></div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#cam", {scale: 1.0}, {scale: 1.04, duration: %DUR%, ease: "none"}, 0);
  %JS%
  window.__timelines["main"] = tl;
</script></body></html>
"""
IN = '{opacity: 0, y: 40}, {opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}'
POP = '{opacity: 0, scale: 0.5}, {opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)"}'


def top(text, sub=None):
    b = f'<div class="abs top" id="tp">{text}</div>' + (f'<div class="abs top2" id="tp2">{sub[0]}</div>' if sub else "")
    j = f'tl.fromTo("#tp", {IN}, 0.0);tl.set("#tp", {{opacity: 1, y: 0}}, 0);'
    if sub:
        j += f'tl.fromTo("#tp2", {IN}, {sub[1]});'
    return b, j


# ----------------------------------------------------------------------------------------------------- scenes
def hook(D):
    css = """
.grid { left: 110px; top: 640px; width: 860px; display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.tile { position: relative; height: 300px; border-radius: 26px; background: #262742; overflow: hidden; }
.tile .ini { position: absolute; left: 50%; top: 46%; transform: translate(-50%,-50%); width: 120px; height: 120px; border-radius: 50%;
  font: 800 46px/120px PJS; text-align: center; color: #fff; }
.tile .nm { position: absolute; left: 16px; bottom: 14px; padding: 6px 12px; border-radius: 10px; background: rgba(0,0,0,.45); font: 700 22px/1 PJS; }
.tile .wave { position: absolute; right: 18px; bottom: 16px; display: flex; gap: 4px; align-items: flex-end; height: 30px; }
.tile .wave i { width: 6px; height: 10px; border-radius: 3px; background: var(--grn); }
.tile.you { outline: 4px solid var(--ind); }
.bub { left: 0; top: 0; padding: 12px 18px; border-radius: 20px 20px 20px 4px; background: #fff; color: var(--ink); font: 800 26px/1 PJS; white-space: nowrap;
  box-shadow: 0 10px 24px rgba(0,0,0,.35); }
.mic { left: 0; top: 0; width: 70px; height: 70px; border-radius: 50%; background: #3A3B5C; font: 36px/70px sans-serif; text-align: center; }
.lock { left: 0; top: 0; width: 96px; height: 96px; border-radius: 24px; background: var(--red); font: 52px/96px sans-serif; text-align: center;
  box-shadow: 0 14px 30px rgba(0,0,0,.4); }
.cap { left: 110px; top: 1300px; width: 860px; text-align: center; font: 800 40px/1.2 PJS; color: #fff; }
"""
    tiles = [("RS", "Rahul", "#E0795A", True), ("PK", "Priya", "#3BA58B", True), ("AM", "Arjun", "#C9A227", True), ("YOU", "You", "#5E5CE6", False)]
    body = '<div class="abs grid">' + "".join(
        f'<div class="tile{" you" if not talk else ""}" id="tl{i}"><div class="ini" style="background:{c}">{a}</div><div class="nm">{n}</div>'
        + ('<div class="wave">' + "".join(f'<i id="w{i}{k}"></i>' for k in range(4)) + '</div>' if talk else "") + '</div>'
        for i, (a, n, c, talk) in enumerate(tiles)) + '</div>'
    # "You" tile is bottom-right: x 110+430+18 .. 970, y 640+318 .. 1258
    body += ('<div class="abs bub" id="b1" style="left:600px;top:930px">💡 New idea</div>'
             '<div class="abs bub" id="b2" style="left:700px;top:1000px">📈 Better plan</div>'
             '<div class="abs mic" id="mc" style="left:880px;top:1170px">🎙️</div>'
             '<div class="abs lock" id="lk" style="left:860px;top:1150px">🔒</div>'
             '<div class="abs cap" id="cp">You: 🔇 <span style="color:var(--red)">muted</span> — English ka darr</div>')
    b, j = top("Meeting mein <em>ideas</em> hote hain 💭", ("…par bolte nahi 🤐", D * 0.62))
    js = j + f'tl.fromTo(".tile", {{opacity: 0, scale: 0.9}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "power3.out", stagger: 0.08}}, 0.1);'
    for i in range(3):
        for k in range(4):
            js += f'tl.fromTo("#w{i}{k}", {{height: 8}}, {{height: {12 + (k * 7 + i * 5) % 18}, duration: 0.22, yoyo: true, repeat: {int(D / 0.44)}, ease: "sine.inOut"}}, {0.2 + 0.05 * k + 0.07 * i:.2f});'
    js += f'tl.fromTo("#b1", {POP}, {D * 0.22:.2f});tl.fromTo("#b2", {POP}, {D * 0.34:.2f});'
    js += f'tl.fromTo("#mc", {POP}, 0.5);tl.fromTo("#lk", {{opacity: 0, y: -260, rotation: -20}}, {{opacity: 1, y: 0, rotation: 0, duration: 0.5, ease: "bounce.out"}}, {D * 0.55:.2f});'
    js += f'tl.to("#b1, #b2", {{opacity: 0.25, scale: 0.9, duration: 0.4}}, {D * 0.62:.2f});tl.to("#tl3", {{filter: "grayscale(1) brightness(.6)", duration: 0.4}}, {D * 0.6:.2f});'
    js += f'tl.fromTo("#cp", {IN}, {D * 0.66:.2f});'
    return css, b + "<!--VIS-->" + body, js


def update(D):
    css = """
.board { left: 90px; top: 640px; width: 900px; height: 640px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.col { border-radius: 24px; background: rgba(255,255,255,.07); padding: 18px 14px; }
.col h4 { margin: 0 0 14px; font: 800 24px/1 PJS; letter-spacing: 2px; color: #B9BAD6; }
.task { left: 0; top: 0; width: 272px; padding: 18px; border-radius: 20px; background: #fff; color: var(--ink); box-shadow: 0 16px 34px rgba(0,0,0,.4); }
.task b { display: block; font: 800 25px/1.15 PJS; padding-right: 66px; } .task span { display: block; margin-top: 10px; font: 700 20px/1 PJS; color: var(--mut); }
.ring { }
.msgf { left: 220px; top: 1340px; width: 640px; padding: 20px 26px; border-radius: 26px 26px 26px 6px; background: #fff; color: var(--ink);
  font: 800 34px/1.2 PJS; box-shadow: 0 20px 44px rgba(0,0,0,.45); }
.msgf small { display: block; font: 700 22px/1 PJS; color: var(--mut); margin-bottom: 8px; }
"""
    body = ('<div class="abs board"><div class="col"><h4>TO DO</h4></div><div class="col"><h4>IN PROGRESS</h4></div><div class="col"><h4>DONE</h4></div></div>'
            '<div class="abs task" id="tk" style="left:107px;top:720px"><b>Client report 📊</b><span>Due: Friday</span>'
            '<svg class="ring" width="70" height="70" viewBox="0 0 70 70" style="position:absolute;right:14px;top:14px"><circle cx="35" cy="35" r="28" fill="none" stroke="#E6E6EF" stroke-width="8"/>'
            '<circle id="rg" cx="35" cy="35" r="28" fill="none" stroke="#5E5CE6" stroke-width="8" stroke-linecap="round" stroke-dasharray="176" stroke-dashoffset="176" transform="rotate(-90 35 35)"/></svg></div>'
            '<div class="abs" id="pc" style="left:420px;top:900px;font:800 44px/1 PJS;color:#fff">0%</div>'
            '<div class="abs msgf" id="mf"><small>You → Manager</small>Quick update 📋 report is 60% done</div>')
    b, j = top("Boss ko task ka <em>update</em> dena hai 📋")
    js = j + f'tl.fromTo(".board .col", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power3.out"}}, 0.1);'
    js += f'tl.fromTo("#tk", {POP}, 0.35);tl.to("#tk", {{x: 305, duration: 0.6, ease: "power3.inOut"}}, {D * 0.28:.2f});'
    js += f'tl.to("#rg", {{strokeDashoffset: 70, duration: 0.8, ease: "power2.out"}}, {D * 0.45:.2f});'
    js += f'tl.fromTo("#mf", {{opacity: 0, x: -80, scale: 0.9}}, {{opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "back.out(1.8)"}}, {D * 0.62:.2f});'
    js += 'tl.set("#pc", {opacity: 0}, 0);'
    return css, b + "<!--VIS-->" + body, js


def delay(D):
    css = """
.cal { left: 100px; top: 650px; width: 880px; padding: 24px; }
.days { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-top: 16px; }
.day { height: 150px; border-radius: 18px; background: #F2F2F7; text-align: center; padding-top: 20px; font: 800 26px/1 PJS; color: var(--mut); }
.day b { display: block; font: 800 46px/1.3 Brico; color: var(--ink); }
.flag { left: 0; top: 0; padding: 10px 16px; border-radius: 14px; background: var(--red); color: #fff; font: 800 24px/1 PJS; white-space: nowrap; }
.plus { left: 0; top: 0; padding: 8px 14px; border-radius: 14px; background: var(--y); color: var(--ink); font: 800 26px/1 PJS; }
.bell { left: 470px; top: 1110px; width: 140px; height: 140px; border-radius: 40px; background: var(--ind); font: 70px/140px sans-serif; text-align: center;
  box-shadow: 0 20px 44px rgba(0,0,0,.45); transform-origin: 50% 10%; }
.note { left: 140px; width: 800px; padding: 18px 24px; border-radius: 22px; background: #fff; color: var(--ink); font: 800 30px/1 PJS;
  box-shadow: 0 14px 30px rgba(0,0,0,.4); display: flex; align-items: center; gap: 14px; }
.note i { font-style: normal; width: 40px; height: 40px; border-radius: 12px; background: var(--ind); color: #fff; font: 22px/40px sans-serif; text-align: center; }
"""
    days = "".join(f'<div class="day">{d}<b>{n}</b></div>' for d, n in (("MON", 12), ("TUE", 13), ("WED", 14), ("THU", 15), ("FRI", 16)))
    body = (f'<div class="abs card cal" id="cl"><div class="lbl">THIS WEEK · DEADLINE</div><div class="days">{days}</div></div>'
            '<div class="abs flag" id="fg" style="left:510px;top:640px">⏰ Deadline</div>'
            '<div class="abs plus" id="pl" style="left:690px;top:870px">+1 day · slight delay</div>'
            '<div class="abs bell" id="bl">🔔</div>'
            + "".join(f'<div class="abs note" id="nt{i}" style="top:{1280 + i * 84}px"><i>💬</i>{t}</div>'
                      for i, t in enumerate(("Update: 70% done", "Update: testing now", "Update: ready by Thu ✅"))))
    b, j = top("Kaam mein thoda <em>delay</em> 😬", ("…aur updates dete rahoge 🔔", D * 0.5))
    js = j + f'tl.fromTo("#cl", {IN}, 0.1);tl.fromTo("#fg", {POP}, 0.4);'
    js += f'tl.to("#fg", {{x: 166, duration: 0.6, ease: "power3.inOut"}}, {D * 0.22:.2f});tl.fromTo("#pl", {POP}, {D * 0.36:.2f});'
    js += f'tl.fromTo("#bl", {POP}, {D * 0.48:.2f});tl.to("#bl", {{rotation: 14, duration: 0.08, yoyo: true, repeat: 7, ease: "sine.inOut"}}, {D * 0.55:.2f});'
    for i in range(3):
        js += f'tl.fromTo("#nt{i}", {{opacity: 0, x: 80}}, {{opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}}, {D * (0.56 + 0.1 * i):.2f});'
    return css, b + "<!--VIS-->" + body, js


def help_(D):
    css = """
.doc { left: 120px; top: 640px; width: 840px; height: 760px; padding: 34px; }
.ln { height: 22px; border-radius: 11px; background: #E7E7EF; margin: 0 0 24px; }
.bad { position: relative; background: #FFE1E2; }
.q { left: 0; top: 0; width: 64px; height: 64px; border-radius: 50%; background: var(--red); color: #fff; font: 800 40px/64px PJS; text-align: center; }
.ok { left: 0; top: 0; width: 64px; height: 64px; border-radius: 50%; background: var(--grn); color: #fff; font: 800 38px/64px PJS; text-align: center; }
.cur { left: 0; top: 0; }
.cur span { position: absolute; left: 30px; top: 30px; padding: 8px 14px; border-radius: 12px; font: 800 22px/1 PJS; color: #fff; white-space: nowrap; }
.hlt { left: 154px; top: 0; height: 40px; border-radius: 10px; background: rgba(94,92,230,.25); transform-origin: 0 50%; }
"""
    lines = "".join(f'<div class="ln{" bad" if i == 3 else ""}" style="width:{w}%"></div>' for i, w in enumerate((92, 78, 85, 70, 88, 60, 82, 74, 90)))
    cur = lambda id_, c, name, x, y: (f'<svg class="abs cur" id="{id_}" style="left:{x}px;top:{y}px" width="200" height="80" viewBox="0 0 200 80">'  # noqa: E731
                                      f'<path d="M4 4 L4 44 L16 33 L26 54 L34 50 L24 30 L40 30 Z" fill="{c}" stroke="#fff" stroke-width="3"/></svg>'
                                      f'<div class="abs" id="{id_}l" style="left:{x + 34}px;top:{y + 34}px;padding:8px 14px;border-radius:12px;background:{c};font:800 22px/1 PJS;color:#fff">{name}</div>')
    body = (f'<div class="abs card doc" id="dc"><div class="lbl" style="margin-bottom:26px">TASK · Q3 BUDGET SHEET</div>{lines}</div>'
            '<div class="abs hlt" id="hl" style="top:820px;width:540px"></div>'
            '<div class="abs q" id="qq" style="left:880px;top:808px">?</div><div class="abs ok" id="ok" style="left:880px;top:808px">✓</div>'
            + cur("c1", "#5E5CE6", "You", 640, 880) + cur("c2", "#2FBF71", "Teammate", 980, 1300)
            + '<div class="abs" id="sv" style="left:0;top:1440px;width:1080px;text-align:center;font:800 40px/1 PJS;color:#fff">🤝 Teammate joined · <span style="color:var(--grn)">solved</span></div>')
    b, j = top("Kaam mein <em>doubt</em> hai… help chahiye 🙋")
    js = j + f'tl.fromTo("#dc", {IN}, 0.1);tl.fromTo("#qq", {POP}, 0.5);tl.fromTo("#c1, #c1l", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, 0.6);'
    js += f'tl.to("#qq", {{scale: 1.15, duration: 0.25, yoyo: true, repeat: 3}}, 0.9);'
    js += f'tl.fromTo("#c2, #c2l", {{opacity: 0, x: 200, y: 200}}, {{opacity: 1, x: -380, y: -440, duration: 0.9, ease: "power3.inOut"}}, {D * 0.35:.2f});'
    js += f'tl.fromTo("#hl", {{scaleX: 0, opacity: 1}}, {{scaleX: 1, duration: 0.5, ease: "power2.out"}}, {D * 0.58:.2f});'
    js += f'tl.to("#qq", {{opacity: 0, scale: 0.4, duration: 0.2}}, {D * 0.7:.2f});tl.fromTo("#ok", {POP}, {D * 0.72:.2f});'
    js += f'tl.to(".bad", {{backgroundColor: "#DDF5E7", duration: 0.3}}, {D * 0.72:.2f});tl.fromTo("#sv", {IN}, {D * 0.74:.2f});'
    return css, b + "<!--VIS-->" + body, js


def done(D):
    css = """
.list { left: 140px; top: 640px; width: 800px; padding: 34px 40px; }
.it { display: flex; align-items: center; gap: 22px; height: 96px; font: 800 36px/1 PJS; color: var(--ink); }
.bx { width: 54px; height: 54px; border-radius: 14px; border: 5px solid #CFD0DC; position: relative; }
.bx b { position: absolute; inset: -5px; border-radius: 14px; background: var(--grn); color: #fff; font: 800 34px/54px PJS; text-align: center; }
.stamp { left: 280px; top: 1210px; padding: 16px 30px; border: 8px solid var(--grn); border-radius: 22px; color: var(--grn); font: 800 72px/1 Brico;
  transform: rotate(-8deg); background: rgba(16,17,22,.6); }
"""
    items = ("Research done", "Draft written", "Review complete", "Sent to client")
    body = ('<div class="abs card list" id="ls"><div class="lbl" style="margin-bottom:14px">TASK · CLIENT REPORT</div>'
            + "".join(f'<div class="it"><div class="bx"><b id="ck{i}">✓</b></div><span id="tx{i}">{t}</span></div>' for i, t in enumerate(items))
            + '</div><div class="abs stamp" id="st">COMPLETED ✓</div>')
    b, j = top("Task <em>poora</em> ho gaya ✅")
    js = j + f'tl.fromTo("#ls", {IN}, 0.1);'
    for i in range(4):
        at = 0.45 + i * (D * 0.5 - 0.45) / 4
        js += f'tl.fromTo("#ck{i}", {{opacity: 0, scale: 0.3}}, {{opacity: 1, scale: 1, duration: 0.25, ease: "back.out(3)"}}, {at:.2f});'
        js += f'tl.fromTo("#tx{i}", {{color: "#16171B"}}, {{color: "#9A9CA6", duration: 0.2}}, {at:.2f});'
    js += f'tl.fromTo("#st", {{opacity: 0, scale: 2.2, rotation: -25}}, {{opacity: 1, scale: 1, rotation: -8, duration: 0.3, ease: "power3.in"}}, {D * 0.6:.2f});'
    return css, b + "<!--VIS-->" + body, js


def priority(D):
    css = """
.tc { left: 0; top: 0; width: 360px; padding: 18px 22px; border-radius: 20px; background: #fff; color: var(--ink); box-shadow: 0 16px 34px rgba(0,0,0,.45);
  font: 800 30px/1.1 PJS; }
.tc span { display: block; margin-top: 8px; font: 700 20px/1 PJS; color: var(--mut); }
.num { position: absolute; left: -26px; top: -22px; width: 52px; height: 52px; border-radius: 50%; background: var(--ind); color: #fff; font: 800 28px/52px PJS;
  text-align: center; opacity: 0; }
.hi { position: absolute; right: 14px; top: 14px; padding: 6px 10px; border-radius: 10px; background: var(--red); color: #fff; font: 800 18px/1 PJS; opacity: 0; }
.qm { left: 0; top: 860px; width: 1080px; text-align: center; font: 800 220px/1 Brico; color: rgba(255,228,92,.9); }
"""
    tasks = [("Client report 📊", "Due today"), ("Team meeting 👥", "11 AM"), ("Emails ✉️", "23 unread"), ("Budget sheet 📈", "Due Friday"), ("Slides 🖥️", "Next week")]
    scat = [(130, 700, -9), (560, 760, 7), (200, 1030, 5), (590, 1090, -6), (360, 1330, 4)]
    body = "".join(f'<div class="abs tc" id="t{i}" style="left:{x}px;top:{y}px;transform:rotate({r}deg)"><div class="num" id="n{i}">{i + 1}</div>'
                   f'{"<div class=hi id=hi>HIGH</div>" if i == 0 else ""}{a}<span>{s}</span></div>' for i, ((a, s), (x, y, r)) in enumerate(zip(tasks, scat)))
    body += '<div class="abs qm" id="qm">?</div>'
    b, j = top("Bahut saare tasks… <em>pehle</em> kaunsa? 🤯")
    js = j
    for i in range(5):
        js += f'tl.fromTo("#t{i}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)"}}, {0.15 + 0.12 * i:.2f});'
        js += f'tl.to("#t{i}", {{x: {(-1) ** i * 10}, duration: 0.09, yoyo: true, repeat: 7, ease: "sine.inOut"}}, {0.9 + 0.03 * i:.2f});'
    js += f'tl.fromTo("#qm", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)"}}, 1.0);'
    sort_at = D * 0.5
    js += f'tl.to("#qm", {{opacity: 0, scale: 1.4, duration: 0.3}}, {sort_at - 0.1:.2f});'
    for i in range(5):
        x0, y0, _ = scat[i]
        js += f'tl.to("#t{i}", {{x: {360 - x0}, y: {660 + i * 140 - y0}, rotation: 0, duration: 0.6, ease: "power3.inOut"}}, {sort_at + 0.06 * i:.2f});'
        js += f'tl.to("#n{i}", {{opacity: 1, duration: 0.2}}, {sort_at + 0.6 + 0.08 * i:.2f});'
    js += f'tl.fromTo("#hi", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)"}}, {sort_at + 1.1:.2f});'
    return css, b + "<!--VIS-->" + body, js


def idea(D):
    css = """
.wb { left: 100px; top: 640px; width: 880px; height: 760px; padding: 30px; }
.bulb { left: 430px; top: 760px; width: 220px; height: 220px; border-radius: 50%; background: #EDEDF3; font: 120px/220px sans-serif; text-align: center; }
.glow { left: 380px; top: 710px; width: 320px; height: 320px; border-radius: 50%; background: radial-gradient(circle, rgba(255,228,92,.85), rgba(255,228,92,0) 70%); }
.stk { left: 330px; top: 1030px; width: 420px; padding: 22px 26px; background: var(--y); color: var(--ink); border-radius: 4px 4px 20px 4px;
  transform: rotate(-3deg); box-shadow: 0 16px 30px rgba(0,0,0,.35); font: 700 54px/1 Cav; }
.stk small { display: block; font: 800 20px/1 PJS; letter-spacing: 2px; margin-bottom: 8px; }
.vote { left: 260px; top: 1240px; width: 560px; display: flex; gap: 14px; justify-content: center; }
.vote span { padding: 12px 18px; border-radius: 22px; background: #EDEDF3; color: var(--ink); font: 800 30px/1 PJS; }
.ok2 { left: 0; top: 1460px; width: 1080px; text-align: center; font: 800 40px/1 PJS; color: #fff; }
"""
    body = ('<div class="abs card wb" id="wb"><div class="lbl">TEAM BOARD · IDEAS</div></div><div class="abs glow" id="gl"></div><div class="abs bulb" id="bb">💡</div>'
            '<div class="abs stk" id="sk"><small>SUGGESTION</small>Automate the weekly report?</div>'
            '<div class="abs vote" id="vt"><span>👍 <b id="vc">0</b></span><span id="v2">🔥 3</span><span id="v3">👏 2</span></div>'
            '<div class="abs ok2" id="ok">Team: <span style="color:var(--y)">“Let’s consider it!”</span></div>')
    b, j = top("Mere paas ek <em>idea</em> hai 💡")
    js = j + f'tl.fromTo("#wb", {IN}, 0.1);tl.fromTo("#bb", {POP}, 0.4);tl.fromTo("#gl", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.5}}, 0.9);'
    js += f'tl.to("#bb", {{backgroundColor: "#FFF3B0", duration: 0.3}}, 0.9);'
    js += f'tl.fromTo("#sk", {{opacity: 0, y: -120, rotation: -15}}, {{opacity: 1, y: 0, rotation: -3, duration: 0.5, ease: "back.out(1.6)"}}, {D * 0.3:.2f});'
    js += f'tl.fromTo("#vt span", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3, stagger: 0.12, ease: "back.out(2)"}}, {D * 0.48:.2f});'
    for k in range(1, 6):
        js += f'tl.set("#vc", {{innerHTML: "{k}"}}, {D * 0.52 + 0.18 * k:.2f});'
    js += f'tl.fromTo("#ok", {IN}, {D * 0.7:.2f});'
    return css, b + "<!--VIS-->" + body, js


def leave(D):
    css = """
.mon { left: 120px; top: 640px; width: 840px; padding: 28px 30px; }
.mg { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; margin-top: 18px; }
.mg div { height: 76px; border-radius: 14px; background: #F2F2F7; font: 800 28px/76px PJS; color: var(--ink); text-align: center; }
.mg .h { background: none; height: 30px; font: 800 18px/30px PJS; color: var(--mut); }
.mg .today { background: var(--ind); color: #fff; } .mg .tom { background: #FFE1E2; }
.circ { left: 0; top: 0; width: 100px; height: 100px; border-radius: 50%; border: 6px solid var(--red); }
.lv { left: 0; top: 0; padding: 12px 20px; border-radius: 16px; background: var(--y); color: var(--ink); font: 800 32px/1 PJS; transform: rotate(-6deg);
  box-shadow: 0 12px 26px rgba(0,0,0,.35); }
.comp { left: 90px; top: 1360px; width: 900px; height: 116px; border-radius: 58px; background: #fff; display: flex; align-items: center; padding: 0 30px;
  font: 700 42px/1 PJS; color: #B5B6BE; box-shadow: 0 22px 50px rgba(0,0,0,.45); }
.comp i { display: inline-block; width: 4px; height: 48px; background: var(--ind); margin-left: 6px; }
"""
    cells = "".join(f'<div class="h">{d}</div>' for d in ("M", "T", "W", "T", "F", "S", "S"))
    days = [""] * 2 + [str(d) for d in range(1, 31)]
    for k, d in enumerate(days[:35]):
        cls = ' class="today"' if d == "12" else (' class="tom"' if d == "13" else "")
        cells += f'<div{cls} id="d{d or "x" + str(k)}">{d}</div>'
    body = (f'<div class="abs card mon" id="mn"><div class="lbl">NOVEMBER</div><div class="mg">{cells}</div></div>'
            '<div class="abs circ" id="cc" style="left:151px;top:910px"></div>'
            '<div class="abs lv" id="lv" style="left:250px;top:1010px">🏖️ Leave tomorrow (13th)?</div>'
            '<div class="abs comp" id="cm" style="top:1300px">Type in English…<i id="cr"></i></div>')
    b, j = top("Kal office nahi jaana… <em>chhutti</em> chahiye 🏖️")
    js = j + f'tl.fromTo("#mn", {IN}, 0.1);'
    js += f'tl.fromTo("#cc", {{opacity: 0, scale: 1.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "power3.out"}}, {D * 0.25:.2f});'
    js += f'tl.fromTo("#lv", {POP}, {D * 0.38:.2f});tl.fromTo("#cm", {IN}, {D * 0.55:.2f});'
    js += f'tl.fromTo("#cr", {{opacity: 1}}, {{opacity: 0, duration: 0.35, yoyo: true, repeat: 7, ease: "steps(1)"}}, {D * 0.6:.2f});'
    return css, b + "<!--VIS-->" + body, js


SCENES = {"hook": hook, "update": update, "delay": delay, "help": help_, "done": done, "priority": priority, "idea": idea, "leave": leave}


def write():
    durs = {b["key"]: b["dur"] for b in SP.brolls()}
    for name, fn in SCENES.items():
        D = durs[name] + 0.2
        css, body, js = fn(D)
        d = HERE / name
        (d / "vendor").mkdir(parents=True, exist_ok=True)
        (d / "fonts").mkdir(exist_ok=True)
        shutil.copy(C.ROOT / "node_modules/gsap/dist/gsap.min.js", d / "vendor/gsap.min.js")
        for f in (EDIT / "board" / "fonts").glob("*.woff2"):
            shutil.copy(f, d / "fonts" / f.name)
        (d / "hyperframes.json").write_text('{"name":"nikita9-%s"}\n' % name)
        tx, vis = body.split("<!--VIS-->")
        body = tx + '<div id="vis" style="position:absolute;inset:0;transform:translateY(60px) scale(1.07);transform-origin:50% 36%">' + vis + "</div>"
        (d / "index.html").write_text(HEAD.replace("%CSS%", css).replace("%BODY%", body).replace("%JS%", js).replace("%DUR%", f"{D:.3f}"))
        print("wrote", name, f"{D:.2f}s")


def render(names=None):
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names or SCENES:
        subprocess.run(["npx", "hyperframes", "render", str(HERE / name), "-o", str(OUT / f"{name}.mp4"), "--quality", "high", "--quiet"],
                       check=True, env=ENV, cwd=C.ROOT, stdout=subprocess.DEVNULL)
        print("rendered", name, flush=True)


if __name__ == "__main__":
    write()
    if "render" in sys.argv:
        render([a for a in sys.argv[2:]] or None)
