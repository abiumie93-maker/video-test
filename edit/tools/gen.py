"""Generate the HyperFrames edit: cut list, punch-ins, motion-graphic scenes, SFX.
All graphic anchors are written in SOURCE seconds and mapped to output time."""
import json, os, sys

PROJ = sys.argv[1]
W, H = 1080, 1920

# ---- Edit decision list (source in/out, seconds). Cuts snapped to real silence gaps.
EDL = [
    ("hook", 45.10, 51.75),   # cold open: strongest line
    ("a",     0.00, 53.50),   # question -> catat rutin -> lifestyle 10 tahun
    ("b",    63.20, 84.18),   # (cut repeat "umur 30 ... 10 tahun ke belakang")
    ("c",    85.24, 108.62),  # (cut "Buat yang itu dulu")
    ("d",   109.88, 176.21),  # (cut "Cuba buat yang itu dulu")
    ("e",   178.30, 255.55),  # (cut "Pukul itu pukul 2 pagi baru nak tidur")
    ("f",   257.62, 291.20),  # (cut "Dan dekat situlah pentingnya kat sini")
]
segs, t = [], 0.0
for name, a, b in EDL:
    segs.append(dict(name=name, src_in=a, src_out=b, out=round(t, 3), dur=round(b - a, 3)))
    t += b - a
TOTAL = round(t, 3)


def out(src, seg=None):
    """Map a source time to output time (first non-hook segment that holds it)."""
    for s in segs:
        if seg and s["name"] != seg:
            continue
        if not seg and s["name"] == "hook":
            continue
        if s["src_in"] <= src <= s["src_out"]:
            return round(s["out"] + src - s["src_in"], 3)
    raise ValueError(f"source {src} was cut")


# ---- Camera: hard re-frame on every cut, smooth zoom in/out on sentence starts, fast punch on key words.
WORDS = json.load(open(os.path.join(PROJ, "transcript.json")))
CUTS = [s["out"] for s in segs] + [TOTAL]
LEVELS = [(1.12, 0), (1.0, 0), (1.2, -24), (1.05, 18), (1.15, 22), (1.0, 0), (1.24, -16), (1.08, 0)]
PUNCH_SRC = [46.0, 87.5, 184.64, 202.56, 213.02, 224.28, 233.6, 247.8, 264.7]  # zoom slam on these words
ZOOM = []  # (out_t, kind, scale, x)
def seg_bounds(t):
    for i in range(len(CUTS) - 1):
        if CUTS[i] <= t < CUTS[i + 1]:
            return CUTS[i], CUTS[i + 1]
    return CUTS[-2], CUTS[-1]
for i, c in enumerate(CUTS[:-1]):
    ZOOM.append((c, "set", *([(1.1, 0), (1.0, 0), (1.08, 12), (1.0, -10)][i % 4])))
punch_out = []
for src in PUNCH_SRC:
    try: punch_out.append(out(src))
    except ValueError: pass
cands = []
for n in range(1, len(WORDS)):
    if WORDS[n - 1]["text"].strip()[-1:] in ".?!":
        for s in segs:
            if s["src_in"] + 0.05 <= WORDS[n]["start"] <= s["src_out"] - 0.05:
                cands.append(round(s["out"] + WORDS[n]["start"] - s["src_in"], 3))
k, last = 0, -9
for t in sorted(set(cands)):
    a, b = seg_bounds(t)
    if t - a < 0.8 or b - t < 0.9 or t - last < 2.2:
        continue
    if any(abs(t - p) < 1.3 for p in punch_out):
        continue
    sc_, x_ = LEVELS[k % len(LEVELS)]; k += 1
    ZOOM.append((t, "ease", sc_, x_)); last = t
for p in punch_out:
    a, b = seg_bounds(p)
    if b - p > 0.4:
        ZOOM.append((round(p - 0.05, 3), "punch", 1.26, 0))
ZOOM.sort()

