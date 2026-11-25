"""VERSI 1 (house style) - Sihaté Extra Virgin Olive Oil (For Kids + Early Harvest). Reuses promo/tools/gen1.py look.
Run: python3 tools/gen1.py  -> v1/index.html + v1/edit-plan.json
Label facts (read from the packaging in the footage): For Kids = Unfiltered, Cold Press, <=0.6 acidity, 250 ml;
Early Harvest = Award Winner, Cold Press, <0.3 acidity, 250 ml; both USDA Organic."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Edit, write_project, ROOT, WORDS

E = Edit()
FT = "assets/footage/"
M = "main"
hook = E.say("hook", 103.86, 107.11, clip=M)  # "Wow, tengoklah. Budak-budak pun dah pandai bagi review."
s1 = E.say("s1", 11.38, 23.93, clip=M)       # "...olive oil untuk kanak-kanak! Sebelum ni saya ambil Sihaté Early Harvest untuk dewasa... for kids"
s2 = E.say("s2", 23.93, 38.32, clip=M)       # acidity: 0.6% masih bagus, 0.3% sangat-sangat bagus
s3 = E.say("s3", 43.44, 48.60, clip=M)       # "ini botol untuk dewasa, yang ini botol untuk kanak-kanak"
T_MON = E.hold(7.0)
s4 = E.say("s4", 56.63, 68.00, clip=M)       # bau sama; 0.6% kurang pedas, sesuai budak-budak; kena cuba
s5 = E.say("s5", 76.32, 85.84, clip=M)       # ayah rasa: memang kurang pedas... sangat-sangat light... rasa sedap
s6 = E.say("s6", 86.19, 92.47, clip=M)       # Pia rasa: "Kita cuba ya. Bismillah... Kan, sedap kan?"
s7 = E.say("s7", 107.11, 118.12, clip=M)     # Pia suka mana? budak-budak -> For Kids, dewasa -> dewasa
ct = E.say("cta", 118.12, 124.80, clip=M)    # "korang boleh dapatkan dua-dua jenis ni dekat... Mana Pia? KUNING!"
T_END = E.hold(2.6)
TOTAL = round(E.t, 3)
o = E.o
def w(seg, text, near): return E.w(text, near, seg["name"])

# ---------------- picture
for s in (hook, s1, s2, s3, s4, s5, s6, s7, ct):
    E.synced(s)
MON = [("1012_073631.mp4", 0.8, 1.4, "EARLY HARVEST", "UNTUK DEWASA"), ("1021_224438.mp4", 0.8, 1.4, "FOR KIDS", "UNTUK BUDAK-BUDAK"),
       ("1012_073717.mp4", 1.2, 1.4, "USDA", "ORGANIC"), ("1012_073637.mp4", 1.4, 1.4, "2x", "LAB TEST"),
       ("1021_224913.mp4", 1.2, 1.4, "COLD", "PRESS")]
t = T_MON; mon = []
for f, ms, du, l1, l2 in MON:
    E.shot(t, du, FT + f, ms); mon.append((t, du, l1, l2)); t += du
E.shot(T_END, TOTAL - T_END, FT + "main.mp4", 122.2)           # heart hands, held under the CTA card

# ---------------- camera
for i, c_ in enumerate(E.cuts()):
    E.zoom.append((c_, "set", *[(1.0, 0), (1.08, 12), (1.04, -10), (1.1, 0)][i % 4]))
PUNCH = [w(hook, "review", 106.8), o(12.4, "s1"), w(s1, "Sihaté", 16.6), w(s1, "kids", 23.4), w(s2, "0.6", 30.1),
         w(s2, "0.3", 34.8), w(s2, "sangat-sangat", 37.0), w(s3, "kanak-kanak", 47.2), w(s4, "kurang", 63.1),
         w(s5, "light", 82.9), w(s5, "sedap", 85.4), w(s6, "sedap", 91.7), w(s7, "kids", 114.8), o(121.85, "cta")]
LV = [(1.14, 0), (1.0, 0), (1.2, -20), (1.06, 16), (1.16, 18), (1.0, 0), (1.22, -14), (1.08, 0)]
cands = []
for n in range(1, len(WORDS)):
    if WORDS[n - 1]["text"].strip()[-1:] in ".?!,":
        for s in E.vo:
            if s["src_in"] <= WORDS[n]["start"] <= s["src_out"]:
                cands.append(round(s["out"] + WORDS[n]["start"] - s["src_in"], 3))
cuts = E.cuts(); last, k = -9, 0
for tt in sorted(set(cands)):
    prev = max([c for c in cuts if c <= tt] or [0]); nxt = min([c for c in cuts if c > tt] or [TOTAL])
    if tt - prev < .7 or nxt - tt < .8 or tt - last < 2.2 or any(abs(tt - p) < 1.0 for p in PUNCH):
        continue
    E.zoom.append((tt, "ease", *LV[k % len(LV)])); k += 1; last = tt
for p in PUNCH:
    E.zoom.append((round(p - .05, 3), "punch", 1.28, 0))
for p in PUNCH[::2]:
    E.fx("whoosh-short", p)
for st_, du, *_ in mon:
    E.zoom.append((st_ + .02, "slow", 1.14, 0))
E.zoom.append((T_END + .02, "slow", 1.1, 0))

# ---------------- shared Versi 1 look + helpers (single source: promo/tools/gen1.py)
src = open(os.path.join(ROOT, "..", "promo", "tools", "gen1.py")).read()
exec(src[src.index("# ---------------- graphics helpers"):src.index("# ---------------- HOOK")])

# ---------------- HOOK: "OLIVE OIL untuk BUDAK-BUDAK?!" -> PIA BAGI REVIEW!
E.html.append('''      <div id="hk-scrim" class="scrim"></div>
      <div id="hk-box" class="ov" style="left:60px; right:60px; top:1260px; text-align:center; opacity:1">
        <div id="hk-l1" class="big" style="font-size:96px"><span class="wd">OLIVE OIL</span></div>
        <div id="hk-l2" class="big y" style="font-size:84px; margin-top:6px"><span class="wd">untuk budak-budak?!</span></div>
        <svg width="760" height="46" viewBox="0 0 760 46" style="display:block;margin:-2px auto 0"><path id="hk-ul" class="ink y thick" pathLength="1" d="M40 28 C 220 8, 440 40, 720 16"/></svg>
      </div>
      <div id="st-rv" class="stamp" style="left:300px; top:1060px; font-size:66px; transform:rotate(-7deg)">PIA BAGI REVIEW!</div>''')
A('tl.set("#hk-scrim", {opacity:1}, 0);')
A('tl.set("#hk-l1 .wd, #hk-l2 .wd", {opacity:1}, 0);')
E.fx("impact-bass-1", 0.05, .45); draw("#hk-ul", .25, .45)
t_r = w(hook, "review", 106.8)
A(f'tl.fromTo("#st-rv", {{opacity:0, scale:1.9, rotation:-14}}, {{opacity:1, scale:1, rotation:-7, duration:.3, ease:"back.out(2)"}}, {t_r - .1});')
E.fx("impact-bass-1", t_r - .08, .45)
A(f'tl.to("#hk-box, #st-rv, #hk-scrim", {{opacity:0, duration:.2}}, {s1["out"] - .1});')
E.fx("whoosh", s1["out"], .45)

# ---------------- s1: reveal + SIHATÉ stamps + 2 jenis card
E.html.append('''      <div id="c0" class="ov" style="left:60px; right:60px; top:1330px; text-align:center">
        <div class="big" style="font-size:70px"><span class="wd">Olive oil untuk</span></div>
        <div class="big y" style="font-size:120px"><span class="wd">KANAK-KANAK!</span></div></div>
      <div id="c1" class="card" style="top:930px">
        <div class="eyebrow">Olive oil Sihat&eacute; ada 2 jenis</div>
        <div class="row" id="j0" style="font-size:44px"><div class="box">''' + TICK + '''</div><div>EARLY HARVEST <span style="font-weight:600; opacity:.8">&mdash; dewasa</span></div></div>
        <div class="row" id="j1" style="font-size:44px"><div class="box">''' + TICK + '''</div><div><span class="y">FOR KIDS</span> <span style="font-weight:600; opacity:.8">&mdash; kanak-kanak</span></div></div>
      </div>
      <div id="st-sh" class="stamp" style="left:600px; top:770px; font-size:70px; transform:rotate(-8deg)">SIHAT&Eacute;!</div>''')
A(f'tl.set("#c0", {{opacity:1}}, {s1["out"] + .05});'); words_in("#c0 .wd", s1["out"] + .1, .3)
E.fx("pop", o(12.4, "s1"), .45)
A(f'tl.to("#c0", {{opacity:0, duration:.2}}, {o(14.4, "s1")});')
card_in("#c1", o(14.6, "s1")); lift(o(14.55, "s1"), s2["out"] - .05)
for j, s_ in enumerate((16.6, 19.9, 21.1)):
    t_ = w(s1, "Sihaté", s_); ir = "" if j == 0 else ", immediateRender:false"
    A(f'tl.fromTo("#st-sh", {{opacity:0, scale:1.8, rotation:-14}}, {{opacity:1, scale:1, rotation:-8, duration:.3, ease:"back.out(2)"{ir}}}, {t_});')
    A(f'tl.to("#st-sh", {{opacity:0, duration:.15}}, {round(t_ + .7, 3)});')
    E.fx("impact-bass-1", t_ + .02, .3)
for i, (wd, s_) in enumerate((("dewasa", 18.9), ("kids", 23.4))):
    t_ = w(s1, wd, s_)
    A(f'tl.to("#j{i}", {{opacity:1, duration:.2}}, {t_});'); draw(f"#j{i} path", t_ + .1, .3); E.fx("pop", t_ + .2, .5)
card_out("#c1", s2["out"] - .2)

# ---------------- s2: acidity comparison
E.css.append("""
  .bar { height:26px; border-radius:13px; background:rgba(255,255,255,.12); margin-top:10px; overflow:hidden; }
  .bar i { display:block; height:100%; width:0; border-radius:13px; }
