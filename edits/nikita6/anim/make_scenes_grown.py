"""Grown-up animated cutaways for the Nikita 6 examples (user, 19 Nov: audience is 20+; picked the "grown-up"
lock-screen test over the cartoon scenes).

Style rules: real adult moments (apps, chats, work, desks), flat editorial illustration, NO characters or faces,
calm motion (power3/power2 slides, gentle drift; no bounce, no wobble), few emoji, WH Family colours
(cocoa #4A2E22, latte #FFF4E6, heart red #E8475A + the tile pastels), Quicksand for UI text, Baloo for accents.
Each scene: 2.2 s, 1080x1920 stage rendered at 2160x3840; subject below y ~760 (the big question sits above).
"Tum late kyun ho?" (anim/ex3_late_v2) is hand-written in the same style.

Usage: python3 -I make_scenes_grown.py           # write anim/<name>_v2 projects
       python3 -I make_scenes_grown.py render    # + render all seven to footage/nikita6/broll/<name>_v2_anim.mp4
"""

import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "footage" / "nikita6" / "broll"

HEAD = """<!doctype html><html><head><meta charset="utf-8">
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "Quick"; src: url(fonts/quicksand.woff2) format("woff2"); font-weight: 300 700; }
@font-face { font-family: "Baloo"; src: url(fonts/baloo.woff2) format("woff2"); font-weight: 400 800; }
html, body { margin: 0; background: #1E120D; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; background: #1E120D; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; overflow: hidden;
  background: radial-gradient(ellipse at 50% 62%, #5A3828 0%, #3A231A 50%, #1E120D 100%); font-family: Quick; }
#cam { position: absolute; inset: 0; transform-origin: 50% 65%; }
.abs { position: absolute; }
* { box-sizing: border-box; }
/* phone mockup shared by the app / chat scenes */
.phone { left: 250px; top: 740px; width: 580px; height: 1180px; border-radius: 86px; background: #15100D;
  box-shadow: 0 40px 90px rgba(0,0,0,.6), inset 0 0 0 5px #4A2E22; }
.scr { left: 18px; top: 18px; width: 544px; height: 1144px; border-radius: 70px; overflow: hidden; background: #FFF4E6; }
.island { left: 212px; top: 22px; width: 120px; height: 34px; border-radius: 17px; background: #000; }
.card { border-radius: 30px; background: #FFFFFF; box-shadow: 0 10px 24px rgba(74,46,34,.14); }
%CSS%
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2.2" data-width="2160" data-height="3840" data-fps="30">
<div id="stage"><div id="cam">
%BODY%
</div></div></div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#cam", {scale: 1.0, y: 0}, {scale: 1.05, y: -20, duration: 2.2, ease: "none"}, 0);
  %JS%
  window.__timelines["main"] = tl;
</script></body></html>
"""

PHONE_IN = 'tl.fromTo(".phone", {y: 260, opacity: 0}, {y: 0, opacity: 1, duration: 0.55, ease: "power3.out"}, 0);'

SCENES = {}

