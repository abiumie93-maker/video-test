"""TikTok Shop awareness video in the style of the user's reference clip (df22d424...mp4):
warm moody talking head, gold condensed titles over the head, serif subtitles with an italic gold keyword,
full-screen cream canvas scenes (italic heavy headings with a gold highlight bar, phone mockups playing the user's
screen recordings, white / orange flow cards, stamps, chart), a "WHICH DO YOU PREFER?"-style poll bar and a
search-bar end card.  Run: python3 tools/gen_ref.py -> v1/index.html"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Edit, write_project, ROOT, WORDS, H

E = Edit()
FT = "assets/footage/"
a = E.say("a", 0.00, 52.02, clip="main")     # hook ... "tahun terakhir kita rasa seronok"
b = E.say("b", 55.52, 114.28, clip="main")   # (cut repeat "dan sekarang ni pun kita dah start rasa dah") ... "Korang rasa macam mana?"
T_END = E.hold(3.0)
TOTAL = round(E.t, 3)
o = E.o
def w(text, near): return E.w(text, near, "a" if near < 51.9 else "b")
A = E.add
def r3(x): return round(max(x, 0), 3)

E.synced(a); E.synced(b)
E.shot(T_END, TOTAL - T_END, FT + "main.mp4", 114.28, style="filter:blur(40px) brightness(.35)")

# ---------------- canvas windows (output seconds) -> subtitle colour + camera
CAN = {
    "c1": (w("yang", 10.6), w("Apps", 14.0)),
    "c2": (w("Apps", 14.0), w("tak", 21.5) - .05),
    "c3": (w("tak", 21.5) - .05, w("dan", 26.0)),
    "c4": (w("Seller-seller", 29.0) - .1, w("So", 36.0)),
    "c5": (o(55.38), w("So", 62.1)),
    "c6": (w("So", 62.1), w("So", 72.9)),
    "c7": (w("Yang", 87.0), w("So", 99.0)),
}

# ---------------- camera: subtle punch-ins on the talking parts
for i, c_ in enumerate(E.cuts()):
    E.zoom.append((c_, "set", 1.0, 0))
PUNCH = [w("parah", 4.7), w("Shop", 10.2), w("komision", 39.3), w("terakhir", 49.9), w("game", 78.5), w("membunuh", 104.9)]
LV = [(1.08, 0), (1.0, 0), (1.12, -10), (1.04, 8)]
cands, k, last = [], 0, -9
for n in range(1, len(WORDS)):
    if WORDS[n - 1]["text"].strip()[-1:] in ".?!,":
        for s in E.vo:
            if s["src_in"] <= WORDS[n]["start"] <= s["src_out"]:
                cands.append(round(s["out"] + WORDS[n]["start"] - s["src_in"], 3))
for tt in sorted(set(cands)):
    if tt - last < 2.5 or any(abs(tt - p) < 1.0 for p in PUNCH) or any(x - .3 < tt < y + .3 for x, y in CAN.values()):
        continue
    E.zoom.append((tt, "ease", *LV[k % len(LV)])); k += 1; last = tt
for p in PUNCH:
    E.zoom.append((round(p - .05, 3), "punch", 1.16, 0))

# ---------------- look
BR, GOLD, ORG = "#3A2414", "#F2B33D", "#E8922A"
E.css.append("""
  @font-face { font-family:'Anton'; src:url('assets/fonts/anton.woff2') format('woff2'); }
  @font-face { font-family:'Montserrat'; font-style:italic; font-weight:800; src:url('assets/fonts/montserrat-italic.woff2') format('woff2'); }
  @font-face { font-family:'Playfair Display'; font-weight:500; src:url('assets/fonts/playfair-display.woff2') format('woff2'); }
  @font-face { font-family:'Playfair Display'; font-style:italic; font-weight:500; src:url('assets/fonts/playfair-display-italic.woff2') format('woff2'); }
