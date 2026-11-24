"""VIDEO 2 - style of the user's reference clip: persistent dark top pill, giant neon-lime keyword with a 3D
carousel of product cards, blur-to-neon transition, clean light canvas scenes (dot grid, soft blobs, glass cards,
section badge, two-tone captions with a blue keyword, equation tiles), floating glass tags, glass end card + CTA pill.
Run: python3 tools/gen2.py  -> v2/index.html + v2/edit-plan.json"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Edit, write_project, ROOT, WORDS

E = Edit()
M = "assets/footage/main.mp4"
h = E.say("h", 0.20, 3.81)        # "Guys, mari sini... Tengoklah ini."
b = E.say("b", 3.81, 18.77)       # items + "Jenama? Alooma."
br = E.say("br", 18.77, 22.86)    # "korang boleh tahulah ini adalah brand? Alooma lah guys."
wp = E.say("w", 40.97, 49.65)     # waterproof / non-waterproof -> ambil waterproof
tt = E.say("t", 49.65, 55.64)     # 2-3 bulan masih cantik, bersih
m = E.say("m", 55.64, 65.83)      # wajib pakai... tilam mahal... tompok-tompok peta dunia
g = E.say("g", 65.83, 69.33)      # pasang lapik cadar ni kat tilam. Let's go.
T_MON = E.hold(8.0)
T_DONE = E.hold(3.4)
T_END = E.hold(5.6)
TOTAL = round(E.t, 3)
o, w = E.o, E.w
A = E.add

# ---------------- picture
E.synced(h); E.synced(b)
s_br = E.synced(br)
E.synced(wp); E.synced(tt)
E.synced(m, a=55.64, b=58.0)
T_OLD = o(58.0)
E.shot(T_OLD, g["out"] - T_OLD, "assets/img/oldmattress-bg.jpg", kind="img", style="filter:blur(34px) brightness(.55); transform:scale(1.2)")
E.shot(g["out"], g["dur"], M, 69.45)
MON = [(72.1, 1.6, "pasang cadar"), (76.7, 1.6, "kemas &amp; muat"), (81.55, 1.6, "comforter"),
       (87.25, 1.6, "sarung bantal"), (92.15, 1.6, "siap bantal")]
t = T_MON; mon = []
for ms, du, lab in MON:
    E.shot(t, du, M, ms); mon.append((t, du, lab)); t += du
E.shot(T_DONE, T_END - T_DONE, M, 103.6)
E.shot(T_END, TOTAL - T_END, "assets/footage/20261029_232831.mp4", 0.0, style="filter:blur(30px) brightness(.7); transform:scale(1.15)")

# ---------------- camera (lighter than video 1, still zooming in/out a lot)
for i, ct in enumerate(E.cuts()):
    E.zoom.append((ct, "set", *[(1.0, 0), (1.07, 10), (1.03, -8), (1.1, 0)][i % 4]))
PUNCH = [w("Alooma", 4.8), w("Alooma", 11.0), w("Alooma", 17.75), w("wajib", 56.1), w("go.", 68.8)]
LV = [(1.12, 0), (1.0, 0), (1.16, -16), (1.05, 14), (1.14, 12), (1.0, 0)]
cuts = E.cuts(); last, k = -9, 0
for n in range(1, len(WORDS)):
    if WORDS[n - 1]["text"].strip()[-1:] not in ".?!,":
        continue
    try: t_ = E.o(WORDS[n]["start"])
    except ValueError: continue
    prev = max([c for c in cuts if c <= t_] or [0]); nxt = min([c for c in cuts if c > t_] or [TOTAL])
    if t_ - prev < .8 or nxt - t_ < .9 or t_ - last < 2.2 or any(abs(t_ - p) < 1.2 for p in PUNCH) or t_ > T_MON:
        continue
    E.zoom.append((t_, "ease", *LV[k % len(LV)])); k += 1; last = t_
for p in PUNCH:
    E.zoom.append((round(p - .05, 3), "punch", 1.24, 0)); E.fx("whoosh-short", p, .35)
for st_, du, _ in mon:
    E.zoom.append((st_ + .02, "slow", 1.14, 0))
E.zoom.append((g["out"] + .02, "slow", 1.12, 0)); E.zoom.append((T_DONE + .02, "slow", 1.12, 0))
E.zoom.append((T_OLD + .02, "slow", 1.1, 0))

# ---------------- look
LIME, BLUE, RED, INK = "#C8FF2E", "#2347FF", "#E5383B", "#12131A"
E.css.append(f"""
  body, .jk {{ font-family:'Plus Jakarta Sans', sans-serif; }}
  .wd {{ display:inline-block; opacity:0; }}
  #pill {{ position:absolute; left:0; right:0; margin:0 auto; width:fit-content; top:64px; padding:14px 34px 16px; border-radius:26px;
          background:rgba(40,40,44,.72); backdrop-filter:blur(14px); color:#fff; text-align:center; opacity:0; z-index:50;
          box-shadow:0 8px 26px rgba(0,0,0,.25); font-family:'Plus Jakarta Sans'; white-space:nowrap; }}
  #pill .s {{ font-size:24px; font-weight:600; opacity:.8; }} #pill .b {{ font-size:40px; font-weight:800; letter-spacing:.01em; }}
  .neon {{ font-family:'Plus Jakarta Sans'; font-weight:800; color:{LIME}; letter-spacing:-.03em; line-height:.9;
          text-shadow:0 0 22px rgba(200,255,46,.85), 0 0 60px rgba(200,255,46,.55), 0 0 120px rgba(200,255,46,.35); }}
  .wt {{ font-family:'Plus Jakarta Sans'; font-weight:800; color:#fff; line-height:1; text-shadow:0 4px 22px rgba(0,0,0,.45); }}
  .spill {{ position:absolute; left:0; right:0; margin:0 auto; width:fit-content; padding:12px 26px; border-radius:999px; background:#fff; color:{INK};
           font-weight:700; font-size:34px; white-space:nowrap; box-shadow:0 8px 22px rgba(0,0,0,.25); opacity:0; }}
  .spill b {{ color:{BLUE}; font-weight:800; }}
  .glass {{ position:absolute; background:rgba(255,255,255,.62); border:2px solid rgba(255,255,255,.85); border-radius:34px;
           box-shadow:0 24px 60px rgba(40,50,90,.18); backdrop-filter:blur(16px); opacity:0; }}
  .dglass {{ position:absolute; background:rgba(255,255,255,.16); border:2px solid rgba(255,255,255,.4); border-radius:999px;
            backdrop-filter:blur(12px); color:#fff; font-weight:800; padding:14px 30px; font-size:38px; opacity:0; white-space:nowrap;
            box-shadow:0 10px 30px rgba(0,0,0,.25); }}
  .canvas {{ position:absolute; inset:0; opacity:0; overflow:hidden; background:#F3F3F0; }}
  .canvas::before {{ content:""; position:absolute; inset:0;
     background:radial-gradient(circle at 22% 38%, rgba(165,180,255,.55), rgba(165,180,255,0) 34%),
                radial-gradient(circle at 80% 78%, rgba(214,255,120,.6), rgba(214,255,120,0) 32%); }}
  .canvas::after {{ content:""; position:absolute; inset:0; opacity:.55;
     background-image:radial-gradient(rgba(30,30,40,.22) 1.6px, transparent 1.8px); background-size:26px 26px; }}
  .badge {{ position:absolute; left:64px; top:230px; display:flex; align-items:center; gap:18px; z-index:2; font-weight:700;
           font-size:34px; color:{INK}; }}
  .badge i {{ font-style:normal; width:56px; height:56px; border-radius:16px; background:#fff; color:{BLUE}; display:grid; place-items:center;
             font-weight:800; font-size:34px; box-shadow:0 6px 18px rgba(40,50,90,.15); }}
  .cap {{ position:absolute; left:0; right:0; text-align:center; font-weight:800; font-size:66px; color:{INK}; line-height:1.08; z-index:3; }}
  .cap b {{ color:{BLUE}; }} .cap .rd {{ color:{RED}; }}
  .tile {{ position:absolute; width:190px; height:190px; border-radius:40px; background:#fff; display:grid; place-items:center; z-index:2;
          box-shadow:0 14px 40px rgba(40,50,90,.18); font-weight:800; font-size:44px; color:{BLUE}; opacity:0; text-align:center; line-height:1.05; }}
  .op {{ position:absolute; font-weight:800; font-size:70px; color:{INK}; opacity:0; z-index:2; }}
  .ok {{ position:absolute; padding:10px 22px; border-radius:999px; background:{LIME}; color:{INK}; font-weight:800; font-size:30px; opacity:0;
        box-shadow:0 6px 18px rgba(120,160,0,.35); white-space:nowrap; z-index:4; }}
  .rtag {{ position:absolute; padding:16px 30px; border-radius:999px; background:rgba(229,56,59,.88); color:#fff; font-weight:800; font-size:40px;
          opacity:0; white-space:nowrap; box-shadow:0 10px 30px rgba(0,0,0,.35); border:2px solid rgba(255,255,255,.5); }}
""")


def r3(x): return round(max(x, 0), 3)
def fade(sel, t, v=1, d=.3): A(f'tl.to("{sel}", {{opacity:{v}, duration:{d}}}, {r3(t)});')
def rise(sel, t, d=.45, y=40, sfx="pop", st=0):
    A(f'tl.fromTo("{sel}", {{opacity:0, y:{y}, scale:.92, filter:"blur(10px)"}}, {{opacity:1, y:0, scale:1, filter:"blur(0px)", duration:{d}, ease:"expo.out", stagger:{st}}}, {r3(t)});')
    if sfx: E.fx(sfx, t + .08, .45)
def pill_in(sel, t, sfx="pop"):
    A(f'tl.fromTo("{sel}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.32, ease:"back.out(1.8)"}}, {r3(t)});')
    if sfx: E.fx(sfx, t + .08, .4)
def out(sel, t, d=.22): A(f'tl.to("{sel}", {{opacity:0, filter:"blur(8px)", duration:{d}, ease:"power2.in"}}, {r3(t)});')
def words(sel, t, st=.08):
    A(f'tl.fromTo("{sel}", {{opacity:0, y:24, filter:"blur(8px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:.22, ease:"power4.out", stagger:{st}}}, {r3(t)});')
for x in ["#pill .s", "#pill .b"]:
    pass

# ---------------- persistent top pill
E.html.append('''      <div id="pill"><div class="s">Nak bilik cantik macam hotel?</div><div class="b">1 SET ALOOMA</div></div>''')

# ---------------- HOOK: giant "6 ITEM / 1 SET SAHAJA" + rotating carousel of product cards
IMGS = ["lapik", "comforter", "lapikbantal", "pillow", "tuala", "pinkpack", "bed", "clean"]
cards = "".join(
    f'<div class="cc" style="transform:rotateY({i * 360 / len(IMGS)}deg) translateZ(420px)"><img src="assets/img/{n}.jpg"/></div>'
    for i, n in enumerate(IMGS))
E.css.append("""
  #hk-num { position:absolute; left:84px; top:250px; font-size:300px; opacity:1; }
  #hk-r { position:absolute; left:300px; top:300px; opacity:1; }
  #hk-r .wt { font-size:92px; }
  #car-wrap { position:absolute; left:0; right:0; top:1150px; height:640px; perspective:1500px; opacity:0; }
  #car { position:absolute; left:50%; top:40px; width:0; height:0; transform-style:preserve-3d; }
  .cc { position:absolute; left:-140px; top:0; width:280px; height:420px; border-radius:34px; overflow:hidden; backface-visibility:hidden;
        box-shadow:0 20px 50px rgba(0,0,0,.45); border:4px solid rgba(255,255,255,.9); background:#fff; }
  .cc img { width:100%; height:100%; object-fit:cover; }
""")
E.html.append(f'''      <div id="hk-num" class="neon">6</div>
      <div id="hk-r"><div class="wt" id="hk-r1">ITEM</div><div class="wt" id="hk-r2">1 SET <span style="color:{LIME}">SAHAJA</span></div></div>
      <div id="car-wrap"><div id="car">{cards}</div></div>
      <div id="hk-sp" class="spill" style="top:1060px">guys, <b>tengok ni!</b></div>''')
A('tl.set("#car-wrap", {opacity:1}, 0);')
A(f'tl.fromTo("#car", {{rotationY:0}}, {{rotationY:-200, duration:{h["dur"] + .2}, ease:"power1.inOut"}}, 0);')
A('tl.from("#hk-num", {scale:.3, opacity:0, duration:.5, ease:"back.out(1.6)", immediateRender:false}, 0.0);')
A('tl.from("#hk-r1, #hk-r2", {x:60, opacity:0, duration:.4, stagger:.12, ease:"expo.out", immediateRender:false}, 0.15);')
E.fx("impact-bass-1", .05, .5); E.fx("whoosh", .2, .4)
pill_in("#hk-sp", w("Tengoklah", 2.7))
# collapse the big title into the top pill (as in the reference)
A(f'tl.to("#hk-num, #hk-r", {{scale:.25, x:200, y:-260, opacity:0, duration:.4, ease:"power3.in", transformOrigin:"50% 0%"}}, {h["dur"] - .3});')
A(f'tl.to("#car-wrap", {{opacity:0, y:200, duration:.35, ease:"power2.in"}}, {h["dur"] - .3});')
out("#hk-sp", h["dur"] - .25)
A(f'tl.fromTo("#pill", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(1.6)"}}, {h["dur"] - .05});')
E.fx("whoosh-short", h["dur"] - .1, .4)

# ---------------- b: item names, "jenama? ALOOMA" pill
ITEMS = [("LAPIK TILAM", 3.85), ("COMFORTER", 5.52), ("LAPIK BANTAL", 8.16), ("BANTAL", 11.70), ("TUALA", 14.54)]
for i, (n, s_) in enumerate(ITEMS):
    E.html.append(f'      <div id="it{i}" class="wt" style="position:absolute; left:0; right:0; top:1300px; text-align:center; font-size:96px; opacity:0">{n}</div>')
    t0 = o(s_); t1 = o(ITEMS[i + 1][1]) if i + 1 < len(ITEMS) else o(16.9)
    A(f'tl.fromTo("#it{i}", {{opacity:0, scale:1.25, filter:"blur(12px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.3, ease:"expo.out"}}, {t0});')
    E.fx("pop", t0 + .08, .4)
    out(f"#it{i}", t1 - .12, .15)
E.html.append('      <div id="it2b" class="spill" style="top:1420px"><b>waterproof</b> &#10003;</div>')
pill_in("#it2b", w("waterproof", 9.9)); out("#it2b", o(11.6))
E.html.append(f'      <div id="al" class="spill" style="top:1440px">jenama? <b>ALOOMA</b> &#10003;</div>')
for j, s_ in enumerate((4.78, 7.47, 13.85, 17.75)):
    t_ = w("Alooma", s_)
    ir = "" if j == 0 else ", immediateRender:false"
    A(f'tl.fromTo("#al", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"{ir}}}, {t_});')
    A(f'tl.to("#al", {{opacity:0, duration:.15}}, {round(min(t_ + .9, o(18.7)), 3)});')
    E.fx("notification", t_ + .05, .3)
E.html.append(f'      <div id="tuala2" class="spill" style="top:1420px">yang saya <b>pakai semalam</b> &#128516;</div>'.replace(" &#128516;", ""))
pill_in("#tuala2", w("semalam", 16.2)); out("#tuala2", w("Alooma", 17.75) - .1)

# ---------------- br: blur -> giant neon ALOOMA
A(f'tl.fromTo("#{s_br}", {{filter:"blur(0px) brightness(1)"}}, {{filter:"blur(36px) brightness(.7)", duration:.45, ease:"power2.out"}}, {br["out"]});')
E.fx("whoosh", br["out"], .45)
E.html.append(f'''      <div id="br-s" class="wt" style="position:absolute; left:0; right:0; top:760px; text-align:center; font-size:40px; font-weight:600; opacity:0">brand dia dipanggil</div>
      <div id="br-n" class="neon" style="position:absolute; left:0; right:0; top:840px; text-align:center; font-size:210px; opacity:0">ALOOMA</div>
      <div id="br-chips" style="position:absolute; left:0; right:0; top:1110px; text-align:center">
        <span class="dglass" style="position:relative; margin:0 8px" id="bc1">lapik</span><span class="dglass" style="position:relative; margin:0 8px" id="bc2">cadar</span><span class="dglass" style="position:relative; margin:0 8px" id="bc3">comforter</span></div>''')
fade("#br-s", br["out"] + .3)
A(f'tl.fromTo("#br-n", {{opacity:0, scale:.6, filter:"blur(20px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.5, ease:"expo.out"}}, {w("Alooma", 21.8, "br")});')
E.fx("impact-bass-1", w("Alooma", 21.8, "br"), .5)
for i in range(3):
    A(f'tl.fromTo("#bc{i+1}", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3, ease:"back.out(1.6)"}}, {r3(w("Alooma", 21.8, "br") + .35 + i * .15)});')
E.fx("pop", w("Alooma", 21.8, "br") + .4, .35)

# ---------------- canvas W: waterproof vs non-waterproof
E.html.append(f'''      <div id="cw" class="canvas">
        <div class="badge"><i>W</i>Waterproof</div>
        <div id="wc1" class="glass" style="left:70px; top:480px; width:450px; height:640px; z-index:2">
          <img src="assets/img/lapik.jpg" style="position:absolute; left:20px; top:20px; width:406px; height:420px; object-fit:cover; border-radius:22px"/>
          <svg width="70" height="90" viewBox="0 0 70 90" style="position:absolute; left:30px; top:470px"><path d="M35 6 C 20 32, 8 48, 8 62 a27 27 0 0 0 54 0 C 62 48, 50 32, 35 6 Z" fill="{BLUE}"/></svg>
          <div style="position:absolute; left:110px; top:478px; font-weight:800; font-size:44px; color:{INK}">Waterproof</div>
          <div style="position:absolute; left:110px; top:536px; font-weight:600; font-size:28px; color:#667">kalis air, tilam selamat</div>
        </div>
        <div id="wc2" class="glass" style="left:560px; top:480px; width:450px; height:640px; z-index:2">
          <img src="assets/img/lapik.jpg" style="position:absolute; left:20px; top:20px; width:406px; height:420px; object-fit:cover; border-radius:22px; filter:grayscale(1) brightness(1.05)"/>
          <svg width="70" height="90" viewBox="0 0 70 90" style="position:absolute; left:30px; top:470px"><path d="M35 6 C 20 32, 8 48, 8 62 a27 27 0 0 0 54 0 C 62 48, 50 32, 35 6 Z" fill="none" stroke="#99A" stroke-width="6"/><path d="M6 84 L64 10" stroke="{RED}" stroke-width="7"/></svg>
          <div style="position:absolute; left:110px; top:478px; font-weight:800; font-size:40px; color:{INK}">Non-waterproof</div>
          <div style="position:absolute; left:110px; top:536px; font-weight:600; font-size:28px; color:#667">biasa</div>
        </div>
        <div id="wok" class="ok" style="left:300px; top:500px">&#10003; cadangan</div>
        <div id="wcap1" class="cap" style="top:1290px">Alooma ada <b>DUA</b> jenis</div>
        <div id="wcap2" class="cap" style="top:1290px; opacity:0">ambil yang<br><b>WATERPROOF</b></div>
      </div>''')
T_W = wp["out"]
A(f'tl.fromTo("#cw", {{opacity:0}}, {{opacity:1, duration:.3}}, {T_W - .1});'); E.fx("whoosh", T_W - .05, .45)
A(f'tl.to("#br-s, #br-n, #br-chips", {{opacity:0, duration:.2}}, {T_W});')
A(f'tl.from("#cw .badge", {{x:-40, opacity:0, duration:.35, ease:"expo.out", immediateRender:false}}, {T_W + .15});')
rise("#wcap1", T_W + .3, sfx=None)
A(f'tl.set("#wcap1", {{opacity:0}}, {T_W});')
rise("#wc1", w("waterproof", 43.9) - .1); rise("#wc2", w("non-waterproof", 44.9) - .1)
out("#wcap1", w("Cadangan", 46.0) - .1)
words("#wcap2", w("waterproof", 48.7) - .4)
A(f'tl.to("#wc2", {{opacity:.35, scale:.94, duration:.35}}, {w("waterproof", 48.7)});')
A(f'tl.to("#wc1", {{scale:1.06, duration:.35, ease:"back.out(2)"}}, {w("waterproof", 48.7)});')
A(f'tl.fromTo("#wok", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {w("waterproof", 48.7) + .15});')
E.fx("notification", w("waterproof", 48.7) + .2, .4)

# ---------------- canvas T: Lapik + 2-3 bulan = clean
E.html.append(f'''      <div id="ct" class="canvas">
        <div class="badge"><i>B</i>Bukti</div>
        <div id="t1" class="tile" style="left:90px; top:470px">Lapik</div>
        <div id="op1" class="op" style="left:310px; top:520px">+</div>
        <div id="t2" class="tile" style="left:380px; top:470px; font-size:40px">2&ndash;3<br>bulan</div>
        <div id="op2" class="op" style="left:600px; top:520px">=</div>
        <div id="t3" class="tile" style="left:680px; top:470px; background:{BLUE}; color:#fff; font-size:90px">&#10003;</div>
        <div id="tc" class="glass" style="left:240px; top:730px; width:600px; height:520px; padding:20px">
          <img src="assets/img/clean.jpg" style="width:560px; height:480px; object-fit:cover; border-radius:24px"/></div>
        <div id="tok" class="ok" style="left:610px; top:705px">&#10003; masih bersih</div>
        <div id="tcap" class="cap" style="top:1330px">tilam masih <b>CANTIK</b><br>&amp; masih <b>BERSIH</b></div>
      </div>''')
T_T = tt["out"]
A(f'tl.fromTo("#ct", {{opacity:0}}, {{opacity:1, duration:.3}}, {T_T - .1});'); E.fx("whoosh-short", T_T - .05, .4)
A(f'tl.to("#cw", {{opacity:0, duration:.2}}, {T_T + .2});')
rise("#t1", w("selepas", 50.2)); fade("#op1", w("pakai", 51.3), d=.2)
rise("#t2", w("2-3", 52.0)); fade("#op2", w("bulan", 52.6), d=.2)
A(f'tl.fromTo("#t3", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)"}}, {w("tilam", 53.2)});')
E.fx("pop", w("tilam", 53.2) + .1, .5)
rise("#tc", w("cantik", 54.1) - .3, sfx="whoosh-short")
A(f'tl.set("#tcap", {{opacity:0}}, 0);')
rise("#tcap", w("cantik", 54.1), sfx=None)
A(f'tl.fromTo("#tok", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {w("bersih", 55.2)});')
E.fx("notification", w("bersih", 55.2) + .05, .4)
A(f'tl.to("#ct", {{opacity:0, duration:.25}}, {m["out"] - .05});'); E.fx("whoosh-short", m["out"] - .05, .4)

# ---------------- m: WAJIB PAKAI, then old mattress card with red tags
E.html.append(f'''      <div id="wj" class="wt" style="position:absolute; left:0; right:0; top:1280px; text-align:center; font-size:110px; opacity:0">WAJIB <span style="color:{LIME}">PAKAI</span></div>
      <div id="wj2" class="spill" style="top:1430px">supaya korang <b>jaga tilam</b></div>
      <div id="oc" class="glass" style="left:150px; top:330px; width:780px; height:870px; padding:22px; background:rgba(255,255,255,.22); border-color:rgba(255,255,255,.55)">
        <img src="assets/img/oldmattress.jpg" style="width:736px; height:826px; object-fit:cover; border-radius:26px"/></div>
      <div id="ocap" class="wt" style="position:absolute; left:0; right:0; top:1300px; text-align:center; font-size:72px; opacity:0">tilam beli <span style="color:#FF5A5F">MAHAL</span>&hellip;</div>
      <div id="rt1" class="rtag" style="left:70px; top:520px">&#10007; tompok</div>
      <div id="rt2" class="rtag" style="left:700px; top:760px">&#10007; kotor</div>
      <div id="rt3" class="rtag" style="left:110px; top:1050px">&#10007; peta dunia</div>''')
A(f'tl.fromTo("#wj", {{opacity:0, scale:1.4, filter:"blur(12px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.3, ease:"expo.out"}}, {w("wajib", 56.1) - .05});')
E.fx("impact-bass-1", w("wajib", 56.1), .4)
pill_in("#wj2", w("supaya", 57.4))
out("#wj, #wj2", T_OLD - .15)
rise("#oc", T_OLD + .05, y=80, sfx="whoosh")
words("#ocap", w("mahal", 61.8) - .15)
rise("#rt1", w("tompok", 63.8), sfx="error"); rise("#rt2", w("tompok", 63.8) + .45, sfx=None)
rise("#rt3", w("dunia", 65.5) - .1, sfx="error")
A(f'tl.to("#oc", {{x:"+=10", duration:.05, yoyo:true, repeat:5}}, {w("dunia", 65.5)});')
A(f'tl.to("#oc, #ocap, #rt1, #rt2, #rt3", {{opacity:0, scale:.9, duration:.25, ease:"power2.in"}}, {g["out"] - .2});')

# ---------------- g + montage
E.fx("whoosh", g["out"], .45)
E.html.append(f'''      <div id="gp" style="position:absolute; left:0; right:0; top:1250px; text-align:center">
        <div class="wt" style="font-size:60px"><span class="wd">pasang</span></div>
        <div class="wt" style="font-size:104px; color:{LIME}"><span class="wd">LAPIK</span> <span class="wd">+</span> <span class="wd">CADAR</span></div></div>
      <div id="go" class="neon" style="position:absolute; left:0; right:0; top:820px; text-align:center; font-size:170px; opacity:0">LET'S GO!</div>''')
words("#gp .wd", w("pasang", 65.9) + .05, .12)
A(f'tl.to("#gp", {{opacity:0, duration:.2}}, {w("go.", 68.8) - .45});')
A(f'tl.fromTo("#go", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {w("go.", 68.8) - .35});')
E.fx("impact-bass-1", w("go.", 68.8) - .3, .45)
out("#go", T_MON - .15)
for i, (st_, du, lab) in enumerate(mon):
    E.html.append(f'      <div id="ml{i}" class="spill" style="top:1450px; font-size:44px">{lab}</div>')
    pill_in(f"#ml{i}", st_ + .12, sfx=None); out(f"#ml{i}", st_ + du - .15, .12)
    E.fx("whoosh-short", st_, .4)
E.fx("riser", T_DONE)
E.html.append(f'''      <div id="sp" class="neon" style="position:absolute; left:0; right:0; top:1180px; text-align:center; font-size:220px; opacity:0">SIAP!</div>
      <div id="tg1" class="dglass" style="left:90px; top:520px">LEMBUT +</div>
      <div id="tg2" class="dglass" style="left:650px; top:690px">CANTIK +</div>
      <div id="tg3" class="dglass" style="left:180px; top:860px">PREMIUM +</div>''')
A(f'tl.fromTo("#sp", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(1.6)"}}, {T_DONE + .1});')
E.fx("impact-bass-1", T_DONE + .12, .5)
for i in range(3):
    rise(f"#tg{i+1}", T_DONE + .6 + i * .45, sfx="pop")
    A(f'tl.to("#tg{i+1}", {{y:-18, duration:1.4, yoyo:true, repeat:1, ease:"sine.inOut"}}, {r3(T_DONE + 1.1 + i * .45)});')
A(f'tl.to("#sp, #tg1, #tg2, #tg3", {{opacity:0, duration:.25}}, {T_END - .2});')

# ---------------- end card + CTA
E.html.append(f'''      <div id="ec" class="glass" style="left:170px; top:300px; width:740px; height:870px; padding:22px; background:rgba(255,255,255,.85)">
        <img src="assets/img/bed.jpg" style="width:696px; height:640px; object-fit:cover; border-radius:24px"/>
        <div style="font-weight:800; font-size:58px; color:{INK}; margin-top:22px; text-align:center">Set <span style="color:#FF5C9A">Alooma</span> Premium</div>
        <div style="font-weight:600; font-size:30px; color:#556; margin-top:10px; text-align:center">Lapik &bull; Cadar &bull; Comforter &bull; Bantal &bull; Tuala</div>
      </div>
      <div id="ebtn" style="position:absolute; left:0; right:0; margin:0 auto; width:fit-content; top:1330px; padding:30px 56px; border-radius:999px; background:{BLUE};
           color:#fff; font-weight:800; font-size:48px; white-space:nowrap; box-shadow:0 0 0 6px rgba(35,71,255,.25), 0 16px 40px rgba(35,71,255,.55); opacity:0">TEKAN BEG KUNING SEKARANG</div>
      <div id="esub" class="wt" style="position:absolute; left:0; right:0; top:1470px; text-align:center; font-size:36px; font-weight:600; opacity:0">klik beg kuning &darr;</div>
      <div id="ecom" class="spill" style="top:1560px">komen <b>1 hingga 5</b>, korang rasa?</div>''')
rise("#ec", T_END + .1, y=90, sfx="whoosh")
pill_in("#ebtn", T_END + .8)
A(f'tl.to("#ebtn", {{scale:.93, duration:.09, yoyo:true, repeat:1}}, {T_END + 1.7});'); E.fx("click-soft", T_END + 1.7)
A(f'tl.to("#ebtn", {{scale:1.05, duration:.4, yoyo:true, repeat:4, ease:"sine.inOut"}}, {T_END + 2.0});')
fade("#esub", T_END + 1.2)
pill_in("#ecom", T_END + 2.4, sfx="notification")
A(f'tl.to("#root", {{opacity:0, duration:.4}}, {round(TOTAL - .4, 3)});')

E.music = [(0, .14), (T_MON - .4, .14), (T_MON + .2, .58), (TOTAL - 1.6, .58), (TOTAL, 0)]
write_project(E, os.path.join(ROOT, "v2"), TOTAL, card_lift=False, bg="#F3F3F0")
p = json.load(open(os.path.join(ROOT, "v2/edit-plan.json"))); p["music_file"] = "assets/music/be-chillin.mp3"
json.dump(p, open(os.path.join(ROOT, "v2/edit-plan.json"), "w"), indent=1)