# 1 -- "Aaj aapne kya khaya?": a food-delivery order, delivered
SCENES["ex1_food"] = dict(css="""
.hdr { left: 0; top: 0; width: 544px; height: 150px; background: #E8475A; }
.ht { left: 40px; top: 80px; font: 700 34px/1 Quick; color: #FFF4E6; }
.dish { left: 30px; top: 180px; width: 484px; height: 230px; border-radius: 30px; overflow: hidden; background: linear-gradient(160deg, #F6A15C, #E8475A); }
.plate { left: 152px; top: 25px; width: 180px; height: 180px; border-radius: 50%; background: radial-gradient(circle at 40% 35%, #FFFFFF, #D9D3CB); }
.bowl { width: 70px; height: 70px; border-radius: 50%; }
.row { left: 30px; width: 484px; height: 86px; padding: 0 26px; display: flex; align-items: center; justify-content: space-between;
  font: 700 30px/1 Quick; color: #2B1A13; }
.row span:last-child { color: #8A6A5C; font-weight: 600; }
.status { left: 30px; top: 790px; width: 484px; height: 200px; padding: 28px; }
.st { font: 700 24px/1 Quick; color: #8A6A5C; letter-spacing: 1px; }
.bar { left: 28px; top: 80px; width: 428px; height: 14px; border-radius: 7px; background: #F1E4D6; }
.fill { left: 28px; top: 80px; width: 428px; height: 14px; border-radius: 7px; background: #3FA27A; transform-origin: 0 50%; }
.ok { left: 28px; top: 120px; font: 700 38px/1 Quick; color: #2E7D5E; display: flex; align-items: center; gap: 14px; }
.tick { width: 48px; height: 48px; border-radius: 50%; background: #3FA27A; color: #fff; font: 700 30px/48px Quick; text-align: center; }
""", body="""
<div class="abs phone"><div class="abs scr">
  <div class="abs hdr"><div class="abs ht">Your order</div></div>
  <div class="abs dish"><div class="abs plate"></div>
    <div class="abs bowl" style="left:182px;top:50px;background:radial-gradient(circle,#FFD25C,#E8A93A)"></div>
    <div class="abs bowl" style="left:232px;top:95px;background:radial-gradient(circle,#F6A15C,#C9632E)"></div>
    <div class="abs bowl" style="left:180px;top:118px;width:60px;height:60px;background:radial-gradient(circle,#F3D29A,#D9A55F)"></div></div>
  <div class="abs row card r" style="top:440px"><span>Dal makhani × 1</span><span>₹220</span></div>
  <div class="abs row card r" style="top:546px"><span>Butter roti × 2</span><span>₹60</span></div>
  <div class="abs row card r" style="top:652px"><span>Jeera rice × 1</span><span>₹140</span></div>
  <div class="abs status card"><div class="st">ORDER STATUS</div><div class="abs bar"></div><div class="abs fill"></div>
    <div class="abs ok"><div class="tick">✓</div>Delivered · 1:42 PM</div></div>
</div><div class="abs island"></div></div>
""", js=PHONE_IN + """
  tl.fromTo(".dish", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}, 0.2);
  tl.fromTo(".r", {opacity: 0, x: 40}, {opacity: 1, x: 0, duration: 0.4, ease: "power3.out", stagger: 0.12}, 0.4);
  tl.fromTo(".status", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 0.75);
  tl.fromTo(".fill", {scaleX: 0}, {scaleX: 1, duration: 0.6, ease: "power2.inOut"}, 0.95);
  tl.fromTo(".ok", {opacity: 0, x: -20}, {opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}, 1.45);
""")

# 2 -- "Meri book kahan hai?": a desk from above, a dotted outline where the book should be
SCENES["ex2_book"] = dict(css="""
.desk { left: 60px; top: 760px; width: 960px; height: 1040px; border-radius: 40px; background: linear-gradient(160deg, #A87250, #8A5534);
  box-shadow: 0 40px 90px rgba(0,0,0,.55); overflow: hidden; }
.grain { inset: 0; background: repeating-linear-gradient(100deg, rgba(255,255,255,.04) 0 6px, rgba(0,0,0,.03) 6px 14px); }
.lap { left: 110px; top: 120px; width: 500px; height: 330px; border-radius: 22px; background: #2B2B30; box-shadow: 0 14px 30px rgba(0,0,0,.35); }
.lscr { left: 20px; top: 20px; width: 460px; height: 290px; border-radius: 12px; background: linear-gradient(160deg, #9EB9F5, #C9A8F2); }
.mug { left: 690px; top: 150px; width: 170px; height: 170px; border-radius: 50%; background: #FFF4E6; box-shadow: 0 12px 26px rgba(0,0,0,.35); }
.cof { left: 25px; top: 25px; width: 120px; height: 120px; border-radius: 50%; background: radial-gradient(circle at 40% 40%, #8A5534, #4A2E22); }
.handle { left: 840px; top: 205px; width: 60px; height: 60px; border-radius: 50%; border: 16px solid #FFF4E6; }
.note { left: 640px; top: 470px; width: 240px; height: 300px; border-radius: 12px; background: #FFE2CF; transform: rotate(8deg); box-shadow: 0 10px 22px rgba(0,0,0,.3); }
.line { left: 30px; width: 180px; height: 8px; border-radius: 4px; background: rgba(74,46,34,.25); }
.pen { left: 520px; top: 560px; width: 16px; height: 230px; border-radius: 8px; background: #E8475A; transform: rotate(-30deg); }
.slot { left: 130px; top: 560px; width: 330px; height: 400px; border-radius: 18px; border: 7px dashed rgba(255,244,230,.85); }
.slotq { left: 130px; top: 680px; width: 330px; text-align: center; font: 800 140px/1 Baloo; color: rgba(255,244,230,.9); }
.lens { left: 330px; top: 600px; font: 120px/1 sans-serif; filter: drop-shadow(0 10px 18px rgba(0,0,0,.4)); }
""", body="""
<div class="abs desk"><div class="abs grain"></div>
  <div class="abs lap"><div class="abs lscr"></div></div>
  <div class="abs mug"><div class="abs cof"></div></div><div class="abs handle"></div>
  <div class="abs note"><div class="abs line" style="top:50px"></div><div class="abs line" style="top:90px"></div><div class="abs line" style="top:130px;width:120px"></div></div>
  <div class="abs pen"></div>
  <div class="abs slot"></div><div class="abs slotq">?</div>
  <div class="abs lens">🔍</div>
</div>
""", js="""
  tl.fromTo(".desk", {opacity: 0, y: 200}, {opacity: 1, y: 0, duration: 0.55, ease: "power3.out"}, 0);
  tl.fromTo(".lap, .mug, .handle, .note, .pen", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out", stagger: 0.07}, 0.2);
  tl.fromTo(".slot", {opacity: 0, scale: 0.92}, {opacity: 1, scale: 1, duration: 0.45, ease: "power2.out"}, 0.55);
  tl.fromTo(".slotq", {opacity: 0}, {opacity: 1, duration: 0.35, ease: "power2.out"}, 0.75);
  tl.fromTo(".lens", {opacity: 0, x: -260, y: 120}, {opacity: 1, x: 0, y: 0, duration: 0.7, ease: "power2.inOut"}, 0.7);
  tl.to(".lens", {x: 60, y: -40, duration: 0.6, ease: "sine.inOut"}, 1.4);
""")