# ---- Scenes (motion graphics). start/end in source seconds.
SCENES = [
    dict(id="hook",   start=0.0,            end=segs[0]["dur"], kind="hook"),
    dict(id="soalan", start=out(0.30),      end=out(8.60),      kind="soalan"),
    dict(id="sendiri", start=out(41.30),    end=out(53.40),     kind="sendiri"),
    dict(id="cermin", start=out(96.50),     end=out(108.55),    kind="cermin"),
    dict(id="jumpa",  start=out(109.95),    end=out(117.85),    kind="jumpa"),
    dict(id="masa",   start=out(226.50),    end=out(232.45),    kind="masa"),
    dict(id="sel",    start=out(232.55),    end=out(240.80),    kind="sel"),
    dict(id="graf",   start=out(240.90),    end=out(249.25),    kind="graf"),
    dict(id="langkah", start=out(257.70),   end=out(272.95),    kind="langkah"),
    dict(id="catat",  start=out(11.02),     end=out(41.15),     kind="catat"),
    dict(id="umur",   start=out(63.25),     end=out(72.20),     kind="umur"),
    dict(id="bukan",  start=out(72.40),     end=out(81.05),     kind="bukan"),
    dict(id="fomo",   start=out(86.60),     end=out(96.40),     kind="fomo"),
    dict(id="rutin",  start=out(117.90),    end=out(187.50),    kind="rutin"),
    dict(id="hutang", start=out(189.80),    end=out(226.40),    kind="hutang"),
    dict(id="kunci",  start=out(249.30),    end=out(255.50),    kind="kunci"),
    dict(id="badan",  start=out(273.00),    end=out(277.95),    kind="badan"),
    dict(id="cta",    start=out(278.50),    end=out(290.90),    kind="cta"),
]
for s in SCENES:
    s["dur"] = round(s["end"] - s["start"], 3)


def L(sc, src):
    """Scene-local time for a source anchor."""
    return round(out(src) - sc["start"], 3)


SFX = []  # (id, file, out_time_of_visual_hit, peak_offset, volume)
PEAK = {"whoosh": 0.162, "whoosh-short": 0.162, "pop": 0.12, "impact-bass-1": 0.073,
        "riser": 3.472, "click-soft": 0.05, "notification": 0.229, "error": 0.745}
DUR = {"whoosh": 0.574, "whoosh-short": 0.574, "pop": 0.72, "impact-bass-1": 2.115, "riser": 4.3,
       "click-soft": 0.365, "notification": 1.5, "error": 1.0}
VOL = {"whoosh": 0.45, "whoosh-short": 0.35, "pop": 0.55, "impact-bass-1": 0.32, "riser": 0.18,
       "click-soft": 0.5, "notification": 0.35, "error": 0.9}


def sfx(name, at):
    SFX.append((name, at))


CSS_BASE = """
  @font-face { font-family:'Caveat'; font-weight:700; src:url('assets/fonts/caveat-700.woff2') format('woff2'); }
  @font-face { font-family:'Permanent Marker'; src:url('assets/fonts/permanent-marker.woff2') format('woff2'); }
  #root { position:absolute; inset:0; overflow:visible; }
  .paper { position:absolute; left:120px; width:660px; box-sizing:border-box; background:#FFF8E7; border-radius:12px;
           box-shadow:0 18px 44px rgba(0,0,0,.38); color:#1d1d1f; }
  .paper::before { content:""; position:absolute; left:50%; top:-16px; width:150px; height:34px; margin-left:-75px;
                   background:rgba(255,201,40,.75); border-radius:3px; }
  .ink { fill:none; stroke:#1d1d1f; stroke-width:6; stroke-linecap:round; stroke-linejoin:round;
         stroke-dasharray:1; stroke-dashoffset:1; }
  .ink.r { stroke:#E63434; } .ink.g { stroke:#1FA855; } .ink.y { stroke:#F2B705; } .ink.thick { stroke-width:12; }
  .hand { position:absolute; font-family:'Caveat',cursive; font-weight:700; color:#1d1d1f; line-height:1; white-space:nowrap;
          clip-path:inset(0 100% 0 0); }
  .mk { font-family:'Permanent Marker',cursive; font-weight:400; }
  .hand.r { color:#E63434; } .hand.g { color:#1FA855; } .hand.b { color:#1F5FD1; }
  .card { position:absolute; left:120px; width:660px; box-sizing:border-box;
          background:rgba(12,18,38,.86); border-radius:28px; padding:28px 34px;
          box-shadow:0 18px 50px rgba(0,0,0,.35); color:#fff; font-family:'Montserrat',sans-serif; }
  .eyebrow { font-family:'Montserrat',sans-serif; font-weight:800; font-size:28px; letter-spacing:.14em;
             color:#FFC928; text-transform:uppercase; }
  .big { font-family:'Archivo Black',sans-serif; color:#fff; text-transform:uppercase; line-height:1.02; }
  .y { color:#FFC928; }
  .r { color:#FF4D4D; }
"""


def scene_html(sc, css, markup, js):
    i = sc["id"]
    return f"""<template>
  <style>{CSS_BASE}{css}</style>
  <div id="root" data-composition-id="{i}" data-width="{W}" data-height="{H}">
{markup}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{i}"] = tl;
  </script>
</template>
"""


def card_in(sel, t, y=40):
    return (f'    tl.fromTo("{sel}", {{opacity:0, y:{y}, scale:.96}}, '
            f'{{opacity:1, y:0, scale:1, duration:.45, ease:"expo.out"}}, {t});\n')


def card_out(sel, t):
    return f'    tl.to("{sel}", {{opacity:0, y:-20, filter:"blur(6px)", duration:.25, ease:"power2.in"}}, {t});\n'


