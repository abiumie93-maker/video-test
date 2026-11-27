"""Pesanan jalan raya - storytelling edit. Angry red hook, hand-drawn paper story cards (Versi 1 helpers from
promo/tools/gen1.py), serif subtitles + gold titles (tiktokshop/tools/gen_ref.py look), calm CC0 music.
Run: python3 tools/gen.py -> v1/index.html"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Edit, write_project, ROOT, WORDS, H

E = Edit()
M = "main"
SEGS = [("hook", 0.05, 8.00), ("a", 8.21, 17.78), ("b", 22.47, 44.50), ("c", 44.59, 53.60), ("d", 54.01, 59.50),
        ("e", 86.58, 133.60), ("g", 134.12, 136.35), ("h", 146.74, 201.02), ("j", 204.64, 238.74)]
for n_, a_, b_ in SEGS:
    E.say(n_, a_, b_, clip=M)
T_END = E.hold(5.0)
TOTAL = round(E.t, 3)
for s in E.vo:
    E.synced(s)
E.shot(T_END, TOTAL - T_END, "assets/footage/main.mp4", 238.9, style="filter:blur(26px) brightness(.55)")
o = E.o
def seg_of(src): return next(n_ for n_, a_, b_ in SEGS if a_ - .3 <= src <= b_ + .3)
def w(text, near): return E.w(text, near, seg_of(near))
S = {s["name"]: s for s in E.vo}

# ---------------- shared helpers: Versi 1 (paper/dark cards) + reference look (subs, gold titles, stamps)
src1 = open(os.path.join(ROOT, "..", "promo", "tools", "gen1.py")).read()
exec(src1[src1.index("# ---------------- graphics helpers"):src1.index("# ---------------- HOOK")])
src2 = open(os.path.join(ROOT, "..", "tiktokshop", "tools", "gen_ref.py")).read()
exec(src2[src2.index("# ---------------- look"):src2.index("# ---------------- HOOK")])
E.css.append("""
  #cam video { filter: brightness(1.06) saturate(1.15) contrast(1.05); }
  #vig { background:radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 60%, rgba(25,12,0,.2) 100%); }
  .sub { top:1650px; }
  .paper, .card { margin-top:200px; }
  .sub.red { color:#fff; } .sub.red i { color:#FF4D4D; }
  #redwash { position:absolute; inset:0; z-index:3; pointer-events:none; opacity:0;
             background:radial-gradient(ellipse at 50% 40%, rgba(255,40,40,.18), rgba(150,0,0,.55)); mix-blend-mode:multiply; }
  #redflash { position:absolute; inset:0; z-index:3; pointer-events:none; opacity:0; background:rgba(255,30,30,.35); }
  .redt { position:absolute; left:0; right:0; text-align:center; font-family:'Archivo Black'; text-transform:uppercase; color:#FF3B3B; z-index:6; opacity:0;
          line-height:.98; text-shadow:0 0 30px rgba(255,0,0,.55), 0 6px 0 #5a0000, 0 10px 30px rgba(0,0,0,.6); }
  .tagr { position:absolute; left:60px; top:110px; z-index:9; padding:12px 26px; border-radius:999px; font-family:'Anton'; font-size:44px; letter-spacing:.04em;
          color:#fff; background:#D62828; box-shadow:0 8px 24px rgba(0,0,0,.3); opacity:0; }
  .paper .hand.mk { font-family:'Permanent Marker'; }
  .emo { font-size:64px; position:absolute; opacity:0; }
""")
HTML = E.html
def gold_t(id_, html, t0, t1, top=170, size=170):
    HTML.append(f'      <div id="{id_}" class="goldt" style="top:{top}px; font-size:{size}px">{html}</div>'); gold(f"#{id_}", t0, t1)
def red_t(id_, html, t0, t1, top=170, size=170, shake=True):
    HTML.append(f'      <div id="{id_}" class="redt" style="top:{top}px; font-size:{size}px">{html}</div>')
    A(f'tl.fromTo("#{id_}", {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, duration:.25, ease:"expo.out"}}, {r3(t0)});')
    if shake: A(f'tl.fromTo("#{id_}", {{x:-12}}, {{x:12, duration:.05, yoyo:true, repeat:7}}, {r3(t0 + .25)});')
    A(f'tl.to("#{id_}", {{opacity:0, duration:.2}}, {r3(t1)});'); E.fx("impact-bass-1", t0 + .02, .55)
def redflash(t0, d=.5):
    A(f'tl.fromTo("#redflash", {{opacity:.9}}, {{opacity:0, duration:{d}, ease:"power2.out"}}, {r3(t0)});')
def tagr(id_, text, t0, t1):
    HTML.append(f'      <div id="{id_}" class="tagr">{text}</div>')
    A(f'tl.fromTo("#{id_}", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.35, ease:"expo.out"}}, {r3(t0)});'); A(f'tl.to("#{id_}", {{opacity:0, duration:.2}}, {r3(t1)});')
def dcard(id_, eyebrow, rows, t0, t1, top=900, row_ts=None, size=52):
    rs = "".join(f'<div class="row" id="{id_}r{i}" style="font-size:{size}px"><div class="box">{TICK}</div><div>{r}</div></div>' for i, r in enumerate(rows))
    HTML.append(f'      <div id="{id_}" class="card" style="top:{top}px"><div class="eyebrow">{eyebrow}</div>{rs}</div>')
    card_in(f"#{id_}", t0); lift(t0 - .05, t1 + .2)
    for i, t_ in enumerate(row_ts or []):
        A(f'tl.to("#{id_}r{i}", {{opacity:1, duration:.2}}, {r3(t_)});'); draw(f"#{id_}r{i} path", t_ + .1, .3); E.fx("pop", t_ + .2, .5)
    card_out(f"#{id_}", t1)

HTML.append('      <div id="redwash"></div><div id="redflash"></div>')

# ======================= HOOK (red, angry)
hk = S["hook"]
A('tl.set("#redwash", {opacity:1}, 0);')
HTML.append('''      <div id="hk1" class="redt" style="top:150px; font-size:96px; opacity:1">SUSAH SANGAT<br>KE NAK BAGI</div>
      <div id="hk2" class="redt" style="top:360px; font-size:200px">SIGNAL?!</div>''')
E.fx("impact-bass-1", .05, .55)
t_sig = w("signal", 5.0)
A(f'tl.fromTo("#hk2", {{opacity:0, scale:1.8}}, {{opacity:1, scale:1, duration:.25, ease:"expo.out"}}, {r3(t_sig - .1)});')
A(f'tl.fromTo("#hk2", {{x:-14}}, {{x:14, duration:.05, yoyo:true, repeat:7}}, {r3(t_sig + .15)});')
E.fx("impact-bass-1", t_sig - .08, .6); redflash(t_sig - .1)
A(f'tl.to("#hk1, #hk2", {{opacity:0, duration:.2}}, {r3(w("Kena", 7.0) - .15)});')
# indicator lever drawing crossed out
svg = (P("M120 90 C 200 60, 320 60, 400 90 M260 75 L260 210", "", 'id="lev"') +
       P("M150 150 l-50 30 l50 30 z M370 150 l50 30 l-50 30 z", "y thick", 'id="arr"') + P("M90 60 L450 250 M450 60 L90 250", "r thick", 'id="lx"'))
HTML.append(f'''      <div id="hkp" class="paper" style="top:930px; height:330px; left:270px; width:540px">
        <svg width="540" height="330" viewBox="0 0 540 330" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("hkp-t", "signal", 200, 255, 56, "r")}</div>''')
A('tl.set("#hkp", {marginTop:"330px"}, 0);'); paper_in("#hkp", t_sig - .3, rot=-3); draw("#lev", t_sig - .1, .3); draw("#arr", t_sig + .1, .3); draw("#lx", w("Kena", 7.0) - .2, .3)
write("#hkp-t", t_sig + .2, 6); E.fx("error", w("Kena", 7.0) - .15, .5); lift(t_sig - .35, S["a"]["out"])
red_t("hk3", "KENA<br>BAYAR KE?!", w("Kena", 7.0) - .1, S["a"]["out"] - .1, top=170, size=190)
paper_out("#hkp", S["a"]["out"] - .25)
A(f'tl.to("#redwash", {{opacity:0, duration:.6}}, {r3(S["a"]["out"] + .2)});')
E.fx("whoosh", S["a"]["out"], .45)

# ======================= a: geram, hampir accident depan mata dengan anak
a = S["a"]
tagr("tg1", "KISAH PAGI TADI", a["out"] + .2, w("anak.", 17.4) + .6)
gold_t("ga1", "HARI NI<br>GERAM!", w("geram,", 8.7) - .1, w("sebab", 11.2) - .2, size=190)
svg = "".join([
    P("M60 250 h420 M60 250 c0 -60 40 -90 100 -95 l60 -55 h140 l50 55 c50 5 70 40 70 95", "", 'id="car1"'),
    '<circle cx="150" cy="260" r="34" class="ink" pathLength="1" id="wh1"/><circle cx="400" cy="260" r="34" class="ink" pathLength="1" id="wh2"/>',
    P("M235 150 m-18 0 a18 18 0 1 0 36 0 a18 18 0 1 0 -36 0 M300 158 m-12 0 a12 12 0 1 0 24 0 a12 12 0 1 0 -24 0", "b", 'id="ppl"'),
    P("M600 70 l40 170 M640 290 v4", "r thick", 'id="excl"'),
])
HTML.append(f'''      <div id="pa" class="paper" style="top:900px; height:380px">
        <svg width="840" height="380" viewBox="0 0 840 380" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("pa-t1", "Saya + anak", 170, 315, 46, "b")}
        {hand("pa-t2", "HAMPIR", 480, 60, 56, "mk r")}
        {hand("pa-t3", "ACCIDENT!", 470, 140, 60, "mk r")}</div>''')
t_ac = w("hampir", 13.3)
paper_in("#pa", w("sebab", 11.2) - .1); lift(w("sebab", 11.2) - .15, a["out"] + a["dur"])
draw("#car1", w("sebab", 11.2) + .2, .6); draw("#wh1", w("sebab", 11.2) + .6, .25); draw("#wh2", w("sebab", 11.2) + .7, .25)
write("#pa-t2", t_ac - .1, 6); write("#pa-t3", w("accident", 15.6) - .2, 9); draw("#excl", w("accident", 15.6), .3)
E.fx("error", w("accident", 15.6), .45)
draw("#ppl", w("anak.", 17.4) - .5, .4); write("#pa-t1", w("anak.", 17.4) - .4, 11)
paper_out("#pa", a["out"] + a["dur"] - .2)

# ======================= b: the road story diagram (top-down)
b = S["b"]
CAR = lambda x, y, cls, id_: P(f"M{x} {y} h46 a10 10 0 0 1 10 10 v80 a10 10 0 0 1 -10 10 h-46 a10 10 0 0 1 -10 -10 v-80 a10 10 0 0 1 10 -10 z M{x} {y+25} h46", cls, f'id="{id_}"')
svg = "".join([
    P("M140 20 V450 M700 20 V450", "", 'id="rd"'),
    P("M420 20 V70 M420 110 V160 M420 200 V250 M420 290 V340 M420 380 V430", "y", 'id="lane"'),
    CAR(520, 260, "r", "ck"),
    P("M545 380 v40 M530 385 v28 M560 385 v28", "r", 'id="spd"'),
    P("M548 250 C 548 170, 300 190, 290 110", "r thick", 'id="cut"'),
    P("M275 120 l15 -18 l15 18", "r thick", 'id="cuth"'),
    P("M270 230 h22 l10 24 v60 h-42 v-60 z M281 222 v-12", "b thick", 'id="mb"'),
    CAR(255, 350, "g", "me"),
    P("M262 330 v-18 M300 330 v-18", "", 'id="skid"'),
    P("M600 120 l60 60 M660 120 l-60 60", "r thick", 'id="nosig"'),
])
HTML.append(f'''      <div id="pb" class="paper" style="top:860px; height:470px">
        <svg width="840" height="470" viewBox="0 0 840 470" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("pb-k", "kereta laju", 590, 420, 40, "r")}
        {hand("pb-ns", "TANPA SIGNAL", 480, 200, 40, "mk r")}
        {hand("pb-m", "motor besar", 20, 255, 40, "b")}
        {hand("pb-me", "SAYA", 160, 380, 44, "mk g")}
        {hand("pb-br", "BRAKE!", 20, 40, 66, "mk r")}</div>''')
t_k = w("kereta", 23.7)
paper_in("#pb", b["out"] + .1, rot=-1); lift(b["out"] + .05, b["out"] + b["dur"])
draw("#rd", b["out"] + .4, .5); draw("#lane", b["out"] + .7, .5)
draw("#ck", t_k - .1, .35); write("#pb-k", w("laju", 25.5) - .3, 11); draw("#spd", w("laju", 25.5), .3); E.fx("whoosh", w("laju", 25.5), .4)
draw("#cut", w("potong", 28.3), .7); draw("#cuth", w("potong", 28.3) + .6, .2); E.fx("whoosh-short", w("potong", 28.3), .45)
draw("#nosig", w("tanpa", 31.2), .3); write("#pb-ns", w("tanpa", 31.2), 12); E.fx("error", w("tanpa", 31.2) + .1, .5)
draw("#mb", w("motor,", 33.7) - .1, .4); write("#pb-m", w("motor,", 33.7), 11)
draw("#me", w("saya.", 35.7) - .2, .35); write("#pb-me", w("saya.", 35.7) - .1, 4)
t_mg = w("mengejut,", 39.1)
A(f'tl.fromTo("#pb", {{x:-10}}, {{x:10, duration:.05, yoyo:true, repeat:5}}, {r3(t_mg)});'); E.fx("impact-bass-1", t_mg, .5)
draw("#skid", w("brake", 41.5) - .1, .3); write("#pb-br", w("brake", 41.5) - .1, 6); E.fx("error", w("brake", 41.5), .5)
paper_out("#pb", b["out"] + b["dur"] - .2)
red_t("rt1", "MENGEJUT!", t_mg - .05, w("brake", 41.5) - .3, top=170, size=180)
gold_t("gb1", "NASIB BAIK<br>SEMPAT BRAKE", w("nasib", 42.4) - .1, b["out"] + b["dur"] - .1, size=150)

# ======================= c: motor respon standard
c = S["c"]
dcard("dc1", "Respon motor tu &mdash; standard", ["Bagi signal", "Lampu tinggi (high beam)", "Hon"], c["out"] + .1, c["out"] + c["dur"] - .25,
      row_ts=[w("signal,", 48.1) - .1, w("lampu", 49.4) - .1, w("horn,", 52.1) - .3])
# ======================= d: kejar-kejar
d = S["d"]
red_t("rt2", "AKSI<br>KEJAR-KEJAR", w("aksi", 55.8) - .2, d["out"] + d["dur"] - .1, top=170, size=170, shake=False)

# ======================= e: pesanan untuk semua + pemandu kereta
e = S["e"]
E.fx("riser", e["out"] - 3.0, .18)
tagr("tg2", "PESANAN SAYA", e["out"] + .2, w("Satu", 112.1) - .3)
gold_t("ge1", "PATUH ADAB<br>&amp; PERATURAN", w("patuh,", 98.2) - .2, w("sebab", 102.6) - .1, size=160)
svg = "".join([
    P("M100 280 h640 M100 280 c0 -70 50 -100 120 -105 l80 -70 h200 l70 70 c80 5 110 45 110 105", "", 'id="car2"'),
    '<circle cx="230" cy="290" r="36" class="ink" pathLength="1" id="w21"/><circle cx="620" cy="290" r="36" class="ink" pathLength="1" id="w22"/>',
    P("M330 170 m-20 0 a20 20 0 1 0 40 0 a20 20 0 1 0 -40 0 M420 170 m-20 0 a20 20 0 1 0 40 0 a20 20 0 1 0 -40 0 M500 180 m-13 0 a13 13 0 1 0 26 0 a13 13 0 1 0 -26 0 M560 180 m-13 0 a13 13 0 1 0 26 0 a13 13 0 1 0 -26 0", "b", 'id="fam"'),
    P("M690 90 c -20 -30, -60 -10, -40 25 l40 40 l40 -40 c20 -35 -20 -55 -40 -25 z", "r thick", 'id="ht"'),
])
HTML.append(f'''      <div id="pe" class="paper" style="top:900px; height:400px">
        <svg width="840" height="400" viewBox="0 0 840 400" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("pe-t1", "Bukan kita bawa seorang&hellip;", 60, 30, 50)}
        {hand("pe-t2", "orang lain pun ada FAMILY", 150, 340, 50, "r")}</div>''')
paper_in("#pe", w("sebab", 102.6) - .1); lift(w("sebab", 102.6) - .15, w("So", 110.4))
write("#pe-t1", w("bukan", 102.9) - .1, 24); draw("#car2", w("bukan", 102.9), .6); draw("#w21", w("bukan", 102.9) + .4, .25); draw("#w22", w("bukan", 102.9) + .5, .25)
draw("#fam", w("orang", 105.8) - .2, .5); write("#pe-t2", w("family.", 106.8) - .5, 24); draw("#ht", w("family.", 106.8), .4); E.fx("pop", w("family.", 106.8) + .1, .5)
paper_out("#pe", w("So", 110.4) - .1)
dcard("dc2", "Tadi ada 2 keadaan", ["Memandu dalam keadaan bahaya", "Tak bagi signal"], w("dua", 111.2) - .3, w("So", 117.2) - .2,
      row_ts=[w("memandu", 113.5) - .2, w("Tak", 115.7) - .1], size=46)
tagr("tg3", "1: UNTUK PEMANDU KERETA", w("So", 117.2), w("Yang", 134.2) + .4 if False else e["out"] + e["dur"] - .2)
svg = "".join([
    P("M70 120 h700", "", 'id="tl1"'), P("M70 280 h700", "", 'id="tl2"'),
    P("M40 100 l20 22 l40 -45", "g thick", 'id="ok1"'), P("M40 250 l50 50 M90 250 l-50 50", "r thick", 'id="x2"'),
])
HTML.append(f'''      <div id="pf" class="paper" style="top:880px; height:420px">
        <svg width="840" height="420" viewBox="0 0 840 420" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("pf-a", "&#11013;&#65039; Signal dulu", 130, 50, 52, "g")}{hand("pf-b", "&rarr; baru masuk", 470, 50, 52, "g")}
        {hand("pf-c", "Masuk dulu", 130, 210, 52, "r")}{hand("pf-d", "&rarr; baru signal?!", 450, 210, 52, "r")}
        {hand("pf-e", "Tak susah pun &mdash; tekan je!", 170, 330, 54, "b")}</div>''')
paper_in("#pf", w("Kalau", 119.2) - .2); lift(w("Kalau", 119.2) - .25, w("Apa", 131.9) - .1)
draw("#tl1", w("Kalau", 119.2), .4); write("#pf-a", w("bagi", 121.5) - .1, 12); write("#pf-b", w("signal.", 121.9) + .2, 12); draw("#ok1", w("signal.", 121.9) + .5, .3)
E.fx("pop", w("signal.", 121.9) + .6, .45)
write("#pf-e", w("tekan,", 125.2) - .3, 26)
draw("#tl2", w("Masalahnya", 127.8), .4); write("#pf-c", w("selepas", 131.1) - .6, 10); write("#pf-d", w("masuk.", 131.7) - .4, 14)
draw("#x2", w("masuk.", 131.7), .3); E.fx("error", w("masuk.", 131.7), .5)
paper_out("#pf", w("Apa", 131.9) - .05)
t_ab = w("Apa", 131.9)
A(f'tl.to("#redwash", {{opacity:1, duration:.15}}, {r3(t_ab - .05)}); tl.to("#redwash", {{opacity:0, duration:.5}}, {r3(e["out"] + e["dur"] - .1)});')
redflash(t_ab - .05)
red_t("rt3", "APA BENDA<br>KAU?!", t_ab - .05, e["out"] + e["dur"] - .15, top=170, size=180)

# ======================= g + h: penunggang motor
g = S["g"]; h = S["h"]
tagr("tg4", "2: UNTUK PENUNGGANG MOTOR", g["out"] + .05, w("So", 158.6) - .2)
gold_t("gm1", "MOTOR,<br>TOLONG!", g["out"] + .1, h["out"] - .05, size=180)
HTML.append(f'''      <div id="ph" class="paper" style="top:900px; height:400px">
        {hand("ph-t", "Saya sendiri banyak kali HAMPIR EKSIDEN:", 50, 30, 48, "r")}
        <div class="emo" id="em0" style="left:80px; top:110px">&#128016;</div>{hand("ph-0", "kambing", 160, 120, 54)}
        <div class="emo" id="em1" style="left:460px; top:110px">&#128167;</div>{hand("ph-1", "jalan licin", 540, 120, 54)}
        <div class="emo" id="em2" style="left:80px; top:230px">&#128663;</div>{hand("ph-2", "kereta", 160, 240, 54)}
        <div class="emo" id="em3" style="left:460px; top:230px">&#129704;</div>{hand("ph-3", "batu tengah jalan", 540, 240, 42)}
      </div>''')
paper_in("#ph", w("Dan", 146.9)); lift(w("Dan", 146.9) - .05, w("So", 158.6))
write("#ph-t", w("banyak", 147.1), 30)
for i_, (wd, nr) in enumerate([("kambing", 151.3), ("licin", 153.4), ("Kereta", 154.1), ("Batu", 156.8)]):
    t_ = w(wd, nr) - .2
    A(f'tl.fromTo("#em{i_}", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {r3(t_)});'); write(f"#ph-{i_}", t_ + .1, 10); E.fx("pop", t_ + .1, .45)
paper_out("#ph", w("So", 158.6) - .1)
dcard("dc3", "Penunggang motor", ["Memang BERISIKO", "Kalau eksiden &mdash; selalunya PALING TERUK"], w("So", 158.6), w("So", 169.6) - .2,
      row_ts=[w("berisiko.", 163.0) - .3, w("paling", 168.5) - .3], size=44)
dcard("dc4", "Tolong hati-hati", ["Keluar simpang, tengok sikit", "Jangan langgar lampu isyarat", "Bawa dengan hati-hati"], w("So", 169.6), w("Kita", 178.4) - .2,
      row_ts=[w("Keluar", 173.2) - .1, w("Jangan", 175.1) - .1, w("Tolonglah", 176.9)], size=46)
# kita sama-sama
words_sm = [("bawa.", 179.3, "BAWA"), ("jalan.", 180.4, "ATAS JALAN"), ("hak.", 181.9, "ADA HAK"), ("sampai.", 183.1, "NAK SAMPAI")]
HTML.append('      <div id="ks0" class="goldt" style="top:150px; font-size:110px">KITA SAMA-SAMA</div>')
gold("#ks0", w("Kita", 178.4) - .1, w("Sebab", 187.3) - .2)
for i_, (wd, nr, txt) in enumerate(words_sm):
    t0 = w(wd, nr) - .4; t1 = (w(words_sm[i_ + 1][0], words_sm[i_ + 1][1]) - .45) if i_ + 1 < len(words_sm) else w("selamat.", 186.9) - .9
    HTML.append(f'      <div id="ks{i_+1}" class="goldt" style="top:290px; font-size:150px">{txt}</div>'); gold(f"#ks{i_+1}", t0, t1)
HTML.append('      <div id="ks5" class="goldt" style="top:290px; font-size:150px">DENGAN SELAMAT</div>'); gold("#ks5", w("selamat.", 186.9) - .8, w("Sebab", 187.3) - .2)
# three families
svg = "".join([
    P(f"M{cx} 110 m-22 0 a22 22 0 1 0 44 0 a22 22 0 1 0 -44 0 M{cx} 132 v70 M{cx} 150 l-28 30 M{cx} 150 l28 30 M{cx} 202 l-22 50 M{cx} 202 l22 50 "
      f"M{cx+60} 140 m-15 0 a15 15 0 1 0 30 0 a15 15 0 1 0 -30 0 M{cx+60} 155 v45 M{cx+60} 200 l-14 32 M{cx+60} 200 l14 32 "
      f"M{cx-55} 120 m-20 0 a20 20 0 1 0 40 0 a20 20 0 1 0 -40 0 M{cx-55} 140 v65 M{cx-55} 205 l-20 47 M{cx-55} 205 l20 47", cls, f'id="fm{k}"')
    for k, (cx, cls) in enumerate([(150, "g"), (420, "b"), (690, "r")])])
HTML.append(f'''      <div id="pi" class="paper" style="top:900px; height:400px">
        <svg width="840" height="400" viewBox="0 0 840 400" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("pi-0", "Saya", 100, 280, 44, "g")}{hand("pi-0b", "anak &amp; isteri", 50, 330, 38, "g")}
        {hand("pi-1", "Penunggang motor", 300, 280, 40, "b")}{hand("pi-1b", "anak &amp; isteri", 330, 330, 38, "b")}
        {hand("pi-2", "Pemandu kereta", 590, 280, 40, "r")}{hand("pi-2b", "suami &amp; anak", 600, 330, 38, "r")}
        {hand("pi-t", "Semua orang ada FAMILY", 200, 20, 52)}</div>''')
paper_in("#pi", w("Saya", 191.4) - .4); lift(w("Saya", 191.4) - .45, h["out"] + h["dur"])
draw("#fm0", w("Saya", 191.4) - .2, .6); write("#pi-0", w("anak,", 191.9) - .2, 4); write("#pi-0b", w("bini.", 192.7) - .3, 14)
draw("#fm1", w("Dia", 195.0) - .4, .6); write("#pi-1", w("Dia", 195.0) - .3, 16); write("#pi-1b", w("bini.", 196.2) - .3, 14)
draw("#fm2", w("Yang", 196.6), .6); write("#pi-2", w("kereta", 196.9), 14); write("#pi-2b", w("suami", 198.8) - .2, 14)
write("#pi-t", w("anak.", 200.4) - .4, 22); E.fx("pop", w("anak.", 200.4), .4)
paper_out("#pi", h["out"] + h["dur"] - .2)

# ======================= j: satu kematian = banyak kehilangan
j = S["j"]
A(f'tl.to("#cam video", {{filter:"brightness(.95) saturate(.75) contrast(1.05)", duration:1.2}}, {r3(j["out"])});')
gold_t("gj0", "SATU<br>KEMATIAN&hellip;", j["out"] + .1, w("Tetapi", 207.5) - .2, size=170)
svg = "".join([
    P("M420 120 m-30 0 a30 30 0 1 0 60 0 a30 30 0 1 0 -60 0 M420 150 v80 M420 175 l-35 35 M420 175 l35 35 M420 230 l-28 60 M420 230 l28 60", "", 'id="cw"'),
    P("M380 150 C 300 140, 230 140, 180 170 M180 170 l26 -4 M180 170 l14 22", "r", 'id="ar0"'),
    P("M420 300 C 420 320, 420 330, 420 340 M420 340 l-12 -18 M420 340 l12 -18", "r", 'id="ar1"'),
    P("M460 150 C 540 140, 610 140, 660 170 M660 170 l-26 -4 M660 170 l-14 22", "r", 'id="ar2"'),
])
HTML.append(f'''      <div id="pj" class="paper" style="top:880px; height:440px">
        <svg width="840" height="440" viewBox="0 0 840 440" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("pj-w", "seorang wanita", 330, 40, 40)}
        {hand("pj-0", "Anak kehilangan IBU", 20, 200, 38, "r")}
        {hand("pj-1", "Ibu bapa kehilangan ANAK", 230, 360, 44, "r")}
        {hand("pj-2", "Suami kehilangan ISTERI", 500, 200, 36, "r")}</div>''')
paper_in("#pj", w("Tetapi", 207.5) - .3); lift(w("Tetapi", 207.5) - .35, w("Faham", 220.0) + .3)
draw("#cw", w("Tetapi", 207.5), .6); write("#pj-w", w("seorang", 208.9) - .2, 14)
draw("#ar0", w("anak", 214.6) - .3, .4); write("#pj-0", w("kehilangan", 215.0) - .1, 20); E.fx("pop", w("ibu.", 215.7), .4)
draw("#ar2", w("suami", 216.4) - .2, .4); write("#pj-2", w("kehilangan", 217.1) - .2, 22); E.fx("pop", w("isteri.", 217.5), .4)
draw("#ar1", w("ibu", 218.2) - .2, .3); write("#pj-1", w("kehilangan", 218.9) - .3, 24); E.fx("pop", w("anak.", 219.5), .4)
paper_out("#pj", w("Faham", 220.0) + .3)
gold_t("gj1", "BUKAN SATU<br>KEMATIAN SAHAJA", w("bukan", 221.7) - .3, w("Dia", 223.0) - .1, size=140)
gold_t("gj2", "KEHILANGAN<br>BANYAK JIWA", w("kehilangan", 223.6) - .2, w("So", 226.9) - .2, size=150)
gold_t("gj3", "HATI-HATI<br>DI JALAN RAYA", w("hati-hati", 229.2) - .4, T_END - .2, size=170)

# ======================= end card
HTML.append('''      <div id="end" style="position:absolute; inset:0; opacity:0; z-index:10; background:radial-gradient(ellipse at 50% 45%, rgba(42,29,18,.85), rgba(14,10,7,.95))">
        <div style="position:absolute; left:0; right:0; top:560px; text-align:center; font-family:'Caveat'; font-weight:700; font-size:84px; color:#FFE9B0">Semoga kita semua</div>
        <div style="position:absolute; left:0; right:0; top:660px; text-align:center; font-family:'Anton'; font-size:130px; color:#F7C24A; text-transform:uppercase">selamat sampai</div>
        <div style="position:absolute; left:0; right:0; top:880px; text-align:center; font-family:Montserrat; font-weight:800; font-size:40px; letter-spacing:.14em; color:#fff">SHARE PADA ORANG TERSAYANG</div>
        <div id="end-sb" style="position:absolute; left:170px; right:170px; top:990px; height:120px; border-radius:24px; background:#fff; display:flex; align-items:center; gap:22px; padding:0 34px;
             box-shadow:-6px 0 0 #25F4EE, 6px 0 0 #FE2C55, 0 20px 50px rgba(0,0,0,.5)">
          <span style="font-size:52px">&#128269;</span><span id="end-tx" style="font-family:Montserrat; font-weight:700; font-size:52px; color:#161616; display:inline-block; overflow:hidden; white-space:nowrap; width:0">@khalidkacak</span></div>
      </div>''')
A(f'tl.to("#end", {{opacity:1, duration:.6}}, {r3(T_END)});'); E.fx("whoosh", T_END, .35)
A(f'tl.fromTo("#end-sb", {{scale:.8, opacity:0}}, {{scale:1, opacity:1, duration:.4, ease:"back.out(1.6)"}}, {r3(T_END + 1.2)});')
A(f'tl.to("#end-tx", {{width:"440px", duration:1.0, ease:"steps(12)"}}, {r3(T_END + 1.7)});'); E.fx("click-soft", T_END + 2.75, .5)
A(f'tl.to("#root", {{opacity:0, duration:.5}}, {r3(TOTAL - .5)});')

# ======================= camera
for i, c_ in enumerate(E.cuts()):
    E.zoom.append((c_, "set", *[(1.0, 0), (1.08, 10), (1.04, -8), (1.1, 0)][i % 4]))
PUNCH = [w("signal", 5.0), w("Kena", 7.0), w("geram,", 8.7), w("mengejut,", 39.1), w("patuh,", 98.2), w("Tak", 122.5), w("Apa", 131.9), w("berisiko.", 163.0),
         w("teruk.", 169.0), w("bukan", 221.7)]
LV = [(1.12, 0), (1.0, 0), (1.18, -16), (1.05, 12), (1.14, 14), (1.0, 0)]
cands, k, last = [], 0, -9
for n in range(1, len(WORDS)):
    if WORDS[n - 1]["text"].strip()[-1:] in ".?!,":
        for s in E.vo:
            if s["src_in"] <= WORDS[n]["start"] <= s["src_out"]:
                cands.append(round(s["out"] + WORDS[n]["start"] - s["src_in"], 3))
cuts = E.cuts()
for tt in sorted(set(cands)):
    prev = max([c for c in cuts if c <= tt] or [0]); nxt = min([c for c in cuts if c > tt] or [TOTAL])
    if tt - prev < .7 or nxt - tt < .8 or tt - last < 2.4 or any(abs(tt - p) < 1.0 for p in PUNCH):
        continue
    E.zoom.append((tt, "ease", *LV[k % len(LV)])); k += 1; last = tt
for p in PUNCH:
    E.zoom.append((round(p - .05, 3), "punch", 1.26, 0))
for p in PUNCH[::2]:
    E.fx("whoosh-short", p, .35)

# ======================= subtitles
RED = [(0, S["a"]["out"]), (t_ab - .1, e["out"] + e["dur"]), (w("mengejut,", 39.1) - 1, w("brake", 41.5))]
KEY = re.compile(r"(?i)^(signal|geram|accident|eksiden|laju|potong|motor|brake|mengejut|patuh|adab|peraturan|family|bahaya|simpang|berisiko|teruk|"
                 r"hati-hati|selamat|anak|isteri|bini|suami|ibu|kematian|kehilangan|jiwa|bayar|lampu|horn|hak|kambing|licin|batu)")
FIX = {"beli": "bagi", "masin": "masa", "len": "lane", "kejam-kejam": "kejar-kejar", "ikan": "kanan", "sisi": "cc", "Uzmila": "", "Mizalik.": "",
       "bengkak,": "bengang,", "motong": "potong"}
words = []
for s in E.vo:
    for x in WORDS:
        if not (s["src_in"] - .05 <= x["start"] < s["src_out"] - .05): continue
        txt = x["text"]
        if txt in FIX: txt = FIX[txt]
        if not txt.strip(".,?!"): continue
        if s["name"] == "hook" and txt == "beli": txt = "bagi"
        words.append([round(s["out"] + x["start"] - s["src_in"], 3), txt])
words.sort()
i = 0
while i < len(words):
    j_ = i
    while j_ + 1 < len(words) and words[j_ + 1][0] <= words[i][0] + .02: j_ += 1
    if j_ > i:
        nxt = words[j_ + 1][0] if j_ + 1 < len(words) else words[i][0] + .3 * (j_ - i + 1)
        step = (nxt - words[i][0]) / (j_ - i + 1)
        for m in range(i, j_ + 1): words[m][0] = round(words[i][0] + step * (m - i), 3)
    i = j_ + 1
seg_end = sorted({round(s["out"] + s["dur"], 3) for s in E.vo})
chunks, cur = [], []
for t0, txt in words:
    if cur and any(cur[-1][0] < e_ <= t0 for e_ in seg_end):
        chunks.append(cur); cur = []
    cur.append((t0, txt))
    if txt[-1:] in ".?!," or len(cur) >= 4:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
for i, ch in enumerate(chunks):
    t0 = ch[0][0]; t1 = chunks[i + 1][0][0] if i + 1 < len(chunks) else t0 + 2
    ends = [e_ for e_ in seg_end if e_ > t0]
    t1 = max(min(t1, t0 + 2.6, min(ends) + .1 if ends else t1), t0 + .35)
    words_ = " ".join(f"<i>{t.strip('.,?!')}</i>{t[len(t.strip('.,?!')):]}" if KEY.match(t) else t for _, t in ch)
    red = any(a_ <= t0 < b_ for a_, b_ in RED)
    HTML.append(f'      <div id="sb{i}" class="sub{" red" if red else ""}">{words_}</div>')
    A(f'tl.fromTo("#sb{i}", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:.12}}, {r3(t0 - .05)});')
    A(f'tl.to("#sb{i}", {{opacity:0, duration:.08}}, {r3(t1 - .06)});')

E.music = [(0, .0), (S["a"]["out"] - .5, 0), (S["a"]["out"] + .5, .12), (T_END - .3, .12), (T_END + .3, .5), (TOTAL - .6, 0), (TOTAL, 0)]
write_project(E, os.path.join(ROOT, "v1"), TOTAL, card_lift=True, bg="#000")
p = json.load(open(os.path.join(ROOT, "v1/edit-plan.json"))); p["music_file"] = "assets/music/river-meditation.mp3"
json.dump(p, open(os.path.join(ROOT, "v1/edit-plan.json"), "w"), indent=1)
