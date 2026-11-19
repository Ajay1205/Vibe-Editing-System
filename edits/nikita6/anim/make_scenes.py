"""Animated cutaways for the Nikita 6 examples (user, 19 Nov: "create animations on all examples").

Each scene is a 2.2 s HyperFrames project (anim/<name>/index.html) in the WH Family palette, designed on a
1080x1920 stage and rendered natively at 2160x3840. The big popping question (main overlay, y 420-680 on the
stage) sits above every scene, so each subject lives between y ~760 and ~1750. The cinema (anim/movie) is
hand-written; this script writes the other six.

Usage: python3 -I make_scenes.py            # write the projects
       python3 -I make_scenes.py render     # + render each to footage/nikita6/broll/ex<N>_<name>_anim.mp4
"""

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
@font-face { font-family: "Baloo"; src: url(fonts/baloo.woff2) format("woff2"); font-weight: 400 800; }
html, body { margin: 0; background: #1E120D; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; background: #1E120D; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0;
  overflow: hidden; background: radial-gradient(ellipse at 50% 50%, #6A4430 0%, #4A2E22 45%, #24150F 100%); }
#cam { position: absolute; inset: 0; transform-origin: 50% 60%; }
.abs { position: absolute; }
.glow { left: 140px; top: 760px; width: 800px; height: 800px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,214,170,.38) 0%, rgba(255,214,170,0) 70%); }
.spark { font: 60px/1 sans-serif; }
.q { font: 800 110px/1 Baloo; text-shadow: 0 8px 20px rgba(0,0,0,.35); }
%CSS%
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2.2" data-width="2160" data-height="3840" data-fps="30">
<div id="stage"><div id="cam"><div class="abs glow" id="glow"></div>
%BODY%
</div></div></div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#cam", {scale: 1.0}, {scale: 1.06, duration: 2.2, ease: "none"}, 0);
  tl.fromTo("#glow", {opacity: 0, scale: 0.7}, {opacity: 1, scale: 1, duration: 0.6, ease: "power2.out"}, 0);
  tl.fromTo(".spark", {scale: 0, rotation: -40, opacity: 0}, {scale: 1, rotation: 0, opacity: 1, duration: 0.4, ease: "back.out(3)", stagger: 0.16}, 0.45);
  tl.to(".spark", {scale: 0.7, duration: 0.3, yoyo: true, repeat: 3, stagger: 0.1}, 0.95);
  %JS%
  window.__timelines["main"] = tl;