def word_in(sel, t, stagger=.08):
    return (f'    tl.fromTo("{sel}", {{opacity:0, filter:"blur(8px)"}}, '
            f'{{opacity:1, filter:"blur(0px)", duration:.16, ease:"power4.out", stagger:{stagger}}}, {t});\n')


def pop_in(sel, t):
    return (f'    tl.fromTo("{sel}", {{opacity:0, scale:.6}}, '
            f'{{opacity:1, scale:1, duration:.38, ease:"back.out(1.6)"}}, {t});\n')


def build(sc):
    k, d = sc["kind"], sc["dur"]
    end = round(d - 0.3, 3)
    st = sc["start"]
    if k == "hook":
        css = """
  #hk-scrim { position:absolute; left:0; right:0; bottom:0; height:1000px;
              background:linear-gradient(to bottom, rgba(0,0,0,0), rgba(0,0,0,.55) 55%, rgba(0,0,0,.7)); }
  #hk-box { position:absolute; left:110px; right:110px; top:930px; text-align:center; }
  #hk-l1 { font-size:58px; } #hk-l2 { font-size:104px; margin-top:6px; } #hk-l3 { font-size:58px; margin-top:6px; }
  .w { display:inline-block; }
"""
        markup = """    <div id="hk-scrim"></div>
    <div id="hk-box">
      <div id="hk-l1" class="big"><span class="w">Penyakit</span> <span class="w">hari</span> <span class="w">ini</span></div>
      <div id="hk-l2" class="big y"><span class="w">=&nbsp;Lifestyle</span></div>
      <svg id="hk-ul" width="620" height="40" viewBox="0 0 620 40" style="display:block;margin:-6px auto 0"><path class="ink y thick" pathLength="1" d="M20 24 C 160 8, 330 34, 600 14"/></svg>
      <div id="hk-l3" class="big"><span class="w">10</span> <span class="w">tahun</span> <span class="w">lepas</span></div>
    </div>"""
        # first line on screen at frame 0 (thumbnail), rest lands on the words
        js = ('    tl.set("#hk-l1 .w", {opacity:1}, 0);\n'
              '    tl.fromTo("#hk-scrim", {opacity:.0}, {opacity:1, duration:.3}, 0);\n'
              + word_in("#hk-l2 .w", round(48.25 - 45.10, 2))
              + word_in("#hk-l3 .w", round(50.15 - 45.10, 2), .1)
              + f'    tl.fromTo("#hk-ul path", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:.45, ease:"power2.out"}}, {round(48.9-45.10,2)});\n'
              + f'    tl.fromTo("#hk-l2", {{scale:1.25}}, {{scale:1, duration:.5, ease:"expo.out"}}, {round(48.25-45.10,2)});\n'
              + f'    tl.to("#hk-box, #hk-scrim", {{opacity:0, filter:"blur(8px)", duration:.2, ease:"power2.in"}}, {round(d-0.22,3)});\n')
        sfx("impact-bass-1", round(48.25 - 45.10, 2))
        sfx("whoosh", segs[1]["out"])
        return css, markup, js
    if k == "catat":
        items = [("Bangun pukul berapa", 19.12), ("Sarapan apa", 21.14), ("Bergerak / duduk je?", 24.45),
                 ("Makan tengah hari", 25.86), ("Balik kerja & makan malam", 30.94), ("Tidur pukul berapa", 37.71)]
        css = """
  #ct-card { top:800px; padding:22px 30px 18px; }
  #ct-title { font-family:'Archivo Black',sans-serif; font-size:40px; margin:4px 0 6px; }
  .ct-row { display:flex; align-items:center; gap:16px; font-weight:700; font-size:30px; padding:5px 0; opacity:0; }
  .ct-box { width:34px; height:34px; border-radius:8px; border:4px solid #FFC928; flex:none; position:relative; }
  .ct-tick { position:absolute; left:6px; top:-2px; width:12px; height:22px; border:solid #FFC928;
             border-width:0 6px 6px 0; transform:rotate(45deg); }
"""
        rows = "\n".join(f'      <div class="ct-row" id="ct-r{n}"><div class="ct-box"><div class="ct-tick" id="ct-t{n}"></div></div>{txt}</div>'
                         for n, (txt, _) in enumerate(items))
        markup = f"""    <div id="ct-card" class="card">
      <div class="eyebrow">Langkah 1</div>
      <div id="ct-title">Catat rutin harian</div>
{rows}
    </div>"""
        js = card_in("#ct-card", 0.1)
        sfx("whoosh-short", st + 0.1)
        for n, (_, src) in enumerate(items):
            lt = L(sc, src)
            js += (f'    tl.fromTo("#ct-r{n}", {{opacity:0, x:-24}}, {{opacity:1, x:0, duration:.3, ease:"expo.out"}}, {lt});\n'
                   f'    tl.fromTo("#ct-t{n}", {{opacity:0, scale:0}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {round(lt+.15,3)});\n')
            sfx("pop", st + lt + 0.15)
        js += card_out("#ct-card", end)
        return css, markup, js
    if k == "umur":
        css = """
  #um-card { top:980px; padding:30px 38px; }
  #um-row { display:flex; justify-content:space-between; align-items:flex-end; margin-top:8px; }
  .um-age { font-family:'Archivo Black',sans-serif; font-size:30px; text-align:center; }
  .um-age b { display:block; font-size:76px; line-height:1; }
  #um-track { position:relative; height:16px; border-radius:8px; background:rgba(255,255,255,.18); margin:18px 0 10px; }
  #um-fill { position:absolute; left:0; top:0; bottom:0; width:100%; border-radius:8px;
             background:linear-gradient(90deg,#FFC928,#FF4D4D); transform-origin:left center; }
  #um-cap { font-weight:700; font-size:30px; text-align:center; }
"""
        markup = """    <div id="um-card" class="card">
      <div class="eyebrow">Pengalaman saya</div>
      <div id="um-row"><div class="um-age" id="um-a">UMUR<b>20</b></div><div class="um-age r" id="um-b">UMUR<b>30</b></div></div>
      <div id="um-track"><div id="um-fill"></div></div>
      <div id="um-cap"><span class="y">10 tahun</span> lifestyle &rarr; <span class="r">penyakit</span></div>
    </div>"""
        js = card_in("#um-card", 0.05)
        js += f'    tl.fromTo("#um-fill", {{scaleX:0}}, {{scaleX:1, duration:{round(L(sc,67.28)-L(sc,64.7),2)}, ease:"power2.inOut"}}, {L(sc,64.7)});\n'
        js += pop_in("#um-b", L(sc, 67.28))
        sfx("whoosh-short", st + 0.05)
        sfx("pop", st + L(sc, 67.28))
        js += card_out("#um-card", end)
        return css, markup, js
    if k == "bukan":
        css = """
  #bk-c1, #bk-c2, #bk-ans { opacity:0; }
  #bk-box { position:absolute; left:120px; width:660px; top:930px; }
  .bk-chip { display:inline-block; position:relative; background:rgba(12,18,38,.86); color:#fff; border-radius:999px;
             padding:14px 28px; font-family:'Archivo Black',sans-serif; font-size:40px; margin:0 10px 14px 0; }
  .bk-x { position:absolute; left:18px; right:18px; top:50%; height:8px; margin-top:-4px; background:#FF4D4D;
          border-radius:4px; transform-origin:left center; }
  #bk-ans { background:#FFC928; color:#111; font-family:'Archivo Black',sans-serif; font-size:44px; border-radius:22px;
            padding:18px 28px; display:inline-block; text-transform:uppercase; }
"""
        markup = """    <div id="bk-box">
      <div class="bk-chip" id="bk-c1">UBAT<div class="bk-x" id="bk-x1"></div></div>
      <div class="bk-chip" id="bk-c2">SUPPLEMENT<div class="bk-x" id="bk-x2"></div></div>
      <div id="bk-ans">Tahu dulu di mana salah</div>
    </div>"""
        js = pop_in("#bk-c1", L(sc, 73.11)) + pop_in("#bk-c2", L(sc, 75.3))
        js += f'    tl.fromTo("#bk-x1", {{scaleX:0}}, {{scaleX:1, duration:.25, ease:"power3.out"}}, {L(sc,74.3)});\n'
        js += f'    tl.fromTo("#bk-x2", {{scaleX:0}}, {{scaleX:1, duration:.25, ease:"power3.out"}}, {L(sc,76.6)});\n'
        js += (f'    tl.fromTo("#bk-ans", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"expo.out"}}, {L(sc,77.6)});\n')
        js += card_out("#bk-box", end)
        sfx("pop", st + L(sc, 73.11)); sfx("pop", st + L(sc, 75.3))
        sfx("error", st + L(sc, 74.3)); sfx("error", st + L(sc, 76.6))
        sfx("whoosh-short", st + L(sc, 77.6))
        return css, markup, js
    if k == "fomo":
        css = """
  #fm-box { position:absolute; left:120px; width:660px; top:860px; }
  #fm-tag, .fm-b { opacity:0; }
  #fm-tag { font-family:'Archivo Black',sans-serif; font-size:96px; color:#FF4D4D; letter-spacing:.02em; margin-bottom:10px;
            text-shadow:0 6px 24px rgba(0,0,0,.4); }
  .fm-b { background:#fff; color:#111; border-radius:26px 26px 26px 6px; padding:16px 26px; font-weight:800; font-size:34px;
          display:inline-block; margin:0 0 14px; box-shadow:0 10px 30px rgba(0,0,0,.3); font-family:'Montserrat',sans-serif; }
"""
        markup = """    <div id="fm-box">
      <div id="fm-tag">FOMO?</div>
      <div><div class="fm-b" id="fm-1">"Supplement ni bagus!"</div></div>
      <div><div class="fm-b" id="fm-2">"Supplement ni terbaik!"</div></div>
      <div><div class="fm-b" id="fm-3">"Ubat? Buang, campak!"</div></div>
    </div>"""
        js = ''
        js += pop_in("#fm-tag", L(sc, 87.5))
        for n, src in [(1, 88.46), (2, 89.64), (3, 90.69)]:
            js += (f'    tl.fromTo("#fm-{n}", {{opacity:0, scale:.7, x:-30}}, {{opacity:1, scale:1, x:0, duration:.35, ease:"back.out(1.7)"}}, {L(sc,src)});\n')
            sfx("notification" if n == 1 else "click-soft", st + L(sc, src))
        js += card_out("#fm-box", end)
        sfx("pop", st + L(sc, 87.5))
        return css, markup, js
    if k == "rutin":
        beats = [("PAGI", "Kopi + teh tarik", 118.37, False),
                 ("10:00 PG", "Kunyah benda manis, 3-in-1", 125.3, False),
                 ("1:00 TGH", "Fast food & ultra-processed", 134.28, False),
                 ("PETANG", "Jem + stres", 148.11, False),
                 ("8–9 MLM", "Tinggi karbo, tinggi gula", 152.72, False),
                 ("12 MLM", "Scroll, movie, gosip…", 164.86, False),
                 ("2–3 PAGI", "Baru boleh tidur", 176.15, False),
                 ("REHAT", "3 jam sahaja", 184.64, True)]
        css = """
  #rt-card { top:1000px; height:220px; padding:24px 34px; }
  .rt-beat { opacity:0; position:absolute; left:34px; right:34px; top:24px; }
  .rt-time { font-family:'Archivo Black',sans-serif; font-size:70px; color:#FFC928; line-height:1; }
  .rt-what { font-weight:800; font-size:38px; margin-top:12px; }
  .rt-hot .rt-time { color:#FF4D4D; font-size:84px; }
  #rt-clock { position:absolute; right:34px; top:30px; width:110px; height:110px; border-radius:50%; border:7px solid rgba(255,255,255,.85); }
  #rt-hand { position:absolute; left:50%; top:50%; width:6px; height:40px; margin-left:-3px; margin-top:-40px; background:#FFC928;
             border-radius:3px; transform-origin:50% 100%; }
  #rt-hand2 { position:absolute; left:50%; top:50%; width:6px; height:28px; margin-left:-3px; margin-top:-28px; background:#fff;
             border-radius:3px; transform-origin:50% 100%; }
"""
        rows = "\n".join(f'      <div class="rt-beat{" rt-hot" if hot else ""}" id="rt-b{n}"><div class="rt-time">{tm}</div><div class="rt-what">{wh}</div></div>'
                         for n, (tm, wh, _, hot) in enumerate(beats))
        markup = f"""    <div id="rt-card" class="card">
      <div id="rt-clock"><div id="rt-hand2"></div><div id="rt-hand"></div></div>
{rows}
    </div>"""
        js = card_in("#rt-card", 0.0)
        sfx("whoosh-short", st)
        rot = 0
        for n, (_, _, src, hot) in enumerate(beats):
            lt = max(L(sc, src), 0.05)
            if n:
                js += f'    tl.to("#rt-b{n-1}", {{opacity:0, filter:"blur(8px)", duration:.16, ease:"power2.in"}}, {round(lt-.16,3)});\n'
            js += f'    tl.fromTo("#rt-b{n}", {{opacity:0, filter:"blur(8px)"}}, {{opacity:1, filter:"blur(0px)", duration:.16, ease:"power4.out"}}, {lt});\n'
            rot += 360 * (1 if n < 7 else 0.5)
            js += f'    tl.to("#rt-hand", {{rotation:{rot}, duration:.5, ease:"power3.inOut"}}, {round(lt-.3,3) if n else 0});\n'
            js += f'    tl.to("#rt-hand2", {{rotation:{rot/12+30*n}, duration:.5, ease:"power3.inOut"}}, {round(lt-.3,3) if n else 0});\n'
            sfx("impact-bass-1" if hot else "click-soft", st + lt)
        js += '    tl.fromTo("#rt-b7 .rt-time", {scale:1.3}, {scale:1, duration:.5, ease:"expo.out", transformOrigin:"left center"}, ' + str(L(sc, 184.64)) + ');\n'
        js += card_out("#rt-card", end)
        return css, markup, js
    if k == "hutang":
        css = """
  #hu-card { top:930px; padding:28px 34px; }
  .hu-lbl { font-weight:800; font-size:30px; display:flex; justify-content:space-between; margin:16px 0 8px; }
  .hu-bar { position:relative; height:46px; border-radius:12px; background:rgba(255,255,255,.14); overflow:hidden; }
  .hu-fill { position:absolute; left:0; top:0; bottom:0; border-radius:12px; transform-origin:left center; }
  #hu-need { width:100%; background:#3DDC84; }
  #hu-got { width:50%; background:#FFC928; }
  #hu-debt { position:absolute; left:50%; top:0; bottom:0; width:50%;
             background:repeating-linear-gradient(135deg,#FF4D4D 0 14px,rgba(255,77,77,.45) 14px 28px); transform-origin:left center; }
  #hu-big, #hu-q, #hu-stamp, #hu-q1 { opacity:0; }
  #hu-big { position:absolute; left:120px; width:660px; top:1010px; text-align:center; background:rgba(12,18,38,.86); border-radius:28px; padding:24px 20px; }
  #hu-y { font-family:'Archivo Black',sans-serif; font-size:46px; color:#fff; }
  #hu-y2 { font-family:'Archivo Black',sans-serif; font-size:104px; color:#FF4D4D; line-height:1; margin-top:8px; }
  #hu-q { position:absolute; left:120px; width:660px; top:1000px; text-align:center; }
  #hu-q1 { display:inline-block; font-family:'Archivo Black',sans-serif; font-size:44px; color:#fff; background:rgba(12,18,38,.86); border-radius:22px; padding:14px 26px; }
  #hu-stamp { display:inline-block; margin-top:14px; border:10px solid #FF4D4D; color:#FF4D4D; border-radius:18px; padding:8px 30px;
              font-family:'Archivo Black',sans-serif; font-size:110px; transform:rotate(-6deg); background:rgba(255,255,255,.92); }
"""
        markup = """    <div id="hu-card" class="card">
      <div class="eyebrow">Sel dibaiki masa tidur</div>
      <div class="hu-lbl"><span>Badan perlukan</span><span>8 jam</span></div>
      <div class="hu-bar"><div class="hu-fill" id="hu-need"></div></div>
      <div class="hu-lbl"><span>Korang tidur</span><span>4 jam</span></div>
      <div class="hu-bar"><div class="hu-fill" id="hu-got"></div><div id="hu-debt"></div></div>
      <div class="hu-lbl"><span class="r">Hutang repair setiap hari</span><span></span></div>
    </div>
    <div id="hu-big"><div id="hu-y">Setahun berhutang =</div><div id="hu-y2">6 BULAN</div></div>
    <div id="hu-q"><div id="hu-q1">Nak repair dalam 1 bulan?</div><div id="hu-stamp">TAK LOGIK</div></div>"""
        js = ''
        js += card_in("#hu-card", 0.1)
        sfx("whoosh-short", st + 0.1)
        js += f'    tl.fromTo("#hu-need", {{scaleX:0}}, {{scaleX:1, duration:.7, ease:"power2.out"}}, {L(sc,196.3)});\n'
        js += f'    tl.fromTo("#hu-got", {{scaleX:0}}, {{scaleX:1, duration:.6, ease:"power2.out"}}, {L(sc,199.2)});\n'
        js += f'    tl.fromTo("#hu-debt", {{scaleX:0, opacity:0}}, {{scaleX:1, opacity:1, duration:.5, ease:"power3.out"}}, {L(sc,202.5)});\n'
        sfx("error", st + L(sc, 202.5))
        js += card_out("#hu-card", L(sc, 205.8))
        js += word_in("#hu-y", L(sc, 208.4)) + pop_in("#hu-y2", L(sc, 213.0))
        js += '    tl.set("#hu-big", {opacity:1}, ' + str(L(sc, 208.3)) + ');\n'
        sfx("impact-bass-1", st + L(sc, 213.0))
        js += card_out("#hu-big", L(sc, 221.1))
        js += '    tl.set("#hu-q", {opacity:1}, ' + str(L(sc, 221.4)) + ');\n'
        js += word_in("#hu-q1", L(sc, 221.4))
        js += (f'    tl.fromTo("#hu-stamp", {{opacity:0, scale:2.2}}, {{opacity:1, scale:1, duration:.28, ease:"power4.in"}}, {round(L(sc,224.28)-.2,3)});\n')
        sfx("riser", st + L(sc, 224.28) - 0.02)  # riser peak lands just before the stamp
        sfx("impact-bass-1", st + L(sc, 224.28) + 0.08)
        js += card_out("#hu-q", end)
        return css, markup, js
    if k == "kunci":
        words = [("LIFESTYLE", 250.37), ("KONSISTEN", 252.79), ("DISIPLIN", 254.96)]
        css = """
  #ku-box { position:absolute; left:120px; width:660px; top:880px; text-align:center; }
  #ku-pre { font-weight:800; font-size:34px; color:#fff; letter-spacing:.12em; text-shadow:0 4px 16px rgba(0,0,0,.5); }
  .ku-w, #ku-pre { opacity:0; }
  .ku-w { font-family:'Archivo Black',sans-serif; font-size:88px; line-height:1.08; color:#fff; text-shadow:0 6px 24px rgba(0,0,0,.45); }
  .ku-on { color:#FFC928; }
"""
        markup = '    <div id="ku-box">\n      <div id="ku-pre">PENTINGNYA</div>\n' + \
            "\n".join(f'      <div class="ku-w" id="ku-{n}">{w}</div>' for n, (w, _) in enumerate(words)) + "\n    </div>"
        js = word_in("#ku-pre", 0.15)
        for n, (_, src) in enumerate(words):
            lt = max(L(sc, src) - 0.25, 0.3)
            js += (f'    tl.fromTo("#ku-{n}", {{opacity:0, scale:1.4, filter:"blur(8px)"}}, '
                   f'{{opacity:1, scale:1, filter:"blur(0px)", duration:.3, ease:"expo.out"}}, {lt});\n')
            js += f'    tl.to("#ku-{n}", {{color:"#FFC928", duration:.15}}, {lt});\n'
            if n:
                js += f'    tl.to("#ku-{n-1}", {{color:"#ffffff", opacity:.55, duration:.2}}, {lt});\n'
            sfx("pop", st + lt)
        js += card_out("#ku-box", end)
        return css, markup, js
    if k == "badan":
        css = """
  #bd-box { position:absolute; left:120px; width:660px; top:1000px; text-align:center; }
  #bd-1 { font-family:'Archivo Black',sans-serif; font-size:68px; color:#fff; line-height:1.08; background:rgba(12,18,38,.86);
          border-radius:28px; padding:24px 26px; }
  #bd-1 .w { display:inline-block; }
"""
        markup = '    <div id="bd-box"><div id="bd-1"><span class="w">Setiap</span> <span class="w">badan</span> <span class="w y">tak sama</span></div></div>'
        js = word_in("#bd-1 .w", L(sc, 273.41), .12) + card_out("#bd-box", end)
        sfx("whoosh-short", st + L(sc, 273.41))
        return css, markup, js
    if k == "cta":
        css = """
  #cta-btn { position:absolute; left:240px; top:1040px; width:420px; text-align:center; background:#FFC928; color:#111;
             border-radius:999px; padding:24px 0; font-family:'Archivo Black',sans-serif; font-size:54px; box-shadow:0 14px 40px rgba(0,0,0,.35); }
  #cta-arrow { display:inline-block; margin-left:12px; }
  #cta-pray { opacity:0; }
  #cta-pray { position:absolute; left:120px; width:660px; top:1040px; text-align:center; font-family:'Archivo Black',sans-serif;
              font-size:54px; color:#fff; line-height:1.08; text-shadow:0 6px 24px rgba(0,0,0,.5); }
"""
        markup = """    <div id="cta-btn">SHARE<span id="cta-arrow">&#10148;</span></div>
    <div id="cta-pray">Semoga kembali <span class="y">sihat</span> &amp; <span class="y">sembuh</span></div>"""
        js = ''
        js += pop_in("#cta-btn", L(sc, 281.29) - 0.1)
        js += f'    tl.to("#cta-btn", {{scale:.92, duration:.08, ease:"power2.in", yoyo:true, repeat:1}}, {L(sc,281.6)});\n'
        js += card_out("#cta-btn", L(sc, 283.6))
        js += word_in("#cta-pray", L(sc, 286.6))
        js += f'    tl.to("#cta-pray", {{opacity:0, duration:.3}}, {end});\n'
        sfx("pop", st + L(sc, 281.29) - 0.1)
        sfx("click-soft", st + L(sc, 281.6))
        return css, markup, js
    return build_draw(sc)


exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "draw.py")).read())
for p_ in [z[0] for z in ZOOM if z[1] == "punch"][::2]:
    sfx("whoosh-short", p_ + 0.05)

os.makedirs(f"{PROJ}/compositions", exist_ok=True)
hosts = []
for sc in SCENES:
    css, markup, js = build(sc)
    open(f"{PROJ}/compositions/{sc['id']}.html", "w").write(scene_html(sc, css, markup, js))
    hosts.append(f'      <div id="{sc["id"]}" class="clip" data-composition-id="{sc["id"]}" data-composition-src="compositions/{sc["id"]}.html" '
                 f'data-start="{sc["start"]}" data-duration="{sc["dur"]}" data-track-index="1" data-track-kind="graphics" '
                 f'data-width="{W}" data-height="{H}" style="z-index:10"></div>')

videos = []
for s in segs:
    fi = 0.04 if s["name"] != "hook" else 0
    videos.append(f'        <video id="v-{s["name"]}" class="clip" src="assets/footage.mp4" playsinline data-has-audio="true" '
                  f'data-start="{s["out"]}" data-duration="{s["dur"]}" data-media-start="{s["src_in"]}" data-track-index="0" '
                  f'data-fade-in="{fi}" data-fade-out="0.04" '
                  f'style="position:absolute; left:0; top:0; width:{W}px; height:{H}px; object-fit:cover"></video>')

