"""Caption layer for Nikita 12 (motivational: kids learn English fast because they don't fear mistakes).
User picked "A + B combined" from board_opts: A = reel subtitles (2-5 words, big bold white, black outline, power word
yellow) running through the whole reel at chest height; B = big ANTON statements above her head (one word boxed yellow)
at the 5 key moments. Two versions (user, 27 Nov): v1 = her words in Hinglish (Roman script); v2 = "Hindi as in words
written in Hindi language": Devanagari, English words kept in English (Mukta font). In Roman script "gaddhe" can read as
"gadhe", so v1 says potholes / speed breakers; v2 writes गड्ढे.
Rendered natively at 2160x3840.   Usage: python3 -I overlay.py v1|v2 -> overlay/<v>/index.html
"""

import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cut as C  # noqa: E402

# (take, source start, Hinglish in Roman script, Hindi in Devanagari with English words kept in English); *word* = yellow.
CHUNKS = [
    (2, 0.09, "Kabhi aapne socha hai", "कभी आपने सोचा है"),
    (2, 1.12, "ki bachche", "कि बच्चे"),
    (2, 1.90, "English itni *jaldi*", "English इतनी *जल्दी*"),
    (2, 3.00, "bolna kaise seekh jaate hain?", "बोलना कैसे सीख जाते हैं?"),
    (2, 4.44, "Lekin mere jaise", "लेकिन मेरे जैसे"),
    (2, 5.46, "aur aapke jaise *adults*", "और आपके जैसे *adults*"),
    (2, 6.72, "hum log itni jaldi", "हम लोग इतनी जल्दी"),
    (2, 7.78, "*nahi* seekh paate", "*नहीं* सीख पाते"),
    (3, 0.03, "Kyunki jo bachche hote hain", "क्योंकि जो बच्चे होते हैं"),
    (3, 1.14, "wo ye *nahi* sochte", "वो ये *नहीं* सोचते"),
    (3, 2.16, "ki agar mujhse *galti* ho gayi", "कि अगर मुझसे *गलती* हो गई"),
    (3, 3.62, "toh saamne wala", "तो सामने वाला"),
    (3, 4.50, "mere baare mein kya sochega?", "मेरे बारे में क्या सोचेगा?"),
    (5, 0.12, "Bachche *bina soche*", "बच्चे *बिना सोचे*"),
    (5, 1.34, "English bolne ka try karte hain", "English बोलने का try करते हैं"),
    (5, 2.90, "aur bahut baar aisa bhi hota hai", "और बहुत बार ऐसा भी होता है"),
    (5, 4.48, "ki wo English", "कि वो English"),
    (5, 5.34, "*galat* bhi bolte hain", "*गलत* भी बोलते हैं"),
    (6, 0.18, "Aur wo unhi *galtiyon* se", "और वो उन्हीं *गलतियों* से"),
    (6, 1.42, "*seekh* jaate hain", "*सीख* जाते हैं"),
    (6, 2.44, "ki correct sentences kaunse hain", "कि correct sentences कौन से हैं"),
    (6, 4.08, "aur galat kaunse", "और गलत कौन से"),
    (7, 0.03, "Aur aap aur mere jaise log", "और आप और मेरे जैसे लोग"),
    (7, 1.28, "kya sochte hain?", "क्या सोचते हैं?"),
    (7, 2.19, "Agar mujhse *galti* ho gayi toh?", "अगर मुझसे *गलती* हो गई तो?"),
    (7, 4.14, "Kisi ne agar mujhe", "किसी ने अगर मुझे"),
    (7, 4.66, "*judge* kar liya toh?", "*judge* कर लिया तो?"),
    (7, 6.12, "Aur inhi thoughts ki wajah se", "और इन्हीं thoughts की वजह से"),
    (7, 7.54, "hum English seekhna *chhod* dete hain", "हम English सीखना *छोड़* देते हैं"),
    (8, 0.03, "Jab tak aap ye soch", "जब तक आप ये सोच"),
    (8, 1.28, "apne dimaag se *nahi nikaaloge*", "अपने दिमाग से *नहीं निकालोगे*"),
    (8, 2.97, "tab tak aap", "तब तक आप"),
    (8, 3.80, "ek *lifelong learner*", "एक *lifelong learner*"),
    (8, 4.84, "nahi ban paoge", "नहीं बन पाओगे"),
    (9, 0.06, "Aur is poore reel ka purpose ye hai", "और इस पूरी reel का purpose ये है"),
    (9, 2.00, "main aapko samjhana chahti hoon", "मैं आपको समझाना चाहती हूँ"),
    (9, 3.56, "ki galtiyon par *focus*", "कि गलतियों पर *focus*"),
    (9, 4.76, "karna *band* kijiye", "करना *बंद* कीजिए"),
    (9, 6.46, "For example,", "For example,"),
    (9, 7.18, "jab hum ghar se bahar nikalte hain", "जब हम घर से बाहर निकलते हैं"),
    (9, 8.78, "kahin jaane ke liye", "कहीं जाने के लिए"),
    (9, 10.05, "toh raaste mein", "तो रास्ते में"),
    (9, 10.72, "bahut saare *speed breakers*", "बहुत सारे *speed breakers*"),
    (9, 12.10, "aur potholes aate hain", "और गड्ढे आते हैं"),
    (9, 13.11, "Lekin", "लेकिन"),
    (9, 13.72, "inhi potholes ki wajah se", "इन्हीं गड्ढों की वजह से"),
    (9, 14.74, "hum *gaadi* chalana", "हम *गाड़ी* चलाना"),
    (9, 15.66, "toh *nahi chhod* dete", "तो *नहीं छोड़* देते"),
    (9, 16.80, "Theek usi tarah", "ठीक उसी तरह"),
    (9, 17.94, "*judgement* aur *galtiyon* ki wajah se", "*judgement* और *गलतियों* की वजह से"),
    (9, 20.30, "aap English bolna", "आप English बोलना"),
    (9, 21.14, "*mat chhodiye*", "*मत छोड़िए*"),
    (9, 21.90, "Kyunki eventually", "क्योंकि eventually"),
    (9, 22.88, "hamara *goal* hai", "हमारा *goal* है"),
    (9, 23.68, "galtiyan sudhaar kar", "गलतियाँ सुधार कर"),
    (9, 24.68, "English *seekhna*", "English *सीखना*"),
]
# big statements: (start (take, s), end (take, s) or None = to the end, Hinglish, Hindi); [word] = yellow box
BIG = [
    ((2, 0.0), (2, 8.70), "Bachche [English] jaldi kyun seekhte hain? 🤔", "बच्चे [English] जल्दी क्यों सीखते हैं? 🤔"),
    ((7, 2.19), (7, 9.33), "Log kya [sochenge?] 😰", "लोग क्या [सोचेंगे?] 😰"),
    ((8, 0.0), (8, 5.93), "Ye [darr] dimaag se nikaalo 🧠", "ये [डर] दिमाग से निकालो 🧠"),
    ((9, 10.05), (9, 16.70), "Speed breakers aate hain, [gaadi] nahi rukti 🚗", "Speed breakers आते हैं, [गाड़ी] नहीं रुकती 🚗"),
    ((9, 21.90), None, "Galtiyon se [seekho], English [bolo] 💪", "गलतियों से [सीखो], English [बोलो] 💪"),
]


