"""Pokok olive tiruan (1.5 m) - same style as tiktokshop/ (user's reference clip): warm graded footage, gold titles over the head,
serif subtitles with gold italic keywords, cream canvas scenes with photo cards / flow cards / stamps, dark glass CTA bar
(beg kuning) and a search-bar end card.  Look + helpers are loaded from tiktokshop/tools/gen_ref.py (single source).
Run: python3 tools/gen_ref.py -> v1/index.html"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Edit, write_project, ROOT, WORDS, H

E = Edit()
FT = "assets/footage/"
a = E.say("a", 0.02, 35.93, clip="main")     # hook (wife marah, beli pokok sendiri) ... olive design lain ... cantum
c = E.say("c", 38.68, 64.26, clip="main")    # (cut "boleh satu ha? sekali sekali ya?") pasu 2 cara, 1.5 m, berat, steady
d = E.say("d", 67.90, 98.72, clip="main")    # (cut silent walk) kembangkan, wire, pasu tinggi, exclusive, beg kuning
T_END = E.hold(5.4)
TOTAL = round(E.t, 3)
o = E.o
def seg_of(src): return "a" if src < 36 else ("c" if src < 65 else "d")
def w(text, near): return E.w(text, near, seg_of(near))
A = E.add
def r3(x): return round(max(x, 0), 3)

E.synced(a); E.synced(c); E.synced(d)
E.shot(T_END, TOTAL - T_END, FT + "main.mp4", 99.6)          # the finished tree in its corner (no voice)

CAN = {
    "c1": (w("olive", 17.7) - .1, w("lengkor-lengkor", 21.1) + .9),
    "c2": (w("bila", 27.5), w("so", 34.0) + .1),
    "c3": (w("so", 38.6), w("cantik", 50.8) + .6),
    "c4": (w("ketinggian", 53.0) - .2, w("jom", 62.4)),
    "c5": (w("saya", 79.3) - .1, w("cantik", 86.6) + .3),
}

# ---------------- camera
for i, c_ in enumerate(E.cuts()):
    E.zoom.append((c_, "set", 1.0, 0))
PUNCH = [w("marah", 6.2), w("sendiri", 11.8), w("zaitut", 22.8), w("exclusive,", 87.0), w("kuring", 96.5)]
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
E.zoom.append((T_END + .02, "slow", 1.12, 0))

# ---------------- shared look + helpers (single source: tiktokshop/tools/gen_ref.py)
src = open(os.path.join(ROOT, "..", "tiktokshop", "tools", "gen_ref.py")).read()
exec(src[src.index("# ---------------- look"):src.index("# ---------------- HOOK")])
E.css.append(f"""
  #s1, #s2, #s3, #s4 {{ filter: brightness(1.08) saturate(1.22) contrast(1.06); }}
  #vig {{ background:radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 60%, rgba(25,12,0,.18) 100%); }}
  .pcard {{ position:absolute; background:#fff; padding:16px 16px 0; border-radius:22px; box-shadow:0 24px 50px rgba(110,70,10,.28); z-index:3; opacity:0; }}
  .pcard img {{ display:block; width:100%; border-radius:12px; object-fit:cover; }}
  .pcard .cap {{ font-family:'Anton'; font-size:46px; color:{BR}; text-align:center; padding:14px 6px 18px; line-height:1.05; }}
  .pcard .cap small {{ display:block; font-family:'Montserrat'; font-weight:800; font-size:28px; color:{ORG}; letter-spacing:.04em; margin-top:4px; }}
  .glass {{ position:absolute; left:120px; width:840px; padding:26px 34px; border-radius:26px; background:rgba(28,18,10,.82); border:2px solid rgba(247,194,74,.35);
           font-family:'Montserrat'; font-weight:800; font-size:42px; color:#fff; opacity:0; z-index:6; line-height:1.15; }}
  .glass .k {{ display:block; font-size:28px; letter-spacing:.12em; color:#F7C24A; margin-bottom:6px; }}
""")

# ---------------- HOOK: "Guys tengoklah..." -> WIFE SAYA MARAH?! -> DIA BELI POKOK SENDIRI!
E.html.append('''      <div id="hk-s" class="script" style="top:140px; font-size:62px">Guys, tengoklah wife saya beli apa&hellip;</div>
      <div id="hk-g" class="goldt" style="top:215px; font-size:180px">WIFE SAYA<br>MARAH?!</div>
      <div id="hk-c" class="glass" style="top:1060px"><span class="k">SEBAB APA?</span>Pokok dia saya letak <span style="color:#F7C24A">kat atas</span>&hellip;</div>
      <div id="hk-g2" class="goldt" style="top:215px; font-size:160px">DIA BELI<br>POKOK SENDIRI!</div>''')
A('tl.set("#hk-s", {opacity:1}, 0); tl.set("#hk-g", {opacity:1}, 0);')
E.fx("impact-bass-1", .05, .45)
A(f'tl.fromTo("#hk-g", {{x:-10}}, {{x:10, duration:.05, yoyo:true, repeat:5}}, {w("marah", 6.2)});'); E.fx("impact-bass-1", w("marah", 6.2), .5)
rise("#hk-c", w("sebab", 7.9) - .1, sfx="pop")
E.html.append('''      <div id="hk-p" class="pcard" style="left:250px; top:250px; width:580px; transform:rotate(-3deg); z-index:7"><img src="assets/img/pokok_atas.jpg" style="height:640px; object-position:50% 60%"/>
        <div class="cap">POKOK DIA<small>dah pindah letak kat atas</small></div></div>''')
A(f'tl.to("#hk-s, #hk-g", {{opacity:0, y:-20, duration:.25}}, {r3(w("pokok", 8.2) - .25)});')
A(f'tl.fromTo("#hk-p", {{opacity:0, y:80, rotation:-10, scale:.85}}, {{opacity:1, y:0, rotation:-3, scale:1, duration:.45, ease:"back.out(1.6)"}}, {r3(w("pokok", 8.2) - .1)});')
E.fx("whoosh-short", w("pokok", 8.2) - .05, .4)
A(f'tl.to("#hk-p", {{opacity:0, y:-40, duration:.25, ease:"power2.in"}}, {r3(w("beli", 10.8) - .3)});')
gold("#hk-g2", w("beli", 10.8) - .1, w("olive", 17.7) - .4)
A(f'tl.to("#hk-c", {{opacity:0, duration:.25}}, {r3(w("so", 12.7))});')

# ---------------- C1: pokok olive, design lain (melengkor)
c1a, c1b = CAN["c1"]
E.html.append('''      <div id="c1" class="canvas">
        <div class="hd"><span class="l1">Pokok olive</span><br><span class="hl">tapi design lain</span></div>
        <div id="c1-p" class="pcard" style="left:150px; top:430px; width:420px; transform:rotate(-4deg)"><img src="assets/img/tree.jpg" style="height:720px"/>
          <div class="cap">POKOK OLIVE<small>tinggi &amp; lebat</small></div></div>
        <div id="c1-q" class="pcard" style="left:560px; top:560px; width:380px; transform:rotate(4deg)"><img src="assets/img/trunk.jpg" style="height:470px"/>
          <div class="cap">BATANG<small>melengkor</small></div></div>
        <div id="c1-st" class="stamp2" style="left:420px; top:1260px; font-size:66px; transform:rotate(-6deg)">MELENGKOR!</div>
      </div>''')
show_canvas("c1", c1a, c1b); head_in("#c1", c1a)
rise("#c1-p", c1a + .25); rise("#c1-q", w("lengkor-lengkor", 19.9) - .2)
stamp("#c1-st", w("lengkor-lengkor", 21.1))
# ---------------- footage: buah zaitun / minyak zaitun callback
E.html.append('''      <div id="g-bz" class="goldt" style="top:200px; font-size:170px">ADA BUAH<br>ZAITUN!</div>
      <div id="bz-c" class="glass" style="top:1060px"><span class="k">PADANLAH&hellip;</span>Dia memang minum <span style="color:#F7C24A">minyak zaitun</span> &#128516;</div>''')
gold("#g-bz", w("buah", 22.5) - .15, w("bila", 27.5) - .4)
rise("#bz-c", w("semenjak", 24.3) - .1, sfx="pop"); A(f'tl.to("#bz-c", {{opacity:0, duration:.2}}, {r3(w("bila", 27.5) - .3)});')
# ---------------- C2: cantum -> jadi tinggi
c2a, c2b = CAN["c2"]
E.html.append('''      <div id="c2" class="canvas">
        <div class="hd"><span class="l1">Cantum je</span><br><span class="hl">terus jadi tinggi</span></div>
        <div id="j0" class="wcard" style="left:90px; top:520px; width:430px"><span class="ic">1</span>Bahagian 1</div>
        <div id="j1" class="wcard" style="left:90px; top:700px; width:430px"><span class="ic">2</span>Bahagian 2</div>
        <div id="j-ar" class="arrow" style="left:530px; top:640px">&rarr;</div>
        <div id="j2" class="pcard" style="left:600px; top:430px; width:390px; transform:rotate(3deg)"><img src="assets/img/join.jpg" style="height:560px"/>
          <div class="cap">TERUS TINGGI</div></div>
        <div id="c2-st" class="stamp2" style="left:150px; top:930px; font-size:70px; transform:rotate(-6deg)">SENANG!</div>
      </div>''')
show_canvas("c2", c2a, c2b); head_in("#c2", c2a)
rise("#j0", w("gabungkan", 27.9) - .1); rise("#j1", w("gabungkan", 27.9) + .25)
A(f'tl.fromTo("#j-ar", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:.3}}, {r3(w("tinggi", 29.1) - .2)});')
rise("#j2", w("tinggi", 29.1))
stamp("#c2-st", w("cantumkan", 30.4))
# ---------------- C3: pasu, 2 cara
c3a, c3b = CAN["c3"]
E.html.append('''      <div id="c3" class="canvas">
        <div class="hd"><span class="l1">Pasu boleh</span><br><span class="hl">2 cara letak</span></div>
        <div id="p0" class="pcard" style="left:90px; top:450px; width:430px; transform:rotate(-3deg)"><img src="assets/img/pot_in.jpg" style="height:430px"/>
          <div class="cap">A: TUTUP<small>masuk dalam pasu</small></div></div>
        <div id="p1" class="pcard" style="left:560px; top:450px; width:430px; transform:rotate(3deg)"><img src="assets/img/pot_top.jpg" style="height:430px"/>
          <div class="cap">B: ATAS PASU<small>bawah tak kotor &#10003;</small></div></div>
        <div id="c3-st" class="stamp2" style="left:340px; top:1180px; font-size:72px; transform:rotate(-6deg)">DUA-DUA CANTIK!</div>
      </div>''')
show_canvas("c3", c3a, c3b); head_in("#c3", c3a)
rise("#p0", w("tutup", 42.3) - .3); rise("#p1", w("letak", 43.9) - .2)
A(f'tl.to("#p1", {{scale:1.05, duration:.3, ease:"back.out(2)"}}, {r3(w("kotor", 48.5))});'); E.fx("pop", w("kotor", 48.5), .45)
stamp("#c3-st", w("cantik", 50.8) - .1)
# ---------------- C4: 1.5 meter + quality
c4a, c4b = CAN["c4"]
E.html.append(f'''      <div id="c4" class="canvas">
        <div class="hd"><span class="l1">Ketinggian</span><br><span class="hl">1.5 meter</span></div>
        <div id="c4-p" class="pcard" style="left:90px; top:420px; width:400px; transform:rotate(-3deg)"><img src="assets/img/tree.jpg" style="height:760px"/></div>
        <svg id="c4-m" width="80" height="780" viewBox="0 0 80 780" style="position:absolute; left:500px; top:430px; z-index:3; opacity:0">
          <path d="M40 10 V770 M15 10 H65 M15 770 H65" stroke="{BR}" stroke-width="6" fill="none"/></svg>
        <div id="c4-n" style="position:absolute; left:470px; top:740px; font-family:Anton; font-size:64px; color:{BR}; background:#F2B33D; padding:4px 14px;
             transform:rotate(-90deg); transform-origin:50% 50%; z-index:4; opacity:0">1.5 M</div>
        <div class="lbl2" id="c4-l" style="left:600px; top:520px; opacity:0">The best part:</div>
        <div id="q0" class="wcard or" style="left:590px; top:580px; width:440px; font-size:44px"><span class="ic">&#9878;</span>Sangat berat</div>
        <div id="q1" class="wcard or" style="left:590px; top:770px; width:440px; font-size:44px"><span class="ic">&#9875;</span>Sangat steady</div>
        <div id="q2" class="wcard" style="left:590px; top:960px; width:440px; font-size:44px"><span class="ic">&#10024;</span>Melengkor cantik</div>
      </div>''')
show_canvas("c4", c4a, c4b); head_in("#c4", c4a)
rise("#c4-p", c4a + .25)
A(f'tl.to("#c4-m", {{opacity:1, duration:.3}}, {r3(w("meter", 54.4) - .3)});')
A(f'tl.fromTo("#c4-n", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {r3(w("meter", 54.4) - .1)});')
E.fx("impact-bass-1", w("meter", 54.4), .4)
A(f'tl.to("#c4-l", {{opacity:.6, duration:.3}}, {r3(w("best", 55.4))});')
rise("#q0", w("berat", 58.4) - .15); rise("#q1", w("steady", 59.5) - .15); rise("#q2", w("cantik", 62.0) - .3)
# ---------------- footage: tips kembangkan + wire
E.html.append('''      <div id="tp1" class="glass" style="top:1060px"><span class="k">TIPS 1</span>Bila dah dapat, <span style="color:#F7C24A">kembangkan</span> dahan dia sikit</div>
      <div id="tp2" class="glass" style="top:1060px"><span class="k">ADA WIRE DALAM DAHAN</span>Senang bentukkan ikut suka</div>''')
rise("#tp1", w("kembang-kembangkan", 71.0) - .4, sfx="pop")
A(f'tl.to("#tp1", {{opacity:0, duration:.2}}, {r3(w("wire", 74.1) - .3)});')
rise("#tp2", w("wire", 74.1) - .1, sfx="pop")
A(f'tl.to("#tp2", {{opacity:0, duration:.2}}, {r3(CAN["c5"][0] - .2)});')
# ---------------- C5: tips pasu lebih tinggi
c5a, c5b = CAN["c5"]
E.html.append('''      <div id="c5" class="canvas">
        <div class="hd"><span class="l1">Tips 2: cari pasu</span><br><span class="hl">lagi tinggi &amp; besar</span></div>
        <div id="t0" class="wcard" style="left:60px; top:520px; width:470px; font-size:44px"><span class="ic">&#9651;</span>Pasu besar</div>
        <div id="t1" class="wcard" style="left:60px; top:700px; width:470px; font-size:44px"><span class="ic">&#8593;</span>Nampak tinggi</div>
        <div id="t3" class="pcard" style="left:560px; top:440px; width:440px; transform:rotate(3deg)"><img src="assets/img/pasu_besar.jpg" style="height:600px; object-position:50% 75%"/>
          <div class="cap">PASU LEBIH BESAR<small>contoh macam ni</small></div></div>
        <div id="t2" class="wcard or" style="left:60px; top:880px; width:470px; font-size:44px"><span class="ic">&#10024;</span>Lebih cantik!</div>
      </div>''')
show_canvas("c5", c5a, c5b); head_in("#c5", c5a)
rise("#t3", w("pasu", 80.3) - .3); rise("#t0", w("besar", 81.7) - .2); rise("#t1", w("nampak", 84.1) - .1); rise("#t2", w("cantik", 86.6) - .3)
# ---------------- footage: EXCLUSIVE + CTA bar
E.html.append('''      <div id="g-ex" class="goldt" style="top:190px; font-size:210px">EXCLUSIVE!</div>
      <div id="ex-c" class="glass" style="top:1060px"><span class="k">LAIN DARI POKOK OLIVE DI LUAR</span>Batang dia <span style="color:#F7C24A">melengkor</span>, design sangat cantik</div>
      <div id="cta" style="position:absolute; left:110px; right:110px; top:1480px; padding:30px 30px 34px; border-radius:30px; background:rgba(28,18,10,.86);
           border:2px solid rgba(247,194,74,.45); opacity:0; z-index:9; text-align:center">
        <div style="font-family:Montserrat; font-weight:800; font-size:38px; color:#fff; letter-spacing:.06em">DAH ADA DI BEG KUNING</div>
        <div id="cta-b" style="margin:20px auto 0; width:fit-content; display:flex; align-items:center; gap:18px; padding:22px 44px; border-radius:999px;
             background:linear-gradient(180deg,#FFD873,#F2B33D); color:#2A1A0C; font-family:Anton; font-size:58px; box-shadow:0 10px 30px rgba(242,179,61,.45)">
          <svg width="64" height="60" viewBox="0 0 74 70"><path d="M6 22 H68 L60 64 H14 Z" fill="#2A1A0C"/><path d="M22 24 C 22 2, 52 2, 52 24" fill="none" stroke="#2A1A0C" stroke-width="7"/></svg>
          CHECKOUT SEKARANG</div></div>''')
gold("#g-ex", w("exclusive,", 87.0) - .1, w("kalau", 94.9) - .3)
rise("#ex-c", w("pokok", 88.9) - .2, sfx="pop"); A(f'tl.to("#ex-c", {{opacity:0, duration:.2}}, {r3(w("kalau", 94.9) - .3)});')
A(f'tl.fromTo("#cta", {{opacity:0, y:80}}, {{opacity:1, y:0, duration:.45, ease:"expo.out"}}, {r3(w("kalau", 94.9) - .1)});'); E.fx("whoosh-short", w("kalau", 94.9), .4)
t_k = w("kuring", 96.5)
A(f'tl.fromTo("#cta-b", {{scale:.6}}, {{scale:1, duration:.35, ease:"back.out(2)"}}, {r3(t_k - .1)});'); E.fx("impact-bass-1", t_k, .45)
A(f'tl.to("#cta-b", {{scale:.93, duration:.09, yoyo:true, repeat:1}}, {r3(w("cek", 97.1))});'); E.fx("click-soft", w("cek", 97.1))
A(f'tl.to("#cta-b", {{scale:1.06, duration:.35, yoyo:true, repeat:3, ease:"sine.inOut"}}, {r3(T_END + .1)});')
E.fx("notification", T_END + .2, .35)
A(f'tl.to("#cta", {{opacity:0, duration:.25}}, {r3(T_END + 2.4)});')

# ---------------- end card: search bar with the handle
E.html.append('''      <div id="end" style="position:absolute; inset:0; opacity:0; z-index:10; background:radial-gradient(ellipse at 50% 45%, rgba(42,29,18,.92), rgba(14,10,7,.97))">
        <div style="position:absolute; left:0; right:0; top:690px; text-align:center; font-family:Montserrat; font-weight:800; font-size:44px; letter-spacing:.14em; color:#F7C24A">FOLLOW UNTUK REVIEW JUJUR</div>
        <div id="end-sb" style="position:absolute; left:170px; right:170px; top:800px; height:120px; border-radius:24px; background:#fff; display:flex; align-items:center; gap:22px; padding:0 34px;
             box-shadow:-6px 0 0 #25F4EE, 6px 0 0 #FE2C55, 0 20px 50px rgba(0,0,0,.5)">
          <span style="font-size:52px">&#128269;</span><span id="end-tx" style="font-family:Montserrat; font-weight:700; font-size:52px; color:#161616; display:inline-block; overflow:hidden; white-space:nowrap; width:0">@khalidkacak</span></div>
      </div>''')
T_H = T_END + 2.6
A(f'tl.to("#end", {{opacity:1, duration:.4}}, {r3(T_H)});'); E.fx("whoosh", T_H, .4)
A(f'tl.fromTo("#end-sb", {{scale:.8, opacity:0}}, {{scale:1, opacity:1, duration:.4, ease:"back.out(1.6)"}}, {r3(T_H + .3)});')
A(f'tl.to("#end-tx", {{width:"440px", duration:1.0, ease:"steps(12)"}}, {r3(T_H + .8)});'); E.fx("click-soft", T_H + 1.85, .5)

# ---------------- subtitles
KEY = re.compile(r"(?i)^(wife|marah|pokok|olive|desain|design|lengk|melengk|zaitun|tinggi|cantum|pasu|kotor|cantik|meter|berat|steady|best|"
                 r"wire|kembang|exclusive|kuning|checkout|sendiri)")
FIX = {"zaitut": "zaitun", "lengkor-lengkor": "melengkor", "melengkor": "melengkor", "desain": "design", "kuring": "kuning", "beli kuning": "beg kuning",
       "isyak": "insya", "umur": "Allah", "dulu tanya": "duduknya", "andai": "andai"}
words = []
for x in WORDS:
    try: t0 = o(x["start"])
    except ValueError: continue
    if 35.93 <= x["start"] < 38.68 or 64.26 <= x["start"] < 67.9:
        continue
    txt = x["text"]
    for k_, v_ in FIX.items(): txt = txt.replace(k_, v_)
    if txt.lower().startswith("lengkor"): txt = "me" + txt
    words.append([t0, txt])
# whisper sometimes stacks several words on one timestamp: spread them evenly up to the next distinct time
i = 0
while i < len(words):
    j = i
    while j + 1 < len(words) and words[j + 1][0] <= words[i][0] + .02:
        j += 1
    if j > i:
        nxt = words[j + 1][0] if j + 1 < len(words) else words[i][0] + .3 * (j - i + 1)
        step = (nxt - words[i][0]) / (j - i + 1)
        for m in range(i, j + 1):
            words[m][0] = round(words[i][0] + step * (m - i), 3)
    i = j + 1
for i in range(len(words) - 1):                                 # "beli kuning" -> "beg kuning"
    if words[i][1].lower() == "beli" and words[i + 1][1].lower().startswith("kuning"):
        words[i][1] = "beg"
chunks, cur = [], []
for t0, txt in words:
    cur.append((t0, txt))
    if txt[-1:] in ".?!," or len(cur) >= 4:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
for i, ch in enumerate(chunks):
    t0 = ch[0][0]; t1 = chunks[i + 1][0][0] if i + 1 < len(chunks) else T_END
    t1 = max(min(t1, t0 + 2.6), t0 + .35)
    words_ = " ".join(f"<i>{t.strip('.,?!')}</i>{t[len(t.strip('.,?!')):]}" if KEY.match(t) else t for _, t in ch)
    dk = any(x_ - .05 <= t0 < y_ for x_, y_ in CAN.values())
    sid = f"sb{i}"
    E.html.append(f'      <div id="{sid}" class="sub{" dk" if dk else ""}">{words_}</div>')
    A(f'tl.fromTo("#{sid}", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:.12}}, {r3(t0 - .05)});')
    A(f'tl.to("#{sid}", {{opacity:0, duration:.08}}, {r3(t1 - .06)});')

E.music = [(0, .11), (T_END - .3, .11), (T_END + .3, .5), (TOTAL - .5, 0), (TOTAL, 0)]
write_project(E, os.path.join(ROOT, "v1"), TOTAL, card_lift=False, bg="#000")
p = json.load(open(os.path.join(ROOT, "v1/edit-plan.json"))); p["music_file"] = "assets/music/be-chillin.mp3"
json.dump(p, open(os.path.join(ROOT, "v1/edit-plan.json"), "w"), indent=1)