SFX.sort(key=lambda x: x[1])
audios = []
lane_end = []
for n, (name, at) in enumerate(SFX):
    start = round(max(at + 1 / 30 - PEAK[name], 0), 3)  # peak one frame after the picture
    for li, e in enumerate(lane_end):
        if e <= start:
            lane_end[li] = start + DUR[name]; lane = li; break
    else:
        lane_end.append(start + DUR[name]); lane = len(lane_end) - 1
    audios.append(f'      <audio id="sfx-{n}" src="assets/sfx/{name}.mp3" data-start="{start}" data-duration="{DUR[name]}" data-volume="{VOL[name]}" data-track-index="{3 + lane}"></audio>')

# Camera needs: while a lower card is on screen, keep the face above it (zoom >= 1.2 and lift the frame).
CARD_SCENES = {"hook","soalan","catat","sendiri","bukan","fomo","cermin","jumpa","hutang","masa","sel","graf","kunci","langkah","umur"}
WIN = [(sc["start"], sc["end"]) for sc in SCENES if sc["id"] in CARD_SCENES]
def lifted(t):
    return any(a_ <= t < b_ for a_, b_ in WIN)
def frame(s_, x_, t):
    y_ = 0
    if lifted(t + 0.01):
        s_ = round(1.2 + (s_ - 1.0) * 0.5, 3)
        y_ = -round(1113.6 * (s_ - 1.0) - 3, 1)
    lim = 540 * (s_ - 1.0)
    x_ = max(-lim, min(lim, x_))
    return s_, round(x_, 1), y_