# 4 -- "Tum kab aaoge?": a real-looking chat, messages arriving
SCENES["ex4_phone"] = dict(css="""
.chdr { left: 0; top: 0; width: 544px; height: 170px; background: #FFFFFF; box-shadow: 0 6px 16px rgba(74,46,34,.10); }
.av { left: 36px; top: 84px; width: 66px; height: 66px; border-radius: 50%; background: linear-gradient(160deg, #FFC995, #E8475A); }
.nm { left: 120px; top: 90px; font: 700 32px/1 Quick; color: #2B1A13; }
.ol { left: 120px; top: 130px; font: 600 22px/1 Quick; color: #3FA27A; }
.wall { left: 0; top: 170px; width: 544px; height: 974px; background: #F6EBDD; }
.b { left: 30px; max-width: 380px; padding: 20px 26px; border-radius: 28px 28px 28px 8px; background: #FFFFFF; box-shadow: 0 6px 14px rgba(74,46,34,.10);
  font: 700 32px/1.25 Quick; color: #2B1A13; }
.me { left: auto; right: 30px; border-radius: 28px 28px 8px 28px; background: #E8475A; color: #FFF4E6; }
.tm { font: 600 18px/1 Quick; color: #8A6A5C; margin-top: 8px; text-align: right; }
.me .tm { color: rgba(255,244,230,.8); }
.dots { padding: 22px 26px; }
.dot { display: inline-block; width: 16px; height: 16px; margin: 0 4px; border-radius: 50%; background: #C5B3A8; }
""", body="""
<div class="abs phone"><div class="abs scr">
  <div class="abs wall"></div>
  <div class="abs chdr"><div class="abs av"></div><div class="abs nm">Mumma ❤️</div><div class="abs ol">online</div></div>
  <div class="abs b me" id="m0" style="top:230px">Office se nikal rahi hoon<div class="tm">7:41 PM ✓✓</div></div>
  <div class="abs b dots" id="ty" style="top:410px"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
  <div class="abs b" id="m1" style="top:410px">Kab aaoge? 🏠<div class="tm">7:42 PM</div></div>
  <div class="abs b" id="m2" style="top:560px">Khana ready hai 🍲<div class="tm">7:42 PM</div></div>
</div><div class="abs island"></div></div>
""", js=PHONE_IN + """
  tl.fromTo("#m0", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}, 0.15);
  tl.fromTo("#ty", {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: 0.2, ease: "power3.out"}, 0.3);
  tl.fromTo("#ty .dot", {opacity: 0.35}, {opacity: 1, duration: 0.1, yoyo: true, repeat: 1, stagger: 0.06}, 0.32);
  tl.set("#ty", {opacity: 0}, 0.55);
  tl.fromTo("#m1", {opacity: 0, y: 24, scale: 0.97}, {opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "power3.out"}, 0.55);
  tl.fromTo("#m2", {opacity: 0, y: 24, scale: 0.97}, {opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "power3.out"}, 0.85);
""")

