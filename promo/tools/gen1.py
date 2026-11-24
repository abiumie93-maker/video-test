"""VIDEO 1 - house style (talking footage, zoom in/out + zoom slams, dark cards + hand-drawn paper cards).
Run: python3 tools/gen1.py  -> v1/index.html + v1/edit-plan.json"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Edit, write_project, ROOT

E = Edit()
M = "assets/footage/main.mp4"

# ---------------- voice edit (source seconds, snapped to quiet frames)
hook = E.say("hook", 59.83, 65.83)     # "Sayang lah, tilam korang beli mahal. Tiba-tiba banyak tompok-tompok, peta-peta dunia"
hook2 = E.say("hook2", 65.83, 69.33)   # "pasang lapik cadar ni kat tilam. Let's go."
a = E.say("a", 0.20, 3.81)             # "Guys, mari sini... Tengoklah ini."
b = E.say("b", 3.81, 18.77)            # item list, "Jenama? Alooma." x5
c = E.say("c", 23.12, 28.58)           # wife: "warna putih tak cantik, abang"   (cut "...ini adalah brand? Alooma lah guys")
d = E.say("d", 30.01, 39.05)           # "dia nak warna pink... satu set warna pink" (cut repeat "warna putih tak cantik")
e = E.say("e", 40.97, 59.83)           # waterproof, 2-3 bulan, wajib pakai
T_MON = E.hold(13.4)                   # montage (music)
T_ROOM = E.hold(4.4)
T_CTA = E.hold(5.8)
TOTAL = E.t
o, w = E.o, E.w

# ---------------- picture
E.shot(0, hook["dur"], "assets/img/oldmattress-bg.jpg", kind="img",
       style="filter:blur(26px) brightness(.45); transform:scale(1.15)")
E.shot(0, hook["dur"], "assets/img/oldmattress.jpg", kind="img",
       style="width:1080px; height:1168px; top:150px; object-fit:cover")
E.shot(hook2["out"], hook2["dur"], M, 109.95)          # jump onto the finished pink bed
for s in (a, b, c, d, e):
    E.synced(s)
MON = [(69.45, 2.0, "PASANG", "CADAR"), (72.1, 1.7, None, None), (76.7, 1.8, "KEMAS &", "MUAT"),
       (81.55, 2.0, "COMFORTER", None), (87.25, 1.9, "SARUNG", "BANTAL"), (92.15, 1.8, None, None)]
t = T_MON
mon_cuts = []
for ms, du, l1, l2 in MON:
    E.shot(t, du, M, ms); mon_cuts.append((t, du, l1, l2)); t += du
REVEAL = round(t, 3)
E.shot(REVEAL, T_ROOM - REVEAL, M, 103.6)                          # finished bed
E.shot(T_ROOM, 2.7, "assets/footage/20261029_232802.mp4", 0.4)     # glowing headboard, pink bed
E.shot(T_ROOM + 2.7, T_CTA - T_ROOM - 2.7, "assets/footage/20261028_210240.mp4", 0.4)
E.shot(T_CTA, TOTAL - T_CTA, "assets/footage/20261029_232831.mp4", 0.0)

# ---------------- camera
for i, ct in enumerate(E.cuts()):
    E.zoom.append((ct, "set", *[(1.0, 0), (1.08, 12), (1.04, -10), (1.1, 0)][i % 4]))
LV = [(1.14, 0), (1.0, 0), (1.2, -20), (1.06, 16), (1.16, 18), (1.0, 0), (1.22, -14), (1.08, 0)]
PUNCH = [w("mahal", 61.8), w("dunia", 65.5), w("go.", 68.8), w("Alooma", 4.8), w("Alooma", 11.0), w("Alooma", 17.75),
         w("cantik", 27.3), w("pink", 33.9), w("waterproof", 48.7), w("bersih", 55.2), w("wajib", 56.1)]
cands = []
for n in range(1, len(__import__("common").WORDS)):
    W_ = __import__("common").WORDS
    if W_[n - 1]["text"].strip()[-1:] in ".?!,":
        try: cands.append(o(W_[n]["start"]))
        except ValueError: pass
last, k = -9, 0
cuts = E.cuts()
for tt in sorted(set(cands)):
    prev = max([c_ for c_ in cuts if c_ <= tt] or [0]); nxt = min([c_ for c_ in cuts if c_ > tt] or [TOTAL])
    if tt - prev < .8 or nxt - tt < .9 or tt - last < 2.2 or any(abs(tt - p) < 1.2 for p in PUNCH) or tt > T_MON:
        continue
    E.zoom.append((tt, "ease", *LV[k % len(LV)])); k += 1; last = tt
for p in PUNCH:
    E.zoom.append((round(p - .05, 3), "punch", 1.28, 0))
# hook: slow push into the stains; montage/room: slow push on every shot
E.zoom.append((0.02, "slow", 1.12, 0))
for st_, du, *_ in mon_cuts:
    E.zoom.append((st_ + .02, "slow", 1.12, 0))
E.zoom.append((REVEAL + .02, "slow", 1.1, 0))
E.zoom.append((T_ROOM + .02, "slow", 1.15, 0)); E.zoom.append((T_ROOM + 2.72, "slow", 1.12, 0))
E.zoom.append((T_CTA + .02, "slow", 1.1, 0))
for p in PUNCH[::2]:
    E.fx("whoosh-short", p)

# ---------------- graphics helpers
E.css.append("""
  .scrim { position:absolute; left:0; right:0; bottom:0; height:1000px; opacity:0;
           background:linear-gradient(to bottom, rgba(0,0,0,0), rgba(0,0,0,.55) 55%, rgba(0,0,0,.72)); }
  .big { font-family:'Archivo Black',sans-serif; color:#fff; text-transform:uppercase; line-height:1.02;
         text-shadow:0 6px 24px rgba(0,0,0,.45); }
  .y { color:#FFC928; } .rd { color:#FF4D4D; } .gr { color:#3DDC84; }
  .wd { display:inline-block; opacity:0; }
  .card { position:absolute; left:120px; width:840px; background:rgba(12,18,38,.88); border-radius:28px;
          padding:30px 38px; box-shadow:0 18px 50px rgba(0,0,0,.4); color:#fff; font-family:'Montserrat',sans-serif; opacity:0; }
  .eyebrow { font-weight:800; font-size:30px; letter-spacing:.14em; color:#FFC928; text-transform:uppercase; }
  .row { display:flex; align-items:center; gap:22px; font-weight:800; font-size:44px; margin-top:16px; opacity:.35; }
  .box { width:48px; height:48px; border-radius:12px; border:4px solid rgba(255,255,255,.55); position:relative; flex:none; }
  .box svg { position:absolute; left:-4px; top:-8px; }
  .chip { display:inline-block; padding:14px 26px; border-radius:999px; font-weight:800; font-size:38px;
          background:rgba(255,255,255,.12); border:3px solid rgba(255,255,255,.3); margin:14px 12px 0 0; position:relative; opacity:0; }
  .stamp { position:absolute; font-family:'Archivo Black',sans-serif; text-transform:uppercase; padding:14px 30px;
           border:8px solid #FFC928; color:#FFC928; border-radius:18px; background:rgba(12,18,38,.75); opacity:0; }
  .paper { position:absolute; left:120px; width:840px; background:#FFF8E7; border-radius:14px; opacity:0;
           box-shadow:0 18px 44px rgba(0,0,0,.4); color:#1d1d1f; }
  .paper::before { content:""; position:absolute; left:50%; top:-18px; width:170px; height:38px; margin-left:-85px;
                   background:rgba(255,201,40,.8); border-radius:3px; }
  .ink { fill:none; stroke:#1d1d1f; stroke-width:6; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:1; stroke-dashoffset:1; }
  .ink.r { stroke:#E63434; } .ink.g { stroke:#1FA855; } .ink.y { stroke:#F2B705; } .ink.b { stroke:#1F5FD1; }
  .ink.p { stroke:#F48FB1; } .ink.thick { stroke-width:12; } .ink.w { stroke:#fff; }
  .hand { position:absolute; font-family:'Caveat',cursive; font-weight:700; color:#1d1d1f; line-height:1; white-space:nowrap;
          clip-path:inset(0 100% 0 0); }
  .mk { font-family:'Permanent Marker',cursive; font-weight:400; }
  .hand.r { color:#E63434; } .hand.g { color:#1FA855; } .hand.b { color:#1F5FD1; }
  .lbl { position:absolute; left:0; right:0; text-align:center; font-size:124px; opacity:0; }
""")
A = E.add


def r3(x): return round(max(x, 0), 3)
def show(sel, t, d=.3): A(f'tl.to("{sel}", {{opacity:1, duration:{d}}}, {r3(t)});')
def hide(sel, t, d=.25): A(f'tl.to("{sel}", {{opacity:0, duration:{d}, ease:"power2.in"}}, {r3(t)});')
def card_in(sel, t):
    A(f'tl.fromTo("{sel}", {{opacity:0, y:50, scale:.95}}, {{opacity:1, y:0, scale:1, duration:.45, ease:"expo.out"}}, {r3(t)});')
    E.fx("whoosh-short", t + .05, .35)
def card_out(sel, t): A(f'tl.to("{sel}", {{opacity:0, y:-24, filter:"blur(6px)", duration:.25, ease:"power2.in"}}, {r3(t)});')
def paper_in(sel, t, rot=-1.5):
    A(f'tl.fromTo("{sel}", {{opacity:0, y:80, rotation:-7, scale:.82, transformOrigin:"50% 0%"}}, '
      f'{{opacity:1, y:0, rotation:{rot}, scale:.92, transformOrigin:"50% 0%", duration:.55, ease:"back.out(1.4)"}}, {r3(t)});')
    E.fx("whoosh-short", t + .05, .35)
def paper_out(sel, t): A(f'tl.to("{sel}", {{opacity:0, y:-30, rotation:3, filter:"blur(5px)", duration:.28, ease:"power2.in"}}, {r3(t)});')
def draw(sel, t, d=.5): A(f'tl.fromTo("{sel}", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{d}, ease:"power1.inOut"}}, {r3(t)});')
def write(sel, t, n=10):
    d = round(min(max(.045 * n, .3), .9), 2)
    A(f'tl.fromTo("{sel}", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{d}, ease:"none"}}, {r3(t)});')
def pop(sel, t, sfx="pop"):
    A(f'tl.fromTo("{sel}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.38, ease:"back.out(1.8)"}}, {r3(t)});')
    if sfx: E.fx(sfx, t + .1)
def words_in(sel, t, st=.09):
    A(f'tl.fromTo("{sel}", {{opacity:0, y:30, filter:"blur(8px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:.22, ease:"power4.out", stagger:{st}}}, {r3(t)});')
def P(d, cls="", extra=""): return f'<path class="ink {cls}" pathLength="1" d="{d}" {extra}/>'
def hand(id_, text, x, y, size, cls=""):
    return f'<div class="hand {cls}" id="{id_}" style="left:{x}px; top:{y}px; font-size:{size}px">{text}</div>'
def lift(a_, b_): E.lift.append((round(a_, 3), round(b_, 3)))
TICK = '<svg width="64" height="60" viewBox="0 0 64 60"><path class="ink g thick" pathLength="1" d="M8 30 L26 48 L58 6"/></svg>'

# ---------------- HOOK (0 - 9.5): "Tilam beli mahal... jadi PETA DUNIA?!"
E.cam_html.append('''        <svg id="hk-rings" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">
          <path class="ink r thick" pathLength="1" d="M180 1010 C 90 1000, 80 1150, 200 1170 C 330 1185, 360 1040, 250 1000"/>
          <path class="ink r thick" pathLength="1" d="M820 760 C 720 730, 690 880, 800 905 C 930 925, 960 790, 860 755"/>
          <path class="ink r thick" pathLength="1" d="M560 1180 C 450 1160, 440 1300, 560 1320 C 690 1335, 720 1200, 610 1175"/>
        </svg>''')
E.html.append('''      <div id="hk-scrim" class="scrim"></div>
      <div id="hk-box" class="ov" style="left:70px; right:70px; top:1395px; text-align:center; opacity:1">
        <div id="hk-l1" class="big" style="font-size:66px"><span class="wd">Tilam</span> <span class="wd">beli</span> <span class="wd y">mahal...</span></div>
        <div id="hk-l2" class="big" style="font-size:60px; margin-top:14px"><span class="wd">tiba-tiba</span> <span class="wd">jadi</span></div>
        <div id="hk-l3" class="big rd" style="font-size:132px; margin-top:4px"><span class="wd">PETA DUNIA?!</span></div>
        <svg width="760" height="46" viewBox="0 0 760 46" style="display:block;margin:-4px auto 0"><path id="hk-ul" class="ink y thick" pathLength="1" d="M20 28 C 200 8, 420 40, 740 16"/></svg>
      </div>
      <div id="hk2" class="ov" style="left:70px; right:70px; top:1300px; text-align:center">
        <div class="big" style="font-size:54px"><span class="wd">Penyelesaian</span> <span class="wd">dia?</span></div>
        <div class="big y" style="font-size:118px; margin-top:6px"><span class="wd">SET</span> <span class="wd">ALOOMA</span></div>
        <div class="big" style="font-size:58px; margin-top:8px"><span class="wd">Lapik</span> <span class="wd">+</span> <span class="wd">Cadar</span> <span class="wd">+</span> <span class="wd">Comforter</span></div>
      </div>''')
A('tl.set("#hk-scrim", {opacity:1}, 0);')
A('tl.set("#hk-l1 .wd", {opacity:1}, 0);')                       # thumbnail frame already has the hook line
E.fx("impact-bass-1", 0.05, .45)
for i, sel in enumerate(["#hk-rings path:nth-child(1)", "#hk-rings path:nth-child(2)", "#hk-rings path:nth-child(3)"]):
    draw(sel, w("tompok", 63.8) + i * .28, .4)
E.fx("error", w("tompok", 63.8) + .1, .5)
words_in("#hk-l2 .wd", w("Tiba-tiba", 62.6))
pop("#hk-l3 .wd", w("dunia", 65.5) - .05, "impact-bass-1")
draw("#hk-ul", w("dunia", 65.5) + .2, .45)
A(f'tl.to("#hk-box", {{opacity:0, y:-30, duration:.2}}, {hook2["out"] - .12});')
A(f'tl.to("#hk-rings", {{opacity:0, duration:.15}}, {hook2["out"] - .1});')
E.fx("whoosh", hook2["out"])
words_in("#hk2 .wd", hook2["out"] + .15, .1)
E.fx("impact-bass-1", w("go.", 68.8), .4)
A(f'tl.to("#hk2", {{opacity:1, duration:.01}}, {hook2["out"] + .1});')
A(f'tl.to("#hk2, #hk-scrim", {{opacity:0, duration:.25}}, {a["out"] - .25});')

# ---------------- a: "Guys mari sini... tengoklah ini" -> product name card
E.html.append('''      <div id="ca" class="card" style="top:1040px">
        <div class="eyebrow">Unboxing &bull; Review jujur</div>
        <div class="big" style="font-size:78px; margin-top:8px">SET <span class="y">ALOOMA</span> PREMIUM</div>
      </div>''')
card_in("#ca", o(0.5)); lift(o(0.45), o(3.75)); card_out("#ca", o(3.55))

# ---------------- b: checklist + ALOOMA stamp on every "Alooma"
ITEMS = [("Lapik tilam", 3.85), ("Comforter", 5.52), ("Lapik bantal waterproof", 8.16), ("Bantal", 11.70), ("Tuala", 14.54)]
rows = "".join(f'<div class="row" id="it{i}"><div class="box">{TICK}</div><div>{n}</div></div>' for i, (n, _) in enumerate(ITEMS))
E.html.append(f'''      <div id="cb" class="card" style="top:900px">
        <div class="eyebrow">Dalam 1 set ada&hellip;</div>
        {rows}
      </div>
      <div id="stamp-al" class="stamp" style="left:560px; top:820px; font-size:64px; transform:rotate(-8deg)">ALOOMA!</div>''')
card_in("#cb", o(3.9) - .25); lift(o(3.85) - .3, o(18.7))
for i, (n, s_) in enumerate(ITEMS):
    A(f'tl.to("#it{i}", {{opacity:1, duration:.2}}, {o(s_)});')
    draw(f"#it{i} path", o(s_) + .15, .3)
    E.fx("pop", o(s_) + .25, .45)
for j, s_ in enumerate((4.78, 7.47, 11.01, 13.85, 17.75)):
    t_ = w("Alooma", s_)
    ir = "" if j == 0 else ", immediateRender:false"
    A(f'tl.fromTo("#stamp-al", {{opacity:0, scale:1.8, rotation:-14}}, {{opacity:1, scale:1, rotation:-8, duration:.3, ease:"back.out(2)"{ir}}}, {t_});')
    A(f'tl.to("#stamp-al", {{opacity:0, duration:.18}}, {round(t_ + .75, 3)});')
    E.fx("impact-bass-1", t_ + .02, .3)
card_out("#cb", o(18.6))

# ---------------- c + d: wife wants pink (paper card), then "1 set pink"
svg = "".join([
    '<circle cx="130" cy="120" r="44" class="ink" pathLength="1" />',
    P("M86 112 C 80 60, 180 60, 174 112 M150 70 C 160 40, 196 50, 186 80", "", 'id="wf-hair"'),
    P("M130 164 L130 290 M130 200 L80 250 M130 200 L185 240 M130 290 L92 370 M130 290 L168 370", "", 'id="wf-body"'),
    P("M240 40 h520 a24 24 0 0 1 24 24 v110 a24 24 0 0 1 -24 24 h-430 l-60 50 l10 -50 h-40 a24 24 0 0 1 -24 -24 v-110 a24 24 0 0 1 24 -24 z", "", 'id="wf-bub"'),
    P("M300 270 h150 v150 h-150 z", "", 'id="sw-w"'),
    P("M290 260 L460 430 M460 260 L290 430", "r thick", 'id="sw-x"'),
    P("M560 270 h150 v150 h-150 z", "p thick", 'id="sw-p"'),
    P("M585 345 L622 385 L695 290", "g thick", 'id="sw-ok"'),
    P("M470 345 C 500 310, 520 310, 545 340 M530 322 l18 18 l-24 6", "", 'id="sw-ar"'),
])
E.html.append(f'''      <div id="pw" class="paper" style="top:880px; height:470px">
        <svg width="840" height="470" viewBox="0 0 840 470" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("wf-t1", "Putih tak cantik,", 280, 62, 62)}
        {hand("wf-t2", "abang!", 280, 126, 62, "r")}
        {hand("wf-t3", "Isteri", 84, 380, 50, "b")}
        {hand("wf-t4", "PINK!", 730, 300, 70, "mk g")}
      </div>''')
E.css.append("#pw .ink { stroke-width:7; } #wf-t4 { transform:rotate(-8deg); }")
paper_in("#pw", o(23.15)); lift(o(23.12), o(34.5))
draw("#pw circle", o(23.3), .35); draw("#wf-hair", o(23.5), .35); draw("#wf-body", o(23.7), .5)
draw("#wf-bub", w("bini", 25.7), .5)
write("#wf-t3", w("bini", 25.7) + .1, 6)
write("#wf-t1", w("putih", 26.9), 16); E.fx("pop", w("putih", 26.9) + .1, .3)
draw("#sw-w", w("warna", 26.5), .35)
draw("#sw-x", w("cantik", 27.3), .3); E.fx("error", w("cantik", 27.3), .45)
write("#wf-t2", w("abang", 27.9), 6)
draw("#sw-ar", w("nak", 30.5), .3)
draw("#sw-p", w("pink", 31.1), .4)
draw("#sw-ok", w("grab", 33.0), .35); write("#wf-t4", w("grab", 33.0) + .1, 5); E.fx("pop", w("grab", 33.0) + .2)
paper_out("#pw", o(34.45))
E.html.append('''      <div id="cd" class="card" style="top:980px; text-align:center">
        <div class="eyebrow">Kali ni dapat</div>
        <div class="big" style="font-size:96px; margin-top:6px">1 SET <span style="color:#FF8FC0">PINK</span></div>
        <div style="display:flex; gap:16px; justify-content:center; margin-top:16px">
          <span class="chip" id="cd1">Cadar</span><span class="chip" id="cd2">Sarung bantal</span><span class="chip" id="cd3">Comforter</span></div>
      </div>''')
card_in("#cd", w("kali", 34.8)); lift(w("kali", 34.8) - .05, o(39.0))
for i in range(3):
    pop(f"#cd{i+1}", w("satu", 36.7) + i * .2, "pop" if i == 0 else None)
card_out("#cd", o(38.9))

# ---------------- e1: waterproof vs non-waterproof
E.html.append('''      <div id="cw" class="card" style="top:930px">
        <div class="eyebrow" id="cw-e1">Lapik Alooma ada 2 jenis</div>
        <div><span class="chip" id="wp" style="font-size:44px">WATERPROOF</span><span class="chip" id="nwp" style="font-size:44px">NON-WATERPROOF</span></div>
        <svg id="nwp-x" width="840" height="120" viewBox="0 0 840 120" style="position:absolute;left:0;top:96px"><path class="ink r thick" pathLength="1" d="M440 70 L790 66"/></svg>
        <div id="cw-rec" style="opacity:0; margin-top:22px; font-weight:800; font-size:46px">Cadangan saya: <span class="y">ambil WATERPROOF</span></div>
      </div>
      <div id="stamp-wp" class="stamp" style="left:600px; top:850px; font-size:56px; border-color:#3DDC84; color:#3DDC84; transform:rotate(-6deg)">PILIH INI!</div>''')
card_in("#cw", o(41.05)); lift(o(41.0), o(49.6))
pop("#wp", w("waterproof", 43.9)); pop("#nwp", w("non-waterproof", 44.9))
show("#cw-rec", w("Cadangan", 46.0), .3)
A(f'tl.to("#nwp", {{opacity:.35, duration:.3}}, {w("waterproof", 48.7)});')
draw("#nwp-x path", w("waterproof", 48.7), .3); E.fx("error", w("waterproof", 48.7) + .05, .35)
A(f'tl.to("#wp", {{background:"#3DDC84", borderColor:"#3DDC84", color:"#0C1226", scale:1.08, duration:.25}}, {w("waterproof", 48.7) + .1});')
A(f'tl.fromTo("#stamp-wp", {{opacity:0, scale:1.8}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {w("waterproof", 48.7) + .2});')
E.fx("impact-bass-1", w("waterproof", 48.7) + .2, .35)
card_out("#cw", o(49.55)); hide("#stamp-wp", o(49.5))

# ---------------- e2: 2-3 bulan, masih cantik & bersih (paper)
svg = "".join([
    P("M60 60 h220 v200 h-220 z M60 110 h220 M110 40 v40 M230 40 v40", "", 'id="cal"'),
    P("M310 160 C 360 130, 400 130, 440 160 M420 140 l22 20 l-28 10", "", 'id="cal-ar"'),
    P("M480 120 L780 120 L800 250 L460 250 Z M460 250 v26 h340 v-26", "", 'id="mat"'),
    P("M560 170 l0 26 M547 183 l26 0 M690 150 l0 30 M675 165 l30 0 M720 215 l0 20 M710 225 l20 0", "y thick", 'id="spark"'),
])
E.html.append(f'''      <div id="pb" class="paper" style="top:900px; height:470px">
        <svg width="840" height="470" viewBox="0 0 840 470" style="position:absolute;left:0;top:0">{svg}</svg>
        {hand("cal-t", "2-3", 104, 132, 92, "mk r")}
        {hand("cal-t2", "bulan", 110, 214, 44)}
        {hand("pb-t1", "Masih CANTIK", 70, 300, 66, "g")}
        {hand("pb-t2", "Masih BERSIH", 450, 300, 66, "g")}
        {hand("pb-t3", "&#10003; lepas 2-3 bulan pakai", 220, 385, 52, "b")}
      </div>''')
paper_in("#pb", w("Tengok", 49.7)); lift(w("Tengok", 49.7) - .05, o(55.6))
draw("#cal", w("selepas", 50.2), .45); write("#cal-t", w("2-3", 52.0), 3); write("#cal-t2", w("bulan", 52.6), 5)
E.fx("pop", w("2-3", 52.0) + .1)
draw("#cal-ar", w("tilam", 53.2), .3); draw("#mat", w("tilam", 53.2) + .2, .45)
write("#pb-t1", w("cantik", 54.1), 12); draw("#spark", w("cantik", 54.1) + .1, .35); E.fx("pop", w("cantik", 54.1) + .15, .4)
write("#pb-t2", w("bersih", 55.2), 12); E.fx("pop", w("bersih", 55.2) + .1, .4)
paper_out("#pb", o(55.55))

# ---------------- e3: WAJIB PAKAI
E.html.append('''      <div id="cj" class="card" style="top:980px; text-align:center">
        <div class="big" style="font-size:110px"><span class="wd y">WAJIB</span> <span class="wd">PAKAI!</span></div>
        <div style="font-weight:800; font-size:46px; margin-top:12px; opacity:0" id="cj-2">Supaya korang <span class="y">jaga tilam</span> korang</div>
        <svg width="120" height="140" viewBox="0 0 120 140" style="position:absolute; right:40px; top:-70px"><path id="shield" class="ink y thick" pathLength="1" d="M60 10 L105 28 C 105 80, 90 112, 60 130 C 30 112, 15 80, 15 28 Z M40 70 L56 86 L84 52"/></svg>
      </div>''')
card_in("#cj", w("Korang", 55.6) - .1); lift(w("Korang", 55.6) - .15, o(59.8))
pop("#cj .wd", w("wajib", 56.1), "impact-bass-1")
show("#cj-2", w("supaya", 57.4)); draw("#shield", w("jaga", 58.3), .5); E.fx("pop", w("jaga", 58.3) + .2, .4)
card_out("#cj", o(59.75))

# ---------------- montage labels + reveal
LBL = []
for i, (st_, du, l1, l2) in enumerate(mon_cuts):
    E.fx("whoosh-short", st_, .4)
    if not l1:
        continue
    lid = f"lb{i}"
    E.html.append(f'      <div id="{lid}" class="lbl big" style="top:1420px">{l1}{"<br><span class=y>" + l2 + "</span>" if l2 else ""}</div>')
    A(f'tl.fromTo("#{lid}", {{opacity:0, scale:1.5, filter:"blur(10px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.28, ease:"expo.out"}}, {r3(st_ + .1)});')
    A(f'tl.to("#{lid}", {{opacity:0, duration:.2}}, {r3(st_ + du - .2)});')
E.fx("riser", REVEAL)
E.html.append('''      <div id="rv" class="lbl big" style="top:1380px; font-size:190px"><span class="y">SIAP!</span></div>
      <svg id="rv-sp" width="1080" height="400" viewBox="0 0 1080 400" style="position:absolute;left:0;top:1300px">
        <path class="ink y thick" pathLength="1" d="M180 90 v60 M150 120 h60 M900 70 v70 M865 105 h70 M820 330 v40 M800 350 h40 M250 320 v40 M230 340 h40"/></svg>''')
A(f'tl.fromTo("#rv", {{opacity:0, scale:2.2}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(1.6)"}}, {REVEAL + .15});')
draw("#rv-sp path", REVEAL + .4, .4)
E.fx("impact-bass-1", REVEAL + .2, .5)
A(f'tl.to("#rv, #rv-sp", {{opacity:0, duration:.25}}, {T_ROOM - .25});')
E.html.append('''      <div id="rm" class="ov" style="left:60px; right:60px; top:1330px; text-align:center">
        <div class="big" style="font-size:62px"><span class="wd">Bilik</span> <span class="wd">terus</span> <span class="wd">nampak</span></div>
        <div class="big y" style="font-size:150px"><span class="wd">MEWAH</span></div>
        <div class="big" style="font-size:54px"><span class="wd">macam</span> <span class="wd">hotel</span></div>
      </div>''')
E.fx("whoosh", T_ROOM, .4)
A(f'tl.set("#rm", {{opacity:1}}, {T_ROOM});'); words_in("#rm .wd", T_ROOM + .2, .12)
E.fx("pop", T_ROOM + .6, .4)
A(f'tl.to("#rm", {{opacity:0, duration:.25}}, {T_CTA - .25});')

# ---------------- CTA
E.html.append('''      <div id="cta" class="card" style="top:880px; text-align:center; padding:40px 40px 46px">
        <div class="eyebrow">Set Alooma Premium</div>
        <div class="big" style="font-size:70px; margin-top:10px">Nak bilik cantik<br>macam ni?</div>
        <div id="cta-btn" style="opacity:0; display:inline-flex; align-items:center; gap:22px; margin-top:28px; padding:26px 46px; border-radius:999px;
             background:#FFC928; color:#0C1226; font-family:'Archivo Black'; font-size:50px; white-space:nowrap; box-shadow:0 10px 0 #C99A00">
          <svg width="74" height="70" viewBox="0 0 74 70"><path d="M6 22 H68 L60 64 H14 Z" fill="#0C1226"/><path d="M22 24 C 22 2, 52 2, 52 24" fill="none" stroke="#0C1226" stroke-width="7"/></svg>
          TEKAN BEG KUNING</div>
        <div id="cta-2" style="opacity:0; font-weight:800; font-size:40px; margin-top:26px">Komen <span class="y">1 hingga 5</span>, korang rasa cantik tak?</div>
      </div>''')
card_in("#cta", T_CTA + .1); lift(T_CTA, TOTAL)
pop("#cta-btn", T_CTA + .7)
A(f'tl.to("#cta-btn", {{scale:.93, duration:.09, yoyo:true, repeat:1}}, {T_CTA + 1.6});'); E.fx("click-soft", T_CTA + 1.6)
A(f'tl.to("#cta-btn", {{scale:1.06, duration:.35, yoyo:true, repeat:5, ease:"sine.inOut"}}, {T_CTA + 2.0});')
show("#cta-2", T_CTA + 2.3); E.fx("notification", T_CTA + 2.3, .35)
A(f'tl.to("#root", {{opacity:0, duration:.4}}, {round(TOTAL - .4, 3)});')

# ---------------- music bed: low under the voice, up for the montage, out at the end
E.music = [(0, .16), (T_MON - .4, .16), (T_MON + .2, .62), (TOTAL - 1.6, .62), (TOTAL, 0)]
E.music_file = "assets/music/inspiration.mp3"
write_project(E, os.path.join(ROOT, "v1"), round(TOTAL, 3))
import json
p = json.load(open(os.path.join(ROOT, "v1/edit-plan.json"))); p["music_file"] = E.music_file
json.dump(p, open(os.path.join(ROOT, "v1/edit-plan.json"), "w"), indent=1)
