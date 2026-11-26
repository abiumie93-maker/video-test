"""RtopR Mango Blackhead Mask - 3 videos in the TikTok Shop reference concept (bright grade, gold titles over the head,
cream canvas scenes with photo / flow cards and stamps, serif subtitles with gold italic keywords, beg-kuning CTA bar,
@khalidkacak end card).  Look + helpers come from tiktokshop/tools/gen_ref.py (single source).
Run: python3 tools/gen.py 1|2|3   -> v1/ (Unboxing & apply), v2/ (Part 2: result), v3/ (Sebelum & selepas)"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Edit, write_project, ROOT, WORDS, H

VID = sys.argv[1]
E = Edit()
FT = "assets/footage/"
A_, B1, V_, G_, W_ = "a184402", "b192254", "b192506", "b192646", "b192552"
A = E.add
def r3(x): return round(max(x, 0), 3)
def w(seg, text, near): return E.w(text, near, seg["name"])

# ---------------- shared look + helpers
src = open(os.path.join(ROOT, "..", "tiktokshop", "tools", "gen_ref.py")).read()
exec(src[src.index("# ---------------- look"):src.index("# ---------------- HOOK")])
E.css.append(f"""
  #cam video {{ filter: brightness(1.07) saturate(1.2) contrast(1.06); }}
  #vig {{ background:radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 60%, rgba(25,12,0,.18) 100%); }}
  .pcard {{ position:absolute; background:#fff; padding:16px 16px 0; border-radius:22px; box-shadow:0 24px 50px rgba(110,70,10,.28); z-index:3; opacity:0; }}
  .pcard img {{ display:block; width:100%; border-radius:12px; object-fit:cover; }}
  .pcard .cap {{ font-family:'Anton'; font-size:46px; color:{BR}; text-align:center; padding:14px 6px 18px; line-height:1.05; }}
  .pcard .cap small {{ display:block; font-family:'Montserrat'; font-weight:800; font-size:28px; color:{ORG}; letter-spacing:.04em; margin-top:4px; }}
  .glass {{ position:absolute; left:120px; width:840px; padding:26px 34px; border-radius:26px; background:rgba(28,18,10,.82); border:2px solid rgba(247,194,74,.35);
           font-family:'Montserrat'; font-weight:800; font-size:42px; color:#fff; opacity:0; z-index:6; line-height:1.15; }}
  .glass .k {{ display:block; font-size:28px; letter-spacing:.12em; color:#F7C24A; margin-bottom:6px; }}
  .glass b {{ color:#F7C24A; }}
  .tag {{ position:absolute; left:60px; top:110px; z-index:9; padding:12px 26px; border-radius:999px; font-family:'Anton'; font-size:44px; letter-spacing:.04em;
         color:#2A1A0C; background:linear-gradient(180deg,#FFD873,#F2B33D); box-shadow:0 8px 24px rgba(0,0,0,.3); opacity:0; }}
""")

HTML = E.html
n_ = [0]
def uid(p): n_[0] += 1; return f"{p}{n_[0]}"
def gold_t(html, t0, t1, top=200, size=170):
    i = uid("g"); HTML.append(f'      <div id="{i}" class="goldt" style="top:{top}px; font-size:{size}px">{html}</div>'); gold(f"#{i}", t0, t1); return i
def glass_c(k, html, t0, t1, top=1060):
    i = uid("gl"); HTML.append(f'      <div id="{i}" class="glass" style="top:{top}px"><span class="k">{k}</span>{html}</div>')
    rise(f"#{i}", t0, sfx="pop"); A(f'tl.to("#{i}", {{opacity:0, duration:.2}}, {r3(t1)});'); return i
def tag(text, t0, t1):
    i = uid("tg"); HTML.append(f'      <div id="{i}" class="tag">{text}</div>')
    A(f'tl.fromTo("#{i}", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.35, ease:"expo.out"}}, {r3(t0)});'); A(f'tl.to("#{i}", {{opacity:0, duration:.2}}, {r3(t1)});')
def pcard(img, cap, small, left, top, width, imgh, rot, t0, pos="50% 50%"):
    i = uid("pc")
    sm = f"<small>{small}</small>" if small else ""
    cp = f'<div class="cap">{cap}{sm}</div>' if cap else '<div style="height:16px"></div>'
    el = (f'<div id="{i}" class="pcard" style="left:{left}px; top:{top}px; width:{width}px; transform:rotate({rot}deg)">'
          f'<img src="assets/img/{img}.jpg" style="height:{imgh}px; object-position:{pos}"/>{cp}</div>')
    return i, el, t0
def wcard(text, icon, left, top, width, orange=False, t0=0):
    i = uid("wc")
    return i, f'<div id="{i}" class="wcard{" or" if orange else ""}" style="left:{left}px; top:{top}px; width:{width}px; font-size:46px"><span class="ic">{icon}</span>{text}</div>', t0
def canvas(l1, hl, a_, b_, items, stamps=()):
    cid = uid("cv")
    inner = "".join(el for _, el, _ in items)
    st_html = ""
    for k, (txt, left, top, size, t_) in enumerate(stamps):
        st_html += f'<div id="{cid}s{k}" class="stamp2" style="left:{left}px; top:{top}px; font-size:{size}px; transform:rotate(-6deg)">{txt}</div>'
    HTML.append(f'      <div id="{cid}" class="canvas"><div class="hd"><span class="l1">{l1}</span><br><span class="hl">{hl}</span></div>{inner}{st_html}</div>')
    if a_ <= 0.01:
        A(f'tl.set("#{cid}", {{opacity:1}}, 0); tl.to("#{cid}", {{opacity:0, duration:.25, ease:"power2.in"}}, {r3(b_ - .12)});')
        A(f'tl.set("#{cid} .l1, #{cid} .hl", {{opacity:1}}, 0);')
    else:
        show_canvas(cid, a_, b_); head_in(f"#{cid}", a_)
    for i, _, t_ in items:
        if t_ <= .2: A(f'tl.set("#{i}", {{opacity:1}}, 0);')
        else: rise(f"#{i}", t_)
    for k, (_, _, _, _, t_) in enumerate(stamps):
        stamp(f"#{cid}s{k}", t_)
    CANV.append((a_, b_))
CANV = []
def cta_bar(t_in, t_beg, t_click, t_out, title="DAH ADA DI BEG KUNING", btn="CHECKOUT SEKARANG"):
    HTML.append(f'''      <div id="cta" style="position:absolute; left:110px; right:110px; top:1480px; padding:30px 30px 34px; border-radius:30px; background:rgba(28,18,10,.86);
           border:2px solid rgba(247,194,74,.45); opacity:0; z-index:9; text-align:center">
        <div style="font-family:Montserrat; font-weight:800; font-size:38px; color:#fff; letter-spacing:.06em">{title}</div>
        <div id="cta-b" style="margin:20px auto 0; width:fit-content; display:flex; align-items:center; gap:18px; padding:22px 44px; border-radius:999px;
             background:linear-gradient(180deg,#FFD873,#F2B33D); color:#2A1A0C; font-family:Anton; font-size:58px; box-shadow:0 10px 30px rgba(242,179,61,.45)">
          <svg width="64" height="60" viewBox="0 0 74 70"><path d="M6 22 H68 L60 64 H14 Z" fill="#2A1A0C"/><path d="M22 24 C 22 2, 52 2, 52 24" fill="none" stroke="#2A1A0C" stroke-width="7"/></svg>
          {btn}</div></div>''')
    A(f'tl.fromTo("#cta", {{opacity:0, y:80}}, {{opacity:1, y:0, duration:.45, ease:"expo.out"}}, {r3(t_in)});'); E.fx("whoosh-short", t_in + .05, .4)
    A(f'tl.fromTo("#cta-b", {{scale:.6}}, {{scale:1, duration:.35, ease:"back.out(2)"}}, {r3(t_beg - .1)});'); E.fx("impact-bass-1", t_beg, .45)
    A(f'tl.to("#cta-b", {{scale:.93, duration:.09, yoyo:true, repeat:1}}, {r3(t_click)});'); E.fx("click-soft", t_click)
    A(f'tl.to("#cta-b", {{scale:1.06, duration:.35, yoyo:true, repeat:3, ease:"sine.inOut"}}, {r3(t_click + .4)});')
    A(f'tl.to("#cta", {{opacity:0, duration:.25}}, {r3(t_out)});')
def end_card(t0, line="FOLLOW UNTUK REVIEW JUJUR"):
    HTML.append(f'''      <div id="end" style="position:absolute; inset:0; opacity:0; z-index:10; background:radial-gradient(ellipse at 50% 45%, rgba(42,29,18,.92), rgba(14,10,7,.97))">
        <div style="position:absolute; left:0; right:0; top:690px; text-align:center; font-family:Montserrat; font-weight:800; font-size:44px; letter-spacing:.14em; color:#F7C24A">{line}</div>
        <div id="end-sb" style="position:absolute; left:170px; right:170px; top:800px; height:120px; border-radius:24px; background:#fff; display:flex; align-items:center; gap:22px; padding:0 34px;
             box-shadow:-6px 0 0 #25F4EE, 6px 0 0 #FE2C55, 0 20px 50px rgba(0,0,0,.5)">
          <span style="font-size:52px">&#128269;</span><span id="end-tx" style="font-family:Montserrat; font-weight:700; font-size:52px; color:#161616; display:inline-block; overflow:hidden; white-space:nowrap; width:0">@khalidkacak</span></div>
      </div>''')
    A(f'tl.to("#end", {{opacity:1, duration:.4}}, {r3(t0)});'); E.fx("whoosh", t0, .4)
    A(f'tl.fromTo("#end-sb", {{scale:.8, opacity:0}}, {{scale:1, opacity:1, duration:.4, ease:"back.out(1.6)"}}, {r3(t0 + .3)});')
    A(f'tl.to("#end-tx", {{width:"440px", duration:1.0, ease:"steps(12)"}}, {r3(t0 + .8)});'); E.fx("click-soft", t0 + 1.85, .5)
def montage(clips, labels):
    """music-only stretch: list of (clip, ms, dur); labels: big gold-ish lower labels per shot (or None)."""
    t = E.hold(sum(d for _, _, d in clips)) if False else None
    start = E.t
    for (cl, ms, du), lab in zip(clips, labels):
        E.shot(E.t, du, FT + cl + ".mp4", ms)
        E.fx("whoosh-short", E.t, .4)
        E.zoom.append((round(E.t + .02, 3), "slow", 1.12, 0))
        if lab:
            i = uid("ml")
            HTML.append(f'      <div id="{i}" class="goldt" style="top:1340px; font-size:120px">{lab}</div>')
            A(f'tl.fromTo("#{i}", {{opacity:0, scale:1.4, filter:"blur(10px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.28, ease:"expo.out"}}, {r3(E.t + .1)});')
            A(f'tl.to("#{i}", {{opacity:0, duration:.18}}, {r3(E.t + du - .2)});')
        E.t = round(E.t + du, 3)
    return start, E.t

# ======================================================================== VIDEO 1: UNBOXING & APPLY
if VID == "1":
    h = E.say("h", 7.80, 21.07, clip=A_)        # muka nampak okey... tapi banyak gila whitehead dengan blackhead
    s1 = E.say("s1", 23.25, 31.79, clip=A_)     # wife beritahu... insecure
    s3 = E.say("s3", 43.35, 55.68, clip=A_)     # bau mangga, Mango Blackhead Mask, beg kuning ramai review positif
    s4 = E.say("s4", 65.54, 76.62, clip=A_)     # dalam kotak: solution + kertas
    s5 = E.say("s5", 79.22, 93.50, clip=A_)     # cara: letak dan biarkan 10 minit
    s6 = E.say("s6", 95.79, 100.54, clip=A_)    # bentuk macam gum, bubble gum
    for s in (h, s1, s3, s4, s5, s6): E.synced(s)
    m0, m1 = montage([(A_, 107.0, 1.8), (A_, 118.0, 1.8)], ["SAPU", "KAT HIDUNG"])
    s7 = E.say("s7", 141.86, 148.67, clip=A_)   # ambil kertas, tarik macam ni
    s8 = E.say("s8", 151.84, 153.70, clip=A_)   # first letak tengah-tengah
    s10 = E.say("s10", 221.61, 229.59, clip=A_) # done, biarkan sepuluh minit, tunggu sekejap
    for s in (s7, s8, s10): E.synced(s)
    T_END = E.hold(5.2)
    E.shot(T_END, 5.2, FT + "b192727.mp4", 1.0, style="filter:blur(24px) brightness(.75)")
    TOTAL = round(E.t, 3); o = E.o
    # hook
    HTML.append('      <div id="hk-s" class="script" style="top:140px; font-size:62px">Guys, muka saya nampak&hellip;</div>')
    A('tl.set("#hk-s", {opacity:1}, 0);')
    g0 = gold_t("OKEY<br>KAN?", 0, w(h, "Tapi", 16.5) - .2, top=210, size=200); A(f'tl.set("#{g0}", {{opacity:1}}, 0);')
    E.fx("impact-bass-1", .05, .45)
    A(f'tl.to("#hk-s", {{opacity:0, duration:.2}}, {r3(w(h, "Tapi", 16.5) - .2)});')
    gold_t("PENUH<br>BLACKHEAD!", w(h, "Banyak", 18.5) - .1, s1["out"] - .2, top=210, size=190)
    HTML.append('''      <div id="hk-p" class="pcard" style="left:600px; top:1040px; width:380px; transform:rotate(5deg); z-index:7"><img src="assets/img/strip.jpg" style="height:380px"/>
        <div class="cap">SPOILER<small>result di Part 2 &#128064;</small></div></div>''')
    rise("#hk-p", w(h, "black", 20.3), sfx="pop"); A(f'tl.to("#hk-p", {{opacity:0, duration:.2}}, {r3(s1["out"] + .3)});')
    tag("PART 1: UNBOXING &amp; APPLY", .3, s1["out"] - .1)
    # s1 wife
    glass_c("WIFE SAYA TEGUR&hellip;", '&ldquo;Bang, muka bang ni <b>banyak gila blackhead</b>&rdquo;', w(s1, "Kata", 25.8) - .2, s3["out"] - .25)
    gold_t("INSECURE!", w(s1, "insecure", 30.6) - .1, s3["out"] - .2, top=220, size=200)
    # s3 product
    canvas("RtopR Mango", "Blackhead Mask", s3["out"], s4["out"], [
        pcard("box", "RTOPR", "mango blackhead mask", 110, 420, 420, 560, -4, s3["out"] + .3),
        wcard("Bau mangga", "&#129389;", 580, 470, 420, False, w(s3, "mangga", 44.1) - .1),
        wcard("Ramai review", "&#11088;", 580, 650, 420, True, w(s3, "review", 52.1) - .2),
        wcard("Feedback positif", "&#128077;", 580, 830, 420, True, w(s3, "positif", 55.2) - .4),
    ], stamps=[("VIRAL DI TIKTOK!", 140, 1180, 64, s3["out"] + .8)])
    # s4 dalam kotak
    canvas("Dalam kotak", "dapat 2 benda", s4["out"], s5["out"], [
        pcard("bottle", "1 BOTOL", "solution / mask", 90, 430, 430, 560, -3, w(s4, "bekas", 68.7) - .2),
        pcard("paper", "KERTAS", "untuk hidung", 560, 470, 430, 520, 3, w(s4, "kertas", 73.6) - .2),
    ])
    # s5 cara guna
    canvas("Cara guna", "simple je", s5["out"], s6["out"], [
        wcard("Sapu", "1", 240, 470, 600, False, o(83.0, "s5")),
        wcard("Tampal kertas", "2", 240, 650, 600, False, o(86.6, "s5")),
        wcard("Tunggu 10 minit", "3", 240, 830, 600, True, o(89.5, "s5")),
        wcard("Tarik!", "4", 240, 1010, 600, True, o(91.6, "s5")),
    ], stamps=[("10 MINIT JE!", 330, 1220, 70, o(91.0, "s5"))])
    # s6 bubble gum
    gold_t("BAU MACAM<br>BUBBLE GUM!", w(s6, "Macam", 97.8) - .1, s6["out"] + s6["dur"] * 0 + 4.8 - .1, top=210, size=170)
    # s7-9 kertas
    glass_c("LANGKAH 2", "Tarik kertas, tampal <b>tengah</b> dulu, lepas tu <b>tepi</b>", s7["out"] + .2, s10["out"] - .2)
    gold_t("TENGAH<br>DULU", w(s8, "first", 151.9), s10["out"] - .1, top=200, size=190)
    # s10 done -> wait
    gold_t("TUNGGU<br>10 MINIT&hellip;", w(s10, "biarkan", 225.2) - .2, T_END - .1, top=200, size=180)
    canvas("Result dia?", "tengok Part 2", T_END, T_END + 2.6, [
        pcard("strip", None, None, 300, 430, 480, 560, -3, T_END + .2, pos="50% 50%"),
    ], stamps=[("PART 2 &rarr;", 360, 1100, 90, T_END + .6)])
    end_card(T_END + 2.6)
    SUB_CUT = []
    E.music = [(0, .11), (m0 - .3, .11), (m0 + .2, .5), (m1 - .2, .5), (m1 + .3, .11), (T_END - .3, .11), (T_END + .3, .5), (TOTAL - .4, 0), (TOTAL, 0)]

# ======================================================================== VIDEO 2: RESULT
if VID == "2":
    h = E.say("h", 0.00, 7.45, clip=G_)          # Tengoklah, Ya Allah, biar betul... sekali pakai je banyak macam ni
    s1 = E.say("s1", 14.38, 26.44, clip=B1)      # selepas 10 minit, kita try cabut... so kita cuba eh
    E.synced(h); E.synced(s1)
    m0, m1 = montage([(B1, 30.0, 1.6), (B1, 38.0, 1.6), (B1, 47.0, 1.8)], ["TARIK&hellip;", "PERLAHAN&hellip;", None])
    s2 = E.say("s2", 57.67, 72.84, clip=B1)      # korang tengok sendiri, nampak tak? wow... besar macam ni
    s3 = E.say("s3", 80.79, 88.85, clip=B1)      # memang betullah, boleh cabut banyak... banyak betul
    s4 = E.say("s4", 0.00, 5.43, clip=W_)        # Tengoklah guys. Wah, ambik kau. Memang betul-betul fungsinya
    s5 = E.say("s5", 9.14, 12.74, clip=V_)       # memang boleh cakap... memang fungsi
    s6 = E.say("s6", 19.94, 24.49, clip=V_)      # nampak kesan on the spot selepas 10 minit
    s7 = E.say("s7", 44.56, 57.60, clip=V_)      # pernah cabut sendiri sakit; ni tak sakit; geng lelaki; beg kuning; approved
    for s in (s2, s3, s4, s5, s6, s7): E.synced(s)
    T_END = E.hold(3.0)
    E.shot(T_END, 3.0, FT + "b192727.mp4", 1.0, style="filter:blur(24px) brightness(.75)")
    TOTAL = round(E.t, 3); o = E.o
    HTML.append('      <div id="hk-s" class="script" style="top:140px; font-size:62px">Ya Allah, biar betul&hellip;</div>')
    A('tl.set("#hk-s", {opacity:1}, 0);')
    g0 = gold_t("SEKALI PAKAI<br>JE?!", 0, s1["out"] - .2, top=210, size=180); A(f'tl.set("#{g0}", {{opacity:1}}, 0);')
    E.fx("impact-bass-1", .05, .45)
    A(f'tl.to("#hk-s", {{opacity:0, duration:.2}}, {r3(s1["out"] - .2)});')
    glass_c("BLACKHEAD &amp; WHITEHEAD", 'Banyak <b>macam ni</b> keluar dari hidung saya!', w(h, "banyak", 6.3) - .5, s1["out"] - .2)
    tag("PART 2: RESULT", .3, s1["out"] + 3)
    gold_t("SELEPAS<br>10 MINIT", w(s1, "selepas", 15.5) - .1, m0 - .2, top=200, size=180)
    E.fx("riser", m1 - 3.3, .25)
    gold_t("NAMPAK<br>TAK?!", w(s2, "Nampak", 60.6) - .1, w(s2, "Ni", 66.2) - .2, top=200, size=200)
    gold_t("WOW!", w(s2, "Wow.", 70.1) - .1, s3["out"] - .2, top=220, size=240)
    canvas("Banyak betul", "whitehead &amp; blackhead", s3["out"], s4["out"], [
        pcard("strip", "KERTAS", "lepas tarik", 90, 430, 440, 560, -3, s3["out"] + .25),
        pcard("strip2", "ZOOM IN", "blackhead ditarik keluar", 560, 470, 430, 520, 3, w(s3, "Tengok", 86.6) - .3),
    ], stamps=[("BETUL-BETUL CABUT!", 160, 1180, 62, w(s3, "banyak", 88.4) - .2)])
    gold_t("BETUL-BETUL<br>FUNGSI!", w(s4, "fungsinya", 4.9) - .5, s5["out"] - .2, top=200, size=170)
    glass_c("NAMPAK KESAN", '<b>On the spot</b>, selepas <b>10 minit</b> je', s6["out"] + .1, s7["out"] - .2)
    glass_c("PERNAH CABUT SENDIRI?", 'Sakit! Yang ni <b>tak sakit langsung</b>', w(s7, "sakit", 47.1) - .2, w(s7, "kalau", 52.5) - .3)
    gold_t("GENG LELAKI<br>WAJIB CUBA", w(s7, "lelaki", 51.9) - .5, w(s7, "kalau", 52.5) + .6, top=200, size=160)
    cta_bar(w(s7, "kalau", 52.5) - .1, w(s7, "beg", 55.7), w(s7, "Approved!", 57.1) - .2, T_END + .3)
    end_card(T_END)
    E.music = [(0, .11), (m0 - .3, .11), (m0 + .2, .5), (m1 - .2, .5), (m1 + .3, .11), (T_END - .3, .11), (T_END + .3, .5), (TOTAL - .4, 0), (TOTAL, 0)]

# ======================================================================== VIDEO 3: SEBELUM & SELEPAS
if VID == "3":
    h = E.say("h", 0.00, 7.45, clip=G_)          # result hook
    s1 = E.say("s1", 7.80, 21.07, clip=A_)       # SEBELUM: muka okey tapi banyak blackhead
    s2 = E.say("s2", 7.45, 26.31, clip=G_)       # cara guna ringkas (VO over apply footage)
    s3 = E.say("s3", 57.67, 72.84, clip=B1)      # SELEPAS: nampak tak? wow
    s4 = E.say("s4", 24.49, 35.05, clip=V_)      # kali pertama... banyak gila, warna hitam
    s5 = E.say("s5", 26.31, 32.52, clip=G_)      # tak sakit langsung, beg kuning, approved
    E.synced(h); E.synced(s1)
    # s2 voice-over covered with the unboxing / apply footage
    t = s2["out"]
    for cl, ms, du in [("a184541", 0.8, 2.4), ("a184523", 0.6, 2.2), ("a184532", 0.6, 2.0), (A_, 110.0, 3.0), (A_, 152.5, 2.6), (A_, 200.0, 2.8)]:
        E.shot(t, du, FT + cl + ".mp4", ms); E.zoom.append((round(t + .02, 3), "slow", 1.1, 0)); t += du
    E.shot(t, s3["out"] - t, FT + "b192727.mp4", 0.5)
    E.synced(s3); E.synced(s4); E.synced(s5)
    T_END = E.hold(3.0)
    E.shot(T_END, 3.0, FT + "b192727.mp4", 1.0, style="filter:blur(24px) brightness(.75)")
    TOTAL = round(E.t, 3); o = E.o
    # hook: split before/after canvas over the result voice
    canvas("Sebelum vs", "selepas 10 minit", 0.0, s1["out"] - .05, [
        pcard("nose_before", "SEBELUM", "nampak okey je&hellip;", 80, 420, 440, 520, -4, .15),
        pcard("strip", "SELEPAS", "ya Allah, banyaknya!", 560, 460, 440, 480, 4, w(h, "biar", 2.1) - .2),
    ], stamps=[("SEKALI PAKAI JE!", 230, 1150, 72, w(h, "sekali", 5.5) - .1)])
    E.fx("impact-bass-1", .05, .45)
    tag("SEBELUM", s1["out"] + .1, s1["out"] + s1["dur"] - .2)
    gold_t("NAMPAK<br>OKEY KAN?", s1["out"] + .3, o(16.4, "s1"), top=210, size=180)
    gold_t("PENUH<br>BLACKHEAD!", o(18.5, "s1") - .1, s2["out"] - .2, top=210, size=190)
    glass_c("RTOPR MANGO BLACKHEAD MASK", 'Dapat <b>mask</b> + <b>kertas</b> sekali', s2["out"] + .2, o(17.2, "s2"))
    canvas("Cara guna", "senang je", o(17.3, "s2"), o(23.0, "s2"), [
        wcard("Sapu kat hidung", "1", 220, 470, 640, False, o(17.4, "s2")),
        wcard("Tampal kertas", "2", 220, 650, 640, False, o(19.9, "s2")),
        wcard("Tunggu 5-10 minit", "3", 220, 830, 640, True, o(21.1, "s2")),
    ], stamps=[("SELESAI!", 380, 1060, 80, o(22.4, "s2"))])
    tag("SELEPAS", o(23.0, "s2"), s4["out"] + s4["dur"] - .2)
    gold_t("NAMPAK<br>TAK?!", w(s3, "Nampak", 60.6) - .1, w(s3, "Ni", 66.2) - .2, top=200, size=200)
    gold_t("WOW!", w(s3, "Wow.", 70.1) - .1, s4["out"] - .2, top=220, size=240)
    glass_c("KALI PERTAMA CABUT", 'Memang <b>banyak gila</b>, ada <b>warna hitam</b>!', s4["out"] + .3, s5["out"] - .2)
    canvas("Sebelum", "vs selepas", s5["out"] - .05, s5["out"] + 2.6, [
        pcard("nose_before", "SEBELUM", None, 80, 420, 430, 520, -4, s5["out"] + .1),
        pcard("strip2", "SELEPAS", None, 560, 450, 430, 500, 4, s5["out"] + .4),
    ])
    glass_c("PALING BEST", '<b>Tak sakit langsung!</b>', w(s5, "tak", 28.1) - .2, w(s5, "dapatkan", 29.6) - .2, top=1180)
    cta_bar(w(s5, "dapatkan", 29.6) - .2, w(s5, "Kuning.", 30.9) - .1, w(s5, "Approved!", 31.8) - .15, T_END + .3)
    end_card(T_END)
    E.music = [(0, .12), (T_END - .3, .12), (T_END + .3, .5), (TOTAL - .4, 0), (TOTAL, 0)]

# ---------------- camera (talking parts)
o = E.o
for i, c_ in enumerate(E.cuts()):
    E.zoom.append((c_, "set", *[(1.0, 0), (1.06, 10), (1.03, -8)][i % 3]))
for s in E.vo:
    if s["dur"] > 3.5:
        E.zoom.append((round(s["out"] + s["dur"] / 2, 3), "ease", 1.1, 0))

# ---------------- subtitles (all voice segments; stacked whisper words re-timed)
KEY = re.compile(r"(?i)^(blackhead|whitehead|black|white|rtop|artop|mango|mangga|gum|kertas|hidung|minit|sapu|tarik|cabut|banyak|wow|fungs|sakit|"
                 r"kuning|beg|approved|insecure|okey|review|positif|lelaki|spot|10|sepuluh|tiktok)")
FIX = {"wash": "wife", "Rtop": "RtopR", "Artop": "RtopR", "artop": "RtopR", "Rni": "", "bladehead": "blackhead", "funsyen": "fungsi", "fungsin": "fungsi",
       "pipe": "", "Bek": "beg", "hit": "head", "rezak": "hasil", "mas.": "mask.", "big": "black", "Wanita": "Yang", "main": "ni", "idung": "hidung",
       "Kau": "Korang", "Selai": "Helai"}
words = []
for s in E.vo:
    for x in WORDS:
        if x["file"] != s["clip"] or not (s["src_in"] - .05 <= x["start"] < s["src_out"] - .05):
            continue
        txt = x["text"]
        for k_, v_ in FIX.items():
            if txt.startswith(k_): txt = v_ + txt[len(k_):]
        if txt in ("R.", "R", "orang", "") or not txt.strip(".,?!"):
            if txt == "orang" and words and words[-1][1] == "Korang": continue
            if txt in ("R.", "R", ""): continue
        words.append([round(s["out"] + x["start"] - s["src_in"], 3), txt])
words.sort()
i = 0
while i < len(words):
    j = i
    while j + 1 < len(words) and words[j + 1][0] <= words[i][0] + .02: j += 1
    if j > i:
        nxt = words[j + 1][0] if j + 1 < len(words) else words[i][0] + .3 * (j - i + 1)
        step = (nxt - words[i][0]) / (j - i + 1)
        for m in range(i, j + 1): words[m][0] = round(words[i][0] + step * (m - i), 3)
    i = j + 1
seg_end = {round(s["out"] + s["dur"], 3) for s in E.vo}
chunks, cur = [], []
for t0, txt in words:
    if cur and any(cur[-1][0] < e <= t0 for e in seg_end):
        chunks.append(cur); cur = []
    cur.append((t0, txt))
    if txt[-1:] in ".?!," or len(cur) >= 4:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
for i, ch in enumerate(chunks):
    t0 = ch[0][0]; t1 = chunks[i + 1][0][0] if i + 1 < len(chunks) else t0 + 2
    ends = [e for e in seg_end if e > t0]
    t1 = min(t1, t0 + 2.6, min(ends) + .1 if ends else t1)
    t1 = max(t1, t0 + .35)
    dk_win = [y_ for x_, y_ in CANV if x_ - .05 <= t0 < y_]
    if dk_win: t1 = min(t1, dk_win[0] + .05)
    words_ = " ".join(f"<i>{t.strip('.,?!')}</i>{t[len(t.strip('.,?!')):]}" if KEY.match(t) else t for _, t in ch)
    dk = any(x_ - .05 <= t0 < y_ for x_, y_ in CANV)
    sid = f"sb{i}"
    HTML.append(f'      <div id="{sid}" class="sub{" dk" if dk else ""}">{words_}</div>')
    A(f'tl.fromTo("#{sid}", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:.12}}, {r3(t0 - .05)});')
    A(f'tl.to("#{sid}", {{opacity:0, duration:.08}}, {r3(t1 - .06)});')

write_project(E, os.path.join(ROOT, f"v{VID}"), TOTAL, card_lift=False, bg="#000")
p = json.load(open(os.path.join(ROOT, f"v{VID}/edit-plan.json"))); p["music_file"] = "assets/music/be-chillin.mp3"
json.dump(p, open(os.path.join(ROOT, f"v{VID}/edit-plan.json"), "w"), indent=1)