# 5 -- "Tumhare class teacher kaun hain?": a class schedule with the teacher's name still unknown
SCENES["ex5_teacher"] = dict(css="""
.sh { left: 30px; top: 110px; font: 700 26px/1 Quick; color: #8A6A5C; letter-spacing: 1px; }
.sd { left: 30px; top: 150px; font: 700 48px/1 Quick; color: #2B1A13; }
.cl { left: 30px; width: 484px; height: 150px; padding: 26px 26px 26px 34px; }
.cl::before { content: ""; position: absolute; left: 0; top: 24px; bottom: 24px; width: 8px; border-radius: 4px; background: var(--c); }
.ct { font: 600 22px/1 Quick; color: #8A6A5C; }
.cn { font: 700 34px/1.2 Quick; color: #2B1A13; margin-top: 10px; }
.cr { font: 600 24px/1 Quick; color: #8A6A5C; margin-top: 10px; }
.focus { box-shadow: 0 0 0 5px #E8475A, 0 16px 34px rgba(232,71,90,.30); }
.who { display: inline-block; min-width: 110px; padding: 2px 16px; border-radius: 14px; border: 4px dashed #E8475A; color: #E8475A; text-align: center; }
.pin { left: 420px; top: 470px; width: 70px; height: 70px; border-radius: 50%; background: #F1E4D6; border: 4px dashed #C5B3A8;
  font: 800 40px/62px Baloo; color: #8A6A5C; text-align: center; }
""", body="""
<div class="abs phone"><div class="abs scr">
  <div class="abs sh">MONDAY · NEW TERM</div><div class="abs sd">Today's classes</div>
  <div class="abs card cl" id="c1" style="top:240px;--c:#9EB9F5"><div class="ct">9:00 – 9:45</div><div class="cn">Maths</div><div class="cr">Room 112 · Mr. Sharma</div></div>
  <div class="abs card cl" id="c2" style="top:420px;--c:#E8475A"><div class="ct">10:00 – 10:45 · CLASS TEACHER</div><div class="cn">English</div>
    <div class="cr">Room 204 · <span class="who">?</span></div></div>
  <div class="abs pin" id="pin">?</div>
  <div class="abs card cl" id="c3" style="top:600px;--c:#8FD6B8"><div class="ct">11:00 – 11:45</div><div class="cn">Science</div><div class="cr">Lab 3 · Ms. Iyer</div></div>
</div><div class="abs island"></div></div>
""", js=PHONE_IN + """
  tl.fromTo(".sh, .sd", {opacity: 0, y: 16}, {opacity: 1, y: 0, duration: 0.35, ease: "power3.out", stagger: 0.06}, 0.2);
  tl.fromTo(".cl", {opacity: 0, x: 40}, {opacity: 1, x: 0, duration: 0.4, ease: "power3.out", stagger: 0.12}, 0.35);
  tl.to("#c2", {scale: 1.04, duration: 0.45, ease: "power2.out"}, 0.95);
  tl.call(() => document.querySelector("#c2").classList.add("focus"), null, 0.95);
  tl.fromTo("#pin", {opacity: 0, scale: 0.7}, {opacity: 1, scale: 1, duration: 0.4, ease: "power2.out"}, 1.1);
  tl.fromTo(".who", {opacity: 0.4}, {opacity: 1, duration: 0.3, yoyo: true, repeat: 2, ease: "sine.inOut"}, 1.1);
""")