def T(take, s, d=0.0):
    return round(C.T(take, s) + d, 3)


def clip(id_, s, e, track, inner):
    return (f'<div id="{id_}" class="clip" data-start="{s:.3f}" data-duration="{max(0.05, e - s):.3f}" '
            f'data-track-index="{track}"><div class="layer">{inner}</div></div>')


def build(v):
    hi = v == "v2"
    els, js = [], []
    dur = C.duration()
    # subtitles: each chunk until the next one in the same take (or its take's end)
    rows = []
    for i, (tk, s, hin, eng) in enumerate(CHUNKS):
        text = eng if hi else hin
        if text is None:
            continue
        nxt = None
        for j in range(i + 1, len(CHUNKS)):
            if CHUNKS[j][0] != tk:
                break
            if (CHUNKS[j][3] if hi else CHUNKS[j][2]) is not None:
                nxt = CHUNKS[j][1]
                break
        a = T(tk, s, -0.05)
        b = T(tk, nxt, -0.06) if nxt is not None else C.take_end(tk) - 0.02
        rows.append((a, b, text))
    for n, (a, b, text) in enumerate(rows):
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        els.append(clip(f"s{n}", a, b, 1, f'<div class="sub" id="t{n}">{html}</div>'))
        js.append(f'tl.fromTo("#t{n}", {{scale: 0.82, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.14, ease: "back.out(2.5)"}}, {a:.3f});')
        js.append(f'tl.fromTo("#t{n} em", {{scale: 0.6}}, {{scale: 1, duration: 0.25, ease: "back.out(3)"}}, {a + 0.05:.3f});')
    # big statements
    for k, ((t1, s1), end, hin, eng) in enumerate(BIG):
        a = T(t1, s1, 0.0 if k == 0 else -0.05)
        b = (T(end[0], end[1]) if end else dur + 0.1)
        text = eng if hi else hin
        words = text.split()
        spans, inbox = [], False
        for w in words:
            if w.startswith("["):
                inbox = True
            cls = ' class="bx"' if inbox else ""
            spans.append(f'<span{cls}>{w.replace("[", "").replace("]", "")}</span>')
            if w.endswith("]") or "]" in w:
                inbox = False
        els.append(clip(f"b{k}", a, b, 2, f'<div class="big" id="g{k}">{" ".join(spans)}</div>'))
        if k == 0:  # the hook is readable on frame 1
            js.append('tl.fromTo("#g0 .bx", {backgroundColor: "rgba(255,225,53,1)"}, {backgroundColor: "rgba(255,225,53,1)", duration: 0.01}, 0);')  # static, readable on frame 1
        else:
            js.append(f'tl.fromTo("#g{k} span", {{opacity: 0, scale: 1.7}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "power3.in", stagger: 0.07}}, {a:.3f});')
        js.append(f'tl.fromTo("#g{k} .bx", {{rotation: 0}}, {{rotation: -3, duration: 0.2, ease: "back.out(3)"}}, {a + 0.07 * len(words):.3f});')
        if end:
            js.append(f'tl.to("#g{k}", {{opacity: 0, y: -16, duration: 0.2}}, {b - 0.2:.3f});')
    # follow at the end
    fa = C.duration() - C.TAIL - 0.3
    els.append(clip("fol", fa, dur + 0.1, 3, f'<div class="fol" id="fl">👉 {"Follow करो, रोज़ English सीखो" if hi else "Follow karo, roz English seekho"}</div>'))
    js.append(f'tl.fromTo("#fl", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.4)"}}, {fa:.3f});')

    out = HERE / "overlay" / v
    (out / "vendor").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    shutil.copy(C.ROOT / "node_modules/gsap/dist/gsap.min.js", out / "vendor/gsap.min.js")
    for f in list((HERE / "board_opts" / "fonts").glob("*.woff2")) + list((HERE.parent / "nikita7" / "board" / "fonts").glob("mukta-800-*.woff2")):
        shutil.copy(f, out / "fonts" / f.name)
    (out / "hyperframes.json").write_text('{"name":"nikita12-overlay-%s"}\n' % v)
    page = TEMPLATE.replace("%HCSS%", HINDI_CSS if hi else "").replace("%DUR%", f"{dur:.3f}").replace("%ELS%", "\n".join(els)).replace("%JS%", "\n".join(js))
    (out / "index.html").write_text(page)
    print(out / "index.html", f"{len(els)} clips, {dur:.2f}s")


TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: Anton; src: url(fonts/anton.woff2); }
@font-face { font-family: Pop; src: url(fonts/pop800.woff2); font-weight: 800; }
html, body { margin: 0; background: transparent; }
#root { position: relative; width: 2160px; height: 3840px; overflow: hidden; }
#stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale(2); transform-origin: 0 0; }
.clip { position: absolute; inset: 0; } .layer { position: absolute; inset: 0; }
.layer > div { position: absolute; }
.sub { left: 90px; top: 1190px; width: 900px; text-align: center; font: 800 70px/1.12 Pop; color: #fff; text-transform: uppercase;
  -webkit-text-stroke: 9px #000; paint-order: stroke fill; text-shadow: 0 8px 22px rgba(0,0,0,.5); }
.sub em { font-style: normal; color: #FFE135; display: inline-block; font-size: 1.12em; }
.big { left: 70px; top: 285px; width: 800px; font: 400 104px/1.02 Anton; color: #fff; text-transform: uppercase; text-shadow: 0 8px 24px rgba(0,0,0,.45); }
.big span { display: inline-block; }
.big .bx { padding: 0 14px; background: #FFE135; color: #111; text-shadow: none; }
.fol { left: 0; right: 0; margin: 0 auto; width: fit-content; top: 1400px; padding: 16px 32px; border-radius: 40px; background: #FFE135; color: #111;
  font: 800 42px/1 Pop; box-shadow: 0 10px 26px rgba(0,0,0,.35); }
%HCSS%
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

HINDI_CSS = """
@font-face { font-family: Mukta; src: url(fonts/mukta-800-devanagari.woff2); font-weight: 800; unicode-range: U+0900-097F, U+200C-200D, U+25CC; }
@font-face { font-family: Mukta; src: url(fonts/mukta-800-latin.woff2); font-weight: 800; }
.sub { font: 800 72px/1.25 Mukta, Pop; }
.big { font: 800 98px/1.12 Mukta, Anton; }
.big .bx { padding: 0 14px 4px; }
.fol { font: 800 42px/1.1 Mukta, Pop; }
"""

if __name__ == "__main__":
    build(sys.argv[1])
