"""Caption layer for the Nikita 4 reel -- "Restaurant Menu" style (new for this video).

A cosy restaurant world for a situation-based lesson: a grammar book stamped NAHI, a neon "Restaurant
English" sign, then five situations one after another -- each with an animated icon on a dinner plate (table
for two, a menu opening, a spinning spoon, a glass filling, a bill printing), the Hindi need as a handwritten
waiter's note straight on the wall, and the English line written word by word onto an order ticket (key words
get a mustard marker, "please" a polite stamp). Then a "Today's Menu" recap card and a comment CTA.
DM Serif Display + Outfit + Kalam (+ Pacifico for the neon); tomato / mustard / cream / charcoal;
warm candle-glow bloom transitions and a paper-ticket swipe between situations.

Everything sits in the wall above her head: y 262-830 on the 1080x1920 stage, x 120-960 (Reels safe box,
face never covered). Usage: python3 -I build_overlay.py [--preview]   (--preview = 1080p)
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

PLATE = '<circle cx="80" cy="80" r="76" fill="#FFFDF8"/><circle cx="80" cy="80" r="58" fill="none" stroke="#EADBC2" stroke-width="3"/>'
ICONS = {
    "table": """<g class="i-table"><rect x="34" y="70" width="92" height="12" rx="5" fill="#8A5A3B"/>
        <rect x="44" y="82" width="8" height="34" fill="#8A5A3B"/><rect x="108" y="82" width="8" height="34" fill="#8A5A3B"/>
        <path d="M60 64 Q80 50 100 64" stroke="#F4B63F" stroke-width="5" fill="none" stroke-linecap="round"/></g>
      <g class="i-chairL"><rect x="16" y="56" width="8" height="58" rx="3" fill="#E8452C"/><rect x="16" y="86" width="26" height="8" rx="3" fill="#E8452C"/>
        <rect x="34" y="94" width="6" height="22" fill="#E8452C"/></g>
      <g class="i-chairR"><rect x="136" y="56" width="8" height="58" rx="3" fill="#E8452C"/><rect x="118" y="86" width="26" height="8" rx="3" fill="#E8452C"/>
        <rect x="120" y="94" width="6" height="22" fill="#E8452C"/></g>
      <g class="i-two"><circle cx="122" cy="36" r="17" fill="#F4B63F"/><text x="122" y="44" text-anchor="middle" font-family="Outfit" font-weight="800" font-size="24" fill="#2B2522">2</text></g>""",
    "menu": """<g class="i-pages"><rect x="34" y="36" width="92" height="90" rx="6" fill="#FFF4E0" stroke="#2B2522" stroke-width="3"/>
        <line x1="80" y1="40" x2="80" y2="122" stroke="#2B2522" stroke-width="2"/>
        <g class="i-lines" stroke="#E8452C" stroke-width="4" stroke-linecap="round">
        <line x1="44" y1="56" x2="70" y2="56"/><line x1="44" y1="72" x2="66" y2="72"/><line x1="44" y1="88" x2="70" y2="88"/>
        <line x1="90" y1="56" x2="116" y2="56"/><line x1="90" y1="72" x2="112" y2="72"/><line x1="90" y1="88" x2="116" y2="88"/></g></g>
      <g class="i-cover"><rect x="80" y="36" width="46" height="90" rx="6" fill="#E8452C"/>
        <text x="103" y="88" text-anchor="middle" font-family="DM Serif Display" font-size="18" fill="#FFF4E0">Menu</text></g>""",
    "spoon": """<g class="i-spoon"><ellipse cx="80" cy="54" rx="17" ry="24" fill="#C9CED6" stroke="#8E96A3" stroke-width="3"/>
        <rect x="75" y="74" width="10" height="54" rx="5" fill="#C9CED6" stroke="#8E96A3" stroke-width="3"/>
        <ellipse cx="75" cy="48" rx="5" ry="9" fill="#FFFFFF" opacity=".8"/></g>
      <g class="i-spark" fill="#F4B63F"><path d="M122 34 l4 10 10 4 -10 4 -4 10 -4 -10 -10 -4 10 -4z"/><path d="M36 104 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3z"/></g>""",
    "water": """<defs><clipPath id="glassclip"><path d="M50 32 L110 32 L102 128 L58 128 Z"/></clipPath></defs>
      <g clip-path="url(#glassclip)"><rect class="i-water" x="40" y="130" width="80" height="100" fill="#5DB8F0"/>
        <circle class="i-bub b1" cx="70" cy="122" r="4" fill="#DDF2FF"/><circle class="i-bub b2" cx="88" cy="124" r="3" fill="#DDF2FF"/>
        <circle class="i-bub b3" cx="80" cy="126" r="3.5" fill="#DDF2FF"/></g>
      <path d="M50 32 L110 32 L102 128 L58 128 Z" fill="none" stroke="#2B2522" stroke-width="4" stroke-linejoin="round"/>
      <line x1="60" y1="44" x2="64" y2="110" stroke="#FFFFFF" stroke-width="4" opacity=".7" stroke-linecap="round"/>""",
    "bill": """<defs><clipPath id="billclip"><rect x="30" y="48" width="100" height="100"/></clipPath></defs>
      <g clip-path="url(#billclip)"><g class="i-receipt"><path d="M48 -40 H112 V112 l-8 6 -8 -6 -8 6 -8 -6 -8 6 -8 -6 -8 6 -8 -6 Z" fill="#FFFFFF" stroke="#CBBBA0" stroke-width="2"/>
        <g stroke="#9A8F80" stroke-width="3" stroke-linecap="round"><line x1="58" y1="64" x2="100" y2="64"/><line x1="58" y1="76" x2="92" y2="76"/><line x1="58" y1="88" x2="100" y2="88"/></g>
        <text x="80" y="106" text-anchor="middle" font-family="Outfit" font-weight="800" font-size="15" fill="#E8452C">TOTAL ₹</text></g></g>
      <rect x="34" y="30" width="92" height="22" rx="8" fill="#2B2522"/><rect x="44" y="46" width="72" height="5" rx="2" fill="#111"/>
      <circle cx="114" cy="41" r="4" fill="#5BE37D"/>
      <g class="i-coin"><circle cx="128" cy="34" r="16" fill="#F4B63F" stroke="#C98F1C" stroke-width="3"/>
        <text x="128" y="41" text-anchor="middle" font-family="Outfit" font-weight="800" font-size="19" fill="#7A5310">₹</text></g>""",
}
EMOJI = {"table": "🪑", "menu": "📖", "spoon": "🥄", "water": "🥛", "bill": "🧾"}


def icon_svg(kind):
    """Animated icon from ICONS, or any emoji sitting on the plate (for new situations without a drawn icon)."""
    if kind in ICONS:
        return ICONS[kind]
    return f'<text class="i-emoji" x="80" y="104" text-anchor="middle" font-size="64">{html.escape(kind)}</text>'


def marks(text):
    """<m>word</m> in content text -> mustard marker span."""
    return text.replace("<m>", '<span class="mus">').replace("</m>", "</span>")


def board_js(cid, times, rows):
    """Letter-board rows: each letter pops onto the felt as she says that word."""
    return "".join(
        f'tl.fromTo("#{cid}-r{k} .lt", {{opacity: 0, y: -26, scale: 1.4}}, {{opacity: 1, y: 0, scale: 1, duration: 0.16, '
        f'ease: "back.out(3)", stagger: {min(0.05, 0.45 / max(1, len(r))):.3f}}}, {t - 0.05});'
        for k, (t, r) in enumerate(zip(times, rows)))


def words_html(text):
    """English line -> word spans; **key** words grouped under one marker; 'please' marked for the stamp."""
    out = []
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        ws = [f'<span class="w{" pl" if w.lower().startswith("please") else ""}">{html.escape(w)}</span>'
              for w in part.split()]
        if not ws:
            continue
        lead = " " if part[:1] == " " else ""
        trail = " " if part[-1:] == " " else ""
        inner = " ".join(ws)
        out.append(f'{lead}<span class="key">{inner}</span>{trail}' if i % 2 else f"{lead}{inner}{trail}")
    return "".join(out).strip()


def rich(text, cls):
    parts = re.split(r"\*\*(.+?)\*\*", html.escape(text))
    return "".join(f'<span class="{cls}">{p}</span>' if i % 2 else p for i, p in enumerate(parts))


def clip(id_, start, end, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


def icon_js(cid, kind, c):
    s, k = c["hi_t"], c["key"]
    p = f"#{cid}-ic"
    if kind == "table":
        return f"""
          tl.fromTo("{p} .i-chairL", {{x: -50, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.45, ease: "back.out(2)"}}, {s + 0.35});
          tl.fromTo("{p} .i-chairR", {{x: 50, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.45, ease: "back.out(2)"}}, {s + 0.5});
          tl.fromTo("{p} .i-two", {{scale: 0, transformOrigin: "122px 36px"}}, {{scale: 1, duration: 0.35, ease: "back.out(3)"}}, {s + 1.1});
          tl.to("{p} .i-two", {{scale: 1.25, duration: 0.18, yoyo: true, repeat: 1, transformOrigin: "122px 36px"}}, {k});"""
    if kind == "menu":
        return f"""
          tl.set("{p} .i-lines line", {{strokeDasharray: 40, strokeDashoffset: 40}}, 0);
          tl.fromTo("{p} .i-cover", {{scaleX: 1, transformOrigin: "80px 80px"}}, {{scaleX: -1, duration: 0.6, ease: "power2.inOut"}}, {s + 0.45});
          tl.set("{p} .i-cover", {{opacity: 0}}, {s + 0.75});
          tl.to("{p} .i-lines line", {{strokeDashoffset: 0, duration: 0.25, stagger: 0.08}}, {s + 0.8});
          tl.to("{p} .i-pages", {{scale: 1.08, duration: 0.18, yoyo: true, repeat: 1, transformOrigin: "80px 80px"}}, {k});"""
    if kind == "spoon":
        return f"""
          tl.fromTo("{p} .i-spoon", {{rotation: -540, scale: 0.2, transformOrigin: "80px 80px"}}, {{rotation: 20, scale: 1, duration: 0.8, ease: "power3.out"}}, {s + 0.25});
          tl.to("{p} .i-spoon", {{rotation: -10, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut", transformOrigin: "80px 80px"}}, {s + 1.05});
          tl.fromTo("{p} .i-spark path", {{scale: 0, transformOrigin: "50% 50%"}}, {{scale: 1, duration: 0.3, stagger: 0.12, ease: "back.out(3)"}}, {s + 0.9});
          tl.to("{p} .i-spark path", {{scale: 1.4, opacity: 0.6, duration: 0.2, yoyo: true, repeat: 1}}, {k});"""
    if kind == "water":
        return f"""
          tl.fromTo("{p} .i-water", {{attr: {{y: 130}}}}, {{attr: {{y: 54}}, duration: 1.6, ease: "power1.inOut"}}, {s + 0.3});
          tl.fromTo("{p} .i-bub", {{attr: {{cy: 126}}, opacity: 0}}, {{attr: {{cy: 60}}, opacity: 1, duration: 1.1, stagger: 0.3, repeat: 2, ease: "none"}}, {s + 0.9});
          tl.to("{p} svg", {{rotation: 6, duration: 0.15, yoyo: true, repeat: 3, transformOrigin: "50% 80%"}}, {k});"""
    if kind not in ICONS:
        return f"""
          tl.fromTo("{p} .i-emoji", {{scale: 0.2, rotation: -40, transformOrigin: "80px 80px"}}, {{scale: 1, rotation: 0, duration: 0.6, ease: "back.out(2.4)"}}, {s + 0.2});
          tl.to("{p} .i-emoji", {{scale: 1.18, duration: 0.18, yoyo: true, repeat: 1, transformOrigin: "80px 80px"}}, {k});"""
    if kind == "bill":
        return f"""
          tl.fromTo("{p} .i-receipt", {{y: 0}}, {{y: 0, duration: 0.01}}, {s});
          tl.to("{p} .i-receipt", {{y: 36, duration: 0.5, ease: "steps(6)"}}, {s + 0.4});
          tl.to("{p} .i-receipt", {{y: 84, duration: 0.85, ease: "steps(10)"}}, {k - 0.1});
          tl.to("{p} .i-receipt", {{y: 92, duration: 0.25, ease: "back.out(2)"}}, {k + 0.8});
          tl.fromTo("{p} .i-coin", {{opacity: 0, y: 30, scale: 0.3, transformOrigin: "128px 34px"}}, {{opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(3)"}}, {k});
          tl.to("{p} .i-coin", {{rotationY: 360, duration: 0.6, ease: "power2.out"}}, {k + 0.3});"""
    return ""


def build(res=2160):
    OUT.mkdir(exist_ok=True)
    (OUT / "vendor").mkdir(exist_ok=True)
    shutil.copy(ROOT / "node_modules/gsap/dist/gsap.min.js", OUT / "vendor/gsap.min.js")
    # fonts/ (DM Serif Display, Outfit, Kalam, Pacifico; Google Fonts, OFL) are kept in git with the overlay

    els, js = [], []
    n_sit = sum(c["type"] == "situation" for c in CUES["captions"])
    for i, c in enumerate(CUES["captions"]):
        s, e = c["start"], c["end"]
        cid = f"c{i}"
        if c["type"] == "hook":
            b, tx = c["beats"], c["text"]
            rows = "".join(f'<div class="lb-row" id="{cid}-r{k}">' + "".join(
                f'<span class="lt" style="transform: rotate({((j * 7 + k * 3) % 5 - 2) * 1.2:.1f}deg)">{ch if ch != " " else "&nbsp;"}</span>'
                for j, ch in enumerate(row)) + "</div>" for k, row in enumerate(tx["board"]))
            els.append(clip(cid, s, e, 1, f"""
              <div class="scene" id="{cid}-a">
                <div class="h-q" id="{cid}-q">{marks(tx['question'])}</div>
                <div class="book" id="{cid}-book"><div class="b-spine"></div><div class="b-title">{tx['book']}</div><div class="b-lines"><i></i><i></i><i></i></div></div>
                <div class="stamp" id="{cid}-st" data-layout-allow-overlap>{tx['stamp']}</div>
              </div>
              <div class="scene" id="{cid}-b">
                <div class="board" id="{cid}-board"><div class="lb-felt">{rows}</div><div class="lb-check" id="{cid}-ck">✓</div></div>
                <div class="h-note" id="{cid}-talk">{tx['board_note']}</div>
              </div>
              <div class="scene" id="{cid}-c">
                <div class="h-note top" id="{cid}-aaj">{tx['today']}</div>
                <div class="neon" id="{cid}-neon"><div class="n-a">{tx['neon']}</div><div class="n-b">{tx['neon_sub']}</div></div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-q", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power2.out"}}, 0.15);
              tl.fromTo("#{cid}-book", {{opacity: 0, y: 60, rotation: -8}}, {{opacity: 1, y: 0, rotation: -3, duration: 0.5, ease: "back.out(1.7)"}}, {b['book']});
              tl.fromTo("#{cid}-st", {{opacity: 0, scale: 2.6, rotation: -24}}, {{opacity: 1, scale: 1, rotation: -12, duration: 0.22, ease: "power4.in"}}, {b['stamp'] - 0.22});
              tl.to("#{cid}-book", {{x: 10, duration: 0.05, yoyo: true, repeat: 5}}, {b['stamp']});
              tl.to("#{cid}-a", {{x: -700, rotation: -8, opacity: 0, duration: 0.4, ease: "power2.in"}}, {b['rows'][0] - 0.55});
              tl.fromTo("#{cid}-board", {{opacity: 0, y: -260, rotation: -6}}, {{opacity: 1, y: 0, rotation: 0, duration: 0.5, ease: "bounce.out"}}, {b['rows'][0] - 0.45});
              {board_js(cid, b['rows'], tx['board'])}
              tl.fromTo("#{cid}-ck", {{opacity: 0, scale: 2.4, rotation: -30}}, {{opacity: 1, scale: 1, rotation: 8, duration: 0.25, ease: "power4.in"}}, {b['note'] - 0.1});
              tl.fromTo("#{cid}-talk", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.35}}, {b['note']});
              tl.to("#{cid}-b", {{y: -80, opacity: 0, duration: 0.35, ease: "power2.in"}}, {b['today'] - 0.3});
              tl.fromTo("#{cid}-aaj", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.35}}, {b['today']});
              tl.set("#{cid}-neon", {{opacity: 0}}, 0);
              tl.set("#{cid}-neon", {{opacity: 1}}, {b['neon']});
              tl.set("#{cid}-neon", {{opacity: 0.15}}, {b['neon'] + 0.07});
              tl.set("#{cid}-neon", {{opacity: 1}}, {b['neon'] + 0.14});
              tl.set("#{cid}-neon", {{opacity: 0.25}}, {b['neon'] + 0.2});
              tl.set("#{cid}-neon", {{opacity: 1}}, {b['neon'] + 0.32});
              tl.fromTo("#{cid}-neon .n-b", {{opacity: 0.2}}, {{opacity: 1, duration: 0.3}}, {b['neon'] + 0.32});
              tl.to("#{cid}-neon", {{opacity: 0.55, duration: 0.05, yoyo: true, repeat: 1}}, {b['neon'] + 1.6});
              tl.to("#{cid}-c", {{opacity: 0, scale: 1.08, duration: 0.3, ease: "power2.in"}}, {e - 0.3});""")
        elif c["type"] == "situation":
            n = c["n"]
            dots = "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(n_sit))
            els.append(clip(cid, s, e, 2, f"""
              <div class="sit" id="{cid}-all">
                <div class="plate" id="{cid}-ic"><svg viewBox="0 0 160 160" width="150" height="150">{PLATE}{icon_svg(c['icon'])}</svg></div>
                <div class="chip" id="{cid}-chip">SITUATION {n}/{n_sit}<span class="dots">{dots}</span></div>
                <div class="hi" id="{cid}-hi">“{html.escape(c['hi'])}”</div>
                <div class="ticket" id="{cid}-tk">
                  <div class="t-head"><span>🛎️ ENGLISH MEIN</span></div>
                  <div class="t-ph" id="{cid}-ph">kaise bologe? <span class="pen">✍️</span></div>
                  <div class="t-en" id="{cid}-en">{words_html(c['en'])}</div>
                  <div class="polite" id="{cid}-po" data-layout-allow-overlap>✨ polite!</div>
                </div>
              </div>"""))
            ws_t = c["en_t"]
            js.append(f"""
              tl.fromTo("#{cid}-all", {{x: {360 if n > 1 else 0}, opacity: 0, rotation: {4 if n > 1 else 0}}}, {{x: 0, opacity: 1, rotation: 0, duration: 0.4, ease: "power3.out"}}, {s});
              tl.fromTo("#{cid}-ic", {{scale: 0.3, rotation: -90}}, {{scale: 1, rotation: 0, duration: 0.5, ease: "back.out(1.8)"}}, {c['hi_t']});
              tl.fromTo("#{cid}-chip", {{opacity: 0, y: -14}}, {{opacity: 1, y: 0, duration: 0.3}}, {c['hi_t'] + 0.05});
              tl.fromTo("#{cid}-hi", {{opacity: 0, clipPath: "inset(0 100% 0 0)"}}, {{opacity: 1, clipPath: "inset(0 0% 0 0)", duration: 0.9, ease: "power1.inOut"}}, {c['hi_t'] + 0.15});
              tl.fromTo("#{cid}-tk", {{opacity: 0, y: 40, rotation: -2}}, {{opacity: 1, y: 0, rotation: 0, duration: 0.45, ease: "back.out(1.6)"}}, {min(c['q'], ws_t - 0.6)});
              tl.fromTo("#{cid}-ph .pen", {{x: 0, rotation: 0}}, {{x: 14, rotation: 12, duration: 0.18, yoyo: true, repeat: 7, ease: "sine.inOut"}}, {min(c['q'], ws_t - 0.6) + 0.3});
              tl.to("#{cid}-ph", {{opacity: 0, duration: 0.15}}, {ws_t - 0.12});
              {words_js(cid, ws_t, c['pl'])}
              tl.fromTo("#{cid}-en .key", {{backgroundSize: "0% 42%"}}, {{backgroundSize: "100% 42%", duration: 0.35, ease: "power2.out"}}, {c['key']});
              tl.fromTo("#{cid}-po", {{opacity: 0, scale: 2.2, rotation: 22}}, {{opacity: 1, scale: 1, rotation: 9, duration: 0.2, ease: "power4.in"}}, {c['pl'] + 0.12});
              {icon_js(cid, c['icon'], c)}
              tl.to("#{cid}-all", {{x: -420, y: -40, rotation: -7, opacity: 0, duration: 0.32, ease: "power2.in"}}, {e - 0.32});""")
        elif c["type"] == "recap":
            items = "".join(f'<div class="r-item"><span class="r-ic">{EMOJI.get(k, k)}</span><span class="r-t">{rich(t, "r-k")}</span><span class="r-tick">✓</span></div>'
                            for t, k in zip(c["items"], c["icons"]))
            els.append(clip(cid, s, e, 3, f"""
              <div class="menu" id="{cid}-m">
                <div class="m-title">{c['title']}</div>
                <div class="m-sub">{c['sub']}</div>
                <div class="m-rule"></div>
                {items}
                <div class="m-foot" id="{cid}-say">{c['say']}</div>
              </div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-m", {{opacity: 0, y: 60, rotationX: 40, transformPerspective: 900}}, {{opacity: 1, y: 0, rotationX: 0, duration: 0.55, ease: "back.out(1.4)"}}, {s + 0.05});
              tl.fromTo("#{cid}-m .r-item", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.3, stagger: 0.32, ease: "power2.out"}}, {s + 0.45});
              tl.fromTo("#{cid}-m .r-tick", {{opacity: 0, scale: 2}}, {{opacity: 1, scale: 1, duration: 0.18, stagger: 0.32, ease: "power3.in"}}, {s + 0.7});
              tl.fromTo("#{cid}-say", {{opacity: 0, y: 12}}, {{opacity: 1, y: 0, duration: 0.35}}, {c['say_t']});
              tl.to("#{cid}-m", {{opacity: 0, y: -60, duration: 0.3, ease: "power2.in"}}, {e - 0.3});""")
        elif c["type"] == "cta":
            chips = "".join(f'<span class="idea">{t}</span>' for t in c["ideas"])
            els.append(clip(cid, s, e, 4, f"""
              <div class="cta-h" id="{cid}-h">{marks(c['head'])}</div>
              <div class="ideas" id="{cid}-i">{chips}</div>
              <div class="cbar" id="{cid}-cb"><span class="ph">{c['bar']}<i class="cursor">|</i></span>
                <span class="send" id="{cid}-btn">💬 Comment</span></div>
              <div class="burst" id="{cid}-bu">❤️</div>"""))
            js.append(f"""
              tl.fromTo("#{cid}-h", {{opacity: 0, scale: 0.7}}, {{opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2)"}}, {s + 0.1});
              tl.fromTo("#{cid}-h .mus", {{backgroundSize: "0% 42%"}}, {{backgroundSize: "100% 42%", duration: 0.35}}, {c['more']});
              tl.fromTo("#{cid}-cb", {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: 0.4, ease: "back.out(1.6)"}}, {c['comment']});
              tl.fromTo("#{cid} .cursor", {{opacity: 1}}, {{opacity: 0, duration: 0.25, yoyo: true, repeat: 15}}, {c['comment']});
              tl.fromTo("#{cid}-i .idea", {{opacity: 0, y: 50, scale: 0.6}}, {{opacity: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.2, ease: "back.out(2)"}}, {c['ideas_t']});
              tl.to("#{cid}-i .idea", {{y: -8, duration: 0.9, yoyo: true, repeat: 5, stagger: 0.15, ease: "sine.inOut"}}, {c['ideas_t'] + 1.4});
              tl.to("#{cid}-btn", {{scale: 0.86, duration: 0.08, yoyo: true, repeat: 1}}, {c['tap']});
              tl.fromTo("#{cid}-bu", {{opacity: 0, scale: 0.3, y: 0}}, {{opacity: 1, scale: 1.3, y: -70, duration: 0.45, ease: "back.out(2)"}}, {c['tap'] + 0.05});
              tl.to("#{cid}-bu", {{opacity: 0, duration: 0.3}}, {c['tap'] + 0.6});""")

    for j, f in enumerate(CUES["flashes"]):
        els.append(clip(f"tr{j}", max(0, f - 0.3), f + 0.55, 9, '<div class="glow"></div><div class="flame"></div>'))
        js.append(f"""
              tl.fromTo("#tr{j} .glow", {{yPercent: 45, opacity: 0, scale: 0.7}}, {{yPercent: -10, opacity: 0.8, scale: 1.15, duration: 0.38, ease: "power2.out"}}, {max(0, f - 0.3)});
              tl.to("#tr{j} .glow", {{opacity: 0.45, duration: 0.06, yoyo: true, repeat: 3}}, {f + 0.02});
              tl.to("#tr{j} .glow", {{opacity: 0, yPercent: -40, duration: 0.3}}, {f + 0.25});
              tl.fromTo("#tr{j} .flame", {{opacity: 0, scale: 0.5}}, {{opacity: 0.7, scale: 1.5, duration: 0.2, ease: "power2.out"}}, {max(0, f - 0.12)});
              tl.to("#tr{j} .flame", {{opacity: 0, duration: 0.3}}, {f + 0.1});""")

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


def words_js(cid, t0, pl):
    """Write the English line onto the ticket word by word, finishing on 'please' as she says it."""
    return (f'tl.fromTo("#{cid}-en .w", {{opacity: 0, y: 18, rotation: -4}}, {{opacity: 1, y: 0, rotation: 0, '
            f'duration: 0.22, ease: "power2.out", stagger: {{amount: {max(0.2, pl - t0 - 0.05):.2f}}}}}, {t0});')


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=2160, height=3840" />
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "DM Serif Display"; src: url(fonts/dmserif-400.woff2) format("woff2"); }
@font-face { font-family: "DM Serif Display"; src: url(fonts/dmserif-400i.woff2) format("woff2"); font-style: italic; }
@font-face { font-family: "Outfit"; src: url(fonts/outfit.woff2) format("woff2"); font-weight: 100 900; }
@font-face { font-family: "Kalam"; src: url(fonts/kalam-700.woff2) format("woff2"); font-weight: 700; }
@font-face { font-family: "Pacifico"; src: url(fonts/pacifico-400.woff2) format("woff2"); }
:root { --tomato: #E8452C; --mustard: #F4B63F; --cream: #FFF4E0; --ink: #2B2522; --brown: #8A5A3B;
  --wall: 0 2px 3px rgba(0,0,0,.55), 0 4px 18px rgba(0,0,0,.6), 0 0 2px rgba(0,0,0,.4); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 2160px; height: 3840px; overflow: hidden; background: transparent; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { width: 2160px; height: 3840px; }
.layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; transform: scale(2); }
.layer > div { position: absolute; }
.scene { left: 120px; top: 270px; width: 840px; height: 560px; }
.scene > div { position: absolute; }
.mus { padding: 0 6px; background-image: linear-gradient(var(--mustard), var(--mustard)); background-repeat: no-repeat;
  background-position: 0 88%; background-size: 100% 42%; }

/* hook */
.h-q { left: 0; top: 0; width: 840px; text-align: center; font: 700 56px/1.2 Kalam; color: var(--cream); text-shadow: var(--wall); }
.h-q .mus { color: var(--ink); text-shadow: none; }
.book { left: 290px; top: 120px; width: 260px; height: 330px; border-radius: 10px 18px 18px 10px; background: var(--tomato);
  box-shadow: 0 18px 40px rgba(0,0,0,.4), inset -10px 0 0 rgba(0,0,0,.12); }
.b-spine { position: absolute; left: 0; top: 0; width: 30px; height: 100%; border-radius: 10px 0 0 10px; background: #B8301C; }
.b-title { position: absolute; left: 30px; top: 60px; width: 230px; text-align: center; font: 400 40px/1.1 "DM Serif Display"; color: var(--cream); }
.b-lines { position: absolute; left: 70px; top: 190px; width: 150px; }
.b-lines i { display: block; height: 8px; border-radius: 4px; background: rgba(255,244,224,.55); margin-bottom: 16px; }
.stamp { left: 210px; top: 210px; width: max-content; padding: 10px 30px; border: 8px solid #D21F1F; border-radius: 16px;
  font: 800 92px/1 Outfit; letter-spacing: 4px; color: #D21F1F; background: rgba(255,244,224,.9); box-shadow: 0 10px 30px rgba(0,0,0,.35); }
.board { left: 70px; top: 0; width: 700px; padding: 16px; border-radius: 16px; background: linear-gradient(160deg, #A06A45, #6E4429);
  box-shadow: 0 20px 44px rgba(0,0,0,.45); }
.lb-felt { padding: 22px 10px 18px; border-radius: 8px; text-align: center;
  background: repeating-linear-gradient(180deg, #1F1C1B 0 10px, #171514 10px 12px); box-shadow: inset 0 4px 14px rgba(0,0,0,.6); }
.lb-row { height: 92px; display: flex; justify-content: center; align-items: center; }
.lt { display: inline-block; margin: 0 4px; font: 800 64px/1 Outfit; color: #F7F3EA;
  text-shadow: 0 2px 0 #bdb6a8, 0 4px 6px rgba(0,0,0,.6); }
.lb-check { right: -22px; top: -26px; width: 88px; height: 88px; border-radius: 44px; background: var(--mustard); color: var(--ink);
  font: 800 56px/88px Outfit; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,.4); }
.board > div.lb-check { position: absolute; }
.h-big { left: 0; top: 40px; width: 840px; text-align: center; font: 400 112px/1 "DM Serif Display"; color: #fff; text-shadow: 0 6px 24px rgba(0,0,0,.5); }
.tick { display: inline-block; color: var(--mustard); font: 800 100px/1 Outfit; }
.bub { font: 700 40px/1 Outfit; color: var(--ink); background: var(--cream); padding: 18px 28px; border-radius: 30px; width: max-content;
  box-shadow: 0 10px 26px rgba(0,0,0,.3); }
.bA { left: 20px; top: 210px; border-bottom-left-radius: 6px; }
.bB { left: 300px; top: 300px; background: var(--mustard); }
.bC { right: 10px; top: 210px; border-bottom-right-radius: 6px; }
.h-note { left: 0; top: 400px; width: 840px; text-align: center; font: 700 60px/1.2 Kalam; color: var(--cream); text-shadow: var(--wall); }
.h-note.top { top: 10px; }
.neon { left: 0; top: 110px; width: 840px; text-align: center; }
.n-a { font: 400 132px/1.25 Pacifico; color: #FFE9E2;
  text-shadow: 0 0 6px #fff, 0 0 16px #FF6B4A, 0 0 34px #FF4A2A, 0 0 60px #E8452C, 0 0 90px #E8452C; }
.n-b { margin-top: 6px; font: 800 70px/1 Outfit; letter-spacing: 16px; color: #FFF6D6;
  text-shadow: 0 0 6px #fff, 0 0 16px #FFC94D, 0 0 34px #F4B63F, 0 0 64px #F4A53F; }

/* situation */
.sit { left: 120px; top: 268px; width: 840px; height: 570px; }
.sit > div { position: absolute; }
.plate { left: 0; top: 0; width: 150px; height: 150px; border-radius: 75px; box-shadow: 0 12px 30px rgba(0,0,0,.35); }
.plate svg { display: block; overflow: visible; }
.chip { left: 172px; top: 4px; width: max-content; padding: 10px 20px; border-radius: 24px; background: var(--mustard); color: var(--ink);
  font: 800 26px/1 Outfit; letter-spacing: 3px; display: flex; align-items: center; gap: 14px; box-shadow: 0 6px 16px rgba(0,0,0,.25); }
.dots { display: flex; gap: 6px; }
.dots i { width: 10px; height: 10px; border-radius: 5px; background: rgba(43,37,34,.25); display: block; }
.dots i.on { background: var(--tomato); }
.hi { left: 172px; top: 58px; width: 668px; font: 700 58px/1.14 Kalam; color: #FFFDF6;
  text-shadow: 0 2px 2px rgba(0,0,0,.75), 0 3px 10px rgba(0,0,0,.7), 0 6px 26px rgba(0,0,0,.55), 0 0 2px rgba(0,0,0,.6); }
.ticket { left: 0; top: 232px; width: 840px; padding: 18px 34px 28px; background: var(--cream); border-radius: 18px 18px 0 0;
  box-shadow: 0 18px 40px rgba(0,0,0,.32); border-top: 10px solid var(--tomato); }
.ticket::after { content: ""; position: absolute; left: 0; right: 0; bottom: -16px; height: 16px;
  background: linear-gradient(135deg, var(--cream) 50%, transparent 50%) 0 0 / 32px 16px repeat-x,
              linear-gradient(-135deg, var(--cream) 50%, transparent 50%) 0 0 / 32px 16px repeat-x; }
.t-head { display: flex; justify-content: space-between; font: 800 24px/1 Outfit; letter-spacing: 3px; color: var(--tomato);
  padding-bottom: 12px; margin-bottom: 14px; border-bottom: 3px dashed rgba(43,37,34,.25); }
.t-ph { position: absolute; left: 34px; top: 82px; font: 700 46px/1.2 Kalam; color: rgba(43,37,34,.45); }
.pen { display: inline-block; }
.t-en { font: 700 62px/1.16 Outfit; color: var(--ink); letter-spacing: -1px; min-height: 72px; }
.t-en .w { display: inline-block; }
.t-en .key { color: #B8301C; background-image: linear-gradient(rgba(244,182,63,.75), rgba(244,182,63,.75)); background-repeat: no-repeat;
  background-position: 0 90%; background-size: 0% 42%; }
.t-en .pl { color: var(--tomato); }
.polite { position: absolute; right: -18px; top: -34px; padding: 8px 18px; border: 4px solid var(--tomato); border-radius: 14px; background: #fff;
  font: 700 34px/1 Kalam; color: var(--tomato); box-shadow: 0 6px 14px rgba(0,0,0,.25); }

/* recap menu card */
.menu { left: 125px; top: 262px; width: 830px; padding: 26px 36px 26px; background: var(--cream); border-radius: 26px;
  box-shadow: 0 22px 50px rgba(0,0,0,.4); border: 3px solid #EAD7B5; outline: 3px solid var(--cream); outline-offset: 6px; }
.m-title { text-align: center; font: 400 66px/1 "DM Serif Display"; color: var(--tomato); }
.m-sub { text-align: center; margin-top: 8px; font: 700 30px/1.2 Kalam; color: var(--brown); }
.m-rule { height: 0; border-top: 3px dashed rgba(43,37,34,.25); margin: 14px 0 6px; }
.r-item { display: flex; align-items: center; gap: 14px; padding: 11px 0; border-bottom: 2px dotted rgba(43,37,34,.18); }
.r-ic { font-size: 34px; width: 42px; text-align: center; }
.r-t { flex: 1; font: 600 36px/1.15 Outfit; color: var(--ink); }
.r-k { color: #B8301C; font-weight: 800; }
.r-tick { font: 800 32px/1 Outfit; color: #2E9B57; }
.m-foot { margin-top: 14px; text-align: center; font: 700 38px/1.1 Kalam; color: var(--tomato); }

/* CTA */
.cta-h { left: 120px; top: 276px; width: 840px; text-align: center; font: 400 84px/1.08 "DM Serif Display"; color: #fff; text-shadow: 0 6px 24px rgba(0,0,0,.5); }
.cta-h .mus { color: var(--ink); text-shadow: none; }
.ideas { left: 120px; top: 480px; width: 840px; display: flex; flex-wrap: wrap; justify-content: center; gap: 16px 16px; }
.idea { display: inline-block; padding: 14px 24px; border-radius: 30px; background: var(--cream); color: var(--ink); font: 700 36px/1 Outfit;
  box-shadow: 0 8px 20px rgba(0,0,0,.3); }
.idea:nth-child(3n+2) { background: var(--mustard); }
.cbar { left: 120px; top: 690px; width: 840px; height: 104px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 14px 0 32px; border-radius: 52px; background: #fff; box-shadow: 0 10px 24px rgba(0,0,0,.32); }
.ph { font: 600 34px/1 Outfit; color: #8a7f74; }
.cursor { font-style: normal; color: var(--ink); margin-left: 4px; }
.send { padding: 20px 28px; border-radius: 40px; background: var(--tomato); color: #fff; font: 800 34px/1 Outfit; }
.burst { left: 820px; top: 640px; font-size: 64px; }

/* transition: warm candle glow rising from below, flickering, with a bright flame core */
.glow { position: absolute; left: -540px; top: 200px; width: 2160px; height: 2200px;
  background: radial-gradient(ellipse 40% 34% at 50% 55%, rgba(255,246,220,.95), rgba(255,190,90,.8) 32%, rgba(240,120,50,.45) 58%, rgba(232,69,44,0) 76%); }
.flame { position: absolute; left: 240px; top: 420px; width: 600px; height: 760px; border-radius: 50%;
  background: radial-gradient(ellipse at 50% 60%, rgba(255,255,245,1), rgba(255,214,140,.6) 45%, rgba(255,214,140,0) 70%); }
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
