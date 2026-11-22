# Hand-drawn "paper card" infographics. Loaded by gen.py (exec), uses its L(), sfx() and globals.
# Every stroke draws on (stroke-dashoffset 1 -> 0, pathLength=1); handwriting wipes in left to right.


def P(d, cls="", extra=""):
    return f'<path class="ink {cls}" pathLength="1" d="{d}" {extra}/>'


def paper_in(sel, t, rot=-1.5):
    return (f'    tl.fromTo("{sel}", {{opacity:0, y:70, rotation:-7, scale:.78, transformOrigin:"50% 0%"}}, '
            f'{{opacity:1, y:0, rotation:{rot}, scale:.86, transformOrigin:"50% 0%", duration:.55, ease:"back.out(1.4)"}}, {round(t,3)});\n')


def paper_out(sel, t):
    return (f'    tl.to("{sel}", {{opacity:0, y:-30, rotation:3, filter:"blur(5px)", duration:.28, ease:"power2.in"}}, '
            f'{round(t,3)});\n')


def draw(sel, t, d=.5, ease="power1.inOut"):
    return (f'    tl.fromTo("{sel}", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{d}, ease:"{ease}"}}, '
            f'{round(max(t,0),3)});\n')


def write(sel, t, chars=10):
    d = round(min(max(.045 * chars, .3), .9), 2)
    return (f'    tl.fromTo("{sel}", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{d}, ease:"none"}}, '
            f'{round(max(t,0),3)});\n')


def hand(id_, text, x, y, size, cls=""):
    return f'<div class="hand {cls}" id="{id_}" style="left:{x}px; top:{y}px; font-size:{size}px">{text}</div>'