EV = [(t_, k_, s_, x_) for t_, k_, s_, x_ in ZOOM]
for a_, b_ in WIN:
    EV += [(round(a_, 3), "keep", None, None), (round(b_, 3), "keep", None, None)]
EV.sort(key=lambda e: (e[0], {"set": 0, "keep": 1, "ease": 2, "punch": 3}[e[1]]))
zl, cur, prev_t = [], (1.0, 0), -1
times = [e[0] for e in EV]
for n, (t_, kind, s_, x_) in enumerate(EV):
    if s_ is not None:
        cur = (s_, x_)
    fs, fx, fy = frame(cur[0], cur[1], t_)
    nxt = next((tt for tt in times[n + 1:] if tt > t_ + 1e-6), TOTAL)
    if kind == "set" or (kind == "keep" and any(abs(t_ - c) < 0.05 for c in CUTS)):
        zl.append(f'      tl.set("#cam", {{scale:{fs}, x:{fx}, y:{fy}}}, {t_});')
        continue
    dur = .22 if kind == "punch" else (.55 if kind == "keep" else .7)
    dur = round(min(dur, nxt - t_ - 0.02), 3)
    if dur < 0.12:
        zl.append(f'      tl.set("#cam", {{scale:{fs}, x:{fx}, y:{fy}}}, {t_});')
    else:
        ease = "expo.out" if kind == "punch" else "power2.inOut"
        zl.append(f'      tl.to("#cam", {{scale:{fs}, x:{fx}, y:{fy}, duration:{dur}, ease:"{ease}"}}, {t_});')
import re as _re
_last = {}
for line in zl:
    _last[float(_re.search(r", ([0-9.]+)\);$", line).group(1))] = line
zl = [_last[k_] for k_ in sorted(_last)]
punch_js = "\n".join(zl)

index = f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:{W}px; height:{H}px; overflow:hidden; background:#000; }}
      body {{ font-family:"Montserrat", sans-serif; }}
      #cam {{ position:absolute; inset:0; transform-origin:50% 42%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      <div id="cam">
{chr(10).join(videos)}
      </div>
{chr(10).join(hosts)}
{chr(10).join(audios)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{punch_js}
      tl.set({{}}, {{}}, {TOTAL});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(f"{PROJ}/index.html", "w").write(index)
json.dump(dict(total=TOTAL, segments=segs, scenes=SCENES, sfx=SFX, zoom=ZOOM),
          open(f"{PROJ}/edit-plan.json", "w"), indent=1)
print("total", TOTAL, "scenes", len(SCENES), "sfx", len(SFX), "zoom", len(ZOOM))