""")
E.css.append(f"""
  #s1, #s2 {{ filter: sepia(.22) saturate(.92) brightness(.86) contrast(1.06); }}
  #vig {{ position:absolute; inset:0; pointer-events:none; z-index:2;
          background:radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 45%, rgba(25,12,0,.55) 100%); }}
  .goldt {{ position:absolute; left:0; right:0; text-align:center; font-family:'Anton',sans-serif; text-transform:uppercase; line-height:.95;
           background:linear-gradient(180deg,#FFE9A8 0%,#F7C24A 45%,#C9861C 100%); -webkit-background-clip:text; background-clip:text; color:transparent;
           filter:drop-shadow(0 4px 18px rgba(0,0,0,.55)) drop-shadow(0 0 30px rgba(247,194,74,.35)); opacity:0; z-index:5; }}
  .script {{ position:absolute; left:0; right:0; text-align:center; font-family:'Caveat',cursive; font-weight:700; color:#FFE9B0; opacity:0; z-index:5;
            text-shadow:0 2px 10px rgba(0,0,0,.6); }}
  .canvas {{ position:absolute; inset:0; opacity:0; z-index:4; overflow:hidden;
            background:radial-gradient(ellipse at 50% 38%, #FBEFC9 0%, #F3DC9C 55%, #E6C276 100%); }}
  .canvas::after {{ content:""; position:absolute; inset:0; background:radial-gradient(circle at 20% 80%, rgba(255,255,255,.35), rgba(255,255,255,0) 40%); }}
  .hd {{ position:absolute; left:0; right:0; top:150px; text-align:center; font-family:'Montserrat',sans-serif; font-style:italic; font-weight:800;
        font-size:76px; line-height:1.02; color:{BR}; text-transform:uppercase; letter-spacing:-.01em; z-index:3; }}
  .hd .hl {{ display:inline-block; background:{GOLD}; padding:0 18px; margin-top:6px; box-shadow:0 6px 0 rgba(58,36,20,.12); }}
  .phone {{ position:absolute; width:440px; height:930px; border-radius:64px; background:#1B1410; padding:16px; z-index:3;
           box-shadow:0 40px 80px rgba(80,50,10,.35), inset 0 0 0 3px #3a2e26; }}
  .phone .scr {{ position:relative; width:100%; height:100%; border-radius:50px; overflow:hidden; background:#000; }}
  .phone .notch {{ position:absolute; left:50%; top:26px; width:120px; height:30px; margin-left:-60px; border-radius:20px; background:#1B1410; z-index:2; }}
  .wcard {{ position:absolute; display:flex; align-items:center; gap:22px; padding:26px 34px; border-radius:26px; background:#fff; z-index:3;
           box-shadow:0 16px 36px rgba(110,70,10,.22); font-family:'Anton'; font-size:54px; color:{BR}; opacity:0; }}
  .wcard.or {{ background:linear-gradient(180deg,#F5AE45,#E08A22); color:#fff; }}
  .wcard .ic {{ width:70px; height:70px; border-radius:18px; background:#FBEFD5; display:grid; place-items:center; font-size:40px; }}
  .wcard.or .ic {{ background:rgba(255,255,255,.25); }}
  .stamp2 {{ position:absolute; font-family:'Anton'; text-transform:uppercase; color:{ORG}; border:7px solid {ORG}; border-radius:14px; padding:10px 26px;
            background:rgba(255,248,230,.92); opacity:0; z-index:6; box-shadow:0 10px 24px rgba(110,70,10,.25); }}
  .arrow {{ position:absolute; font-family:'Anton'; color:{BR}; font-size:60px; z-index:3; opacity:0; }}
  .lbl2 {{ position:absolute; font-family:'Montserrat'; font-weight:800; font-size:30px; letter-spacing:.12em; color:{BR}; opacity:.6; z-index:3; text-transform:uppercase; }}
  .sub {{ position:absolute; left:80px; right:80px; top:1310px; text-align:center; font-family:'Playfair Display',serif; font-weight:500; font-size:54px;
         color:#fff; text-shadow:0 2px 14px rgba(0,0,0,.75); opacity:0; z-index:8; line-height:1.15; }}
  .sub i {{ font-family:'Playfair Display',serif; font-style:italic; color:#F7C24A; }}
  .sub.dk {{ color:{BR}; text-shadow:none; top:1600px; }} .sub.dk i {{ color:{ORG}; }}
  #poll {{ position:absolute; left:110px; right:110px; top:1430px; padding:30px 30px 34px; border-radius:30px; background:rgba(28,18,10,.82);
          border:2px solid rgba(247,194,74,.35); backdrop-filter:blur(10px); opacity:0; z-index:9; text-align:center; }}
  #poll .q {{ font-family:'Montserrat'; font-weight:800; font-size:40px; color:#fff; letter-spacing:.06em; }}
  #poll .opts {{ display:flex; gap:18px; margin-top:22px; }}
  #poll .op {{ flex:1; display:flex; align-items:center; gap:14px; padding:20px 22px; border-radius:18px; background:rgba(255,255,255,.1);
              font-family:'Montserrat'; font-weight:800; font-size:36px; color:#fff; text-align:left; line-height:1.05; }}
  #poll .op b {{ font-family:'Anton'; font-size:56px; color:{GOLD}; }}
""")
E.html.append('      <div id="vig"></div>')


def show_canvas(cid, a_, b_):
    A(f'tl.fromTo("#{cid}", {{opacity:0, scale:1.04}}, {{opacity:1, scale:1, duration:.35, ease:"power2.out"}}, {r3(a_ - .15)});')
    A(f'tl.to("#{cid}", {{opacity:0, duration:.25, ease:"power2.in"}}, {r3(b_ - .12)});')
    E.fx("whoosh", a_ - .1, .4)
def head_in(sel, t):
    A(f'tl.fromTo("{sel} .l1", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.35, ease:"expo.out"}}, {r3(t)});')
    A(f'tl.fromTo("{sel} .hl", {{opacity:0, scaleX:0, transformOrigin:"0% 50%"}}, {{opacity:1, scaleX:1, duration:.4, ease:"expo.out"}}, {r3(t + .25)});')
def rise(sel, t, sfx="pop", y=60, st=0):
    A(f'tl.fromTo("{sel}", {{opacity:0, y:{y}, scale:.94}}, {{opacity:1, y:0, scale:1, duration:.45, ease:"back.out(1.5)", stagger:{st}}}, {r3(t)});')
    if sfx: E.fx(sfx, t + .08, .45)
def stamp(sel, t, rot=-7, sfx="impact-bass-1"):
    A(f'tl.fromTo("{sel}", {{opacity:0, scale:2, rotation:{rot - 8}}}, {{opacity:1, scale:1, rotation:{rot}, duration:.3, ease:"back.out(2)"}}, {r3(t)});')
    if sfx: E.fx(sfx, t + .03, .4)
def gold(sel, t, d_out=None):
    A(f'tl.fromTo("{sel}", {{opacity:0, scale:1.5, filter:"blur(14px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.4, ease:"expo.out"}}, {r3(t)});')
    E.fx("impact-bass-1", t + .03, .4)
    if d_out: A(f'tl.to("{sel}", {{opacity:0, y:-20, duration:.25}}, {r3(d_out)});')
def phone(pid, left, top, clip, ms, a_, b_, rot=0):
    vid = f'{pid}-v'
    E.html_phone.append((pid, left, top, rot, vid, clip, ms, a_, b_))
    return vid
E.html_phone = []

# ---------------- HOOK: "Geng affiliate..." -> TAHUN DEPAN PARAH?!
E.html.append('''      <div id="hk-s" class="script" style="top:150px; font-size:64px">Geng-geng affiliate&hellip;</div>
      <div id="hk-g" class="goldt" style="top:215px; font-size:190px">TAHUN DEPAN<br>PARAH?!</div>''')
A('tl.set("#hk-s, #hk-g", {opacity:1}, 0);')            # thumbnail frame carries the hook
E.fx("impact-bass-1", .05, .45)
A(f'tl.fromTo("#hk-g", {{x:-10}}, {{x:10, duration:.05, yoyo:true, repeat:5}}, {w("parah", 4.7)});')
E.fx("impact-bass-1", w("parah", 4.7), .5)
A(f'tl.to("#hk-s, #hk-g", {{opacity:0, y:-30, duration:.3}}, {w("Sebab", 6.3) - .1});')

# ---------------- icon morph: TikTok -> TikTok Shop
E.html.append(f'''      <div id="ic1" style="position:absolute; left:300px; top:230px; width:170px; height:170px; border-radius:40px; background:#111; z-index:5; opacity:0;
           display:grid; place-items:center; box-shadow:0 14px 30px rgba(0,0,0,.4)">
        <svg width="80" height="90" viewBox="0 0 80 90"><path d="M20 10 L70 45 L20 80 Z" fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round"/></svg>
        <div style="position:absolute; top:186px; left:-40px; right:-40px; text-align:center; font-family:Montserrat; font-weight:700; font-size:28px; color:#fff; text-shadow:0 2px 8px rgba(0,0,0,.7)">TikTok app</div></div>
      <div id="ic2" style="position:absolute; left:600px; top:190px; width:250px; height:250px; border-radius:58px; z-index:5; opacity:0;
           background:linear-gradient(160deg,#FF5A7A,#E8174A); display:grid; place-items:center; box-shadow:0 0 0 6px rgba(255,255,255,.15), 0 20px 60px rgba(232,23,74,.55)">
        <svg width="140" height="140" viewBox="0 0 140 140"><path d="M22 46 H118 L108 126 H32 Z" fill="#fff"/><path d="M46 48 C 46 14, 94 14, 94 48" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round"/>
          <path d="M78 66 v34 a12 12 0 1 1 -10 -12 M78 66 c4 10 10 14 18 14" fill="none" stroke="#E8174A" stroke-width="9" stroke-linecap="round"/></svg>
        <div style="position:absolute; top:266px; left:-60px; right:-60px; text-align:center; font-family:Montserrat; font-weight:800; font-size:32px; color:#FFE9A8; text-shadow:0 2px 8px rgba(0,0,0,.7)">TikTok Shop app</div></div>''')
t_tt = w("TikTok", 7.2)
rise("#ic1", t_tt - .1, sfx="pop", y=30)
t_sh = w("Shop", 10.2) - .25
A(f'tl.fromTo("#ic2", {{opacity:0, scale:.3, rotation:-20}}, {{opacity:1, scale:1, rotation:0, duration:.5, ease:"back.out(1.8)"}}, {r3(t_sh)});')
A(f'tl.to("#ic1", {{opacity:.35, scale:.85, duration:.3}}, {r3(t_sh)});')
E.fx("impact-bass-1", t_sh + .1, .45)
A(f'tl.to("#ic1, #ic2", {{opacity:0, scale:.7, duration:.25, ease:"power2.in"}}, {r3(CAN["c1"][0] - .2)});')

# ---------------- C1: apps sendiri (Play Store screen recording)
c1a, c1b = CAN["c1"]
E.html.append('''      <div id="c1" class="canvas">
        <div class="hd"><span class="l1">TikTok Shop</span><br><span class="hl">dah ada apps sendiri</span></div>
        <div id="c1-st" class="stamp2" style="left:560px; top:1030px; font-size:62px; transform:rotate(-8deg)">BOLEH DOWNLOAD!</div>
        <!--PHONE:c1p-->
      </div>''')
show_canvas("c1", c1a, c1b); head_in("#c1", c1a)
phone("c1p", 320, 420, "svid_073404.mp4", 6.5, c1a, c1b, rot=-3)
stamp("#c1-st", w("download", 11.7))
# ---------------- C2: sebiji macam Shopee + search
c2a, c2b = CAN["c2"]
E.html.append('''      <div id="c2" class="canvas">
        <div class="hd"><span class="l1">Sebiji macam</span><br><span class="hl">Shopee</span></div>
        <div id="c2-sb" class="wcard" style="left:90px; top:420px; font-family:Montserrat; font-weight:700; font-size:38px; padding:20px 30px; border-radius:999px">
          <span style="font-size:40px">&#128269;</span><span id="c2-tx" style="display:inline-block; overflow:hidden; white-space:nowrap; width:0">cari barang apa je&hellip;</span></div>
        <div id="c2-ok" class="stamp2" style="left:600px; top:1000px; font-size:64px; transform:rotate(-6deg)">TERUS ADA!</div>
        <!--PHONE:c2p-->
      </div>''')
show_canvas("c2", c2a, c2b); head_in("#c2", c2a)
phone("c2p", 440, 540, "svid_073509.mp4", 20.0, c2a, c2b, rot=3)
rise("#c2-sb", w("search", 17.1) - .3, sfx="click-soft")
A(f'tl.to("#c2-tx", {{width:"420px", duration:.9, ease:"steps(20)"}}, {r3(w("search", 17.1))});')
stamp("#c2-ok", w("terus", 20.3))
# ---------------- C3: dulu vs sekarang
c3a, c3b = CAN["c3"]
E.html.append('''      <div id="c3" class="canvas">
        <div class="hd"><span class="l1">Tak perlu tengok</span><br><span class="hl">video dulu</span></div>
        <div class="lbl2" style="left:150px; top:470px">Dulu</div><div class="lbl2" style="left:610px; top:470px">Sekarang</div>
        <div id="d0" class="wcard" style="left:100px; top:530px; width:400px"><span class="ic">&#9654;</span>Video</div>
        <div id="d1" class="wcard" style="left:100px; top:690px; width:400px"><span class="ic">&#10024;</span>Tertarik</div>
        <div id="d2" class="wcard" style="left:100px; top:850px; width:400px"><span class="ic">&#128722;</span>Beli</div>
        <div id="n0" class="wcard or" style="left:580px; top:530px; width:400px"><span class="ic">&#128269;</span>Search</div>
        <div id="n1" class="wcard or" style="left:580px; top:690px; width:400px"><span class="ic">&#9878;</span>Banding</div>
        <div id="n2" class="wcard or" style="left:580px; top:850px; width:400px"><span class="ic">&#128722;</span>Beli</div>
        <div id="c3-st" class="stamp2" style="left:250px; top:1050px; font-size:60px; transform:rotate(-4deg)">TERUS CARI, TERUS BELI</div>
      </div>''')
show_canvas("c3", c3a, c3b); head_in("#c3", c3a)
rise("#d0, #d1, #d2", c3a + .3, st=.15)
A(f'tl.to("#d0, #d1, #d2", {{opacity:.45, duration:.3}}, {r3(w("beli", 24.9) - .9)});')
rise("#n0, #n1, #n2", w("beli", 24.9) - .9, st=.15)
stamp("#c3-st", w("beli", 24.9) - .1, rot=-4)
# ---------------- C4: video affiliate di page seller (profile screen recording)
c4a, c4b = CAN["c4"]
E.html.append('''      <div id="c4" class="canvas">
        <div class="hd" style="font-size:68px"><span class="l1">Video affiliate kita</span><br><span class="hl">di page seller?</span></div>
        <div id="c4-ar" class="arrow" style="left:520px; top:760px">&rarr;</div>
        <div id="c4-sp" class="wcard or" style="left:600px; top:700px; width:400px; flex-direction:column; gap:10px; text-align:center">
          <span class="ic" style="width:110px; height:110px; font-size:62px">&#127978;</span>Page<br>Seller</div>
        <!--PHONE:c4p-->
      </div>''')
show_canvas("c4", c4a, c4b); head_in("#c4", c4a)
phone("c4p", 70, 460, "svid_073827_slow.mp4", 0.0, c4a, c4b, rot=-4)
A(f'tl.fromTo("#c4-ar", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:.3}}, {r3(w("up", 32.2))});')
rise("#c4-sp", w("page", 34.8) - .3)
# ---------------- footage: KOMISEN? / TAHUN TERAKHIR?
E.html.append('''      <div id="g-km" class="goldt" style="top:170px; font-size:210px">KOMISEN?</div>
      <div id="km-c" class="wcard" style="left:120px; top:1060px; width:840px; flex-direction:column; align-items:flex-start; gap:6px; background:rgba(28,18,10,.82); color:#fff;
           font-family:Montserrat; font-weight:800; font-size:40px; border:2px solid rgba(247,194,74,.35)">
        <span style="font-size:28px; letter-spacing:.12em; color:#F7C24A">KOMISEN AFFILIATE DATANG DARI</span>
        <span>Video &amp; TikTok kita sendiri</span></div>
      <div id="g-tt" class="goldt" style="top:170px; font-size:190px">TAHUN<br>TERAKHIR?</div>''')
gold("#g-km", w("komision", 39.3) - .1, w("So", 47.9) - .3)
rise("#km-c", w("Sebab", 41.2), sfx="pop"); A(f'tl.to("#km-c", {{opacity:0, duration:.25}}, {r3(w("So", 47.9) - .3)});')
gold("#g-tt", w("terakhir", 49.9) - .1, o(51.6))
# ---------------- C5: sales drop
c5a, c5b = CAN["c5"]
E.html.append(f'''      <div id="c5" class="canvas">
        <div class="hd"><span class="l1">Perasan tak?</span><br><span class="hl">sales dah drop</span></div>
        <div class="wcard" id="c5-card" style="left:120px; top:470px; width:840px; height:620px; display:block; padding:30px">
          <div style="font-family:Montserrat; font-weight:800; font-size:30px; letter-spacing:.12em; color:{BR}; opacity:.6">SALES AFFILIATE</div>
          <svg width="780" height="520" viewBox="0 0 780 520" style="position:absolute; left:30px; top:80px">
            <path d="M20 480 H760 M20 480 V20" stroke="#D9C79E" stroke-width="4" fill="none"/>
            <path id="c5-ln" d="M40 400 C 140 360, 200 300, 300 240 C 380 190, 440 150, 520 170 C 600 190, 650 260, 740 330" stroke="{ORG}" stroke-width="12"
                  fill="none" stroke-linecap="round" pathLength="1" style="stroke-dasharray:1; stroke-dashoffset:1; opacity:0"/>
            <path id="c5-ar" d="M600 200 L 720 320 M720 320 l-50 -6 M720 320 l-6 -50" stroke="#D63A2F" stroke-width="12" fill="none" stroke-linecap="round"
                  pathLength="1" style="stroke-dasharray:1; stroke-dashoffset:1; opacity:0"/>
          </svg></div>
        <div id="c5-st" class="stamp2" style="left:560px; top:1010px; font-size:66px; color:#D63A2F; border-color:#D63A2F; transform:rotate(-7deg)">DROP SIKIT</div>
      </div>''')
show_canvas("c5", c5a, c5b); head_in("#c5", c5a)
rise("#c5-card", c5a + .2, sfx=None)
A(f'tl.to("#c5-ln", {{opacity:1, strokeDashoffset:0, duration:1.6, ease:"power1.inOut"}}, {r3(c5a + .5)});')
A(f'tl.to("#c5-ar", {{opacity:1, strokeDashoffset:0, duration:.4}}, {r3(w("drop", 60.6) - .1)});')
stamp("#c5-st", w("drop", 60.6) + .1, sfx="error")
# ---------------- C6: TikTok push download + vouchers
c6a, c6b = CAN["c6"]
vch = "".join(f'''<div id="v{i}" class="wcard or" style="left:{90 + i * 30}px; top:{470 + i * 175}px; width:560px; height:150px; padding:0 34px; border-radius:22px;
      transform:rotate({[-4, 2, -2][i]}deg); justify-content:space-between; border:4px dashed rgba(255,255,255,.55)">
      <span>VOUCHER</span><span style="font-size:42px">{t_}</span></div>''' for i, t_ in enumerate(["DISKAUN", "FREE SHIPPING", "CASHBACK"]))
E.html.append(f'''      <div id="c6" class="canvas">
        <div class="hd"><span class="l1">TikTok tengah push</span><br><span class="hl">download apps</span></div>
        {vch}
        <div id="c6-st" class="stamp2" style="left:600px; top:1010px; font-size:80px; transform:rotate(-8deg)">SENGAJA!</div>
        <!--PHONE:c6p-->
      </div>''')
show_canvas("c6", c6a, c6b); head_in("#c6", c6a)
phone("c6p", 640, 560, "svid_073509.mp4", 3.0, c6a, c6b, rot=5)
for i in range(3):
    rise(f"#v{i}", w("boucher", 67.5) + i * .35 - .2, sfx="pop")
stamp("#c6-st", w("sengaja", 70.9))
# ---------------- footage: NEXT YEAR? GAME PLAN?
E.html.append('''      <div id="g-ny" class="goldt" style="top:170px; font-size:200px">NEXT YEAR<br>PUNYA GAME?</div>
      <div id="gp-c" class="wcard" style="left:120px; top:1060px; width:840px; flex-direction:column; align-items:flex-start; gap:6px; background:rgba(28,18,10,.82); color:#fff;
           font-family:Montserrat; font-weight:800; font-size:40px; border:2px solid rgba(247,194,74,.35)">
        <span style="font-size:28px; letter-spacing:.12em; color:#F7C24A">CIKGU-CIKGU TIKTOK</span>
        <span>Ada game plan untuk survive tahun depan?</span></div>''')
gold("#g-ny", w("next", 77.1) - .2, w("Yang", 87.0) - .3)
rise("#gp-c", w("cikgu", 79.8), sfx="pop"); A(f'tl.to("#gp-c", {{opacity:0, duration:.25}}, {r3(w("Yang", 87.0) - .3)});')
# ---------------- C7: TikTok push LIVE
c7a, c7b = CAN["c7"]
E.html.append(f'''      <div id="c7" class="canvas">
        <div class="hd"><span class="l1">Yang TikTok push:</span><br><span class="hl">video live</span></div>
        <div id="c7-live" style="position:absolute; left:390px; top:440px; padding:16px 40px; border-radius:18px; background:#E8174A; color:#fff; font-family:Anton;
             font-size:90px; letter-spacing:.06em; opacity:0; z-index:3; box-shadow:0 18px 40px rgba(232,23,74,.45)">&#9679; LIVE</div>
        <div id="l0" class="wcard" style="left:100px; top:680px; width:880px; justify-content:space-between"><span>Selalu live?</span><span style="color:{ORG}">IMPROVE &#8599;</span></div>
        <div id="l1" class="wcard or" style="left:100px; top:860px; width:880px; justify-content:space-between"><span>Jarang live?</span><span>KENA BELAJAR &#9998;</span></div>
      </div>''')
show_canvas("c7", c7a, c7b); head_in("#c7", c7a)
A(f'tl.fromTo("#c7-live", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)"}}, {r3(w("live", 90.7) - .2)});')
A(f'tl.to("#c7-live", {{scale:1.08, duration:.4, yoyo:true, repeat:9, ease:"sine.inOut"}}, {r3(w("live", 90.7) + .3)});')
E.fx("impact-bass-1", w("live", 90.7) - .15, .4)
rise("#l0", w("selalu", 92.3) - .2); rise("#l1", w("jarang", 96.8) - .2)

# ---------------- poll + question
E.html.append('''      <div id="poll"><div class="q">KORANG RASA TIKTOK SHOP AKAN&hellip;</div>
        <div class="opts"><div class="op" id="po-a"><b>A</b>BUNUH AFFILIATE</div><div class="op" id="po-b"><b>B</b>BUKA PELUANG BARU</div></div></div>
      <div id="g-dl" class="goldt" style="top:170px; font-size:150px">DAH DOWNLOAD<br>BELUM?</div>''')
gold("#g-dl", w("download", 100.8) - .2, w("membunuh", 104.9) + 2.5)
t_pa = w("membunuh", 104.9)
A(f'tl.fromTo("#poll", {{opacity:0, y:80}}, {{opacity:1, y:0, duration:.45, ease:"expo.out"}}, {r3(w("Adakah", 104.1) - .2)});'); E.fx("whoosh-short", w("Adakah", 104.1) - .15, .4)
A(f'tl.to("#po-a", {{background:"#F2B33D", color:"#2A1A0C", scale:1.04, duration:.2}}, {r3(t_pa)});'); E.fx("click-soft", t_pa)
A(f'tl.to("#po-a", {{background:"rgba(255,255,255,.1)", color:"#fff", scale:1, duration:.2}}, {r3(w("peluang", 107.8) - .2)});')
A(f'tl.to("#po-b", {{background:"#F2B33D", color:"#2A1A0C", scale:1.04, duration:.2}}, {r3(w("peluang", 107.8) - .1)});'); E.fx("click-soft", w("peluang", 107.8) - .1)
A(f'tl.to("#po-b", {{background:"rgba(255,255,255,.1)", color:"#fff", scale:1, duration:.2}}, {r3(w("Korang", 112.3) - .3)});')
E.html.append('      <div id="kom" class="stamp2" style="left:340px; top:1230px; font-size:84px; transform:rotate(-6deg)">KOMEN A / B!</div>')
stamp("#kom", w("Korang", 112.3) - .1, sfx="notification")
A(f'tl.to("#poll, #kom", {{opacity:0, duration:.25}}, {r3(T_END - .15)});')

# ---------------- end card: search bar with the handle
E.html.append('''      <div id="end" style="position:absolute; inset:0; opacity:0; z-index:10; background:radial-gradient(ellipse at 50% 45%, #2A1D12, #0E0A07)">
        <div style="position:absolute; left:0; right:0; top:690px; text-align:center; font-family:Montserrat; font-weight:800; font-size:44px; letter-spacing:.14em; color:#F7C24A">FOLLOW UNTUK UPDATE AFFILIATE</div>
        <div id="end-sb" style="position:absolute; left:170px; right:170px; top:800px; height:120px; border-radius:24px; background:#fff; display:flex; align-items:center; gap:22px; padding:0 34px;
             box-shadow:-6px 0 0 #25F4EE, 6px 0 0 #FE2C55, 0 20px 50px rgba(0,0,0,.5)">
          <span style="font-size:52px">&#128269;</span><span id="end-tx" style="font-family:Montserrat; font-weight:700; font-size:52px; color:#161616; display:inline-block; overflow:hidden; white-space:nowrap; width:0">@khalidkacak</span></div>
      </div>''')
A(f'tl.to("#end", {{opacity:1, duration:.4}}, {r3(T_END)});'); E.fx("whoosh", T_END, .4)
A(f'tl.fromTo("#end-sb", {{scale:.8, opacity:0}}, {{scale:1, opacity:1, duration:.4, ease:"back.out(1.6)"}}, {r3(T_END + .3)});')
A(f'tl.to("#end-tx", {{width:"440px", duration:1.0, ease:"steps(12)"}}, {r3(T_END + .8)});'); E.fx("click-soft", T_END + 1.85, .5)

# ---------------- phones (screen recordings play inside the canvas scenes)
for pid, left, top, rot, vid, clip, ms, a_, b_ in E.html_phone:
    marker = f"<!--PHONE:{pid}-->"
    ph = (f'<div id="{pid}" class="phone" style="left:{left}px; top:{top}px; transform:rotate({rot}deg)"><div class="scr"><div class="notch"></div>'
          f'<video id="{vid}" class="clip" src="{FT + clip}" muted playsinline data-start="{r3(a_ - .15)}" data-duration="{round(b_ - a_ + .15, 3)}" '
          f'data-media-start="{ms}" data-track-index="2" style="position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover"></video></div></div>')
    E.html = [h.replace(marker, ph) for h in E.html]
    A(f'tl.fromTo("#{pid}", {{y:160, opacity:0}}, {{y:0, opacity:1, duration:.55, ease:"expo.out"}}, {r3(a_ + .05)});')

# ---------------- subtitles: 2-4 word phrases, keyword in gold italic
KEY = re.compile(r"(?i)^(tiktok|shop|affiliate|parah|shopee|search|download|seller|komisen|komision|sales|drop|voucher|sengaja|live|"
                 r"terakhir|seronok|membunuh|peluang|apps|game|survive|belajar|improve|baru)")
FIX = {"komision": "komisen", "boucher": "voucher", "dipuat": "dibuat"}
chunks, cur = [], []
for x in WORDS:
    try: t0 = o(x["start"])
    except ValueError: continue
    if not (x["start"] < 52.0 or x["start"] >= 55.3):
        continue
    txt = x["text"]
    for k_, v_ in FIX.items(): txt = txt.replace(k_, v_)
    cur.append((t0, txt))
    if txt[-1:] in ".?!," or len(cur) >= 4:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
subs = []
for i, ch in enumerate(chunks):
    t0 = ch[0][0]; t1 = chunks[i + 1][0][0] if i + 1 < len(chunks) else T_END
    t1 = min(t1, t0 + 2.6)
    words_ = " ".join(f"<i>{t.strip('.,?!')}</i>{t[len(t.strip('.,?!')):]}" if KEY.match(t) else t for _, t in ch)
    dk = any(x_ - .05 <= t0 < y_ for x_, y_ in CAN.values())
    sid = f"sb{i}"
    E.html.append(f'      <div id="{sid}" class="sub{" dk" if dk else ""}">{words_}</div>')
    A(f'tl.fromTo("#{sid}", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:.12}}, {r3(t0 - .05)});')
    A(f'tl.to("#{sid}", {{opacity:0, duration:.08}}, {r3(t1 - .06)});')

E.music = [(0, .11), (T_END - .3, .11), (T_END + .3, .5), (TOTAL - .4, 0), (TOTAL, 0)]
write_project(E, os.path.join(ROOT, "v1"), TOTAL, card_lift=False, bg="#000")
p = json.load(open(os.path.join(ROOT, "v1/edit-plan.json"))); p["music_file"] = "assets/music/be-chillin.mp3"
json.dump(p, open(os.path.join(ROOT, "v1/edit-plan.json"), "w"), indent=1)
