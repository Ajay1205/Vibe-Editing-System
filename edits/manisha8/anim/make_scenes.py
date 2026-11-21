"""Animated cutaways for Manisha 8 (V3 animated, V4 shortest). Grown-up flat editorial style (see CLAUDE.md, Nikita 6
cutaways): no cartoon characters or faces, calm power3 motion, few emoji, the video's palette (deep teal #17423C,
mint #CFEADF, paper #FFF9EE, pencil yellow #FFC94A, red #E8475A). Each scene carries its own text (the caption layer
is off during cutaways). Text sits at the top (y 300-660), the visual below (y 720-1700). 1080x1920 stage rendered
natively at 2160x3840.

  python3 -I anim/make_scenes.py [render]      -> anim/<name>/  (+ footage/manisha8/broll/<name>.mp4)

*_s = with her sentence (V3); *_w = word flash (V4, cut in at 0.95 s, when the visual is complete).
"""

import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
EDIT = HERE.parent
ROOT = EDIT.parents[1]
OUT = ROOT / "footage" / "manisha8" / "broll"

HEAD = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: Anton; src: url(fonts/anton.woff2); }
@font-face { font-family: Brico; src: url(fonts/brico800.woff2); font-weight: 800; }
@font-face { font-family: Cav; src: url(fonts/caveat700.woff2); font-weight: 700; }
@font-face { font-family: PJS; src: url(fonts/pjs800.woff2); font-weight: 800; }
:root { --teal: #17423C; --mint: #CFEADF; --paper: #FFF9EE; --pen: #FFC94A; --red: #E8475A; --ink: #23324A; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #0E2A26; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; background: #0E2A26; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; overflow: hidden;
  background: radial-gradient(ellipse at 50% 58%, #22584E 0%, #17423C 50%, #0E2A26 100%); }
#cam { position: absolute; inset: 0; transform-origin: 50% 60%; }
.abs { position: absolute; }
.top { left: 40px; top: 300px; width: 1000px; text-align: center; font: 800 76px/1.12 Brico; color: #fff; }
.top .hl { display: inline-block; padding: 0 16px; border-radius: 16px; background: var(--pen); color: var(--ink); }
.sub { left: 0; top: 0; width: 1080px; text-align: center; font: 800 36px/1 PJS; color: var(--mint); letter-spacing: 1px; }
.chip { padding: 14px 26px; border-radius: 34px; background: var(--pen); color: var(--teal); font: 800 36px/1 PJS; letter-spacing: 2px;
  box-shadow: 0 12px 26px rgba(0,0,0,.35); white-space: nowrap; }
.word { left: 0; top: 300px; width: 1080px; text-align: center; font: 400 150px/1 Anton; color: #fff; text-transform: uppercase; }
.word small { display: block; font: 800 44px/1 PJS; letter-spacing: 8px; color: var(--pen); margin-bottom: 18px; }
.card { border-radius: 36px; background: var(--paper); box-shadow: 0 40px 90px rgba(0,0,0,.5); overflow: hidden; }
%CSS%
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%" data-width="2160" data-height="3840" data-fps="30">
<div id="stage"><div id="cam">
%BODY%
</div></div></div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#cam", {scale: 1.0}, {scale: 1.05, duration: %DUR%, ease: "none"}, 0);
  %JS%
  window.__timelines["main"] = tl;
</script></body></html>
"""


def top_sentence(text, hl, sub=""):
    t = text.replace(hl, f'<span class="hl">{hl}</span>', 1)
    s = f'<div class="abs top" id="tp">{t}' + (f'<div class="sub" style="position:static;margin-top:16px">{sub}</div>' if sub else "") + '</div>'
    js = 'tl.fromTo("#tp", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 0.05);'
    js += 'tl.fromTo("#tp .hl", {backgroundColor: "rgba(255,201,74,0)", color: "#ffffff"}, {backgroundColor: "rgba(255,201,74,1)", color: "#23324A", duration: 0.3}, 0.6);'
    return s, js


def top_word(kind, word):
    return (f'<div class="abs word" id="wd"><small>{kind}</small>{word}</div>',
            'tl.fromTo("#wd", {opacity: 0, scale: 1.3}, {opacity: 1, scale: 1, duration: 0.3, ease: "power3.out"}, 0.0);')


# ------------------------------------------------------------------------------------------------ visuals
def v_badge():  # Ria: a conference-style name badge, the name handwritten in
    css = """
.lan { left: 520px; top: 640px; width: 40px; height: 260px; background: linear-gradient(90deg, #E8475A, #C93448); border-radius: 10px; }
.badge { left: 230px; top: 860px; width: 620px; height: 760px; border-radius: 44px; background: var(--paper); box-shadow: 0 40px 90px rgba(0,0,0,.5); overflow: hidden; }
.bh { left: 0; top: 0; width: 620px; height: 210px; background: var(--red); text-align: center; color: #fff; }
.bh b { display: block; padding-top: 44px; font: 400 92px/1 Anton; letter-spacing: 4px; }
.bh i { display: block; font: 800 34px/1 PJS; font-style: normal; letter-spacing: 3px; margin-top: 8px; }
.clipw { left: 0; top: 300px; width: 620px; height: 240px; overflow: hidden; }
.name { left: 0; top: 0; width: 620px; text-align: center; font: 700 220px/1 Cav; color: var(--ink); }
.line { left: 90px; top: 560px; width: 440px; height: 6px; background: #D9D0C2; border-radius: 3px; }
.ph { left: 270px; top: 600px; width: 80px; height: 80px; border-radius: 50%; background: #CFEADF; }
.ph2 { left: 230px; top: 670px; width: 160px; height: 90px; border-radius: 80px 80px 0 0; background: #CFEADF; }
.hole { left: 280px; top: 24px; width: 60px; height: 16px; border-radius: 8px; background: rgba(0,0,0,.25); }
.pc { left: 640px; top: 1560px; }"""
    body = """<div class="abs lan"></div>
<div class="abs badge" id="bd"><div class="abs bh"><b>HELLO</b><i>MY NAME IS</i></div><div class="abs hole"></div>
<div class="abs clipw" id="cw"><div class="abs name">Ria</div></div><div class="abs line"></div><div class="abs ph"></div><div class="abs ph2"></div></div>
<div class="abs chip pc" id="pc">👤 PERSON</div>"""
    js = """tl.fromTo("#bd, .lan", {y: -500, rotation: -6}, {y: 0, rotation: 0, duration: 0.55, ease: "power3.out"}, 0.0);
tl.fromTo("#cw", {width: 0}, {width: 620, duration: 0.5, ease: "power1.inOut"}, 0.4);
tl.to("#bd", {rotation: 2, duration: 0.6, yoyo: true, repeat: 3, ease: "sine.inOut", transformOrigin: "50% 0%"}, 0.6);
tl.fromTo("#pc", {opacity: 0, x: 60}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 0.75);"""
    return css, body, js


def v_map():  # Mumbai: a city map, the pin drops, coastline
    css = """
.map { left: 120px; top: 720px; width: 840px; height: 900px; border-radius: 40px; background: #EAF3EC; overflow: hidden; box-shadow: 0 40px 90px rgba(0,0,0,.5); }
.road { background: #FFFFFF; border-radius: 10px; }
.sea { left: 0; top: 0; width: 260px; height: 900px; background: #BFE0EE; border-radius: 0 60% 40% 0; }
.park { border-radius: 40%; background: #CBE7C8; }
.pin { left: 470px; top: 980px; width: 110px; height: 110px; border-radius: 55px 55px 55px 0; transform: rotate(-45deg); background: var(--red); box-shadow: 0 16px 30px rgba(0,0,0,.35); }
.pin i { position: absolute; left: 35px; top: 35px; width: 40px; height: 40px; border-radius: 50%; background: #fff; }
.ring { left: 445px; top: 1060px; width: 160px; height: 60px; border-radius: 50%; border: 6px solid var(--red); }
.city { left: 360px; top: 1130px; padding: 14px 26px; border-radius: 30px; background: #fff; font: 800 48px/1 Brico; color: var(--ink); box-shadow: 0 12px 26px rgba(0,0,0,.25); }
.pc { left: 600px; top: 1560px; }"""
    body = """<div class="abs map" id="mp"><div class="abs sea"></div>
 <div class="abs road" style="left:200px;top:300px;width:700px;height:30px;transform:rotate(-12deg)"></div>
 <div class="abs road" style="left:420px;top:0;width:30px;height:900px;transform:rotate(8deg)"></div>
 <div class="abs road" style="left:250px;top:620px;width:620px;height:22px;transform:rotate(6deg)"></div>
 <div class="abs park" style="left:560px;top:420px;width:200px;height:150px"></div><div class="abs park" style="left:300px;top:720px;width:160px;height:120px"></div></div>
<div class="abs ring" id="rg"></div><div class="abs pin" id="pn"><i></i></div><div class="abs city" id="ct">Mumbai</div>
<div class="abs chip pc" id="pc">📍 PLACE</div>"""
    js = """tl.fromTo("#mp", {opacity: 0, y: 120, scale: 0.94}, {opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power3.out"}, 0.0);
tl.fromTo("#pn", {y: -400, opacity: 0}, {y: 0, opacity: 1, duration: 0.4, ease: "power3.in"}, 0.3);
tl.fromTo("#rg", {scale: 0.2, opacity: 1}, {scale: 1.6, opacity: 0, duration: 0.7, ease: "power2.out"}, 0.7);
tl.fromTo("#ct", {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}, 0.62);
tl.fromTo("#pc", {opacity: 0, x: 60}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 0.8);"""
    return css, body, js


def v_tiger():  # tiger: dark jungle, glowing eyes, paw prints, a stripe card
    css = """
.jun { left: 60px; top: 700px; width: 960px; height: 980px; border-radius: 40px; background: radial-gradient(ellipse at 50% 60%, #1D3B22, #0B1A0E); overflow: hidden;
  box-shadow: 0 40px 90px rgba(0,0,0,.6); }
.leaf { border-radius: 0 100% 0 100%; background: #2F6B3A; }
.eye { width: 70px; height: 40px; border-radius: 50%; background: radial-gradient(circle, #FFE27A 0%, #FFC94A 45%, #B36B00 100%);
  box-shadow: 0 0 40px 10px rgba(255,201,74,.55); }
.eye::after { content: ""; position: absolute; left: 30px; top: 4px; width: 10px; height: 32px; border-radius: 5px; background: #111; }
.paw { font: 64px/1 sans-serif; opacity: 0; filter: grayscale(1) brightness(2.2); }
.stripes { left: 0; top: 0; width: 960px; height: 80px; background: repeating-linear-gradient(115deg, #F28C28 0 50px, #111 50px 80px); }
.pc { left: 620px; top: 1580px; }"""
    body = """<div class="abs jun" id="jn"><div class="abs stripes"></div>
 <div class="abs leaf" style="left:-60px;top:500px;width:420px;height:300px;transform:rotate(-20deg)"></div>
 <div class="abs leaf" style="left:600px;top:560px;width:420px;height:300px;transform:rotate(200deg);background:#245A2F"></div>
 <div class="abs leaf" style="left:250px;top:720px;width:500px;height:320px;transform:rotate(10deg);background:#1F4E29"></div>
 <div class="abs eye" id="e1" style="left:380px;top:360px"></div><div class="abs eye" id="e2" style="left:510px;top:360px"></div>
 <div class="abs paw" style="left:120px;top:860px">🐾</div><div class="abs paw" style="left:300px;top:780px">🐾</div>
 <div class="abs paw" style="left:480px;top:860px">🐾</div><div class="abs paw" style="left:660px;top:780px">🐾</div></div>
<div class="abs chip pc" id="pc">🐯 ANIMAL</div>"""
    js = """tl.fromTo("#jn", {opacity: 0, scale: 0.94}, {opacity: 1, scale: 1, duration: 0.45, ease: "power3.out"}, 0.0);
tl.fromTo(".eye", {opacity: 0, scaleY: 0.1}, {opacity: 1, scaleY: 1, duration: 0.25, ease: "power2.out"}, 0.35);
tl.to(".eye", {scaleY: 0.1, duration: 0.07, yoyo: true, repeat: 1}, 1.4);
tl.to(".paw", {opacity: 0.9, duration: 0.15, stagger: 0.18}, 0.55);
tl.fromTo("#pc", {opacity: 0, x: 60}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 0.75);"""
    return css, body, js


def v_pencil():  # pencil: a paper card, a pencil writes "pencil" and underlines it
    css = """
.paper { left: 110px; top: 740px; width: 860px; height: 760px; border-radius: 30px; background: var(--paper); box-shadow: 0 40px 90px rgba(0,0,0,.5);
  background-image: repeating-linear-gradient(180deg, transparent 0 79px, #CFE0EE 79px 82px); overflow: hidden; }
.mg { left: 90px; top: 0; width: 4px; height: 760px; background: var(--red); opacity: .7; }
.wclip { left: 150px; top: 250px; width: 0; height: 220px; overflow: hidden; }
.wtxt { left: 0; top: 0; width: 700px; font: 700 200px/1 Cav; color: var(--ink); white-space: nowrap; }
.ul { left: 160px; top: 470px; width: 560px; height: 14px; border-radius: 7px; background: var(--pen); transform-origin: 0 50%; }
.pencil { left: 0; top: 0; width: 520px; height: 64px; transform-origin: 0 50%; }
.body { left: 70px; top: 0; width: 380px; height: 64px; background: linear-gradient(180deg, #FFD86B, #FFC94A 50%, #E9A92A); }
.tip { left: 0; top: 0; width: 72px; height: 64px; background: #F1D2A8; clip-path: polygon(0 50%, 100% 0, 100% 100%); }
.lead { left: 0; top: 22px; width: 24px; height: 20px; background: #333; clip-path: polygon(0 50%, 100% 0, 100% 100%); }
.band { left: 450px; top: 0; width: 26px; height: 64px; background: #B9BAC4; }
.eras { left: 476px; top: 0; width: 60px; height: 64px; border-radius: 0 18px 18px 0; background: #F7B3C2; }
.pwrap { left: 150px; top: 380px; transform: rotate(-35deg); transform-origin: 0 50%; }
.pc { left: 640px; top: 1560px; }"""
    body = """<div class="abs paper" id="pp"><div class="abs mg"></div>
 <div class="abs wclip" id="wc"><div class="abs wtxt">pencil</div></div><div class="abs ul" id="ul"></div>
 <div class="abs pwrap" id="pw"><div class="abs pencil"><div class="abs body"></div><div class="abs tip"></div><div class="abs lead"></div>
  <div class="abs band"></div><div class="abs eras"></div></div></div></div>
<div class="abs chip pc" id="pc">✏️ THING</div>"""
    js = """tl.fromTo("#pp", {opacity: 0, y: 120, rotation: 3}, {opacity: 1, y: 0, rotation: 0, duration: 0.45, ease: "power3.out"}, 0.0);
tl.fromTo("#pw", {x: 0, y: -60}, {x: 560, y: -60, duration: 0.6, ease: "none"}, 0.25);
tl.fromTo("#wc", {width: 0}, {width: 620, duration: 0.6, ease: "none"}, 0.25);
tl.to("#pw", {x: 30, y: 60, duration: 0.25, ease: "power2.inOut"}, 0.88);
tl.fromTo("#ul", {scaleX: 0}, {scaleX: 1, duration: 0.35, ease: "power2.out"}, 1.1);
tl.to("#pw", {x: 600, y: 60, duration: 0.35, ease: "power2.out"}, 1.1);
tl.fromTo("#pc", {opacity: 0, x: 60}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 0.75);"""
    return css, body, js


def person(x, y, c="#CFEADF", s=1.0, id_=""):
    return (f'<div class="abs pp" {id_} style="left:{x}px;top:{y}px;transform:scale({s});transform-origin:50% 100%">'
            f'<div class="abs" style="left:30px;top:0;width:80px;height:80px;border-radius:50%;background:{c}"></div>'
            f'<div class="abs" style="left:0;top:90px;width:140px;height:110px;border-radius:70px 70px 20px 20px;background:{c}"></div></div>')


def v_naming(end=False):  # naming word: four things, each gets a hanging name tag
    css = """
.cell { width: 380px; height: 400px; border-radius: 36px; background: rgba(255,249,238,.08); border: 3px solid rgba(207,234,223,.25); }
.ic { left: 0; top: 70px; width: 380px; text-align: center; font: 150px/1 sans-serif; }
.tagx { left: 70px; top: 255px; width: 240px; padding: 18px 0; border-radius: 16px 50px 50px 16px; background: var(--pen); color: var(--ink);
  text-align: center; font: 700 64px/1 Cav; box-shadow: 0 12px 24px rgba(0,0,0,.35); transform-origin: 10% 50%; }
.tagx::before { content: ""; position: absolute; left: 16px; top: 36px; width: 18px; height: 18px; border-radius: 50%; background: var(--teal); }
.fol { left: 140px; top: 1660px; width: 800px; text-align: center; padding: 22px 0; border-radius: 50px; background: var(--red); color: #fff;
  font: 800 40px/1 PJS; box-shadow: 0 14px 30px rgba(0,0,0,.35); }
.bigt { left: 0; top: 300px; width: 1080px; text-align: center; font: 400 120px/1.02 Anton; color: #fff; }
.bigt em { font-style: normal; color: var(--pen); }"""
    cells = [("Ria", "👤", 120, 720), ("Mumbai", "📍", 580, 720), ("Tiger", "🐯", 120, 1160), ("Pencil", "✏️", 580, 1160)]
    body = '<div class="abs bigt" id="bt">NOUN =<br><em>NAMING WORD</em></div>' + "".join(
        f'<div class="abs cell" id="c{k}" style="left:{x}px;top:{y}px"><div class="abs ic">{ic}</div><div class="abs tagx" id="t{k}">{n}</div></div>'
        for k, (n, ic, x, y) in enumerate(cells))
    if end:
        body += '<div class="abs fol" id="fo">🔔 Follow karo — Part 2 aa raha hai</div>'
    js = """tl.fromTo("#bt", {opacity: 0, scale: 1.3}, {opacity: 1, scale: 1, duration: 0.35, ease: "power3.out"}, 0.0);
tl.fromTo(".cell", {opacity: 0, y: 60}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out", stagger: 0.08}, 0.15);
tl.fromTo(".tagx", {opacity: 0, rotation: -40, x: -30}, {opacity: 1, rotation: 0, x: 0, duration: 0.45, ease: "power3.out", stagger: 0.18}, 0.5);
tl.to(".tagx", {rotation: 5, duration: 0.6, yoyo: true, repeat: 4, ease: "sine.inOut", stagger: 0.1}, 1.2);"""
    if end:
        js += 'tl.fromTo("#fo", {opacity: 0, y: 40}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 2.3);tl.to("#fo", {scale: 1.05, duration: 0.35, yoyo: true, repeat: 5, ease: "sine.inOut"}, 2.8);'
    return css, body, js


def v_game():  # bachpan ka game: a notebook page, the round starts -- letter stamp, timer, columns being ruled
    css = """
.nbk { left: 90px; top: 760px; width: 900px; height: 860px; border-radius: 26px; background: var(--paper); box-shadow: 0 40px 90px rgba(0,0,0,.5); overflow: hidden;
  background-image: repeating-linear-gradient(180deg, transparent 0 79px, #CFE0EE 79px 82px); transform: rotate(-3deg); }
.mg { left: 80px; top: 0; width: 4px; height: 860px; background: var(--red); opacity: .7; }
.vl { top: 0; width: 4px; height: 860px; background: #9DB3C6; transform-origin: 50% 0; }
.hdw { top: 100px; width: 200px; text-align: center; font: 700 52px/1 Cav; color: var(--ink); }
.stamp { left: 640px; top: 640px; width: 220px; height: 220px; border-radius: 50%; border: 8px solid var(--red); color: var(--red); text-align: center;
  font: 400 140px/200px Anton; background: rgba(255,249,238,.9); transform: rotate(-12deg); }
.stamp small { position: absolute; left: 0; top: 22px; width: 204px; font: 800 22px/1 PJS; letter-spacing: 3px; }
.timer { left: 120px; top: 640px; padding: 16px 26px; border-radius: 34px; background: var(--teal); color: var(--pen); font: 800 46px/1 PJS; letter-spacing: 2px; }
.tt { left: 0; top: 330px; width: 1080px; text-align: center; font: 700 96px/1.05 Cav; color: #fff; }
.tt b { color: var(--pen); font-weight: 700; }"""
    xs = [84, 288, 492, 696]
    heads = ["Name", "Place", "Animal", "Thing"]
    body = ('<div class="abs tt" id="tt">Yaad hai ye <b>game?</b> 🎮</div>'
            '<div class="abs nbk" id="nb"><div class="abs mg"></div>'
            + "".join(f'<div class="abs vl" style="left:{x + 200}px"></div>' for x in xs[:3])
            + "".join(f'<div class="abs hdw" style="left:{x}px">{h}</div>' for x, h in zip(xs, heads))
            + '</div><div class="abs timer" id="tm">⏱ 00:10</div><div class="abs stamp" id="st"><small>LETTER</small>R</div>')
    js = """tl.fromTo("#tt", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 0.05);
tl.fromTo("#nb", {opacity: 0, y: 160, rotation: 4}, {opacity: 1, y: 0, rotation: -3, duration: 0.55, ease: "power3.out"}, 0.1);
tl.fromTo(".vl", {scaleY: 0}, {scaleY: 1, duration: 0.4, ease: "power2.out", stagger: 0.12}, 0.5);
tl.fromTo(".hdw", {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: 0.3, ease: "power3.out", stagger: 0.2}, 0.7);
tl.fromTo("#st", {opacity: 0, scale: 2, rotation: 20}, {opacity: 1, scale: 1, rotation: -12, duration: 0.25, ease: "power3.in"}, 1.5);
tl.fromTo("#tm", {opacity: 0, x: -60}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 1.2);
["00:09","00:08","00:07"].forEach((t, i) => tl.call(() => document.querySelector("#tm").textContent = "⏱ " + t, null, 1.9 + i * 0.5));"""
    return css, body, js


def v_proper():  # proper vs common: "friend" = any of many people, "Ria" = one particular person
    css = """
.side { top: 760px; width: 440px; height: 820px; border-radius: 36px; background: rgba(255,249,238,.08); border: 3px solid rgba(207,234,223,.3); }
.lbl { left: 0; top: 40px; width: 440px; text-align: center; font: 700 96px/1 Cav; color: #fff; }
.kind { left: 70px; top: 680px; width: 300px; padding: 18px 0; border-radius: 40px; text-align: center; font: 800 38px/1 PJS; letter-spacing: 2px; }
.co { background: var(--mint); color: var(--teal); } .pr { background: var(--pen); color: var(--teal); }
.cap { left: 0; top: 590px; width: 440px; text-align: center; font: 800 30px/1.2 PJS; color: var(--mint); }
.vs { left: 490px; top: 1080px; width: 100px; text-align: center; font: 400 70px/1 Anton; color: var(--pen); }
.glow { box-shadow: 0 0 0 6px var(--pen), 0 0 60px 10px rgba(255,201,74,.45); border-radius: 36px; }"""
    body = ('<div class="abs top" id="tp" style="font-size:80px">My friend is <span class="hl">Ria.</span></div>'
            '<div class="abs side" id="sl" style="left:60px"><div class="abs lbl">friend</div>'
            + person(70, 200, "#CFEADF", 0.9) + person(230, 200, "#CFEADF", 0.9) + person(150, 360, "#CFEADF", 0.9)
            + '<div class="abs cap">koi bhi dost</div><div class="abs kind co">COMMON</div></div>'
            '<div class="abs vs" id="vs">VS</div>'
            '<div class="abs side" id="sr" style="left:580px"><div class="abs lbl">Ria</div>'
            + person(150, 250, "#FFC94A", 1.3)
            + '<div class="abs cap">ek khaas insaan</div><div class="abs kind pr">PROPER</div></div>')
    js = """tl.fromTo("#tp", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 0.05);
tl.fromTo("#sl", {opacity: 0, x: -80}, {opacity: 1, x: 0, duration: 0.45, ease: "power3.out"}, 0.3);
tl.fromTo("#sr", {opacity: 0, x: 80}, {opacity: 1, x: 0, duration: 0.45, ease: "power3.out"}, 0.6);
tl.fromTo("#vs", {opacity: 0, scale: 0.4}, {opacity: 1, scale: 1, duration: 0.3, ease: "power3.out"}, 0.8);
tl.fromTo("#tp .hl", {backgroundColor: "rgba(255,201,74,0)", color: "#ffffff"}, {backgroundColor: "rgba(255,201,74,1)", color: "#23324A", duration: 0.3}, 1.0);
tl.call(() => document.querySelector("#sr").classList.add("glow"), null, 1.2);"""
    return css, body, js


def v_part2():  # part 2: a "next episode" card with a progress bar
    css = """
.ep { left: 110px; top: 760px; width: 860px; height: 760px; border-radius: 40px; background: #0B211E; box-shadow: 0 40px 90px rgba(0,0,0,.6); overflow: hidden; }
.thumb { left: 0; top: 0; width: 860px; height: 460px; background: linear-gradient(135deg, #22584E, #17423C 60%, #E8475A 140%); }
.tk { left: 60px; top: 70px; font: 400 150px/1 Anton; color: var(--pen); }
.tv { left: 60px; top: 240px; width: 740px; font: 800 64px/1.1 Brico; color: #fff; }
.play { left: 690px; top: 330px; width: 120px; height: 120px; border-radius: 50%; background: var(--paper); box-shadow: 0 12px 30px rgba(0,0,0,.4); }
.play::after { content: ""; position: absolute; left: 46px; top: 32px; border-left: 40px solid var(--red); border-top: 28px solid transparent; border-bottom: 28px solid transparent; }
.nx { left: 60px; top: 520px; font: 800 34px/1 PJS; letter-spacing: 3px; color: var(--mint); }
.bar { left: 60px; top: 600px; width: 740px; height: 14px; border-radius: 7px; background: rgba(255,255,255,.15); }
.fill { left: 60px; top: 600px; width: 740px; height: 14px; border-radius: 7px; background: var(--red); transform-origin: 0 50%; }
.tt { left: 0; top: 330px; width: 1080px; text-align: center; font: 700 96px/1.05 Cav; color: #fff; }
.tt b { color: var(--pen); font-weight: 700; }"""
    body = ('<div class="abs tt" id="tt">Difference jaanna hai? <b>👇</b></div>'
            '<div class="abs ep" id="ep"><div class="abs thumb"></div><div class="abs tk">PART 2</div>'
            '<div class="abs tv">Proper vs Common Noun</div><div class="abs play" id="pl"></div>'
            '<div class="abs nx">NEXT EPISODE · COMING UP</div><div class="abs bar"></div><div class="abs fill" id="fl"></div></div>')
    js = """tl.fromTo("#tt", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 0.05);
tl.fromTo("#ep", {opacity: 0, y: 140, scale: 0.94}, {opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power3.out"}, 0.15);
tl.fromTo("#pl", {opacity: 0, scale: 0.4}, {opacity: 1, scale: 1, duration: 0.35, ease: "power3.out"}, 0.6);
tl.fromTo("#fl", {scaleX: 0}, {scaleX: 1, duration: 2.4, ease: "power1.inOut"}, 0.7);"""
    return css, body, js



# ------------------------------------------------------------------------------------------------ v2 visuals (user, 21 Nov)
def v_girl():  # Ria: an illustrated young woman who waves and says hi (user: "the Ria animation should have a girl")
    css = """
.gcard { left: 120px; top: 720px; width: 840px; height: 980px; border-radius: 40px; overflow: hidden;
  background: radial-gradient(ellipse at 50% 40%, #FFE9D6, #F7C9B0 70%); box-shadow: 0 40px 90px rgba(0,0,0,.5); }
.girl { left: 140px; top: 140px; width: 560px; height: 840px; }
.bub { left: 470px; top: 820px; padding: 22px 34px; border-radius: 40px 40px 40px 10px; background: #fff; font: 700 70px/1 Cav; color: var(--ink);
  box-shadow: 0 14px 30px rgba(0,0,0,.25); white-space: nowrap; }
.pc { left: 640px; top: 1600px; }"""
    svg = """<svg class="abs girl" viewBox="0 0 560 840">
 <path d="M120 300 C 90 520, 80 700, 110 840 L 450 840 C 480 700, 470 520, 440 300 Z" fill="#2B1A13"/>
 <path d="M60 840 C 70 700, 160 640, 280 640 C 400 640, 490 700, 500 840 Z" fill="#E8475A"/>
 <path d="M200 660 L 280 740 L 360 660 Z" fill="#C93448"/>
 <rect x="240" y="540" width="80" height="120" rx="30" fill="#D99B72"/>
 <ellipse cx="280" cy="400" rx="150" ry="180" fill="#E6AE86"/>
 <circle cx="128" cy="420" r="26" fill="#D99B72"/><circle cx="432" cy="420" r="26" fill="#D99B72"/>
 <circle cx="128" cy="462" r="10" fill="#FFC94A"/><circle cx="432" cy="462" r="10" fill="#FFC94A"/>
 <path d="M120 360 C 110 200, 220 150, 300 170 C 400 190, 460 260, 440 380 C 400 300, 330 260, 250 280 C 190 290, 150 320, 120 360 Z" fill="#2B1A13"/>
 <g id="eyes"><ellipse cx="225" cy="410" rx="16" ry="20" fill="#2B1A13"/><ellipse cx="335" cy="410" rx="16" ry="20" fill="#2B1A13"/>
  <circle cx="231" cy="403" r="5" fill="#fff"/><circle cx="341" cy="403" r="5" fill="#fff"/></g>
 <path d="M195 372 Q 225 358 255 370" stroke="#2B1A13" stroke-width="8" fill="none" stroke-linecap="round"/>
 <path d="M305 370 Q 335 358 365 372" stroke="#2B1A13" stroke-width="8" fill="none" stroke-linecap="round"/>
 <circle cx="280" cy="360" r="7" fill="#E8475A"/>
 <path d="M272 430 Q 280 462 290 440" stroke="#C98A62" stroke-width="6" fill="none" stroke-linecap="round"/>
 <path d="M235 492 Q 280 530 325 492" stroke="#A8423A" stroke-width="9" fill="#fff" stroke-linecap="round"/>
 <ellipse cx="200" cy="470" rx="26" ry="14" fill="#F29A8C" opacity=".55"/><ellipse cx="360" cy="470" rx="26" ry="14" fill="#F29A8C" opacity=".55"/>
 <g id="arm"><path d="M470 760 C 500 680, 520 600, 520 520" stroke="#E8475A" stroke-width="70" stroke-linecap="round" fill="none"/>
  <ellipse cx="522" cy="480" rx="40" ry="50" fill="#E6AE86"/></g>
</svg>"""
    body = f"""<div class="abs gcard" id="gc">{svg}</div><div class="abs bub" id="bb">Hi, I'm Ria! 👋</div>
<div class="abs chip pc" id="pc">👤 PERSON</div>"""
    js = """tl.fromTo("#gc", {opacity: 0, y: 140}, {opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}, 0.0);
tl.fromTo(".girl", {y: 120}, {y: 0, duration: 0.6, ease: "power3.out"}, 0.05);
tl.fromTo("#arm", {rotation: 0, transformOrigin: "470px 760px"}, {rotation: -14, duration: 0.22, yoyo: true, repeat: 7, ease: "sine.inOut"}, 0.45);
tl.to("#eyes", {scaleY: 0.1, transformOrigin: "280px 410px", duration: 0.06, yoyo: true, repeat: 1}, 1.4);
tl.fromTo("#bb", {opacity: 0, scale: 0.4, transformOrigin: "0% 100%"}, {opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.4)"}, 0.55);
tl.fromTo("#pc", {opacity: 0, x: 60}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 0.8);"""
    return css, body, js


def v_tiger_real():  # tiger: an illustrated tiger rises out of the jungle and growls (user: "should show a tiger")
    css = """
.jun2 { left: 60px; top: 700px; width: 960px; height: 1000px; border-radius: 40px; overflow: hidden;
  background: radial-gradient(ellipse at 50% 45%, #2F5E33, #10261A 75%); box-shadow: 0 40px 90px rgba(0,0,0,.6); }
.tig { left: 180px; top: 170px; width: 600px; height: 620px; }
.lf { border-radius: 0 100% 0 100%; }
.grr { left: 640px; top: 880px; font: 400 92px/1 Anton; color: var(--pen); letter-spacing: 4px; transform: rotate(-8deg); }
.pc { left: 620px; top: 1600px; }"""
    svg = """<svg class="abs tig" viewBox="0 0 600 620">
 <path d="M110 130 L 150 30 L 230 110 Z" fill="#E07A1F"/><path d="M490 130 L 450 30 L 370 110 Z" fill="#E07A1F"/>
 <path d="M140 110 L 160 60 L 205 105 Z" fill="#FFF4E6"/><path d="M460 110 L 440 60 L 395 105 Z" fill="#FFF4E6"/>
 <ellipse cx="300" cy="320" rx="250" ry="250" fill="#F28C28"/>
 <path d="M300 90 L 285 170 L 300 200 L 315 170 Z" fill="#1A1A1A"/>
 <path d="M240 110 Q 255 160 245 200" stroke="#1A1A1A" stroke-width="16" fill="none" stroke-linecap="round"/>
 <path d="M360 110 Q 345 160 355 200" stroke="#1A1A1A" stroke-width="16" fill="none" stroke-linecap="round"/>
 <path d="M60 300 Q 120 290 150 320" stroke="#1A1A1A" stroke-width="18" fill="none" stroke-linecap="round"/>
 <path d="M70 360 Q 125 350 150 375" stroke="#1A1A1A" stroke-width="16" fill="none" stroke-linecap="round"/>
 <path d="M540 300 Q 480 290 450 320" stroke="#1A1A1A" stroke-width="18" fill="none" stroke-linecap="round"/>
 <path d="M530 360 Q 475 350 450 375" stroke="#1A1A1A" stroke-width="16" fill="none" stroke-linecap="round"/>
 <ellipse cx="190" cy="430" rx="120" ry="95" fill="#FFF4E6"/><ellipse cx="410" cy="430" rx="120" ry="95" fill="#FFF4E6"/>
 <ellipse cx="300" cy="500" rx="110" ry="80" fill="#FFF4E6"/>
 <g id="teyes"><ellipse cx="205" cy="290" rx="40" ry="30" fill="#D8F06A"/><ellipse cx="395" cy="290" rx="40" ry="30" fill="#D8F06A"/>
  <ellipse cx="205" cy="290" rx="9" ry="26" fill="#111"/><ellipse cx="395" cy="290" rx="9" ry="26" fill="#111"/></g>
 <path d="M160 255 L 245 270" stroke="#1A1A1A" stroke-width="10" stroke-linecap="round"/><path d="M440 255 L 355 270" stroke="#1A1A1A" stroke-width="10" stroke-linecap="round"/>
 <path d="M262 380 L 338 380 L 300 425 Z" fill="#B5545C"/>
 <path d="M300 425 L 300 455" stroke="#1A1A1A" stroke-width="7"/>
 <g id="jaw"><path d="M240 470 Q 300 545 360 470 Q 300 500 240 470 Z" fill="#6B1F24"/>
  <path d="M255 474 L 265 498 L 275 480 Z" fill="#fff"/><path d="M345 474 L 335 498 L 325 480 Z" fill="#fff"/></g>
 <g stroke="#1A1A1A" stroke-width="4" stroke-linecap="round" opacity=".7"><path d="M230 440 L 140 425"/><path d="M230 455 L 145 465"/>
  <path d="M370 440 L 460 425"/><path d="M370 455 L 455 465"/></g>
</svg>"""
    body = f"""<div class="abs jun2" id="jn">{svg}
 <div class="abs lf" style="left:-80px;top:640px;width:460px;height:340px;background:#3E8A45;transform:rotate(-18deg)"></div>
 <div class="abs lf" style="left:600px;top:680px;width:460px;height:340px;background:#2F7A3A;transform:rotate(195deg)"></div>
 <div class="abs lf" style="left:230px;top:820px;width:520px;height:320px;background:#256B31;transform:rotate(8deg)"></div></div>
<div class="abs grr" id="gr">GRRR!</div><div class="abs chip pc" id="pc">🐯 ANIMAL</div>"""
    js = """tl.fromTo("#jn", {opacity: 0, scale: 0.95}, {opacity: 1, scale: 1, duration: 0.4, ease: "power3.out"}, 0.0);
tl.fromTo(".tig", {y: 420}, {y: 0, duration: 0.6, ease: "power3.out"}, 0.1);
tl.fromTo("#jaw", {scaleY: 0.3, transformOrigin: "300px 470px"}, {scaleY: 1.25, duration: 0.18, yoyo: true, repeat: 3, ease: "power2.inOut"}, 0.7);
tl.fromTo(".tig", {x: 0}, {x: 8, duration: 0.05, yoyo: true, repeat: 7, ease: "none"}, 0.7);
tl.fromTo("#gr", {opacity: 0, scale: 0.4}, {opacity: 1, scale: 1, duration: 0.25, ease: "back.out(3)"}, 0.72);
tl.to("#teyes", {scaleY: 0.15, transformOrigin: "300px 290px", duration: 0.06, yoyo: true, repeat: 1}, 1.6);
tl.fromTo("#pc", {opacity: 0, x: 60}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 0.85);"""
    return css, body, js


def v_mumbai_night():  # Mumbai at night: lit high-rises and the Bandra-Worli Sea Link over the sea (user request)
    import random
    rnd = random.Random(8)
    css = """
.night { left: 60px; top: 700px; width: 960px; height: 1000px; border-radius: 40px; overflow: hidden;
  background: linear-gradient(180deg, #0A1230 0%, #1B2A5A 55%, #3B3870 68%, #0B1A33 68.2%, #0A1530 100%); box-shadow: 0 40px 90px rgba(0,0,0,.6); }
.moon { left: 760px; top: 70px; width: 90px; height: 90px; border-radius: 50%; background: #FFF4D6; box-shadow: 0 0 60px 20px rgba(255,244,214,.35); }
.st { width: 4px; height: 4px; border-radius: 50%; background: #fff; }
.bld { bottom: 320px; background: #121B3A; }
.win { width: 8px; height: 10px; background: #FFD66B; box-shadow: 0 0 6px rgba(255,214,107,.8); }
.rl { width: 8px; height: 8px; border-radius: 50%; background: #FF4D5E; box-shadow: 0 0 10px 4px rgba(255,77,94,.7); }
.link { left: 0; top: 560px; width: 960px; height: 240px; }
.refl { left: 0; top: 690px; width: 960px; height: 310px; background: repeating-linear-gradient(180deg, rgba(255,214,107,.10) 0 6px, transparent 6px 18px); }
.car { width: 12px; height: 5px; border-radius: 3px; background: #FFE9A8; box-shadow: 0 0 10px 4px rgba(255,233,168,.8); }
.car.r { background: #FF6B6B; box-shadow: 0 0 10px 4px rgba(255,107,107,.8); }
.tag2 { left: 40px; top: 40px; padding: 14px 26px; border-radius: 30px; background: #fff; font: 800 44px/1 Brico; color: var(--ink); white-space: nowrap; }
.tag2 small { display: block; font: 800 22px/1 PJS; color: #6B6B6B; letter-spacing: 1px; margin-top: 6px; text-align: center; }
.pc { left: 600px; top: 1600px; }"""
    stars = "".join(f'<div class="abs st" style="left:{rnd.randint(20, 940)}px;top:{rnd.randint(20, 380)}px;opacity:{rnd.uniform(.4, 1):.2f}"></div>' for _ in range(40))
    blds, x = [], 10
    for w, h in [(70, 230), (90, 330), (60, 260), (110, 420), (80, 300), (70, 360), (120, 470), (60, 280), (90, 390), (70, 250), (100, 340)]:
        wins = "".join(f'<div class="abs win {"on" if rnd.random() < .55 else "off"}" style="left:{cx}px;top:{cy}px"></div>'
                       for cy in range(24, h - 20, 26) for cx in range(10, w - 14, 20))
        top = f'<div class="abs rl" style="left:{w // 2 - 4}px;top:-14px"></div>' if h > 380 else ""
        blds.append(f'<div class="abs bld" style="left:{x}px;width:{w}px;height:{h}px">{wins}{top}</div>')
        x += w + 12
    link = """<svg class="abs link" viewBox="0 0 960 240">
 <path d="M-10 170 Q 480 120 970 170" stroke="#C9D2E8" stroke-width="10" fill="none"/>
 <path d="M-10 180 Q 480 130 970 180" stroke="#55607E" stroke-width="6" fill="none"/>
 <g stroke="#E8ECF8" stroke-width="10" stroke-linecap="round"><path d="M310 150 L 340 20 L 370 150"/><path d="M590 150 L 620 20 L 650 150"/></g>
 <g stroke="#C9D2E8" stroke-width="2" opacity=".8">
  <path d="M340 30 L 200 160"/><path d="M340 40 L 230 158"/><path d="M340 50 L 260 156"/><path d="M340 60 L 290 154"/>
  <path d="M340 30 L 480 145"/><path d="M340 40 L 450 147"/><path d="M340 50 L 420 149"/><path d="M340 60 L 390 151"/>
  <path d="M620 30 L 480 145"/><path d="M620 40 L 510 147"/><path d="M620 50 L 540 149"/><path d="M620 60 L 570 151"/>
  <path d="M620 30 L 760 155"/><path d="M620 40 L 730 153"/><path d="M620 50 L 700 152"/><path d="M620 60 L 670 151"/></g>
 <g fill="#FFD66B">""" + "".join(f'<circle cx="{px}" cy="{170 - 50 * (1 - ((px - 480) / 490) ** 2) + 2:.0f}" r="3"/>' for px in range(20, 960, 40)) + """</g>
</svg>"""
    cars = "".join(f'<div class="abs car{" r" if k % 2 else ""}" id="car{k}" style="left:-30px;top:{700 + (0 if k % 2 == 0 else 8)}px"></div>' for k in range(6))
    body = f"""<div class="abs night" id="nt"><div class="abs moon"></div>{stars}{''.join(blds)}<div class="abs refl" id="rf"></div>{link}{cars}
 <div class="abs tag2" id="tg">📍 Mumbai<small>BANDRA–WORLI SEA LINK</small></div></div>
<div class="abs chip pc" id="pc">📍 PLACE</div>"""
    js = """tl.fromTo("#nt", {opacity: 0, y: 120, scale: 0.95}, {opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power3.out"}, 0.0);
tl.fromTo(".bld", {scaleY: 0, transformOrigin: "50% 100%"}, {scaleY: 1, duration: 0.5, ease: "power3.out", stagger: 0.03}, 0.1);
tl.fromTo(".win.on", {opacity: 0}, {opacity: 1, duration: 0.3, stagger: {each: 0.003, from: "random"}}, 0.45);
tl.fromTo(".win.off", {opacity: 0}, {opacity: 0.12, duration: 0.3}, 0.45);
tl.fromTo(".link", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}, 0.35);
tl.fromTo(".st", {opacity: 0.2}, {opacity: 1, duration: 0.4, yoyo: true, repeat: 6, stagger: {each: 0.03, from: "random"}}, 0.2);
tl.fromTo(".rl", {opacity: 1}, {opacity: 0.15, duration: 0.3, yoyo: true, repeat: 9, ease: "steps(1)"}, 0.4);
for (let k = 0; k < 6; k++) { const ltr = k % 2 === 0; tl.fromTo("#car" + k, {x: ltr ? 0 : 1000}, {x: ltr ? 1000 : 0, duration: 1.6, ease: "none"}, 0.5 + k * 0.25); }
tl.fromTo("#rf", {opacity: 0.4}, {opacity: 1, duration: 0.5, yoyo: true, repeat: 5, ease: "sine.inOut"}, 0.5);
tl.fromTo("#tg", {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: 0.35, ease: "power3.out"}, 0.75);
tl.fromTo("#pc", {opacity: 0, x: 60}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 0.9);"""
    return css, body, js


SCENES = {}
for name, vis, sent, hl, sub, kind, word in [
        ("ria", v_girl, "Meri friend Ria hai.", "Ria", "My friend is Ria.", "NAME", "Ria"),
        ("mumbai", v_mumbai_night, "Main Mumbai mein rehti hoon.", "Mumbai", "I live in Mumbai.", "PLACE", "Mumbai"),
        ("tiger", v_tiger_real, "Mujhe tiger se dar lagta hai.", "tiger", "I am scared of tigers.", "ANIMAL", "Tiger"),
        ("pencil", v_pencil, "I have a pencil.", "pencil", "", "THING", "Pencil")]:
    SCENES[f"{name}_s"] = (3.6, vis, ("sent", sent, hl, sub))
    SCENES[f"{name}_w"] = (2.0, vis, ("word", kind, word))
SCENES["naming"] = (3.6, lambda: v_naming(False), None)
SCENES["naming_end"] = (5.0, lambda: v_naming(True), None)
SCENES["game"] = (3.6, v_game, None)
SCENES["proper"] = (3.6, v_proper, None)
SCENES["part2"] = (3.6, v_part2, None)


def write():
    for name, (dur, vis, top) in SCENES.items():
        css, body, js = vis()
        if top and top[0] == "sent":
            b, j = top_sentence(top[1], top[2], top[3])
            body, js = b + body, j + js
        elif top and top[0] == "word":
            b, j = top_word(top[1], top[2])
            body, js = b + body, j + js
        d = HERE / name
        (d / "vendor").mkdir(parents=True, exist_ok=True)
        (d / "fonts").mkdir(exist_ok=True)
        shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", d / "vendor/gsap.min.js")
        for f in (EDIT / "board" / "fonts").glob("*.woff2"):
            shutil.copy(f, d / "fonts" / f.name)
        (d / "hyperframes.json").write_text('{"name":"manisha8-anim-%s"}\n' % name)
        (d / "index.html").write_text(HEAD.replace("%CSS%", css).replace("%BODY%", body).replace("%JS%", js).replace("%DUR%", str(dur)))
    print("wrote", len(SCENES), "scenes")


def render(names=None):
    env = dict(os.environ, NODE_USE_ENV_PROXY="1", NODE_EXTRA_CA_CERTS="/root/.ccr/ca-bundle.crt")
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names or SCENES:
        subprocess.run(["npx", "hyperframes", "render", str(HERE / name), "-o", str(OUT / f"{name}.mp4"), "--quality", "high", "--quiet"],
                       check=True, env=env, cwd=ROOT, stdout=subprocess.DEVNULL)
        print("rendered", name, flush=True)


if __name__ == "__main__":
    write()
    if "render" in sys.argv:
        render([a for a in sys.argv[2:]] or None)