</script></body></html>
"""

SCENES = {}

# 1 -- "Aaj aapne kya khaya?": a steaming thali on a wooden table
SCENES["ex1_food"] = dict(css="""
#table { left: -40px; top: 1180px; width: 1160px; height: 800px; border-radius: 40px 40px 0 0;
  background: repeating-linear-gradient(90deg, #8A5534 0 140px, #7C4A2C 140px 150px, #925C39 150px 290px); box-shadow: 0 -10px 40px rgba(0,0,0,.4); }
#plate { left: 170px; top: 1020px; width: 740px; height: 740px; border-radius: 50%;
  background: radial-gradient(circle at 40% 35%, #FFFFFF 0%, #DCDCE2 35%, #B8B9C2 70%, #9FA0AA 100%); box-shadow: 0 30px 50px rgba(0,0,0,.45); }
#inner { left: 225px; top: 1075px; width: 630px; height: 630px; border-radius: 50%; background: radial-gradient(circle at 45% 40%, #F4F4F7, #CFD0D8); }
.katori { width: 220px; height: 220px; border-radius: 50%; background: radial-gradient(circle at 40% 35%, #FFFFFF, #B9BAC4); box-shadow: 0 10px 18px rgba(0,0,0,.3); }
.fill { position: absolute; left: 22px; top: 22px; width: 176px; height: 176px; border-radius: 50%; }
#rice { left: 560px; top: 1330px; width: 250px; height: 200px; border-radius: 50% 50% 46% 46%; background: radial-gradient(circle at 45% 35%, #FFFFFF, #ECE8DD); box-shadow: 0 8px 14px rgba(0,0,0,.18); }
#roti { left: 300px; top: 1440px; width: 280px; height: 230px; border-radius: 50%; background: radial-gradient(circle at 40% 40%, #F3D29A, #D9A55F);
  box-shadow: 0 8px 14px rgba(0,0,0,.25); }
.spot { width: 26px; height: 18px; border-radius: 50%; background: #B97B3C; opacity: .7; }
.steam { width: 40px; height: 230px; border-radius: 20px; background: linear-gradient(0deg, rgba(255,255,255,.75), rgba(255,255,255,0)); filter: blur(8px); }
""", body="""
<div class="abs" id="table"></div>
<div class="abs" id="plate"></div><div class="abs" id="inner"></div>
<div class="abs katori" id="k1" style="left:270px;top:1130px"><div class="fill" style="background:radial-gradient(circle at 45% 40%,#FFD25C,#E8A93A)"></div></div>
<div class="abs katori" id="k2" style="left:520px;top:1095px"><div class="fill" style="background:radial-gradient(circle at 45% 40%,#F6A15C,#C9632E)"></div></div>
<div class="abs" id="rice"></div>
<div class="abs" id="roti"><div class="abs spot" style="left:80px;top:70px"></div><div class="abs spot" style="left:170px;top:120px"></div><div class="abs spot" style="left:120px;top:160px"></div></div>
<div class="abs steam" style="left:360px;top:900px"></div><div class="abs steam" style="left:610px;top:870px"></div><div class="abs steam" style="left:500px;top:930px"></div>
<div class="abs spark" style="left:110px;top:1000px">✨</div><div class="abs spark" style="left:900px;top:1180px">✨</div><div class="abs spark" style="left:860px;top:900px">✨</div>
""", js="""
  tl.fromTo("#table", {y: 300}, {y: 0, duration: 0.45, ease: "power3.out"}, 0);
  tl.fromTo("#plate, #inner", {scale: 0.4, opacity: 0}, {scale: 1, opacity: 1, duration: 0.5, ease: "back.out(1.8)"}, 0.1);
  tl.fromTo(".katori, #rice, #roti", {y: -260, opacity: 0}, {y: 0, opacity: 1, duration: 0.42, ease: "bounce.out", stagger: 0.1}, 0.3);
  tl.fromTo(".steam", {y: 60, opacity: 0, scaleY: 0.6}, {y: -120, opacity: 1, scaleY: 1.1, duration: 0.9, ease: "sine.out", stagger: 0.2, repeat: 1}, 0.6);
  tl.to(".steam", {x: 18, duration: 0.45, yoyo: true, repeat: 3, ease: "sine.inOut", stagger: 0.15}, 0.6);
""")

# 2 -- "Meri book kahan hai?": a shelf with one book missing, then the book peeks out from under a cushion
SCENES["ex2_book"] = dict(css="""
#shelf { left: 150px; top: 780px; width: 780px; height: 560px; border-radius: 26px; background: #6B3F2A; box-shadow: 0 24px 50px rgba(0,0,0,.45);
  border: 18px solid #8A5534; }
.board { left: 0; width: 744px; height: 18px; background: #8A5534; }
.bk { bottom: 0; width: 62px; border-radius: 8px 8px 4px 4px; box-shadow: inset -6px 0 0 rgba(0,0,0,.15); }
#gap { left: 330px; top: 102px; width: 74px; height: 150px; border: 5px dashed #FFF4E6; border-radius: 10px; }
#qm { left: 336px; top: 70px; color: #FFF4E6; font: 800 110px/1 Baloo; }
#sofa { left: 90px; top: 1420px; width: 900px; height: 360px; border-radius: 90px 90px 40px 40px; background: linear-gradient(180deg, #E8475A, #C93448);
  box-shadow: 0 24px 50px rgba(0,0,0,.45); }
#book { left: 470px; top: 1480px; width: 260px; height: 70px; border-radius: 10px; background: #8FD6B8; box-shadow: inset 0 -12px 0 #6FBF9C; }
#cush { left: 300px; top: 1400px; width: 480px; height: 210px; border-radius: 80px; background: radial-gradient(circle at 40% 35%, #FFE2CF, #F7B3C2);
  box-shadow: 0 16px 30px rgba(0,0,0,.35); transform-origin: 10% 90%; }
#eyes { left: 560px; top: 1470px; font: 80px/1 sans-serif; }
""", body="""
<div class="abs" id="shelf">
  <div class="abs board" style="top:250px"></div>
  <div class="abs" style="left:20px;top:102px;width:700px;height:150px">
    <div class="abs bk" style="left:0;height:140px;background:#F7B3C2"></div><div class="abs bk" style="left:70px;height:120px;background:#FFC995"></div>
    <div class="abs bk" style="left:140px;height:150px;background:#9EB9F5"></div><div class="abs bk" style="left:210px;height:130px;background:#C9A8F2"></div>
    <div class="abs bk" style="left:400px;height:146px;background:#8FD6B8"></div><div class="abs bk" style="left:470px;height:124px;background:#FFD25C"></div>
    <div class="abs bk" style="left:540px;height:140px;background:#F6A15C"></div><div class="abs bk" style="left:610px;height:118px;background:#9EB9F5"></div>
  </div>
  <div class="abs" id="gap"></div><div class="abs" id="qm">?</div>
  <div class="abs" style="left:20px;top:300px;width:700px;height:200px">
    <div class="abs bk" style="left:30px;height:180px;background:#C9A8F2"></div><div class="abs bk" style="left:100px;height:160px;background:#FFC995"></div>
    <div class="abs bk" style="left:170px;height:190px;background:#F7B3C2"></div><div class="abs bk" style="left:300px;height:170px;background:#8FD6B8"></div>
    <div class="abs bk" style="left:370px;height:186px;background:#9EB9F5"></div><div class="abs bk" style="left:520px;height:166px;background:#FFD25C"></div>
  </div>
</div>
<div class="abs" id="sofa"></div><div class="abs" id="book"></div><div class="abs" id="cush"></div><div class="abs" id="eyes">👀</div>
<div class="abs spark" style="left:760px;top:1380px">✨</div><div class="abs spark" style="left:420px;top:1360px">✨</div>
""", js="""
  tl.fromTo("#shelf", {y: 120, opacity: 0, scale: 0.85}, {y: 0, opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.8)"}, 0);
  tl.fromTo("#shelf .bk", {scaleY: 0, transformOrigin: "50% 100%"}, {scaleY: 1, duration: 0.3, ease: "back.out(2)", stagger: 0.025}, 0.15);
  tl.fromTo("#qm", {scale: 0, rotation: -30}, {scale: 1, rotation: 0, duration: 0.35, ease: "back.out(3)"}, 0.45);
  tl.to("#qm", {y: -20, duration: 0.22, yoyo: true, repeat: 5, ease: "sine.inOut"}, 0.8);
  tl.fromTo("#gap", {opacity: 0.3}, {opacity: 1, duration: 0.2, yoyo: true, repeat: 7}, 0.4);
  tl.fromTo("#sofa", {y: 400}, {y: 0, duration: 0.45, ease: "power3.out"}, 0.1);
  tl.fromTo("#cush", {y: 400}, {y: 0, duration: 0.45, ease: "power3.out"}, 0.15);
  tl.to("#cush", {rotation: -16, y: -70, duration: 0.35, ease: "back.out(2)"}, 0.85);
  tl.fromTo("#book", {opacity: 0}, {opacity: 1, duration: 0.01}, 0.85);
  tl.fromTo("#eyes", {opacity: 0, y: 30}, {opacity: 1, y: -40, duration: 0.35, ease: "back.out(2.5)"}, 1.0);
""")

# 3 -- "Tum late kyun ho?": a cartoon wall clock, hands racing, the clock shaking with impatience
SCENES["ex3_late"] = dict(css="""
#clock { left: 220px; top: 820px; width: 640px; height: 640px; border-radius: 50%; background: radial-gradient(circle at 40% 35%, #FFFFFF, #FFF4E6 60%, #F3E3CC);
  border: 34px solid #E8475A; box-shadow: 0 30px 60px rgba(0,0,0,.5), inset 0 0 0 10px #FFF; }
.tick { left: 309px; top: 20px; width: 22px; height: 60px; border-radius: 11px; background: #4A2E22; transform-origin: 11px 300px; }
#hh { left: 304px; top: 160px; width: 32px; height: 170px; border-radius: 16px; background: #4A2E22; transform-origin: 16px 160px; }
#mh { left: 309px; top: 70px; width: 22px; height: 260px; border-radius: 11px; background: #4A2E22; transform-origin: 11px 250px; }
#hub { left: 290px; top: 290px; width: 60px; height: 60px; border-radius: 50%; background: #E8475A; border: 8px solid #FFF4E6; }
.bell { top: 760px; width: 170px; height: 120px; border-radius: 85px 85px 20px 20px; background: #E8475A; box-shadow: 0 10px 20px rgba(0,0,0,.35); }
.leg { top: 1430px; width: 40px; height: 120px; border-radius: 20px; background: #E8475A; }
.mark { font: 800 120px/1 Baloo; color: #FFC94A; text-shadow: 0 8px 18px rgba(0,0,0,.35); }
.puff { font: 80px/1 sans-serif; }
""", body="""
<div class="abs bell" id="bL" style="left:200px;transform:rotate(-24deg)"></div><div class="abs bell" id="bR" style="left:710px;transform:rotate(24deg)"></div>
<div class="abs leg" style="left:330px;transform:rotate(20deg)"></div><div class="abs leg" style="left:710px;transform:rotate(-20deg)"></div>
<div class="abs" id="clock">
  <div class="abs tick"></div><div class="abs tick" style="transform:rotate(90deg)"></div><div class="abs tick" style="transform:rotate(180deg)"></div><div class="abs tick" style="transform:rotate(270deg)"></div>
  <div class="abs" id="hh"></div><div class="abs" id="mh"></div><div class="abs" id="hub"></div>
</div>
<div class="abs mark" id="x1" style="left:110px;top:960px">!</div><div class="abs mark" id="x2" style="left:920px;top:1010px">!</div>
<div class="abs puff" id="p1" style="left:140px;top:1480px">💨</div><div class="abs puff" id="p2" style="left:850px;top:1480px">💨</div>
<div class="abs spark" style="left:900px;top:820px">✨</div>
""", js="""
  tl.fromTo("#clock, .bell, .leg", {scale: 0.3, opacity: 0}, {scale: 1, opacity: 1, duration: 0.45, ease: "back.out(2)"}, 0);
  tl.fromTo("#mh", {rotation: 0}, {rotation: 1440, duration: 1.6, ease: "power2.inOut"}, 0.2);
  tl.fromTo("#hh", {rotation: 60}, {rotation: 180, duration: 1.6, ease: "power2.inOut"}, 0.2);
  tl.to("#clock", {rotation: 6, duration: 0.06, yoyo: true, repeat: 13, ease: "none"}, 0.5);
  tl.to("#bL", {rotation: -34, duration: 0.06, yoyo: true, repeat: 13}, 0.5);
  tl.to("#bR", {rotation: 34, duration: 0.06, yoyo: true, repeat: 13}, 0.5);
  tl.fromTo(".mark", {scale: 0, rotation: -20}, {scale: 1, rotation: 0, duration: 0.3, ease: "back.out(3)", stagger: 0.12}, 0.6);
  tl.fromTo(".puff", {opacity: 0, x: 0}, {opacity: 1, x: (i) => i ? 60 : -60, duration: 0.5, ease: "power2.out", stagger: 0.1}, 0.7);
""")

# 4 -- "Tum kab aaoge?": a phone buzzing, a chat bubble asks when you're coming home
SCENES["ex4_phone"] = dict(css="""
#phone { left: 330px; top: 760px; width: 420px; height: 860px; border-radius: 70px; background: #2B1A13; box-shadow: 0 30px 60px rgba(0,0,0,.5), inset 0 0 0 6px #6B3F2A; }
#scr { left: 22px; top: 22px; width: 376px; height: 816px; border-radius: 52px; background: linear-gradient(180deg, #FFF4E6, #FFE2CF); overflow: hidden; }
#notch { left: 150px; top: 18px; width: 76px; height: 22px; border-radius: 11px; background: #2B1A13; }
#hdr { left: 0; top: 0; width: 376px; height: 120px; background: #E8475A; }
#av { left: 26px; top: 50px; width: 52px; height: 52px; border-radius: 50%; background: #FFC94A; font: 34px/52px sans-serif; text-align: center; }
.bub { left: 30px; max-width: 290px; padding: 18px 26px; border-radius: 30px 30px 30px 8px; background: #FFFFFF; box-shadow: 0 8px 16px rgba(0,0,0,.15);
  font: 800 44px/1.1 Baloo; color: #4A2E22; }
.dot { display: inline-block; width: 18px; height: 18px; margin: 0 5px; border-radius: 50%; background: #B9A6A0; }
.wave { left: 290px; top: 940px; width: 500px; height: 500px; border-radius: 50%; border: 10px solid rgba(255,201,74,.75); }
""", body="""
<div class="abs wave" id="w1"></div><div class="abs wave" id="w2"></div>
<div class="abs" id="phone"><div class="abs" id="scr">
  <div class="abs" id="hdr"><div class="abs" id="av">🏠</div></div>
  <div class="abs bub" id="typing" style="top:220px"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
  <div class="abs bub" id="msg" style="top:220px">Kab aaoge? 🏠</div>
  <div class="abs bub" id="msg2" style="top:350px">❤️</div>
</div><div class="abs" id="notch"></div></div>
<div class="abs spark" style="left:220px;top:820px">✨</div><div class="abs spark" style="left:800px;top:1500px">✨</div>
""", js="""
  tl.fromTo("#phone", {y: 500, rotation: 8}, {y: 0, rotation: 0, duration: 0.5, ease: "back.out(1.6)"}, 0);
  tl.to("#phone", {x: 8, rotation: 2, duration: 0.05, yoyo: true, repeat: 9, ease: "none"}, 0.45);
  tl.fromTo(".wave", {scale: 0.3, opacity: 1}, {scale: 1.5, opacity: 0, duration: 0.8, ease: "power2.out", stagger: 0.3}, 0.4);
  tl.fromTo("#typing", {scale: 0, transformOrigin: "0% 100%"}, {scale: 1, duration: 0.25, ease: "back.out(2.5)"}, 0.35);
  tl.fromTo("#typing .dot", {y: 0}, {y: -10, duration: 0.15, yoyo: true, repeat: 3, stagger: 0.07}, 0.45);
  tl.set("#typing", {opacity: 0}, 0.85);
  tl.fromTo("#msg", {scale: 0, transformOrigin: "0% 100%"}, {scale: 1, duration: 0.35, ease: "back.out(2.5)"}, 0.85);
  tl.fromTo("#msg2", {scale: 0, transformOrigin: "0% 100%"}, {scale: 1, duration: 0.3, ease: "back.out(2.5)"}, 1.35);
""")

# 5 -- "Tumhare class teacher kaun hain?": a cartoon teacher waving in front of a chalkboard
SCENES["ex5_teacher"] = dict(css="""
#board { left: 90px; top: 760px; width: 900px; height: 470px; border-radius: 24px; background: radial-gradient(circle at 50% 40%, #3F7A5E, #2C5A44);
  border: 22px solid #A0663F; box-shadow: 0 24px 50px rgba(0,0,0,.45); }
#tray { left: 120px; top: 1218px; width: 840px; height: 26px; border-radius: 10px; background: #8A5534; }
.chalk { fill: none; stroke: #FFF4E6; stroke-width: 9; stroke-linecap: round; stroke-linejoin: round; }
#head { left: 430px; top: 1060px; width: 220px; height: 240px; border-radius: 50%; background: #E7B48C; box-shadow: 0 10px 20px rgba(0,0,0,.25); }
#hair { left: 410px; top: 1030px; width: 260px; height: 170px; border-radius: 130px 130px 40px 40px; background: #2B1A13; }
#bun { left: 490px; top: 975px; width: 100px; height: 90px; border-radius: 50%; background: #2B1A13; }
.eye { top: 1170px; width: 22px; height: 30px; border-radius: 50%; background: #2B1A13; }
#smile { left: 497px; top: 1215px; width: 86px; height: 44px; border-radius: 0 0 50px 50px; border-bottom: 8px solid #A8423A; }
.cheek { top: 1215px; width: 36px; height: 22px; border-radius: 50%; background: #F29A8C; opacity: .7; }
#bindi { left: 532px; top: 1128px; width: 16px; height: 16px; border-radius: 50%; background: #E8475A; }
#body { left: 340px; top: 1290px; width: 400px; height: 520px; border-radius: 180px 180px 30px 30px; background: linear-gradient(160deg, #F6A15C 0%, #E8475A 55%, #C93448 100%); }
#pallu { left: 330px; top: 1300px; width: 160px; height: 460px; border-radius: 80px 20px 60px 20px; background: #FFC94A; transform: rotate(14deg); opacity: .9; }
#arm { left: 700px; top: 1150px; width: 70px; height: 260px; border-radius: 35px; background: #E7B48C; transform-origin: 35px 230px; }
#sleeve { left: 690px; top: 1320px; width: 100px; height: 110px; border-radius: 40px; background: #E8475A; }
#bookr { left: 300px; top: 1440px; width: 170px; height: 210px; border-radius: 12px; background: #9EB9F5; box-shadow: inset 12px 0 0 #7E9CE0; transform: rotate(-10deg); }
""", body="""
<div class="abs" id="board"><svg class="abs" style="left:0;top:0" width="856" height="426" viewBox="0 0 856 426">
  <path class="chalk" id="c1" d="M80 120 l40 -60 l40 60 M95 100 h50"/>
  <path class="chalk" id="c2" d="M200 60 v60 h35 a15 15 0 0 0 0 -30 h-35 M235 90 a15 15 0 0 0 0 -30"/>
  <path class="chalk" id="c3" d="M330 70 a35 35 0 1 0 0 45"/>
  <path class="chalk" id="c4" d="M560 90 l20 -40 l20 40 l45 6 l-33 30 l9 44 l-41 -22 l-41 22 l9 -44 l-33 -30 z"/>
  <path class="chalk" id="c5" d="M90 260 q60 -50 120 0 t120 0 t120 0 t120 0"/>
  <path class="chalk" id="c6" d="M700 230 h80 M740 190 v80"/>
</svg></div>
<div class="abs" id="tray"></div>
<div class="abs" id="arm"></div><div class="abs" id="body"></div><div class="abs" id="pallu"></div><div class="abs" id="sleeve"></div>
<div class="abs" id="bun"></div><div class="abs" id="hair"></div><div class="abs" id="head"></div>
<div class="abs eye" style="left:480px"></div><div class="abs eye" style="left:578px"></div>
<div class="abs cheek" style="left:452px"></div><div class="abs cheek" style="left:592px"></div>
<div class="abs" id="smile"></div><div class="abs" id="bindi"></div><div class="abs" id="bookr"></div>
<div class="abs spark" style="left:140px;top:1300px">✨</div><div class="abs spark" style="left:880px;top:1280px">✨</div>
""", js="""
  tl.fromTo("#board, #tray", {y: -200, opacity: 0}, {y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.6)"}, 0);
  document.querySelectorAll(".chalk").forEach((p) => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
  tl.to(".chalk", {strokeDashoffset: 0, duration: 0.5, ease: "power1.inOut", stagger: 0.12}, 0.3);
  tl.fromTo("#body, #pallu, #sleeve, #head, #hair, #bun, .eye, .cheek, #smile, #bindi, #bookr, #arm", {y: 600}, {y: 0, duration: 0.5, ease: "back.out(1.4)"}, 0.1);
  tl.fromTo("#arm", {rotation: 10}, {rotation: -22, duration: 0.2, yoyo: true, repeat: 7, ease: "sine.inOut"}, 0.6);
  tl.to(".eye", {scaleY: 0.1, duration: 0.06, yoyo: true, repeat: 1}, 1.3);
""")

# 7 -- "Ye bag kiska hai?": a handbag alone on a chair, question marks floating up around it
SCENES["ex7_bag"] = dict(css="""
#spot { left: 140px; top: 1640px; width: 800px; height: 140px; border-radius: 50%; background: radial-gradient(ellipse, rgba(255,244,230,.45), rgba(255,244,230,0) 70%); }
#back { left: 330px; top: 860px; width: 420px; height: 470px; border-radius: 60px 60px 30px 30px; background: linear-gradient(180deg, #6B3F2A, #4A2E22); box-shadow: inset 0 0 0 14px #85503D; }
#seat { left: 290px; top: 1310px; width: 500px; height: 110px; border-radius: 40px; background: linear-gradient(180deg, #85503D, #5C3626); box-shadow: 0 16px 30px rgba(0,0,0,.4); }
.cl { top: 1410px; width: 34px; height: 260px; border-radius: 17px; background: #3A231A; }
#bag { left: 405px; top: 1060px; width: 270px; height: 230px; border-radius: 30px 30px 50px 50px; background: linear-gradient(170deg, #F7B3C2, #E8475A);
  box-shadow: 0 16px 26px rgba(0,0,0,.35); transform-origin: 50% 100%; }
#handle { left: 455px; top: 980px; width: 170px; height: 130px; border-radius: 85px 85px 0 0; border: 22px solid #C93448; border-bottom: none; }
#clasp { left: 520px; top: 1110px; width: 40px; height: 40px; border-radius: 10px; background: #FFC94A; }
#flap { left: 405px; top: 1060px; width: 270px; height: 90px; border-radius: 30px 30px 80px 80px; background: #C93448; }
""", body="""
<div class="abs" id="spot"></div>
<div class="abs cl" style="left:330px;transform:rotate(8deg)"></div><div class="abs cl" style="left:716px;transform:rotate(-8deg)"></div>
<div class="abs" id="back"></div><div class="abs" id="seat"></div>
<div class="abs" id="handle"></div><div class="abs" id="bag"></div><div class="abs" id="flap"></div><div class="abs" id="clasp"></div>
<div class="abs q" style="left:170px;top:1180px;color:#F7B3C2">?</div><div class="abs q" style="left:820px;top:1120px;color:#FFC995">?</div>
<div class="abs q" style="left:250px;top:880px;color:#9EB9F5">?</div><div class="abs q" style="left:760px;top:860px;color:#8FD6B8">?</div>
<div class="abs q" style="left:500px;top:780px;color:#C9A8F2">?</div>
<div class="abs spark" style="left:640px;top:990px">✨</div>
""", js="""
  tl.fromTo("#back, #seat, .cl, #spot", {opacity: 0, y: 120}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 0);
  tl.fromTo("#bag, #handle, #flap, #clasp", {y: -500}, {y: 0, duration: 0.5, ease: "bounce.out"}, 0.15);
  tl.to("#bag, #handle, #flap, #clasp", {rotation: 4, duration: 0.12, yoyo: true, repeat: 7, ease: "sine.inOut", transformOrigin: "50% 100%"}, 0.7);
  tl.fromTo(".q", {scale: 0, y: 40, rotation: -25}, {scale: 1, y: 0, rotation: 0, duration: 0.35, ease: "back.out(3)", stagger: 0.09}, 0.45);
  tl.to(".q", {y: -40, rotation: 12, duration: 0.6, yoyo: true, repeat: 1, ease: "sine.inOut", stagger: 0.07}, 0.9);
""")


def write():
    for name, sc in SCENES.items():
        d = HERE / name
        (d / "vendor").mkdir(parents=True, exist_ok=True)
        (d / "fonts").mkdir(exist_ok=True)
        shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", d / "vendor/gsap.min.js")
        for f in (HERE.parent / "board" / "fonts").glob("*.woff2"):
            shutil.copy(f, d / "fonts" / f.name)
        (d / "hyperframes.json").write_text('{"name":"nikita6-anim-%s"}\n' % name)
        (d / "index.html").write_text(HEAD.replace("%CSS%", sc["css"]).replace("%BODY%", sc["body"]).replace("%JS%", sc["js"]))
        print("wrote", d / "index.html")


def render():
    import os
    env = dict(os.environ, NODE_USE_ENV_PROXY="1", NODE_EXTRA_CA_CERTS="/root/.ccr/ca-bundle.crt")
    OUT.mkdir(parents=True, exist_ok=True)
    for name in list(SCENES) + ["movie"]:
        out = OUT / (f"{name}_anim.mp4" if name != "movie" else "ex6_movie_anim.mp4")
        subprocess.run(["npx", "hyperframes", "render", str(HERE / name), "-o", str(out), "--quality", "high", "--quiet"],
                       check=True, env=env, cwd=ROOT, stdout=subprocess.DEVNULL)
        print("rendered", out)


if __name__ == "__main__":
    write()
    if "render" in sys.argv:
        render()