def build_draw(sc):
    k, d = sc["kind"], sc["dur"]
    st = sc["start"]
    end = round(d - 0.3, 3)
    i = sc["id"]
    pid = f"#{i}-p"

    if k == "soalan":
        # follower's question: BP gauge spikes, 3 pills, supplement bottle with "?"
        css = f"{pid} {{ top:880px; height:350px; }}"
        svg = "".join([
            P("M40 210 A110 110 0 0 1 260 210", "", 'id="so-arc"'),
            P("M234 139 A110 110 0 0 1 260 210", "r thick", 'id="so-red"'),
            P("M60 160 l14 8 M100 118 l10 13 M150 100 v16 M200 118 l-10 13", "", 'id="so-tick"'),
            '<g id="so-needle"><path class="ink" pathLength="1" style="stroke-dashoffset:0" d="M150 210 L150 125"/>'
            '<circle cx="150" cy="210" r="10" fill="#1d1d1f"/></g>',
            *[P(f"M{x} 52 h34 a18 18 0 0 1 0 36 h-34 a18 18 0 0 1 0 -36 z M{x+17} 52 v36", "so-pill")
              for x in (338, 422, 506)],
            P("M470 172 h40 v18 l14 14 v86 a8 8 0 0 1 -8 8 h-52 a8 8 0 0 1 -8 -8 v-86 l14 -14 z M462 172 h56", "", 'id="so-btl"'),
        ])
        markup = f'''    <div class="paper" id="{i}-p">
      <svg width="660" height="350" viewBox="0 0 660 350" style="position:absolute;left:0;top:0">{svg}</svg>
      {hand("so-t1", "Darah tinggi!", 62, 236, 52, "r")}
      {hand("so-t2", "Ubat 3 serangkai", 330, 104, 44)}
      {hand("so-q", "?", 484, 214, 70, "mk b")}
      {hand("so-t3", "Supplement?", 300, 290, 46, "b")}
    </div>'''
        js = paper_in(pid, 0.0)
        js += '    tl.set("#so-needle", {rotation:-70, svgOrigin:"150 210"}, 0);\n'
        js += draw("#so-arc", 0.15, .5) + draw("#so-tick", .5, .3)
        js += draw("#so-red", L(sc, 1.09), .35)
        js += f'    tl.to("#so-needle", {{rotation:62, duration:.6, ease:"back.out(2.5)", svgOrigin:"150 210"}}, {L(sc,1.09)});\n'
        js += write("#so-t1", L(sc, 1.39), 13)
        js += f'    tl.fromTo(".so-pill", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:.35, stagger:.15}}, {L(sc,3.63)});\n'
        js += write("#so-t2", L(sc, 5.45), 16)
        js += draw("#so-btl", L(sc, 6.91), .55)
        js += write("#so-t3", L(sc, 7.6), 11)
        js += (f'    tl.fromTo("#so-q", {{clipPath:"inset(0 0% 0 0)", opacity:0, scale:2}}, '
               f'{{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {L(sc,7.92)});\n')
        js += paper_out(pid, end)
        sfx("whoosh-short", st); sfx("error", st + L(sc, 1.09)); sfx("pop", st + L(sc, 7.92))
        return css, markup, js

    if k == "sendiri":
        css = f"{pid} {{ top:880px; height:370px; }}"
        svg = "".join([
            P("M30 80 h170 v200 h-170 z M30 124 h170 M72 62 v36 M158 62 v36", "", 'id="se-cal"'),
            P("M408 112 C 420 60, 600 58, 616 104 C 630 150, 450 168, 412 132 C 396 116, 414 92, 440 86", "r", 'id="se-ring"'),
            P("M300 190 C 350 290, 520 290, 560 180 M540 186 L561 178 L566 200", "", 'id="se-arrow"'),
        ])
        markup = f'''    <div class="paper" id="{i}-p">
      <svg width="660" height="370" viewBox="0 0 660 370" style="position:absolute;left:0;top:0">{svg}</svg>
      {hand("se-ttl", "Pengalaman sendiri:", 30, 18, 44, "b")}
      {hand("se-10", "10", 64, 146, 96, "mk r")}
      {hand("se-thn", "tahun", 70, 238, 36)}
      {hand("se-pen", "Penyakit", 430, 92, 54, "r")}
      {hand("se-life", "Lifestyle", 220, 140, 54, "g")}
      {hand("se-lbl", "kekal 10 tahun", 360, 300, 40)}
    </div>'''
        js = paper_in(pid, 0.0, 1.2) + write("#se-ttl", L(sc, 43.56), 19)
        js += draw("#se-cal", 0.3, .6)
        js += write("#se-pen", L(sc, 45.99), 8) + draw("#se-ring", L(sc, 46.85), .5)
        js += write("#se-life", L(sc, 48.25), 9) + draw("#se-arrow", L(sc, 48.9), .55)
        js += write("#se-10", L(sc, 50.15), 2) + write("#se-thn", L(sc, 50.52), 5) + write("#se-lbl", L(sc, 50.8), 14)
        js += paper_out(pid, end)
        sfx("whoosh-short", st); sfx("pop", st + L(sc, 50.15))
        return css, markup, js

    if k == "cermin":
        css = f"{pid} {{ top:880px; height:380px; }}"
        svg = "".join([
            *[P(f"M{x} 100 a26 26 0 1 0 0.1 0 M{x} 152 v52 M{x-26} 230 l26 -26 l26 26 M{x-26} 172 h52", "cm-fig")
              for x in (70, 150, 230)],
            P("M30 70 L280 250 M280 70 L30 250", "r thick", 'id="cm-x"'),
            P("M410 140 a75 100 0 1 0 150 0 a75 100 0 1 0 -150 0", "", 'id="cm-mir"'),
            P("M430 90 q8 -30 34 -42", "", 'id="cm-shine"'),
            P("M465 120 v10 M505 120 v10 M462 160 q23 22 46 0", "", 'id="cm-face"'),
            P("M485 240 v34 M445 276 h80", "", 'id="cm-stand"'),
        ])
        markup = f'''    <div class="paper" id="{i}-p">
      <svg width="660" height="300" viewBox="0 0 660 300" style="position:absolute;left:0;top:0">{svg}</svg>
      {hand("cm-t1", "Semua orang salah?", 26, 262, 42)}
      {hand("cm-t2", "Cermin diri", 410, 258, 46, "b")}
      {hand("cm-t3", "&#10003; Terima salah", 40, 318, 46, "g")}
      {hand("cm-t4", "&#10003; Perbaiki", 380, 318, 46, "g")}
    </div>'''
        js = paper_in(pid, 0.0)
        js += f'    tl.fromTo(".cm-fig", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:.5, stagger:.18}}, {L(sc,99.0)});\n'
        js += write("#cm-t1", L(sc, 99.82), 18) + draw("#cm-x", L(sc, 100.81), .3, "power3.out")
        js += draw("#cm-mir", L(sc, 101.72), .55) + draw("#cm-shine", L(sc, 102.2), .2) + draw("#cm-stand", L(sc, 102.3), .3)
        js += draw("#cm-face", L(sc, 102.56), .35) + write("#cm-t2", L(sc, 102.6), 11)
        js += write("#cm-t3", L(sc, 104.10), 14) + write("#cm-t4", L(sc, 106.41), 10)
        js += paper_out(pid, end)
        sfx("whoosh-short", st); sfx("error", st + L(sc, 100.81)); sfx("pop", st + L(sc, 104.1)); sfx("pop", st + L(sc, 106.41))
        return css, markup, js

    if k == "jumpa":
        lines = [("7 pg - teh tarik + kuih", 110.2), ("10 pg - air 3 in 1", 110.85), ("1 tgh - fast food", 111.39),
                 ("12 mlm - scroll phone", 112.0)]
        css = f"""{pid} {{ top:880px; height:370px;
          background-image:repeating-linear-gradient(#FFF8E7 0 58px, #9DB7E5 58px 60px); background-position:0 30px; }}
  #ju-mag {{ position:absolute; left:0; top:0; }}"""
        rows = "\n      ".join(hand(f"ju-l{n}", t_, 40, 40 + 60 * n, 46) for n, (t_, _) in enumerate(lines))
        svg = P("M22 70 C 20 20, 470 14, 482 58 C 494 104, 60 110, 30 84", "r thick", 'id="ju-ring"')
        mag = ('<svg id="ju-mag" width="160" height="160" viewBox="0 0 160 160">'
               '<circle cx="62" cy="62" r="46" fill="rgba(160,210,255,.25)" stroke="#1d1d1f" stroke-width="8"/>'
               '<path d="M96 96 L145 145" stroke="#1d1d1f" stroke-width="14" stroke-linecap="round"/></svg>')
        markup = f'''    <div class="paper" id="{i}-p">
      {rows}
      <svg width="660" height="370" viewBox="0 0 660 370" style="position:absolute;left:0;top:0">{svg}</svg>
      {mag}
      {hand("ju-oh", "Oh! Aku salah kat sini!", 60, 290, 50, "mk r")}
    </div>'''
        js = paper_in(pid, 0.0, 1.0)
        for n, (t_, src) in enumerate(lines):
            js += write(f"#ju-l{n}", L(sc, src), len(t_) * .6)
        js += (f'    tl.fromTo("#ju-mag", {{opacity:0, x:560, y:220}}, {{opacity:1, x:420, y:150, duration:.4, ease:"power2.out"}}, {L(sc,113.4)});\n'
               f'    tl.to("#ju-mag", {{x:300, y:-30, duration:1.0, ease:"power2.inOut"}}, {L(sc,113.9)});\n')
        js += draw("#ju-ring", L(sc, 115.2), .45, "power2.out") + write("#ju-oh", L(sc, 115.6), 22)
        js += paper_out(pid, end)
        sfx("whoosh-short", st); sfx("pop", st + L(sc, 115.92))
        return css, markup, js

    if k == "masa":
        css = f"""{pid} {{ top:880px; height:340px; }}
  .sand {{ fill:#F2B705; }}"""
        svg = "".join([
            '<path class="sand" id="ma-top" d="M70 60 L150 60 L110 140 Z"/>',
            '<path class="sand" id="ma-bot" d="M66 290 L154 290 L110 226 Z"/>',
            P("M40 30 h140 M40 300 h140 M55 30 C 55 120, 100 132, 108 165 M165 30 C 165 120, 120 132, 112 165 "
              "M108 165 C 100 198, 55 210, 55 300 M112 165 C 120 198, 165 210, 165 300", "", 'id="ma-glass"'),
            '<path id="ma-stream" d="M110 150 V 286" stroke="#F2B705" stroke-width="4" stroke-dasharray="8 8" fill="none"/>',
        ])
        markup = f'''    <div class="paper" id="{i}-p">
      <svg width="220" height="340" viewBox="0 0 220 340" style="position:absolute;left:20px;top:0">{svg}</svg>
      {hand("ma-t1", "Bagi badan", 250, 40, 58)}
      {hand("ma-t2", "MASA", 250, 104, 110, "mk r")}
      {hand("ma-t3", "untuk adapt", 250, 228, 50, "b")}
      {hand("ma-t4", "&amp; repair", 250, 280, 50, "b")}
    </div>'''
        js = paper_in(pid, 0.0, 1.4) + draw("#ma-glass", 0.2, .7)
        js += '    tl.fromTo("#ma-top", {scaleY:1}, {scaleY:.15, svgOrigin:"110 140", duration:5, ease:"none"}, .6);\n'
        js += '    tl.fromTo("#ma-bot", {scaleY:.05}, {scaleY:1, svgOrigin:"110 290", duration:5, ease:"none"}, .6);\n'
        js += '    tl.fromTo("#ma-stream", {strokeDashoffset:0, opacity:0}, {strokeDashoffset:-160, opacity:1, duration:5, ease:"none"}, .6);\n'
        js += write("#ma-t1", L(sc, 227.3), 10) + write("#ma-t2", L(sc, 228.4), 4)
        js += write("#ma-t3", L(sc, 228.7), 11) + write("#ma-t4", L(sc, 231.6), 8)
        js += paper_out(pid, end)
        sfx("whoosh-short", st); sfx("pop", st + L(sc, 228.4))
        return css, markup, js

    if k == "sel":
        css = f"{pid} {{ top:880px; height:370px; }}"
        svg = "".join([
            P("M450 50 C 560 40, 630 130, 600 210 C 575 290, 430 300, 360 240 C 300 190, 330 60, 450 50 Z", "g thick", 'id="sl-cell"'),
            P("M470 150 a34 30 0 1 0 0.1 0", "", 'id="sl-nuc"'),
            P("M445 120 v10 M495 120 v10 M440 205 q30 26 60 0", "", 'id="sl-face"'),
            P("M470 34 v-24 M540 50 l18 -18 M400 50 l-18 -18 M600 110 h22", "y thick", 'id="sl-spark"'),
            P("M40 300 l16 16 l30 -36", "g thick", 'id="sl-tick"'),
        ])
        markup = f'''    <div class="paper" id="{i}-p">
      <svg width="660" height="370" viewBox="0 0 660 370" style="position:absolute;left:0;top:0">{svg}</svg>
      {hand("sl-t1", "Sel badan kita", 30, 40, 54)}
      {hand("sl-t2", "tak bodoh...", 30, 108, 48)}
      {hand("sl-t3", "BIJAK!", 30, 172, 74, "mk g")}
      {hand("sl-t4", "Ramai sembuh dlm beberapa bulan", 100, 286, 40)}
    </div>'''
        js = paper_in(pid, 0.0, -1.0) + draw("#sl-cell", 0.15, .7) + draw("#sl-nuc", .6, .35)
        js += write("#sl-t1", L(sc, 232.8), 14) + write("#sl-t2", L(sc, 233.6), 11) + draw("#sl-face", L(sc, 234.2), .4)
        js += write("#sl-t3", L(sc, 235.7), 6) + draw("#sl-spark", L(sc, 235.75), .3, "power3.out")
        js += draw("#sl-tick", L(sc, 238.6), .3) + write("#sl-t4", L(sc, 238.7), 26)
        js += paper_out(pid, end)
        sfx("whoosh-short", st); sfx("pop", st + L(sc, 235.7)); sfx("pop", st + L(sc, 238.6))
        return css, markup, js

    if k == "graf":
        css = f"{pid} {{ top:880px; height:360px; }}"
        svg = "".join([
            P("M60 30 V 290 H 620", "", 'id="gr-ax"'),
            P("M70 270 C 160 262, 230 150, 340 90", "g thick", 'id="gr-up"'),
            P("M340 90 C 400 70, 440 120, 470 230 L 500 270", "r thick", 'id="gr-dn"'),
            P("M486 246 L500 272 L514 248", "r thick", 'id="gr-ah"'),
            P("M340 290 v14", "", 'id="gr-mark"'),
        ])
        markup = f'''    <div class="paper" id="{i}-p">
      <svg width="660" height="360" viewBox="0 0 660 360" style="position:absolute;left:0;top:0">{svg}</svg>
      {hand("gr-t0", "Kesihatan", 72, 20, 40)}
      {hand("gr-t1", "Sihat &#10003;", 214, 60, 50, "g")}
      {hand("gr-t2", "3-4 bulan", 290, 306, 42)}
      {hand("gr-t3", "Boleh sakit semula!", 320, 16, 32, "mk r")}
    </div>'''
        js = paper_in(pid, 0.0, 1.0) + draw("#gr-ax", .15, .5) + write("#gr-t0", .4, 9)
        js += draw("#gr-up", L(sc, 243.5), 1.0, "power2.inOut") + write("#gr-t1", L(sc, 244.4), 7)
        js += draw("#gr-mark", L(sc, 245.2), .2) + write("#gr-t2", L(sc, 245.2), 9)
        js += draw("#gr-dn", L(sc, 246.6), .6, "power2.in") + draw("#gr-ah", L(sc, 247.15), .2)
        js += write("#gr-t3", L(sc, 247.2), 19)
        js += paper_out(pid, end)
        sfx("whoosh-short", st); sfx("error", st + L(sc, 247.15))
        return css, markup, js

    if k == "langkah":
        css = f"{pid} {{ top:880px; height:410px; }}"
        circ = lambda n, y: P(f"M60 {y} a30 30 0 1 0 0.1 0", "r", f'id="lk-c{n}"')
        svg = "".join([circ(1, 20), circ(2, 110), circ(3, 200),
                       P("M260 360 C 330 352, 380 366, 420 356", "y thick", 'id="lk-u1"'),
                       P("M440 360 C 480 354, 520 364, 560 356", "y thick", 'id="lk-u2"'),
                       P("M70 360 C 130 352, 190 366, 240 356", "y thick", 'id="lk-u0"')])
        markup = f'''    <div class="paper" id="{i}-p">
      <svg width="660" height="410" viewBox="0 0 660 410" style="position:absolute;left:0;top:0">{svg}</svg>
      {hand("lk-n1", "1", 50, 26, 44, "r")} {hand("lk-s1", "Catat setiap hari", 110, 26, 54)}
      {hand("lk-n2", "2", 48, 116, 44, "r")} {hand("lk-s2", "Cari di mana silap", 110, 116, 54)}
      {hand("lk-n3", "3", 48, 206, 44, "r")} {hand("lk-s3", "Baru bincang:", 110, 206, 54)}
      {hand("lk-a", "supplement", 70, 300, 50, "b")}
      {hand("lk-b", "rawatan", 268, 300, 50, "b")}
      {hand("lk-c", "lifestyle", 446, 300, 50, "b")}
    </div>'''
        js = paper_in(pid, 0.0, -1.2)
        for n, src in [(1, 258.8), (2, 263.2), (3, 265.4)]:
            js += draw(f"#lk-c{n}", L(sc, src) - .1, .35) + write(f"#lk-n{n}", L(sc, src) - .1, 1)
            js += write(f"#lk-s{n}", L(sc, src), 16)
            sfx("pop", st + L(sc, src))
        for c, u, src in [("a", 0, 267.6), ("b", 1, 268.8), ("c", 2, 270.0)]:
            js += write(f"#lk-{c}", L(sc, src), 9) + draw(f"#lk-u{u}", L(sc, src) + .3, .3)
            sfx("click-soft", st + L(sc, src))
        js += paper_out(pid, end)
        sfx("whoosh-short", st)
        return css, markup, js

    raise ValueError(k)