# 6 -- "Tumhari favourite movie kaun si hai?": a streaming-app grid, one title gets picked
SCENES["ex6_movie"] = dict(css="""
.tv { left: 40px; top: 760px; width: 1000px; height: 660px; border-radius: 34px; background: #120C09; box-shadow: 0 40px 90px rgba(0,0,0,.6), inset 0 0 0 6px #3A231A; }
.tvs { left: 22px; top: 22px; width: 956px; height: 616px; border-radius: 20px; overflow: hidden; background: linear-gradient(180deg, #2B1A13, #1A100C); }
.lbl { left: 40px; top: 36px; font: 700 30px/1 Quick; color: #FFF4E6; }
.po { top: 100px; width: 200px; height: 290px; border-radius: 18px; overflow: hidden; box-shadow: 0 10px 22px rgba(0,0,0,.45); }
.po2 { top: 410px; height: 170px; }
.pick { box-shadow: 0 0 0 6px #FFF4E6, 0 20px 50px rgba(255,201,74,.45); z-index: 2; }
.shape { border-radius: 50%; opacity: .85; }
.play { left: 70px; top: 100px; width: 60px; height: 60px; border-radius: 50%; background: rgba(255,244,230,.92); }
.play::after { content: ""; position: absolute; left: 23px; top: 17px; border-left: 22px solid #E8475A; border-top: 13px solid transparent; border-bottom: 13px solid transparent; }
.stand { left: 470px; top: 1420px; width: 140px; height: 70px; background: #2B1A13; border-radius: 0 0 20px 20px; }
.base { left: 380px; top: 1485px; width: 320px; height: 24px; border-radius: 12px; background: #2B1A13; }
.sofa { left: 0; top: 1640px; width: 1080px; height: 300px; border-radius: 120px 120px 0 0; background: linear-gradient(180deg, #6B3F30, #3A231A); }
.remote { left: 690px; top: 1600px; width: 70px; height: 210px; border-radius: 30px; background: #1A100C; transform: rotate(18deg); box-shadow: 0 12px 24px rgba(0,0,0,.5); }
.btn { left: 22px; width: 26px; height: 26px; border-radius: 50%; background: #E8475A; }
""", body="""
<div class="abs tv"><div class="abs tvs">
  <div class="abs lbl">Continue watching</div>
  <div class="abs po" style="left:40px;background:linear-gradient(160deg,#9EB9F5,#4A5FA8)"><div class="abs shape" style="left:40px;top:60px;width:120px;height:120px;background:#FFF4E6"></div></div>
  <div class="abs po" id="pk" style="left:268px;background:linear-gradient(160deg,#F7B3C2,#C93448)"><div class="abs shape" style="left:-30px;top:150px;width:260px;height:260px;background:#FFC995"></div><div class="abs play"></div></div>
  <div class="abs po" style="left:496px;background:linear-gradient(160deg,#8FD6B8,#2E7D5E)"><div class="abs shape" style="left:60px;top:40px;width:80px;height:80px;background:#FFF4E6"></div></div>
  <div class="abs po" style="left:724px;background:linear-gradient(160deg,#C9A8F2,#6B4FA8)"><div class="abs shape" style="left:20px;top:170px;width:160px;height:160px;background:#F7B3C2"></div></div>
  <div class="abs po po2" style="left:40px;background:linear-gradient(160deg,#FFC995,#C9632E)"></div>
  <div class="abs po po2" style="left:268px;background:linear-gradient(160deg,#9EB9F5,#6B4FA8)"></div>
  <div class="abs po po2" style="left:496px;background:linear-gradient(160deg,#F7B3C2,#8A5534)"></div>
  <div class="abs po po2" style="left:724px;background:linear-gradient(160deg,#8FD6B8,#4A5FA8)"></div>
</div></div>
<div class="abs stand"></div><div class="abs base"></div>
<div class="abs sofa"></div>
<div class="abs remote"><div class="abs btn" style="top:30px"></div><div class="abs btn" style="top:80px;background:#FFF4E6;opacity:.5"></div></div>
""", js="""
  tl.fromTo(".tv, .stand, .base", {opacity: 0, y: 120}, {opacity: 1, y: 0, duration: 0.55, ease: "power3.out"}, 0);
  tl.fromTo(".sofa, .remote", {opacity: 0, y: 160}, {opacity: 1, y: 0, duration: 0.55, ease: "power3.out"}, 0.1);
  tl.fromTo(".lbl", {opacity: 0}, {opacity: 1, duration: 0.3}, 0.35);
  tl.fromTo(".po", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out", stagger: 0.05}, 0.35);
  tl.to("#pk", {scale: 1.12, duration: 0.5, ease: "power2.out"}, 1.0);
  tl.call(() => document.querySelector("#pk").classList.add("pick"), null, 1.0);
  tl.fromTo(".play", {opacity: 0, scale: 0.6}, {opacity: 1, scale: 1, duration: 0.35, ease: "power2.out"}, 1.2);
""")

