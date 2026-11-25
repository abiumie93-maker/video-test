"""VERSI 2 (reference style) for the insole promo. Reuses the look + helpers of promo/tools/gen2.py.
Run: python3 tools/gen2.py  -> v2/index.html + v2/edit-plan.json"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Edit, write_project, ROOT, WORDS

E = Edit()
FT = "assets/footage/"
h1 = E.say("h1", 0.00, 4.02, clip="073913")
h2 = E.say("h2", 4.50, 6.53, clip="073913")
a1 = E.say("a1", 0.05, 4.69, clip="074041")
b2 = E.say("b2", 4.80, 12.79, clip="074041")
b3 = E.say("b3", 12.94, 14.82, clip="074041")
T_HOLD = E.hold(1.4)
T_MON = E.hold(4.4)
b4 = E.say("b4", 6.53, 10.50, clip="073913")
ct = E.say("cta", 15.03, 17.45, clip="074041")
E.hold(3.0)
TOTAL = round(E.t, 3)
o = E.o
def w(seg, text, near): return E.w(text, near, seg["name"])
A = E.add

# ---------------- picture
E.synced(h1, a=0.0, b=3.0)
E.shot(o(3.0, "h1"), 1.02, FT + "073827.mp4", 0.35)
E.synced(h2); E.synced(a1)
T_BLUR = w(b2, "So", 5.0) - .05
s_b2 = E.synced(b2, a=4.80, b=9.25)                 # talking over close-ups, then blur -> neon
T_CAN = o(9.25, "b2")                                 # canvas from "Memang lawa"
E.shot(T_CAN, T_MON - T_CAN, FT + "074041.mp4", 9.25)  # (under the canvas)
MON = [(0.3, 1.5, "senang pasang"), (4.6, 1.5, "muat elok"), (9.6, 1.4, "terus sedap")]
t = T_MON; mon = []
for ms, du, lab in MON:
    E.shot(t, du, FT + "073815.mp4", ms); mon.append((t, du, lab)); t += du
E.synced(b4)
E.shot(ct["out"], TOTAL - ct["out"], FT + "073758.mp4", 0.5, style="filter:blur(30px) brightness(.7); transform:scale(1.15)")

# ---------------- camera
for i, c_ in enumerate(E.cuts()):
    E.zoom.append((c_, "set", *[(1.0, 0), (1.07, 10), (1.03, -8), (1.1, 0)][i % 4]))
PUNCH = [w(h1, "campak", 3.6) - .1, w(h2, "baru", 6.0), w(a1, "best", 3.8), w(b4, "puas", 7.5)]
LV = [(1.12, 0), (1.0, 0), (1.16, -16), (1.05, 14), (1.14, 12), (1.0, 0)]
cands = []
for n in range(1, len(WORDS)):
    if WORDS[n - 1]["text"].strip()[-1:] in ".?!," and WORDS[n - 1]["file"] == WORDS[n]["file"]:
        for s in E.vo:
            if s["clip"] == WORDS[n]["file"] and s["src_in"] <= WORDS[n]["start"] <= s["src_out"]:
                cands.append(round(s["out"] + WORDS[n]["start"] - s["src_in"], 3))
cuts = E.cuts(); last, k = -9, 0
for tt in sorted(set(cands)):
    prev = max([c for c in cuts if c <= tt] or [0]); nxt = min([c for c in cuts if c > tt] or [TOTAL])
    if tt - prev < .7 or nxt - tt < .8 or tt - last < 2.0 or any(abs(tt - p) < 1.0 for p in PUNCH) or T_BLUR - .3 < tt < T_MON:
        continue
    E.zoom.append((tt, "ease", *LV[k % len(LV)])); k += 1; last = tt
for p in PUNCH:
    E.zoom.append((round(p - .05, 3), "punch", 1.24, 0)); E.fx("whoosh-short", p, .35)
for st_, du, _ in mon:
    E.zoom.append((st_ + .02, "slow", 1.14, 0))

# ---------------- shared Versi 2 look + helpers (single source: promo/tools/gen2.py)
src = open(os.path.join(ROOT, "..", "promo", "tools", "gen2.py")).read()
exec(src[src.index("# ---------------- look"):src.index("# ---------------- persistent top pill")])

E.html.append('''      <div id="pill"><div class="s">Tapak kasut dah lama?</div><div class="b">TUKAR YANG BARU</div></div>''')

# ---------------- HOOK: "Tapak kasut DAH LAMA?" -> neon CAMPAK! -> carousel of the new insole
IMGS = ["bottom", "mesh", "arch", "pad", "inshoe", "bottom2", "pair"]
cards = "".join(
    f'<div class="cc" style="transform:rotateY({i * 360 / len(IMGS)}deg) translateZ(400px)"><img src="assets/img/{n}.jpg"/></div>'
    for i, n in enumerate(IMGS))
E.css.append("""
  #car-wrap { position:absolute; left:0; right:0; top:1150px; height:640px; perspective:1500px; opacity:0; }
  #car { position:absolute; left:50%; top:40px; width:0; height:0; transform-style:preserve-3d; }
  .cc { position:absolute; left:-140px; top:0; width:280px; height:420px; border-radius:34px; overflow:hidden; backface-visibility:hidden;
        box-shadow:0 20px 50px rgba(0,0,0,.45); border:4px solid rgba(255,255,255,.9); background:#fff; }
  .cc img { width:100%; height:100%; object-fit:cover; }
  #hk-top { position:absolute; left:0; right:0; top:110px; text-align:center; }
""")
E.html.append(f'''      <div id="hk-top">
        <div class="wt" id="hk-l1" style="font-size:84px">Tapak kasut</div>
        <div class="neon" id="hk-l2" style="font-size:150px; margin-top:6px">DAH LAMA?</div>
      </div>
      <div id="hk-c" class="neon" style="position:absolute; left:0; right:0; top:1180px; text-align:center; font-size:230px; color:#FF4D4D;
           text-shadow:0 0 22px rgba(255,77,77,.85), 0 0 70px rgba(255,77,77,.5); opacity:0">CAMPAK!</div>
      <div id="hk-n" style="position:absolute; left:0; right:0; top:110px; text-align:center; opacity:0">
        <div class="wt" style="font-size:84px">Dapatkan yang</div>
        <div class="neon" style="font-size:190px; margin-top:6px">BARU!</div>
      </div>
      <div id="car-wrap"><div id="car">{cards}</div></div>''')
A('tl.from("#hk-l2", {scale:.4, opacity:0, duration:.45, ease:"back.out(1.6)", immediateRender:false}, 0.05);')
E.fx("impact-bass-1", .05, .45)
t_c = w(h1, "campak", 3.6) - .12
A(f'tl.fromTo("#hk-c", {{opacity:0, scale:2.2, rotation:-8}}, {{opacity:1, scale:1, rotation:-4, duration:.3, ease:"back.out(2)"}}, {t_c});')
E.fx("impact-bass-1", t_c + .02, .5); E.fx("error", t_c + .05, .4)
A(f'tl.to("#hk-top, #hk-c", {{opacity:0, duration:.2}}, {h2["out"] - .05});')
E.fx("whoosh", h2["out"], .45)
A(f'tl.fromTo("#hk-n", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.35, ease:"expo.out"}}, {h2["out"] + .1});')
A(f'tl.fromTo("#car-wrap", {{opacity:0, y:120}}, {{opacity:1, y:0, duration:.45, ease:"expo.out"}}, {h2["out"] + .15});')
A(f'tl.fromTo("#car", {{rotationY:0}}, {{rotationY:-220, duration:{round(h2["dur"] + .3, 3)}, ease:"power1.inOut"}}, {h2["out"] + .15});')
E.fx("impact-bass-1", w(h2, "baru", 6.0), .4)
A(f'tl.to("#hk-n", {{scale:.25, y:-180, opacity:0, duration:.4, ease:"power3.in", transformOrigin:"50% 0%"}}, {a1["out"] - .3});')
A(f'tl.to("#car-wrap", {{opacity:0, y:200, duration:.35, ease:"power2.in"}}, {a1["out"] - .3});')
A(f'tl.fromTo("#pill", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(1.6)"}}, {a1["out"] - .05});')
E.fx("whoosh-short", a1["out"] - .1, .4)

# ---------------- a1: feet in the new insole
E.html.append('''      <div id="sd" class="spill" style="top:1420px">sedap <b>guys</b> &#10003;</div>
      <div id="bs" class="wt" style="position:absolute; left:0; right:0; top:1280px; text-align:center; font-size:110px; opacity:0">MEMANG <span style="color:#C8FF2E">BEST</span></div>''')
pill_in("#sd", w(a1, "Sedap", .3)); out("#sd", w(a1, "letak", 2.4) - .3)
A(f'tl.fromTo("#bs", {{opacity:0, scale:1.3, filter:"blur(12px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.3, ease:"expo.out"}}, {w(a1, "memang", 3.6) - .05});')
E.fx("pop", w(a1, "best", 3.8), .45)
out("#bs", b2["out"] - .15)

# ---------------- b2: blur -> neon "TAPAK BARU", then canvas with 3 tiles
A(f'tl.fromTo("#{s_b2}", {{filter:"blur(0px) brightness(1)"}}, {{filter:"blur(36px) brightness(.7)", duration:.45, ease:"power2.out"}}, {T_BLUR});')
E.fx("whoosh", T_BLUR, .45)
E.html.append('''      <div id="br-s" class="wt" style="position:absolute; left:0; right:0; top:760px; text-align:center; font-size:42px; font-weight:600; opacity:0">korang dapatkan</div>
      <div id="br-n" class="neon" style="position:absolute; left:0; right:0; top:830px; text-align:center; font-size:170px; opacity:0">TAPAK<br>BARU</div>''')
A(f'tl.fromTo("#br-s", {{opacity:0}}, {{opacity:1, duration:.3}}, {T_BLUR + .25});')
t_n = w(b2, "tapak", 7.0) - .05
A(f'tl.fromTo("#br-n", {{opacity:0, scale:.6, filter:"blur(20px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.5, ease:"expo.out"}}, {t_n});')
E.fx("impact-bass-1", t_n, .5)

E.html.append(f'''      <div id="cq" class="canvas">
        <div class="badge"><i>K</i>Kelebihan</div>
        <div id="q1" class="tile" style="left:90px; top:400px; font-size:42px">Lawa</div>
        <div id="qo1" class="op" style="left:308px; top:450px">+</div>
        <div id="q2" class="tile" style="left:380px; top:400px; font-size:40px">Cantik</div>
        <div id="qo2" class="op" style="left:598px; top:450px">+</div>
        <div id="q3" class="tile" style="left:670px; top:400px; font-size:34px">Berkualiti</div>
        <div id="qc" class="glass" style="left:240px; top:660px; width:600px; height:600px; padding:20px">
          <img src="assets/img/bottom.jpg" style="width:560px; height:560px; object-fit:cover; border-radius:24px"/></div>
        <div id="qok" class="ok" style="left:610px; top:635px">&#10003; kualiti</div>
        <div id="qcap" class="cap" style="top:1340px">memang <b>BERKUALITI</b></div>
      </div>''')
A(f'tl.fromTo("#cq", {{opacity:0}}, {{opacity:1, duration:.3}}, {T_CAN - .15});'); E.fx("whoosh-short", T_CAN - .1, .4)
A(f'tl.to("#br-s, #br-n", {{opacity:0, duration:.2}}, {T_CAN});')
A(f'tl.from("#cq .badge", {{x:-40, opacity:0, duration:.35, ease:"expo.out", immediateRender:false}}, {T_CAN + .1});')
rise("#q1", w(b2, "lawa", 9.5) - .1); fade("#qo1", w(b2, "lawa", 9.5) + .4, d=.2)
rise("#q2", w(b2, "cantik", 10.6) - .1); fade("#qo2", w(b2, "cantik", 10.6) + .4, d=.2)
rise("#q3", w(b2, "berkualiti", 12.0) - .15)
rise("#qc", w(b2, "lawa", 9.5) + .3, sfx="whoosh-short")
A('tl.set("#qcap", {opacity:0}, 0);')
rise("#qcap", w(b2, "berkualiti", 12.0) - .05, sfx=None)
A(f'tl.fromTo("#qok", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {w(b2, "berkualiti", 12.0) + .3});')
E.fx("notification", w(b2, "berkualiti", 12.0) + .35, .4)

# ---------------- b3: canvas "Struktur": keras vs lembut
E.html.append(f'''      <div id="cs" class="canvas">
        <div class="badge"><i>S</i>Struktur</div>
        <div id="sc1" class="glass" style="left:70px; top:420px; width:450px; height:720px; z-index:2">
          <img src="assets/img/arch.jpg" style="position:absolute; left:20px; top:20px; width:406px; height:500px; object-fit:cover; border-radius:22px"/>
          <div style="position:absolute; left:34px; top:548px; font-weight:800; font-size:56px; color:#E5383B">KERAS</div>
          <div style="position:absolute; left:34px; top:620px; font-weight:600; font-size:32px; color:#556">sokong kaki</div>
        </div>
        <div id="sc2" class="glass" style="left:560px; top:420px; width:450px; height:720px; z-index:2">
          <img src="assets/img/pad.jpg" style="position:absolute; left:20px; top:20px; width:406px; height:500px; object-fit:cover; border-radius:22px"/>
          <div style="position:absolute; left:34px; top:548px; font-weight:800; font-size:56px; color:#1FA855">LEMBUT</div>
          <div style="position:absolute; left:34px; top:620px; font-weight:600; font-size:32px; color:#556">empuk di tapak</div>
        </div>
        <div id="sok" class="ok" style="left:330px; top:1190px">&#10003; keras + lembut = sedap</div>
        <div id="scap" class="cap" style="top:1300px">di sini <b>keras</b>,<br>di sini <b>lembut</b></div>
      </div>''')
A(f'tl.fromTo("#cs", {{opacity:0}}, {{opacity:1, duration:.3}}, {b3["out"] - .15});'); E.fx("whoosh-short", b3["out"] - .1, .4)
A(f'tl.to("#cq", {{opacity:0, duration:.2}}, {b3["out"] + .2});')
A(f'tl.from("#cs .badge", {{x:-40, opacity:0, duration:.35, ease:"expo.out", immediateRender:false}}, {b3["out"] + .05});')
rise("#sc1", w(b3, "keras", 13.5) - .15); rise("#sc2", w(b3, "lembut", 14.5) - .15)
A('tl.set("#scap", {opacity:0}, 0);')
words("#scap", w(b3, "keras", 13.5) - .2)
A(f'tl.fromTo("#sok", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {T_HOLD + .2});')
E.fx("notification", T_HOLD + .25, .4)
A(f'tl.to("#cs", {{opacity:0, duration:.25}}, {T_MON - .1});'); E.fx("whoosh", T_MON - .05, .45)

# ---------------- montage
for i, (st_, du, lab) in enumerate(mon):
    E.html.append(f'      <div id="ml{i}" class="spill" style="top:1450px; font-size:46px">{lab}</div>')
    pill_in(f"#ml{i}", st_ + .12, sfx=None); out(f"#ml{i}", st_ + du - .15, .12)
    E.fx("whoosh-short", st_, .4)
E.fx("riser", w(b4, "puas", 7.5) - .1)

# ---------------- b4: PUAS HATI neon + floating glass tags
E.html.append('''      <div id="ph" class="neon" style="position:absolute; left:0; right:0; top:1420px; text-align:center; font-size:170px; opacity:0">PUAS HATI!</div>
      <div id="tg1" class="dglass" style="left:70px; top:560px">SEDAP +</div>
      <div id="tg2" class="dglass" style="left:700px; top:720px">LAWA +</div>
      <div id="tg3" class="dglass" style="left:110px; top:900px">BERKUALITI +</div>
      <div id="sk" class="spill" style="top:1620px">InsyaAllah korang <b>sangat suka</b></div>''')
t_p = w(b4, "puas", 7.5)
A(f'tl.fromTo("#ph", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(1.6)"}}, {t_p - .05});')
E.fx("impact-bass-1", t_p, .5)
for i in range(3):
    rise(f"#tg{i+1}", t_p + .4 + i * .35, sfx="pop")
    A(f'tl.to("#tg{i+1}", {{y:-16, duration:1.2, yoyo:true, repeat:1, ease:"sine.inOut"}}, {r3(t_p + .9 + i * .35)});')
A(f'tl.to("#ph", {{opacity:0, duration:.2}}, {w(b4, "sangat", 9.6) - .45});')
pill_in("#sk", w(b4, "sangat", 9.6) - .3)
A(f'tl.to("#sk, #tg1, #tg2, #tg3", {{opacity:0, duration:.25}}, {ct["out"] - .2});')

# ---------------- end card + CTA
E.html.append('''      <div id="ec" class="glass" style="left:170px; top:300px; width:740px; height:900px; padding:22px; background:rgba(255,255,255,.85)">
        <img src="assets/img/bottom2.jpg" style="width:696px; height:640px; object-fit:cover; border-radius:24px"/>
        <div style="font-weight:800; font-size:58px; color:#12131A; margin-top:22px; text-align:center">Tapak Kasut <span style="color:#FF4D4D">Baru</span></div>
        <div style="font-weight:600; font-size:30px; color:#556; margin-top:10px; text-align:center">Keras sokong kaki &bull; Lembut empuk di tapak</div>
      </div>
      <div id="ebtn" style="position:absolute; left:0; right:0; margin:0 auto; width:fit-content; top:1290px; padding:30px 56px; border-radius:999px; background:#2347FF;
           color:#fff; font-weight:800; font-size:50px; white-space:nowrap; box-shadow:0 0 0 6px rgba(35,71,255,.25), 0 16px 40px rgba(35,71,255,.55); opacity:0">DAPATKAN DI BEG KUNING</div>
      <div id="esub" class="wt" style="position:absolute; left:0; right:0; top:1430px; text-align:center; font-size:38px; font-weight:600; opacity:0">klik beg kuning &darr;</div>''')
rise("#ec", ct["out"] + .05, y=90, sfx="whoosh")
t_b = w(ct, "beg", 17.0)
pill_in("#ebtn", t_b - .1)
A(f'tl.to("#ebtn", {{scale:.93, duration:.09, yoyo:true, repeat:1}}, {t_b + .9});'); E.fx("click-soft", t_b + .9)
A(f'tl.to("#ebtn", {{scale:1.05, duration:.4, yoyo:true, repeat:3, ease:"sine.inOut"}}, {t_b + 1.2});')
fade("#esub", t_b + .5)
A(f'tl.to("#root", {{opacity:0, duration:.4}}, {round(TOTAL - .4, 3)});')

E.music = [(0, .14), (T_HOLD - .2, .14), (T_HOLD + .3, .55), (b4["out"] - .2, .55), (b4["out"] + .3, .14), (TOTAL - 2.8, .14), (TOTAL - 2.5, .5), (TOTAL - .2, 0), (TOTAL, 0)]
write_project(E, os.path.join(ROOT, "v2"), TOTAL, card_lift=False, bg="#F3F3F0")
p = json.load(open(os.path.join(ROOT, "v2/edit-plan.json"))); p["music_file"] = "assets/music/be-chillin.mp3"
json.dump(p, open(os.path.join(ROOT, "v2/edit-plan.json"), "w"), indent=1)