""")
E.html.append('''      <div id="c2" class="card" style="top:900px">
        <div class="eyebrow">Beza dia: kandungan ACIDITY</div>
        <div id="a0" style="opacity:.3; margin-top:18px">
          <div style="display:flex; justify-content:space-between; font-weight:800; font-size:44px"><span>For Kids</span><span class="y">&le; 0.6%</span></div>
          <div class="bar"><i id="a0b" style="background:#FFC928"></i></div>
          <div style="font-weight:700; font-size:32px; opacity:.85; margin-top:6px">masih bagus &#10003;</div></div>
        <div id="a1" style="opacity:.3; margin-top:18px">
          <div style="display:flex; justify-content:space-between; font-weight:800; font-size:44px"><span>Early Harvest</span><span class="gr">&lt; 0.3%</span></div>
          <div class="bar"><i id="a1b" style="background:#3DDC84"></i></div>
          <div style="font-weight:700; font-size:32px; opacity:.85; margin-top:6px">sangat-sangat bagus &#10003;&#10003;</div></div>
      </div>
      <div id="st-sb" class="stamp" style="left:520px; top:820px; font-size:60px; border-color:#3DDC84; color:#3DDC84; transform:rotate(-7deg)">SANGAT BAGUS!</div>''')
card_in("#c2", s2["out"] + .05); lift(s2["out"], s3["out"])
t6 = w(s2, "0.6", 30.1); t3 = w(s2, "0.3", 34.8)
A(f'tl.to("#a0", {{opacity:1, duration:.25}}, {t6 - .1});'); A(f'tl.to("#a0b", {{width:"60%", duration:.6, ease:"power2.out"}}, {t6});')
E.fx("pop", t6 + .1, .5)
A(f'tl.to("#a1", {{opacity:1, duration:.25}}, {t3 - .1});'); A(f'tl.to("#a1b", {{width:"30%", duration:.6, ease:"power2.out"}}, {t3});')
E.fx("pop", t3 + .1, .5)
t_sb = w(s2, "sangat-sangat", 37.0)
A(f'tl.fromTo("#st-sb", {{opacity:0, scale:1.8}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {t_sb});')
E.fx("impact-bass-1", t_sb + .02, .4)
card_out("#c2", s3["out"] - .2); hide("#st-sb", s3["out"] - .2)

# ---------------- s3: two bottles (paper)
svg = "".join([
    P("M150 120 h60 v40 c40 20 50 50 50 90 v170 h-160 v-170 c0 -40 10 -70 50 -90 z M150 105 h60", "", 'id="b-big"'),
    P("M120 300 h120", "y thick", 'id="b-big-l"'),
    P("M520 210 h44 v30 c30 16 38 38 38 64 v116 h-120 v-116 c0 -26 8 -48 38 -64 z M520 198 h44", "g", 'id="b-small"'),
    P("M530 350 a12 12 0 1 0 0.1 0 M560 350 a12 12 0 1 0 0.1 0 M528 380 c10 10 30 10 40 0", "r", 'id="b-face"'),
])
E.html.append(f'''      <div id="p3" class="paper" style="top:860px; height:470px">
        <svg width="840" height="470" viewBox="0 0 840 470" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("p3-t1", "DEWASA", 290, 230, 70, "mk")}
        {hand("p3-t2", "KANAK-KANAK", 470, 90, 66, "mk g")}
        {hand("p3-t3", "comel!", 650, 330, 56, "r")}
      </div>''')
paper_in("#p3", s3["out"] + .05); lift(s3["out"], T_MON + .3)
draw("#b-big", w(s3, "dewasa", 45.2) - .3, .5); draw("#b-big-l", w(s3, "dewasa", 45.2), .3); write("#p3-t1", w(s3, "dewasa", 45.2), 6)
draw("#b-small", w(s3, "kanak-kanak", 47.2) - .3, .45); draw("#b-face", w(s3, "kanak-kanak", 47.2) + .1, .3)
write("#p3-t2", w(s3, "kanak-kanak", 47.2), 11); E.fx("pop", w(s3, "kanak-kanak", 47.2) + .2)
write("#p3-t3", T_MON - .3, 6)
paper_out("#p3", T_MON + .2)

# ---------------- montage labels (all printed on the packaging)
for i, (st_, du, l1, l2) in enumerate(mon):
    E.fx("whoosh-short", st_, .4)
    lid = f"lb{i}"
    E.html.append(f'      <div id="{lid}" class="lbl big" style="top:1440px; font-size:{110 if i else 104}px">{l1}<br><span class=y>{l2}</span></div>')
    A(f'tl.fromTo("#{lid}", {{opacity:0, scale:1.5, filter:"blur(10px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.28, ease:"expo.out"}}, {r3(st_ + (.45 if i == 0 else .08))});')
    A(f'tl.to("#{lid}", {{opacity:0, duration:.18}}, {r3(st_ + du - .18)});')

# ---------------- s4: smell + "kurang pedas, sesuai budak-budak" (paper)
svg = "".join([
    P("M120 150 C 100 120, 140 90, 170 110 C 200 130, 190 170, 160 175", "", 'id="nose"'),
    P("M200 120 C 240 110, 260 140, 300 125 M200 150 C 240 140, 260 170, 300 155", "b", 'id="smell"'),
    P("M540 120 C 600 100, 680 140, 700 230 C 710 280, 690 310, 670 300 C 650 230, 600 170, 540 150 Z M540 120 C 520 100, 525 80, 545 70", "r thick", 'id="chili"'),
    P("M760 150 v120 M735 245 l25 30 l25 -30", "g thick", 'id="down"'),
])
E.html.append(f'''      <div id="p4" class="paper" style="top:880px; height:470px">
        <svg width="840" height="470" viewBox="0 0 840 470" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("p4-t1", "Bau lebih kurang SAMA", 60, 210, 54, "b")}
        {hand("p4-t2", "KURANG PEDAS", 330, 318, 58, "mk r")}
        {hand("p4-t3", "&#10003; sesuai untuk budak-budak", 80, 395, 56, "g")}
      </div>''')
paper_in("#p4", s4["out"] + .05); lift(s4["out"], s5["out"])
draw("#nose", w(s4, "bau", 57.2) - .1, .35); draw("#smell", w(s4, "bau", 57.2) + .2, .4); write("#p4-t1", w(s4, "sama", 58.5) - .4, 20)
draw("#chili", w(s4, "kepedasan", 61.4) - .2, .5); draw("#down", w(s4, "kurang", 63.1), .3)
write("#p4-t2", w(s4, "kurang", 63.1), 12); E.fx("pop", w(s4, "kurang", 63.1) + .1)
write("#p4-t3", w(s4, "budak-budak", 64.8) - .2, 26); E.fx("notification", w(s4, "budak-budak", 64.8) + .2, .35)
paper_out("#p4", s5["out"] - .25)

# ---------------- s5: dad tastes -> checklist
ROWS = [("KURANG PEDAS", o(79.3, "s5")), ("SANGAT LIGHT", w(s5, "light", 82.9)), ("RASA SEDAP!", w(s5, "sedap", 85.4) - .3)]
rows = "".join(f'<div class="row" id="r{i}" style="font-size:56px"><div class="box">{TICK}</div><div>{n}</div></div>' for i, (n, _) in enumerate(ROWS))
E.html.append(f'''      <div id="c5" class="card" style="top:930px">
        <div class="eyebrow">Ayah rasa dulu&hellip;</div>
        {rows}
      </div>''')
card_in("#c5", s5["out"] + .1); lift(s5["out"], s6["out"])
for i, (n, t_) in enumerate(ROWS):
    A(f'tl.to("#r{i}", {{opacity:1, duration:.2}}, {t_});'); draw(f"#r{i} path", t_ + .1, .3); E.fx("pop", t_ + .2, .5)
card_out("#c5", s6["out"] - .2)

# ---------------- s6: Pia tastes -> "Kan, SEDAP kan?"
E.html.append('''      <div id="c6" class="card" style="top:1000px; text-align:center">
        <div class="eyebrow">Giliran Pia pula!</div>
        <div class="big" style="font-size:92px; margin-top:6px; opacity:0" id="c6-b">Kan, <span class="y">SEDAP</span> kan?</div>
      </div>''')
card_in("#c6", s6["out"] + .1); lift(s6["out"], s7["out"])
t_sd = o(91.7, "s6")
A(f'tl.fromTo("#c6-b", {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {t_sd - .05});')
E.fx("impact-bass-1", t_sd, .4)
card_out("#c6", s7["out"] - .2)

# ---------------- s7: who should take which
E.html.append('''      <div id="c7" class="card" style="top:930px">
        <div class="eyebrow" id="c7-e">Pia suka yang mana?</div>
        <div class="row" id="k0" style="font-size:44px"><div class="box">''' + TICK + '''</div><div>Budak-budak &rarr; <span class="y">FOR KIDS</span></div></div>
        <div class="row" id="k1" style="font-size:44px"><div class="box">''' + TICK + '''</div><div>Dewasa &rarr; <span class="gr">EARLY HARVEST</span></div></div>
      </div>''')
card_in("#c7", w(s7, "suka", 108.5) - .4); lift(w(s7, "suka", 108.5) - .45, ct["out"])
for i, (wd, s_) in enumerate((("kids", 114.8), ("dewasa", 117.6))):
    t_ = w(s7, wd, s_)
    A(f'tl.to("#k{i}", {{opacity:1, duration:.2}}, {t_ - .2});'); draw(f"#k{i} path", t_, .3); E.fx("pop", t_ + .1, .5)
card_out("#c7", ct["out"] - .2)

# ---------------- CTA: "...dekat... Mana Pia?" -> "KUNING!"
t_k = o(121.85, "cta")
E.html.append('''      <div id="cta" class="card" style="top:880px; text-align:center; padding:40px 40px 46px">
        <div class="eyebrow">Sihat&eacute; Olive Oil &bull; For Kids &amp; Early Harvest</div>
        <div class="big" style="font-size:72px; margin-top:10px">Dapatkan<br><span class="y">DUA-DUA</span> jenis</div>
        <div id="cta-btn" style="opacity:0; display:inline-flex; align-items:center; gap:22px; margin-top:28px; padding:26px 46px; border-radius:999px;
             background:#FFC928; color:#0C1226; font-family:'Archivo Black'; font-size:54px; white-space:nowrap; box-shadow:0 10px 0 #C99A00">
          <svg width="74" height="70" viewBox="0 0 74 70"><path d="M6 22 H68 L60 64 H14 Z" fill="#0C1226"/><path d="M22 24 C 22 2, 52 2, 52 24" fill="none" stroke="#0C1226" stroke-width="7"/></svg>
          TEKAN BEG KUNING</div>
        <div id="cta-2" style="opacity:0; font-weight:800; font-size:40px; margin-top:26px">Komen <span class="y">1 hingga 5</span>, korang nak cuba yang mana?</div>
      </div>
      <div id="st-k" class="stamp" style="left:200px; top:700px; font-size:120px; transform:rotate(-6deg)">KUNING!</div>''')
card_in("#cta", w(ct, "dapatkan", 119.0) - .2); lift(w(ct, "dapatkan", 119.0) - .25, TOTAL)
A(f'tl.fromTo("#st-k", {{opacity:0, scale:2.2, rotation:-14}}, {{opacity:1, scale:1, rotation:-6, duration:.3, ease:"back.out(2)"}}, {t_k - .05});')
E.fx("impact-bass-1", t_k - .03, .55)
pop("#cta-btn", t_k + .4)
A(f'tl.to("#cta-btn", {{scale:.93, duration:.09, yoyo:true, repeat:1}}, {t_k + 1.3});'); E.fx("click-soft", t_k + 1.3)
A(f'tl.to("#cta-btn", {{scale:1.06, duration:.35, yoyo:true, repeat:5, ease:"sine.inOut"}}, {t_k + 1.6});')
hide("#st-k", t_k + 1.6)
show("#cta-2", t_k + 2.0); E.fx("notification", t_k + 2.1, .35)
A(f'tl.to("#root", {{opacity:0, duration:.4}}, {round(TOTAL - .4, 3)});')

E.music = [(0, .15), (T_MON - .3, .15), (T_MON + .2, .6), (s4["out"] - .2, .6), (s4["out"] + .3, .15),
           (T_END - .3, .15), (T_END + .1, .5), (TOTAL - .3, 0), (TOTAL, 0)]
write_project(E, os.path.join(ROOT, "v1"), TOTAL)
p = json.load(open(os.path.join(ROOT, "v1/edit-plan.json"))); p["music_file"] = "assets/music/inspiration.mp3"
json.dump(p, open(os.path.join(ROOT, "v1/edit-plan.json"), "w"), indent=1)
