"""VERSI 1 (house style) for the insole promo. Reuses the card/paper helpers of promo/tools/gen1.py.
Run: python3 tools/gen1.py  -> v1/index.html + v1/edit-plan.json"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Edit, write_project, ROOT, WORDS

E = Edit()
FT = "assets/footage/"
# ---------------- voice edit (clip, source seconds snapped to quiet frames)
h1 = E.say("h1", 0.00, 4.02, clip="073913")    # "Tapak kasut yang lama ni, korang boleh campak."
h2 = E.say("h2", 4.50, 6.53, clip="073913")    # "Dapatkan yang baru."
a1 = E.say("a1", 0.05, 4.69, clip="074041")    # "Sedap guys. Bila dah letak tapak kasut yang baru, memang best."
b2 = E.say("b2", 4.80, 12.79, clip="074041")   # "So korang dapatkan... memang lawa, memang cantik dan memang berkualiti."
b3 = E.say("b3", 12.94, 14.82, clip="074041")  # "Di sini keras, di sini lembut."
T_MON = E.hold(5.6)
b4 = E.say("b4", 6.53, 10.50, clip="073913")   # "Yang ini memang puas hati. InsyaAllah korang memang sangat suka."
ct = E.say("cta", 15.03, 17.45, clip="074041") # "Dapatkan terus dekat beg kuning."
E.hold(2.4)
TOTAL = round(E.t, 3)
o = E.o
def w(seg, text, near): return E.w(text, near, seg["name"])

# ---------------- picture
E.synced(h1, a=0.0, b=3.0)
E.shot(o(3.0, "h1"), 1.02, FT + "073827.mp4", 0.35)     # old insole thrown on "campak"
for s in (h2, a1, b2, b3):
    E.synced(s)
MON = [(0.3, 1.5, None, None), (4.6, 1.4, "SENANG", "PASANG"), (9.6, 1.4, "MUAT", "ELOK"), (12.2, 1.3, "TERUS", "SEDAP")]
t = T_MON; mon = []
for ms, du, l1, l2 in MON:
    E.shot(t, du, FT + "073815.mp4", ms); mon.append((t, du, l1, l2)); t += du
E.synced(b4)
E.shot(ct["out"], TOTAL - ct["out"], FT + "073758.mp4", 0.5)

# ---------------- camera
for i, c_ in enumerate(E.cuts()):
    E.zoom.append((c_, "set", *[(1.0, 0), (1.08, 12), (1.04, -10), (1.1, 0)][i % 4]))
PUNCH = [w(h1, "campak", 3.6) - .1, w(h2, "baru", 6.0), w(a1, "best", 3.8), w(b2, "lawa", 9.5), w(b2, "cantik", 10.6),
         w(b2, "berkualiti", 12.0), w(b3, "keras", 13.5), w(b3, "lembut", 14.5), w(b4, "puas", 7.5), w(ct, "kuning", 17.3)]
LV = [(1.14, 0), (1.0, 0), (1.2, -20), (1.06, 16), (1.16, 18), (1.0, 0), (1.22, -14), (1.08, 0)]
cands = []
for n in range(1, len(WORDS)):
    if WORDS[n - 1]["text"].strip()[-1:] in ".?!," and WORDS[n - 1]["file"] == WORDS[n]["file"]:
        for s in E.vo:
            if s["clip"] == WORDS[n]["file"] and s["src_in"] <= WORDS[n]["start"] <= s["src_out"]:
                cands.append(round(s["out"] + WORDS[n]["start"] - s["src_in"], 3))
cuts = E.cuts(); last, k = -9, 0
for tt in sorted(set(cands)):
    prev = max([c for c in cuts if c <= tt] or [0]); nxt = min([c for c in cuts if c > tt] or [TOTAL])
    if tt - prev < .7 or nxt - tt < .8 or tt - last < 2.0 or any(abs(tt - p) < 1.0 for p in PUNCH):
        continue
    E.zoom.append((tt, "ease", *LV[k % len(LV)])); k += 1; last = tt
for p in PUNCH:
    E.zoom.append((round(p - .05, 3), "punch", 1.28, 0))
for p in PUNCH[::2]:
    E.fx("whoosh-short", p)
for st_, du, *_ in mon:
    E.zoom.append((st_ + .02, "slow", 1.14, 0))
E.zoom.append((ct["out"] + .02, "slow", 1.12, 0))

# ---------------- shared Versi 1 look + helpers (single source: promo/tools/gen1.py)
src = open(os.path.join(ROOT, "..", "promo", "tools", "gen1.py")).read()
exec(src[src.index("# ---------------- graphics helpers"):src.index("# ---------------- HOOK")])

# ---------------- HOOK: "TAPAK KASUT DAH LAMA?" -> CAMPAK! -> "Dapatkan yang BARU!"
E.html.append('''      <div id="hk-scrim" class="scrim"></div>
      <div id="hk-box" class="ov" style="left:60px; right:60px; top:1270px; text-align:center; opacity:1">
        <div id="hk-l1" class="big" style="font-size:78px"><span class="wd">Tapak</span> <span class="wd">kasut</span> <span class="wd y">dah lama?</span></div>
        <div id="hk-l3" class="big rd" style="font-size:190px; margin-top:6px"><span class="wd">CAMPAK!</span></div>
        <svg width="760" height="46" viewBox="0 0 760 46" style="display:block;margin:-8px auto 0"><path id="hk-ul" class="ink r thick" pathLength="1" d="M60 28 C 240 8, 440 40, 700 16"/></svg>
      </div>
      <div id="hk2" class="ov" style="left:60px; right:60px; top:1290px; text-align:center">
        <div class="big" style="font-size:66px"><span class="wd">Dapatkan</span> <span class="wd">yang</span></div>
        <div class="big y" style="font-size:200px; margin-top:4px"><span class="wd">BARU!</span></div>
        <svg width="700" height="46" viewBox="0 0 700 46" style="display:block;margin:-8px auto 0"><path id="hk2-ul" class="ink y thick" pathLength="1" d="M40 28 C 220 8, 420 40, 660 16"/></svg>
      </div>''')
A('tl.set("#hk-scrim", {opacity:1}, 0);')
A('tl.set("#hk-l1 .wd", {opacity:1}, 0);')
E.fx("impact-bass-1", 0.05, .45)
t_c = w(h1, "campak", 3.6) - .12
pop("#hk-l3 .wd", t_c, "impact-bass-1"); draw("#hk-ul", t_c + .2, .35); E.fx("whoosh", t_c - .25, .4)
A(f'tl.to("#hk-box", {{opacity:0, y:-30, duration:.2}}, {h2["out"] - .1});')
E.fx("whoosh", h2["out"], .45)
A(f'tl.set("#hk2", {{opacity:1}}, {h2["out"] + .05});')
words_in("#hk2 .wd", w(h2, "Dapatkan", 4.6) - .1, .12)
E.fx("impact-bass-1", w(h2, "baru", 6.0), .45); draw("#hk2-ul", w(h2, "baru", 6.0) + .1, .35)
A(f'tl.to("#hk2, #hk-scrim", {{opacity:0, duration:.25}}, {a1["out"] - .2});')

# ---------------- a1: "Sedap guys... memang best" (paper: foot in shoe + comfort waves)
svg = "".join([
    P("M70 300 C 70 250, 120 230, 200 232 L 360 240 C 420 244, 450 280, 450 310 L 70 310 Z", "", 'id="sh-shoe"'),
    P("M90 296 C 180 286, 330 286, 440 296", "r thick", 'id="sh-sole"'),
    P("M160 200 C 160 150, 200 120, 230 160 M240 190 C 250 140, 290 120, 310 170", "b", 'id="sh-wave"'),
    P("M520 120 l14 30 l32 4 l-24 22 l8 32 l-30 -16 l-30 16 l8 -32 l-24 -22 l32 -4 z", "y thick", 'id="sh-star"'),
])
E.html.append(f'''      <div id="pa" class="paper" style="top:900px; height:400px">
        <svg width="840" height="400" viewBox="0 0 840 400" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("pa-t1", "Sedap guys!", 470, 230, 78, "mk b")}
        {hand("pa-t2", "Memang BEST!", 210, 330, 60, "g")}
      </div>''')
paper_in("#pa", a1["out"] + .1); lift(a1["out"], o(4.69, "a1"))
draw("#sh-shoe", a1["out"] + .3, .45); draw("#sh-sole", w(a1, "Sedap", .3) + .3, .35)
write("#pa-t1", w(a1, "Sedap", .3) + .1, 10); E.fx("pop", w(a1, "Sedap", .3) + .2, .4)
draw("#sh-wave", w(a1, "letak", 2.4), .5)
write("#pa-t2", w(a1, "best", 3.8) - .1, 12); draw("#sh-star", w(a1, "best", 3.8), .4); E.fx("pop", w(a1, "best", 3.8) + .1)
paper_out("#pa", o(4.62, "a1"))

# ---------------- b2: checklist LAWA / CANTIK / BERKUALITI
ROWS = [("Lawa", 9.5), ("Cantik", 10.6), ("Berkualiti", 12.0)]
rows = "".join(f'<div class="row" id="ck{i}" style="font-size:58px"><div class="box">{TICK}</div><div>{n.upper()}</div></div>' for i, (n, _) in enumerate(ROWS))
E.html.append(f'''      <div id="cb" class="card" style="top:900px">
        <div class="eyebrow">Tapak kasut baru ni memang&hellip;</div>
        {rows}
      </div>
      <div id="stamp-q" class="stamp" style="left:520px; top:830px; font-size:58px; transform:rotate(-8deg)">BERKUALITI!</div>''')
card_in("#cb", w(b2, "dapatkan", 6.0) - .2); lift(w(b2, "dapatkan", 6.0) - .25, o(12.79, "b2"))
for i, (n, s_) in enumerate(ROWS):
    t_ = w(b2, n.lower(), s_)
    A(f'tl.to("#ck{i}", {{opacity:1, duration:.2}}, {t_});'); draw(f"#ck{i} path", t_ + .1, .3); E.fx("pop", t_ + .2, .5)
t_q = w(b2, "berkualiti", 12.0)
A(f'tl.fromTo("#stamp-q", {{opacity:0, scale:1.8, rotation:-14}}, {{opacity:1, scale:1, rotation:-8, duration:.3, ease:"back.out(2)"}}, {t_q + .25});')
E.fx("impact-bass-1", t_q + .27, .35)
card_out("#cb", o(12.74, "b2")); hide("#stamp-q", o(12.7, "b2"))

# ---------------- b3: "Di sini KERAS, di sini LEMBUT" (paper: insole outline + arrows), held into the montage
svg = "".join([
    P("M250 230 C 250 170, 290 140, 350 140 C 430 140, 480 118, 550 108 C 630 98, 690 140, 690 200 C 690 262, 640 292, 560 292 C 490 292, 450 262, 400 282 C 340 304, 250 300, 250 230 Z", "", 'id="ins"'),
    P("M370 288 C 400 270, 440 264, 480 280", "r thick", 'id="ins-arch"'),
    P("M310 222 m-38 0 a38 48 0 1 0 76 0 a38 48 0 1 0 -76 0", "g thick", 'id="ins-pad"'),
    P("M215 375 C 280 360, 340 330, 395 292 M372 300 l26 -10 l-6 28", "r", 'id="ar-k"'),
    P("M215 95 C 255 110, 285 140, 300 168 M278 156 l22 14 l4 -26", "g", 'id="ar-l"'),
])
E.html.append(f'''      <div id="pk" class="paper" style="top:860px; height:460px">
        <svg width="840" height="460" viewBox="0 0 840 460" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("pk-t1", "KERAS", 40, 330, 70, "mk r")}
        {hand("pk-t1b", "sokong kaki", 500, 360, 44, "r")}
        {hand("pk-t2", "LEMBUT", 30, 40, 70, "mk g")}
        {hand("pk-t2b", "empuk", 400, 50, 44, "g")}
      </div>''')
paper_in("#pk", b3["out"] - .05); lift(b3["out"] - .1, T_MON + 1.45)
draw("#ins", b3["out"] + .15, .45)
t_k = w(b3, "keras", 13.5); t_l = w(b3, "lembut", 14.5)
write("#pk-t1", t_k - .05, 5); draw("#ar-k", t_k, .3); draw("#ins-arch", t_k + .15, .3); E.fx("pop", t_k + .1)
write("#pk-t1b", t_k + .3, 10)
write("#pk-t2", t_l - .05, 6); draw("#ar-l", t_l, .3); draw("#ins-pad", t_l + .15, .3); E.fx("pop", t_l + .1)
write("#pk-t2b", t_l + .3, 6)
paper_out("#pk", T_MON + 1.2)

# ---------------- montage labels, riser into "PUAS HATI"
for i, (st_, du, l1, l2) in enumerate(mon):
    E.fx("whoosh-short", st_, .4)
    if not l1:
        continue
    lid = f"lb{i}"
    E.html.append(f'      <div id="{lid}" class="lbl big" style="top:1420px">{l1}<br><span class=y>{l2}</span></div>')
    A(f'tl.fromTo("#{lid}", {{opacity:0, scale:1.5, filter:"blur(10px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.28, ease:"expo.out"}}, {r3(st_ + .1)});')
    A(f'tl.to("#{lid}", {{opacity:0, duration:.2}}, {r3(st_ + du - .2)});')
E.fx("riser", w(b4, "puas", 7.5) - .1)

# ---------------- b4: PUAS HATI + 5 stars, "korang SUKA"
stars = "".join(P(f"M{60 + i*130} 40 l16 34 l36 5 l-26 25 l7 36 l-33 -18 l-33 18 l7 -36 l-26 -25 l36 -5 z", "y thick", f'id="st{i}"') for i in range(5))
E.html.append(f'''      <div id="ph" class="card" style="top:960px; text-align:center">
        <div class="big" style="font-size:112px"><span class="wd y">PUAS</span> <span class="wd">HATI!</span></div>
        <svg width="740" height="130" viewBox="0 0 740 130" style="display:block; margin:6px auto 0">{stars}</svg>
        <div id="ph-2" style="opacity:0; font-weight:800; font-size:46px; margin-top:4px">InsyaAllah korang <span class="y">sangat suka</span></div>
      </div>''')
card_in("#ph", b4["out"] + .1); lift(b4["out"], ct["out"])
pop("#ph .wd", w(b4, "puas", 7.5) - .05, "impact-bass-1")
for i in range(5):
    draw(f"#st{i}", w(b4, "hati", 7.8) + .1 + i * .12, .25)
E.fx("pop", w(b4, "hati", 7.8) + .2, .4); E.fx("pop", w(b4, "hati", 7.8) + .6, .35)
show("#ph-2", w(b4, "sangat", 9.6) - .2); E.fx("notification", w(b4, "suka", 10.1), .35)
card_out("#ph", ct["out"] - .2)

# ---------------- CTA
E.html.append('''      <div id="cta" class="card" style="top:900px; text-align:center; padding:40px 40px 46px">
        <div class="eyebrow">Tapak kasut baru, kaki terus sedap</div>
        <div class="big" style="font-size:72px; margin-top:10px">Dapatkan<br>terus dekat</div>
        <div id="cta-btn" style="opacity:0; display:inline-flex; align-items:center; gap:22px; margin-top:28px; padding:26px 46px; border-radius:999px;
             background:#FFC928; color:#0C1226; font-family:'Archivo Black'; font-size:56px; white-space:nowrap; box-shadow:0 10px 0 #C99A00">
          <svg width="74" height="70" viewBox="0 0 74 70"><path d="M6 22 H68 L60 64 H14 Z" fill="#0C1226"/><path d="M22 24 C 22 2, 52 2, 52 24" fill="none" stroke="#0C1226" stroke-width="7"/></svg>
          BEG KUNING</div>
        <div id="cta-2" style="opacity:0; font-weight:800; font-size:40px; margin-top:26px">Tekan sekarang &darr;</div>
      </div>''')
card_in("#cta", ct["out"] + .05); lift(ct["out"], TOTAL)
t_b = w(ct, "beg", 17.0)
pop("#cta-btn", t_b - .05)
A(f'tl.to("#cta-btn", {{scale:.93, duration:.09, yoyo:true, repeat:1}}, {t_b + .9});'); E.fx("click-soft", t_b + .9)
A(f'tl.to("#cta-btn", {{scale:1.06, duration:.35, yoyo:true, repeat:3, ease:"sine.inOut"}}, {t_b + 1.2});')
show("#cta-2", t_b + .6); E.fx("notification", t_b + 1.3, .3)
A(f'tl.to("#root", {{opacity:0, duration:.4}}, {round(TOTAL - .4, 3)});')

E.music = [(0, .15), (T_MON - .3, .15), (T_MON + .2, .6), (b4["out"] - .2, .6), (b4["out"] + .3, .15), (TOTAL - 2.2, .15), (TOTAL - 2.0, .5), (TOTAL - .2, 0), (TOTAL, 0)]
write_project(E, os.path.join(ROOT, "v1"), TOTAL)
p = json.load(open(os.path.join(ROOT, "v1/edit-plan.json"))); p["music_file"] = "assets/music/inspiration.mp3"
json.dump(p, open(os.path.join(ROOT, "v1/edit-plan.json"), "w"), indent=1)
