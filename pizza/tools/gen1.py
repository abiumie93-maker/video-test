"""VERSI 1 (house style) - "Pizza buatan Pia", video kenangan keluarga (bukan promosi). Reuses promo/tools/gen1.py look + helpers.
Run: python3 tools/gen1.py  -> v1/index.html + v1/edit-plan.json"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Edit, write_project, ROOT, WORDS

E = Edit()
FT = "assets/footage/"
A_, C_ = "101515", "102643"
hook = E.say("hook", 18.59, 26.42, clip=A_)   # "Kalau sedap boleh jual tak? Tak boleh. Tak boleh kenapa? Sebab ini Pia buat."
s1 = E.say("s1", 0.00, 12.61, clip=A_)        # "Pia buat apa ni? Buat pizza... Siapa ajar? Ibu... Untuk ayah?"
s2 = E.say("s2", 15.71, 18.53, clip=A_)       # "Ya, Pia buat sedap tau."
s3 = E.say("s3", 29.25, 36.20, clip=A_)       # "...dah sedap saja. Belum rasa lagi dah sedap ni. Ayah tunggu ok? Ayah jadi bos hari ni ok?"
s4 = E.say("s4", 38.60, 43.65, clip=A_)       # "Aduh, sedapnya. Wah. Marvelous!"
T_MON = E.hold(5.4)
s5 = E.say("s5", 1.47, 8.83, clip=C_)         # "Belum siap ni. Ini nak buat apa pula lepas ni? Masuk dalam air fryer ni... Oven ni? Wah, okey."
rev = E.say("rev", 12.61, 15.30, clip=A_)     # "MashaAllah, sedapnya pizza."
T_CTA = E.hold(5.6)
TOTAL = round(E.t, 3)
o = E.o
def w(seg, text, near): return E.w(text, near, seg["name"])

# ---------------- picture
PIZ = "assets/img/pizza_siap.jpg"
E.shot(0, o(22.6, "hook"), PIZ, kind="img")
E.synced(hook, a=22.6, b=26.42)
for s in (s1, s2, s3, s4):
    E.synced(s)
MON = [("101558", 0.6, 1.9, "TAMBAH", "PEPPERONI"), ("101558", 15.5, 1.6, "SUSUN", "CANTIK-CANTIK"), (C_, 2.3, 1.9, "KEJU &", "TOMATO")]
t = T_MON; mon = []
for clip, ms, du, l1, l2 in MON:
    E.shot(t, du, FT + clip + ".mp4", ms); mon.append((t, du, l1, l2)); t += du
E.synced(s5)
E.shot(rev["out"], rev["dur"], "assets/img/pizza_siap2.jpg", kind="img")
E.shot(T_CTA, TOTAL - T_CTA, FT + A_ + ".mp4", 37.6)          # Pia tasting the sauce, smiling (music only)

# ---------------- camera
for i, c_ in enumerate(E.cuts()):
    E.zoom.append((c_, "set", *[(1.0, 0), (1.08, 12), (1.04, -10), (1.1, 0)][i % 4]))
PUNCH = [w(hook, "jual", 21.1), w(hook, "boleh", 23.2), w(hook, "Pia", 26.1), w(s1, "pizza", 2.7), w(s1, "Ibu", 5.0),
         w(s1, "Ayah", 10.4), w(s2, "sedap", 17.4), w(s3, "bos", 35.4), w(s4, "Marvelous", 43.2), w(s5, "fryer", 5.7),
         w(rev, "sedapnya", 13.6)]
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
    if tt - prev < .7 or nxt - tt < .8 or tt - last < 2.2 or any(abs(tt - p) < 1.0 for p in PUNCH):
        continue
    E.zoom.append((tt, "ease", *LV[k % len(LV)])); k += 1; last = tt
for p in PUNCH:
    E.zoom.append((round(p - .05, 3), "punch", 1.28, 0))
for p in PUNCH[::2]:
    E.fx("whoosh-short", p)
E.zoom.append((0.02, "slow", 1.15, 0))
for st_, du, *_ in mon:
    E.zoom.append((st_ + .02, "slow", 1.14, 0))
E.zoom.append((rev["out"] + .02, "slow", 1.16, 0)); E.zoom.append((T_CTA + .02, "slow", 1.12, 0))

# ---------------- shared Versi 1 look + helpers (single source: promo/tools/gen1.py)
src = open(os.path.join(ROOT, "..", "promo", "tools", "gen1.py")).read()
exec(src[src.index("# ---------------- graphics helpers"):src.index("# ---------------- HOOK")])

# ---------------- HOOK: "Kalau sedap, boleh jual tak?" -> TAK BOLEH! -> "Sebab PIA yang buat"
E.html.append('''      <div id="hk-scrim" class="scrim"></div>
      <div id="hk-box" class="ov" style="left:60px; right:60px; top:1250px; text-align:center; opacity:1">
        <div id="hk-l1" class="big" style="font-size:70px"><span class="wd">Kalau</span> <span class="wd">sedap,</span></div>
        <div id="hk-l2" class="big y" style="font-size:86px; margin-top:6px"><span class="wd">boleh</span> <span class="wd">jual</span> <span class="wd">tak?</span></div>
        <div id="hk-l3" class="big rd" style="font-size:150px; margin-top:8px"><span class="wd">TAK BOLEH!</span></div>
      </div>
      <div id="hk2" class="ov" style="left:60px; right:60px; top:1330px; text-align:center">
        <div class="big" style="font-size:64px"><span class="wd">Sebab</span> <span class="wd">yang</span> <span class="wd">buat</span></div>
        <div class="big y" style="font-size:180px; margin-top:4px"><span class="wd">PIA!</span></div>
        <svg width="200" height="170" viewBox="0 0 200 170" style="position:absolute; right:150px; top:110px"><path id="hk-heart" class="ink r thick" pathLength="1" d="M100 150 C 20 90, 10 40, 50 25 C 80 15, 100 40, 100 55 C 100 40, 120 15, 150 25 C 190 40, 180 90, 100 150 Z"/></svg>
      </div>''')
A('tl.set("#hk-scrim", {opacity:1}, 0);')
A('tl.set("#hk-l1 .wd, #hk-l2 .wd", {opacity:1}, 0);')       # thumbnail frame already carries the question
E.fx("impact-bass-1", 0.05, .45)
t_tb = w(hook, "Tak", 22.8)
pop("#hk-l3 .wd", t_tb, "impact-bass-1"); E.fx("error", t_tb + .05, .4)
A(f'tl.to("#hk-box", {{opacity:0, y:-30, duration:.2}}, {w(hook, "Sebab", 25.3) - .15});')
A(f'tl.set("#hk2", {{opacity:1}}, {w(hook, "Sebab", 25.3) - .05});')
words_in("#hk2 .wd", w(hook, "Sebab", 25.3), .1)
draw("#hk-heart", w(hook, "Pia", 26.1) + .1, .5); E.fx("pop", w(hook, "Pia", 26.1) + .15)
A(f'tl.to("#hk2, #hk-scrim", {{opacity:0, duration:.25}}, {s1["out"] - .2});')
E.fx("whoosh", s1["out"], .45)

# ---------------- s1: chef cilik PIA / Ibu ajar / Untuk ayah
E.html.append('''      <div id="c1" class="card" style="top:960px">
        <div class="eyebrow">Chef cilik hari ni</div>
        <div class="big" style="font-size:120px; margin-top:4px"><span class="y">PIA</span></div>
        <span class="chip" id="c1-ch" style="position:absolute; right:40px; top:70px; font-size:42px">Menu: PIZZA</span>
      </div>''')
card_in("#c1", s1["out"] + .15); lift(s1["out"], w(s1, "Siapa", 4.1) - .1)
pop("#c1-ch", w(s1, "pizza", 2.7))
card_out("#c1", w(s1, "Siapa", 4.1) - .3)
svg = "".join([
    '<circle cx="140" cy="110" r="40" class="ink" pathLength="1" />',
    P("M92 120 C 90 60, 190 60, 188 120 L 200 200 L 80 200 Z", "b", 'id="ib-hij"'),
    P("M140 200 L140 300 M140 230 L95 270 M140 230 L190 260 M140 300 L105 370 M140 300 L175 370", "", 'id="ib-body"'),
    '<circle cx="300" cy="230" r="28" class="ink p" pathLength="1" />',
    P("M300 258 L300 320 M300 278 L270 300 M300 278 L332 296 M300 320 L280 370 M300 320 L320 370", "p", 'id="pi-body"'),
    P("M400 260 C 470 200, 560 200, 640 260 C 600 330, 470 330, 400 260 Z M520 230 v40 M470 245 l14 30 M570 245 l-14 30", "r", 'id="pz"'),
])
E.html.append(f'''      <div id="p1" class="paper" style="top:880px; height:420px">
        <svg width="840" height="420" viewBox="0 0 840 420" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("p1-t1", "Ibu ajar!", 420, 60, 84, "mk b")}
        {hand("p1-t2", "Pia", 262, 375, 40, "r")}
        {hand("p1-t3", "Ibu pun buat!", 450, 340, 54, "g")}
      </div>''')
paper_in("#p1", w(s1, "Siapa", 4.1) - .1); lift(w(s1, "Siapa", 4.1) - .15, w(s1, "Untuk", 10.0) - .1)
draw("#p1 circle:nth-of-type(1)", w(s1, "Siapa", 4.1) + .2, .3); draw("#ib-hij", w(s1, "Siapa", 4.1) + .35, .35)
draw("#ib-body", w(s1, "Siapa", 4.1) + .55, .4)
draw("#p1 circle:nth-of-type(2)", w(s1, "Siapa", 4.1) + .7, .25); draw("#pi-body", w(s1, "Siapa", 4.1) + .85, .35)
write("#p1-t2", w(s1, "Siapa", 4.1) + 1.0, 3)
write("#p1-t1", w(s1, "Ibu", 5.0), 9); E.fx("pop", w(s1, "Ibu", 5.0) + .1)
draw("#pz", w(s1, "Buat", 7.7), .5); write("#p1-t3", w(s1, "pizza", 8.1) + .1, 13); E.fx("pop", w(s1, "pizza", 8.1) + .2, .4)
paper_out("#p1", w(s1, "Untuk", 10.0) - .3)
svg = P("M260 330 C 140 250, 120 160, 180 130 C 230 110, 260 150, 260 170 C 260 150, 290 110, 340 130 C 400 160, 380 250, 260 330 Z", "r thick", 'id="ay-heart"')
E.html.append(f'''      <div id="p2" class="paper" style="top:900px; height:380px">
        <svg width="840" height="380" viewBox="0 0 840 380" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("p2-t1", "Untuk", 430, 90, 70)}
        {hand("p2-t2", "AYAH!", 430, 170, 120, "mk r")}
      </div>''')
paper_in("#p2", w(s1, "Untuk", 10.0) - .15); lift(w(s1, "Untuk", 10.0) - .2, s2["out"] - .05)
write("#p2-t1", w(s1, "Untuk", 10.0), 6); write("#p2-t2", w(s1, "Ayah", 10.4), 6)
draw("#ay-heart", w(s1, "Ayah", 10.4) + .1, .6); E.fx("pop", w(s1, "Ayah", 10.4) + .2)
paper_out("#p2", s2["out"] - .3)

# ---------------- s2: "Pia buat SEDAP tau!"
E.html.append('''      <div id="c2" class="card" style="top:1000px; text-align:center">
        <div class="big" style="font-size:96px"><span class="wd">Pia</span> <span class="wd">buat</span> <span class="wd y">SEDAP</span> <span class="wd">tau!</span></div>
      </div>''')
card_in("#c2", s2["out"] + .05); lift(s2["out"], s3["out"])
words_in("#c2 .wd", w(s2, "Pia", 16.4) - .1, .12)
E.fx("pop", w(s2, "sedap", 17.4) + .05, .5)
card_out("#c2", s3["out"] - .2)

# ---------------- s3: "Belum rasa, dah SEDAP!" -> stamp AYAH JADI BOS
E.html.append(f'''      <div id="p3" class="paper" style="top:900px; height:330px">
        {hand("p3-t1", "Belum rasa lagi&hellip;", 60, 70, 74)}
        {hand("p3-t2", "dah SEDAP!", 160, 170, 112, "mk g")}
      </div>
      <div id="st-bos" class="stamp" style="left:140px; top:1000px; font-size:66px; transform:rotate(-6deg); text-align:center; line-height:1.05">AYAH JADI<br>BOS HARI NI!</div>''')
paper_in("#p3", s3["out"] + .05); lift(s3["out"], s4["out"])
write("#p3-t1", w(s3, "Belum", 31.3) - .2, 16); write("#p3-t2", w(s3, "sedap", 32.5) - .1, 10); E.fx("pop", w(s3, "sedap", 32.5), .45)
paper_out("#p3", w(s3, "Ayah", 33.3) + 1.2)
t_bos = w(s3, "bos", 35.4)
A(f'tl.fromTo("#st-bos", {{opacity:0, scale:1.9, rotation:-14}}, {{opacity:1, scale:1, rotation:-6, duration:.32, ease:"back.out(2)"}}, {t_bos - .25});')
E.fx("impact-bass-1", t_bos - .22, .45)
hide("#st-bos", s4["out"] - .15)

# ---------------- s4: tasting the sauce -> MARVELOUS!
E.html.append('''      <div id="c4" class="card" style="top:1000px; text-align:center">
        <div class="eyebrow">Pia rasa sos dulu&hellip;</div>
        <div class="big" style="font-size:92px; margin-top:6px"><span class="wd">Aduh,</span> <span class="wd y">sedapnya!</span></div>
      </div>
      <div id="st-mv" class="stamp" style="left:300px; top:880px; font-size:84px; transform:rotate(-8deg)">MARVELOUS!</div>''')
card_in("#c4", s4["out"] + .05); lift(s4["out"], T_MON)
words_in("#c4 .wd", w(s4, "Aduh", 38.8) - .1, .2)
t_mv = w(s4, "Marvelous", 43.2)
A(f'tl.fromTo("#st-mv", {{opacity:0, scale:2, rotation:-16}}, {{opacity:1, scale:1, rotation:-8, duration:.3, ease:"back.out(2)"}}, {t_mv - .05});')
E.fx("impact-bass-1", t_mv - .03, .5)
card_out("#c4", T_MON - .2); hide("#st-mv", T_MON + .6)

# ---------------- montage labels
for i, (st_, du, l1, l2) in enumerate(mon):
    E.fx("whoosh-short", st_, .4)
    lid = f"lb{i}"
    E.html.append(f'      <div id="{lid}" class="lbl big" style="top:1420px">{l1}<br><span class=y>{l2}</span></div>')
    A(f'tl.fromTo("#{lid}", {{opacity:0, scale:1.5, filter:"blur(10px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.28, ease:"expo.out"}}, {r3(st_ + (.85 if i == 0 else .1))});')
    A(f'tl.to("#{lid}", {{opacity:0, duration:.2}}, {r3(st_ + du - .2)});')

# ---------------- s5: into the AIR FRYER OVEN
E.html.append('''      <div id="c5" class="card" style="top:980px">
        <div class="eyebrow" id="c5-e">Lepas tu masuk dalam&hellip;</div>
        <div class="big" style="font-size:96px; margin-top:6px; opacity:0" id="c5-b">AIR <span class="y">FRYER!</span></div>
        <div><span class="chip" id="c5-1">Tunggu masak&hellip;</span></div>
      </div>''')
card_in("#c5", w(s5, "Masuk", 4.3) - .2); lift(w(s5, "Masuk", 4.3) - .25, rev["out"])
A(f'tl.fromTo("#c5-b", {{opacity:0, scale:1.3}}, {{opacity:1, scale:1, duration:.3, ease:"expo.out"}}, {w(s5, "Air", 5.4) - .05});')
E.fx("impact-bass-1", w(s5, "fryer", 5.7), .4)
pop("#c5-1", w(s5, "okey", 8.4) - .2)
card_out("#c5", rev["out"] - .2)

# ---------------- reveal SIAP! + "MashaAllah sedapnya pizza"
E.fx("riser", rev["out"] + .1)
E.html.append('''      <div id="rv" class="lbl big" style="top:1300px; font-size:200px"><span class="y">SIAP!</span></div>
      <svg id="rv-sp" width="1080" height="400" viewBox="0 0 1080 400" style="position:absolute;left:0;top:1230px">
        <path class="ink y thick" pathLength="1" d="M160 90 v60 M130 120 h60 M920 70 v70 M885 105 h70 M820 330 v40 M800 350 h40 M250 320 v40 M230 340 h40"/></svg>
      <div id="rv2" class="ov" style="left:60px; right:60px; top:1560px; text-align:center">
        <div class="big" style="font-size:64px"><span class="wd">MashaAllah,</span> <span class="wd y">sedapnya!</span></div></div>''')
A(f'tl.fromTo("#rv", {{opacity:0, scale:2.2}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(1.6)"}}, {rev["out"] + .1});')
draw("#rv-sp path", rev["out"] + .35, .4); E.fx("impact-bass-1", rev["out"] + .12, .5)
A(f'tl.set("#rv2", {{opacity:1}}, {rev["out"]});'); words_in("#rv2 .wd", w(rev, "MashaAllah", 12.6) + .1, .35)
A(f'tl.to("#rv, #rv-sp, #rv2", {{opacity:0, duration:.25}}, {T_CTA - .2});')

# ---------------- ENDING: memory card (family keepsake, no selling)
svg = "".join([
    P("M600 250 C 520 195, 505 140, 545 122 C 575 110, 600 135, 600 150 C 600 135, 625 110, 655 122 C 695 140, 680 195, 600 250 Z", "r thick", 'id="en-heart"'),
    P("M80 300 C 250 284, 450 310, 700 292", "y thick", 'id="en-ul"'),
])
E.html.append(f'''      <div id="en" class="paper" style="top:930px; height:470px">
        <svg width="840" height="470" viewBox="0 0 840 470" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("en-t0", "Kenangan manis", 70, 50, 56, "b")}
        {hand("en-t1", "Pizza buatan", 70, 130, 82)}
        {hand("en-t2", "PIA", 70, 205, 110, "mk r")}
        {hand("en-t3", "24 November 2026", 80, 330, 52)}
        {hand("en-t4", "Ayah sayang Pia", 300, 395, 58, "r")}
      </div>''')
paper_in("#en", T_CTA + .15); lift(T_CTA, TOTAL)
write("#en-t0", T_CTA + .55, 14); write("#en-t1", T_CTA + 1.0, 12); write("#en-t2", T_CTA + 1.5, 3)
E.fx("pop", T_CTA + 1.6, .4)
draw("#en-heart", T_CTA + 1.9, .6); draw("#en-ul", T_CTA + 2.2, .5)
write("#en-t3", T_CTA + 2.6, 16); write("#en-t4", T_CTA + 3.3, 15); E.fx("pop", T_CTA + 3.5, .35)
A(f'tl.to("#root", {{opacity:0, duration:.6}}, {round(TOTAL - .6, 3)});')

E.music = [(0, .15), (T_MON - .3, .15), (T_MON + .2, .6), (s5["out"] - .2, .6), (s5["out"] + .3, .15),
           (rev["out"], .15), (rev["out"] + .3, .35), (T_CTA, .55), (TOTAL - 1.2, .5), (TOTAL, 0)]
write_project(E, os.path.join(ROOT, "v1"), TOTAL)
p = json.load(open(os.path.join(ROOT, "v1/edit-plan.json"))); p["music_file"] = "assets/music/inspiration.mp3"
json.dump(p, open(os.path.join(ROOT, "v1/edit-plan.json"), "w"), indent=1)