# 7 -- "Ye bag kiska hai?": a lost & found notice pinned on an office board
SCENES["ex7_bag"] = dict(css="""
.board { left: 90px; top: 770px; width: 900px; height: 980px; border-radius: 30px; background: radial-gradient(circle at 40% 30%, #C79A6E, #A8794F);
  box-shadow: 0 40px 90px rgba(0,0,0,.55), inset 0 0 0 18px #6B3F2A; }
.paper { left: 190px; top: 860px; width: 700px; height: 800px; border-radius: 12px; background: #FFFDF8; box-shadow: 0 18px 40px rgba(0,0,0,.35); transform: rotate(-2deg); }
.tack { left: 520px; top: 840px; width: 44px; height: 44px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #FF8A97, #C93448); box-shadow: 0 6px 10px rgba(0,0,0,.35); }
.t1 { left: 0; top: 70px; width: 700px; text-align: center; font: 700 30px/1 Quick; letter-spacing: 6px; color: #8A6A5C; }
.t2 { left: 0; top: 120px; width: 700px; text-align: center; font: 700 62px/1 Quick; color: #2B1A13; }
.bagic { left: 240px; top: 230px; width: 220px; height: 190px; border-radius: 26px 26px 40px 40px; border: 10px solid #4A2E22; }
.bagh { left: 290px; top: 175px; width: 120px; height: 90px; border-radius: 60px 60px 0 0; border: 10px solid #4A2E22; border-bottom: none; }
.bagf { left: 240px; top: 230px; width: 220px; height: 70px; border-bottom: 10px solid #4A2E22; border-radius: 26px 26px 50px 50px; }
.inf { left: 0; width: 700px; text-align: center; font: 600 32px/1.3 Quick; color: #4A2E22; }
.stamp { left: 420px; top: 1475px; width: 330px; height: 150px; border-radius: 20px; border: 9px solid #E8475A; color: #E8475A;
  font: 800 74px/132px Baloo; text-align: center; transform: rotate(-10deg); background: rgba(232,71,90,.06); }
""", body="""
<div class="abs board"></div>
<div class="abs paper">
  <div class="abs t1">LOST &amp; FOUND</div><div class="abs t2">Found a bag</div>
  <div class="abs bagh"></div><div class="abs bagic"></div><div class="abs bagf"></div>
  <div class="abs inf" style="top:470px">Near desk 12, 3rd floor</div>
  <div class="abs inf" style="top:530px;color:#8A6A5C">Today · 11:30 AM</div>
</div>
<div class="abs tack"></div>
<div class="abs stamp">OWNER?</div>
""", js="""
  tl.fromTo(".board", {opacity: 0, y: 120}, {opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}, 0);
  tl.fromTo(".paper", {opacity: 0, y: -80, rotation: -6}, {opacity: 1, y: 0, rotation: -2, duration: 0.45, ease: "power3.out"}, 0.1);
  tl.fromTo(".tack", {opacity: 0, scale: 1.6}, {opacity: 1, scale: 1, duration: 0.25, ease: "power2.out"}, 0.4);
  tl.fromTo(".paper .t1, .paper .t2, .bagh, .bagic, .bagf, .inf", {opacity: 0, y: 14}, {opacity: 1, y: 0, duration: 0.3, ease: "power3.out", stagger: 0.04}, 0.35);
  tl.fromTo(".stamp", {opacity: 0, scale: 1.5, rotation: -18}, {opacity: 1, scale: 1, rotation: -10, duration: 0.3, ease: "power3.out"}, 0.8);
""")


def write():
    for name, sc in SCENES.items():
        d = HERE / f"{name}_v2"
        (d / "vendor").mkdir(parents=True, exist_ok=True)
        (d / "fonts").mkdir(exist_ok=True)
        shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", d / "vendor/gsap.min.js")
        for f in (HERE.parent / "board" / "fonts").glob("*.woff2"):
            shutil.copy(f, d / "fonts" / f.name)
        (d / "hyperframes.json").write_text('{"name":"nikita6-anim-%s-v2"}\n' % name)
        (d / "index.html").write_text(HEAD.replace("%CSS%", sc["css"]).replace("%BODY%", sc["body"]).replace("%JS%", sc["js"]))
        print("wrote", d / "index.html")


def render():
    env = dict(os.environ, NODE_USE_ENV_PROXY="1", NODE_EXTRA_CA_CERTS="/root/.ccr/ca-bundle.crt")
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sorted(list(SCENES) + ["ex3_late"]):
        subprocess.run(["npx", "hyperframes", "render", str(HERE / f"{name}_v2"), "-o", str(OUT / f"{name}_v2_anim.mp4"),
                        "--quality", "high", "--quiet"], check=True, env=env, cwd=ROOT, stdout=subprocess.DEVNULL)
        print("rendered", OUT / f"{name}_v2_anim.mp4")


if __name__ == "__main__":
    write()
    if "render" in sys.argv:
        render()
