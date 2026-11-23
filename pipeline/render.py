#!/usr/bin/env python3
"""Overlay renderer: subtitles, keyword emphasis, infographic cards, full-screen title cards.
Usage: render.py SCRATCH [preview_start preview_end]  -> writes work/final.mp4 (or work/test.mp4)
"""
import json, sys, math, subprocess, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]
W, H, FPS = 1080, 1920, 30
INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
ANTON = f"{S}/fonts/Anton.ttf"
_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(ANTON if name == "Anton" else INTER % name, size)
    return _fc[k]

BLUE_TOP, BLUE_BOT, GLOW = (110, 165, 255), (28, 84, 235), (40, 110, 255)
GREEN, RED, AMBER = (34, 197, 94), (239, 68, 68), (245, 166, 35)

# ---------------------------------------------------------------- timeline mapping
_SJ = json.load(open(f"{S}/work/segs.json"))
SEGS, SP = _SJ["segs"], _SJ["speed"]
def m(t):
    """source time -> edited time"""
    for sg in SEGS:
        if t < sg["a"]:
            return sg["t"]
        if t < sg["b"]:
            return sg["t"] + (t - sg["a"]) / SP
    last = SEGS[-1]
    return last["t"] + last["n"] / FPS
DUR = m(1e9)

# ---------------------------------------------------------------- helpers
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def text_w(txt, f, tracking=0):
    if not txt: return 0
    return int(f.getlength(txt) + tracking * (len(txt) - 1))

def draw_tracked(d, xy, txt, f, fill, tracking=0):
    x, y = xy
    if tracking == 0:
        d.text((x, y), txt, font=f, fill=fill); return
    for ch in txt:
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + tracking

def gradient_text(txt, f, top=BLUE_TOP, bot=BLUE_BOT, glow=True, tracking=0, pad=60, stroke=0):
    """Blue gradient text with soft glow (reference 'SHARE' / 'PROPER FLOW' look)."""
    tw = text_w(txt, f, tracking); asc, desc = f.getmetrics()
    th = asc + desc
    im = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    draw_tracked(md, (pad, pad), txt, f, 255, tracking)
    if stroke:
        md2 = ImageDraw.Draw(mask)
        md2.text((pad, pad), txt, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
    bb = mask.getbbox() or (0, 0, 1, 1)
    grad = np.zeros((im.size[1], im.size[0], 4), np.uint8)
    y0, y1 = bb[1], bb[3]
    for y in range(im.size[1]):
        k = min(max((y - y0) / max(1, y1 - y0), 0), 1)
        grad[y, :, :3] = [int(top[i] * (1 - k) + bot[i] * k) for i in range(3)]
    grad[..., 3] = np.array(mask)
    body = Image.fromarray(grad, "RGBA")
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    if glow:
        g = mask.filter(ImageFilter.GaussianBlur(22))
        gl = Image.new("RGBA", im.size, GLOW + (0,)); gl.putalpha(g.point(lambda v: int(v * 0.85)))
        out = Image.alpha_composite(out, gl)
        # darker drop for depth
        sh = Image.new("RGBA", im.size, (10, 30, 110, 0)); sh.putalpha(mask.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * .55)))
        out.alpha_composite(sh, (0, 5))
    out = Image.alpha_composite(out, body)
    # subtle top highlight line
    hl = Image.new("RGBA", im.size, (255, 255, 255, 0))
    hm = np.array(mask).astype(np.float32)
    rows = np.zeros_like(hm); rows[y0:y0 + max(2, (y1 - y0) // 6)] = 1
    hl.putalpha(Image.fromarray((hm * rows * 0.35).astype(np.uint8)))
    out = Image.alpha_composite(out, hl)
    return out

def shadow_text(txt, f, fill=(255, 255, 255), tracking=0, shadow=150, blur=6, stroke=0):
    tw = text_w(txt, f, tracking); asc, desc = f.getmetrics(); pad = 30
    im = Image.new("RGBA", (tw + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    mask = Image.new("L", im.size, 0); md = ImageDraw.Draw(mask)
    if tracking:
        draw_tracked(md, (pad, pad), txt, f, 255, tracking)
    else:
        md.text((pad, pad), txt, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * shadow / 255)))
    im.alpha_composite(sh, (0, 3))
    d = ImageDraw.Draw(im)
    if tracking: draw_tracked(d, (pad, pad), txt, f, fill + (255,), tracking)
    else: d.text((pad, pad), txt, font=f, fill=fill + (255,))
    return im

def rounded(size, r, fill, outline=None, width=2):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=fill, outline=outline, width=width)
    return im

def icon_status(kind, d=40):
    s = 4; im = Image.new("RGBA", (d * s, d * s), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    col = {"ok": GREEN, "bad": RED, "up": RED, "down": AMBER}[kind]
    g.ellipse((0, 0, d * s - 1, d * s - 1), fill=col + (255,))
    w = 5 * s; c = d * s / 2
    if kind == "ok":
        g.line([(c - 9 * s, c), (c - 2.5 * s, c + 7 * s), (c + 10 * s, c - 7 * s)], fill="white", width=w, joint="curve")
    elif kind == "bad":
        g.line([(c - 8 * s, c - 8 * s), (c + 8 * s, c + 8 * s)], fill="white", width=w)
        g.line([(c + 8 * s, c - 8 * s), (c - 8 * s, c + 8 * s)], fill="white", width=w)
    elif kind == "up":
        g.polygon([(c, c - 11 * s), (c - 10 * s, c + 1 * s), (c + 10 * s, c + 1 * s)], fill="white")
        g.rectangle((c - 3.5 * s, c, c + 3.5 * s, c + 11 * s), fill="white")
    elif kind == "down":
        g.polygon([(c, c + 11 * s), (c - 10 * s, c - 1 * s), (c + 10 * s, c - 1 * s)], fill="white")
        g.rectangle((c - 3.5 * s, c - 11 * s, c + 3.5 * s, c), fill="white")
    return im.resize((d, d), Image.LANCZOS)

def glyph(kind, d=30, col=(170, 178, 192)):
    """tiny line icons for rows / headers"""
    s = 4; im = Image.new("RGBA", (d * s, d * s), (0, 0, 0, 0)); g = ImageDraw.Draw(im); c = col + (255,); w = 2 * s + 2
    D = d * s
    if kind == "drop":
        g.ellipse((D * .22, D * .38, D * .78, D * .94), outline=c, width=w)
        g.line([(D * .5, D * .06), (D * .24, D * .55)], fill=c, width=w); g.line([(D * .5, D * .06), (D * .76, D * .55)], fill=c, width=w)
    elif kind == "pulse":
        g.line([(0, D * .55), (D * .3, D * .55), (D * .42, D * .2), (D * .58, D * .85), (D * .7, D * .55), (D, D * .55)], fill=c, width=w, joint="curve")
    elif kind == "cal":
        g.rounded_rectangle((D * .08, D * .16, D * .92, D * .92), D * .12, outline=c, width=w)
        g.line([(D * .08, D * .38), (D * .92, D * .38)], fill=c, width=w)
    elif kind == "steth":
        g.arc((D * .12, D * .05, D * .7, D * .7), 0, 180, fill=c, width=w)
        g.line([(D * .41, D * .7), (D * .41, D * .85)], fill=c, width=w); g.ellipse((D * .6, D * .62, D * .88, D * .9), outline=c, width=w)
    elif kind == "list":
        g.rounded_rectangle((D * .15, D * .08, D * .85, D * .92), D * .1, outline=c, width=w)
        for yy in (.35, .55, .75): g.line([(D * .3, D * yy), (D * .7, D * yy)], fill=c, width=w)
    elif kind == "family":
        for cx, r in ((.3, .13), (.7, .13), (.5, .09)):
            g.ellipse((D * (cx - r), D * .12, D * (cx + r), D * (.12 + 2 * r)), outline=c, width=w)
        g.arc((D * .08, D * .45, D * .52, D * 1.1), 180, 360, fill=c, width=w)
        g.arc((D * .48, D * .45, D * .92, D * 1.1), 180, 360, fill=c, width=w)
    elif kind == "warn":
        g.polygon([(D * .5, D * .06), (D * .95, D * .9), (D * .05, D * .9)], outline=c, width=w)
        g.line([(D * .5, D * .36), (D * .5, D * .62)], fill=c, width=w); g.ellipse((D * .46, D * .72, D * .54, D * .8), fill=c)
    elif kind == "pill":
        g.rounded_rectangle((D * .05, D * .3, D * .95, D * .7), D * .2, outline=c, width=w); g.line([(D * .5, D * .3), (D * .5, D * .7)], fill=c, width=w)
    return im.resize((d, d), Image.LANCZOS)

# ---------------------------------------------------------------- elements
class Card:
    """Dark glass checklist card (reference: 'Brief aku ke Claude')."""
    def __init__(self, t0, t1, title, items, label="", icon="list", y=1070, width=720, progress=None):
        self.t0, self.t1, self.title, self.items, self.y, self.wd = t0, t1, title, items, y, width
        self.progress = progress
        self.rowh, self.head = 78, 92
        hgt = self.head + len(items) * self.rowh + 26 + (34 if progress else 0)
        self.size = (width, hgt)
        base = Image.new("RGBA", (width, self.head), (0, 0, 0, 0))
        d = ImageDraw.Draw(base)
        base.alpha_composite(glyph(icon, 30, (230, 233, 240)), (30, 31))
        d.text((74, 28), title, font=font("Bold", 33), fill=(245, 246, 250))
        if label and 74 + font("Bold", 33).getlength(title) + font("Medium", 22).getlength(label) + 50 < width:
            f = font("Medium", 22); d.text((width - 30 - f.getlength(label), 36), label, font=f, fill=(120, 126, 140))
        self.base = base
        self.rows = []
        for (txt, kind, ic, _t) in items:
            r = rounded((width - 40, self.rowh - 12), 16, (255, 255, 255, 12))
            rd = ImageDraw.Draw(r)
            r.alpha_composite(glyph(ic, 28), (20, (self.rowh - 12 - 28) // 2))
            rd.text((64, (self.rowh - 12) // 2 - 17), txt, font=font("Medium", 29), fill=(232, 235, 242))
            self.rows.append((r, icon_status(kind, 38) if kind else None))
    def events(self):
        ev = [("whoosh", self.t0)]
        ev += [("pop", it[3] + 0.12) for it in self.items if it[1]]
        return ev
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        vis = 0.0
        for (_, _, _, ti) in self.items: vis += ease_out((t - ti + 0.05) / 0.3)
        hcur = min(self.size[1], int(self.head + max(vis, 0.6) * self.rowh + 16 + (34 if self.progress else 0)))
        im = rounded((self.wd, hcur), 30, (20, 22, 28, 232), (255, 255, 255, 26), 2)
        im.alpha_composite(self.base, (0, 0))
        for i, ((txt, kind, ic, ti), (row, st)) in enumerate(zip(self.items, self.rows)):
            k = ease_out((t - ti) / 0.28)
            if k <= 0: continue
            y = self.head + i * self.rowh
            rr = row.copy()
            if st is not None:
                ks = ease_back((t - ti - 0.12) / 0.25)
                if ks > 0:
                    sz = max(2, int(38 * ks)); s2 = st.resize((sz, sz), Image.LANCZOS)
                    rr.alpha_composite(s2, (row.size[0] - 24 - 19 - sz // 2, (row.size[1] - sz) // 2))
            rr.putalpha(Image.fromarray((np.array(rr.getchannel("A")) * k).astype(np.uint8)))
            im.alpha_composite(rr, (20 + int((1 - k) * 30), y))
        if self.progress:
            p0, p1 = self.progress
            k = min(max((t - p0) / (p1 - p0), 0), 1)
            y = hcur - 46; d = ImageDraw.Draw(im)
            d.rounded_rectangle((30, y, self.wd - 30, y + 10), 5, fill=(255, 255, 255, 22))
            if k > 0: d.rounded_rectangle((30, y, 30 + int((self.wd - 60) * k), y + 10), 5, fill=(70, 130, 255, 255))
        # global in/out animation
        a_in = ease_out((t - self.t0) / 0.35); a_out = ease_out((self.t1 - t) / 0.25)
        a = min(a_in, a_out)
        sc = 0.92 + 0.08 * a
        dy = int((1 - a_in) * 60)
        return im, a, sc, ((W - self.size[0]) // 2, self.y + dy)


class Compare:
    """Bar comparison infographic card."""
    def __init__(self, t0, t1, rows, title, y=1090, width=760):
        self.t0, self.t1, self.rows, self.y, self.wd = t0, t1, rows, y, width
        self.size = (width, 110 + len(rows) * 150)
        b = rounded(self.size, 30, (20, 22, 28, 232), (255, 255, 255, 26), 2); d = ImageDraw.Draw(b)
        b.alpha_composite(glyph("pulse", 30, (230, 233, 240)), (30, 31))
        d.text((74, 28), title, font=font("Bold", 33), fill=(245, 246, 250))
        self.base = b
    def events(self): return [("whoosh", self.t0)] + [("pop", r[4]) for r in self.rows]
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        im = self.base.copy(); d = ImageDraw.Draw(im)
        for i, (lab, val, frac, col, ti) in enumerate(self.rows):
            y = 100 + i * 150
            k = ease_out((t - ti) / 0.6)
            if k <= 0: continue
            d.text((32, y), lab, font=font("SemiBold", 28), fill=(200, 205, 215, int(255 * min(1, k * 2))))
            bw = self.wd - 64
            d.rounded_rectangle((32, y + 48, 32 + bw, y + 92), 22, fill=(255, 255, 255, 16))
            fw = int(bw * frac * k)
            if fw > 44: d.rounded_rectangle((32, y + 48, 32 + fw, y + 92), 22, fill=col + (255,))
            f = font("Bold", 28); tw = f.getlength(val)
            tx = 32 + max(fw, 44) + 16 if 32 + fw + 16 + tw < self.wd - 20 else 32 + fw - tw - 20
            d.text((tx, y + 52), val, font=f, fill=(255, 255, 255, int(255 * k)))
        a_in = ease_out((t - self.t0) / 0.35); a = min(a_in, ease_out((self.t1 - t) / 0.25))
        return im, a, 0.92 + 0.08 * a, ((W - self.size[0]) // 2, self.y + int((1 - a_in) * 60))


class FullCard:
    """Full-screen light title card (reference: 'VIDEO REFERENCE / SHARE')."""
    def __init__(self, t0, t1, caption, big, inner=None, big2=None):
        self.t0, self.t1, self.inner = t0, t1, inner
        bg = np.zeros((H, W, 3), np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        base = 0.965 - 0.07 * (yy / H)
        rad = np.exp(-(((xx - W * .5) / (W * .7)) ** 2 + ((yy - H * .35) / (H * .45)) ** 2))
        v = base + 0.03 * rad
        bg[..., 0] = v * 240; bg[..., 1] = v * 244; bg[..., 2] = v * 250
        self.bg = Image.fromarray(np.clip(bg + np.random.normal(0, 1.2, bg.shape), 0, 255).astype(np.uint8)).convert("RGBA")
        self.cap = shadow_text(caption, font("SemiBold", 34), fill=(70, 78, 92), tracking=9, shadow=0)
        fs = 200
        while text_w(big, font("Anton", fs)) > W - 120: fs -= 6
        self.big = gradient_text(big, font("Anton", fs))
        self.big2 = None
        if big2:
            fs2 = fs
            while text_w(big2, font("Anton", fs2)) > W - 120: fs2 -= 6
            self.big2 = gradient_text(big2, font("Anton", fs2))
    def events(self): return [("hit", self.t0)] + (self.inner.events() if self.inner else [])
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        im = self.bg.copy()
        ka = ease_out((t - self.t0) / 0.3)
        c = self.cap.copy(); c.putalpha(Image.fromarray((np.array(c.getchannel("A")) * ka).astype(np.uint8)))
        cy = 520
        im.alpha_composite(c, ((W - c.size[0]) // 2, cy - 30 + int((1 - ka) * 15)))
        y = cy + 20
        for j, bimg in enumerate([self.big] + ([self.big2] if self.big2 else [])):
            kb = ease_back((t - self.t0 - 0.05 - j * 0.08) / 0.35)
            if kb <= 0: continue
            sc = 1.25 - 0.25 * kb
            b = bimg.resize((max(1, int(bimg.size[0] * sc)), max(1, int(bimg.size[1] * sc))), Image.BICUBIC)
            al = min(1, kb * 1.5)
            b.putalpha(Image.fromarray((np.array(b.getchannel("A")) * al).astype(np.uint8)))
            hh = bimg.size[1] - 120
            im.alpha_composite(b, ((W - b.size[0]) // 2, y + (bimg.size[1] - b.size[1]) // 2 - 60))
            y += hh - 10
        if self.inner:
            r = self.inner.frame(t)
            if r: composite_el(im, *r)
        # quick fade in/out (2-3 frames) to soften the cut
        a = min(1, (t - self.t0) / 0.08, (self.t1 - t) / 0.08)
        return im, a, 1.0, (0, 0)


class Emph:
    """Two-line keyword caption: small white spaced line + big blue glowing word."""
    def __init__(self, t0, t1, small, big, y=1250):
        self.t0, self.t1, self.y = t0, t1, y
        self.s = shadow_text(small.upper(), font("SemiBold", 40), tracking=5, shadow=190, blur=8)
        fs = 150
        while text_w(big, font("Anton", fs)) > W - 110: fs -= 6
        self.b = gradient_text(big.upper(), font("Anton", fs))
    def events(self): return [("pop", self.t0)]
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        im = Image.new("RGBA", (W, self.s.size[1] + self.b.size[1]), (0, 0, 0, 0))
        im.alpha_composite(EMPH_SCRIM.resize((W, im.size[1])), (0, 0))
        im.alpha_composite(self.s, ((W - self.s.size[0]) // 2, 0))
        k = ease_back((t - self.t0 - 0.06) / 0.3)
        if k > 0:
            sc = 0.7 + 0.3 * k
            b = self.b.resize((max(1, int(self.b.size[0] * sc)), max(1, int(self.b.size[1] * sc))), Image.BICUBIC)
            im.alpha_composite(b, ((W - b.size[0]) // 2, self.s.size[1] - 70 + (self.b.size[1] - b.size[1]) // 2))
        a = min(ease_out((t - self.t0) / 0.15), ease_out((self.t1 - t) / 0.15))
        return im, a, 1.0, (0, self.y - 60)


class Badge:
    """Small pill label (disclaimer / hook tag)."""
    def __init__(self, t0, t1, txt, y, dark=True, size=26):
        self.t0, self.t1, self.y = t0, t1, y
        f = font("Medium", size); tw = int(f.getlength(txt))
        self.im = rounded((tw + 56, size + 34), (size + 34) // 2, (15, 17, 22, 170) if dark else (255, 255, 255, 220))
        ImageDraw.Draw(self.im).text((28, 15), txt, font=f, fill=(225, 228, 236) if dark else (40, 44, 52))
    def events(self): return []
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        a = min(ease_out((t - self.t0) / 0.3), ease_out((self.t1 - t) / 0.3))
        return self.im, a, 1.0, ((W - self.im.size[0]) // 2, self.y)


class EndCard:
    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1
        bg = Image.new("RGBA", (W, H), (12, 13, 20, 255))
        g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse((140, 520, 940, 1320), fill=90)
        glowl = Image.new("RGBA", (W, H), (30, 70, 200, 0)); glowl.putalpha(g.filter(ImageFilter.GaussianBlur(160)))
        self.bg = Image.alpha_composite(bg, glowl)
        self.l1 = shadow_text("UBAH. KEKALKAN. AJAK FAMILY.", font("SemiBold", 34), tracking=6, shadow=0, fill=(170, 178, 195))
        self.big = gradient_text("LIFESTYLE", font("Anton", 210))
        bar = rounded((700, 96), 48, (255, 255, 255, 255)); bd = ImageDraw.Draw(bar)
        bd.ellipse((34, 30, 66, 62), outline=(30, 30, 40), width=5); bd.line([(62, 58), (76, 72)], fill=(30, 30, 40), width=6)
        bd.text((100, 26), "Follow untuk tips sihat", font=font("SemiBold", 36), fill=(120, 125, 140))
        btn = rounded((150, 72), 36, BLUE_BOT + (255,)); ImageDraw.Draw(btn).text((28, 16), "Follow", font=font("Bold", 30), fill="white")
        bar.alpha_composite(btn, (538, 12))
        self.bar = bar
        self.disc = shadow_text("Perkongsian pengalaman peribadi — bukan nasihat perubatan. Rujuk doktor anda.", font("Medium", 24), fill=(130, 136, 150), shadow=0)
    def events(self): return [("hit", self.t0)]
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        im = self.bg.copy()
        k = ease_out((t - self.t0) / 0.4)
        c = self.l1.copy(); c.putalpha(Image.fromarray((np.array(c.getchannel("A")) * k).astype(np.uint8)))
        im.alpha_composite(c, ((W - c.size[0]) // 2, 700))
        kb = ease_back((t - self.t0 - 0.1) / 0.4)
        if kb > 0:
            sc = 0.8 + 0.2 * kb
            b = self.big.resize((int(self.big.size[0] * sc), int(self.big.size[1] * sc)), Image.BICUBIC)
            im.alpha_composite(b, ((W - b.size[0]) // 2, 720 + (self.big.size[1] - b.size[1]) // 2))
        kc = ease_out((t - self.t0 - 0.45) / 0.4)
        if kc > 0:
            bb = self.bar.copy(); bb.putalpha(Image.fromarray((np.array(bb.getchannel("A")) * kc).astype(np.uint8)))
            im.alpha_composite(bb, ((W - 700) // 2, 1100 + int((1 - kc) * 40)))
        im.alpha_composite(self.disc, ((W - self.disc.size[0]) // 2, 1640))
        return im, min(1, (t - self.t0) / 0.2), 1.0, (0, 0)


def composite_el(frame, im, a, sc, pos):
    if a <= 0.003: return
    if sc != 1.0:
        nw, nh = max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))
        x = pos[0] + (im.size[0] - nw) // 2; y = pos[1] + (im.size[1] - nh) // 2
        im = im.resize((nw, nh), Image.BICUBIC); pos = (x, y)
    if a < 0.999:
        im = im.copy(); im.putalpha(Image.fromarray((np.array(im.getchannel("A")) * a).astype(np.uint8)))
    # clip
    x, y = pos
    if x < 0 or y < 0 or x + im.size[0] > W or y + im.size[1] > H:
        cx0, cy0 = max(0, -x), max(0, -y)
        im = im.crop((cx0, cy0, min(im.size[0], W - x), min(im.size[1], H - y))); x += cx0; y += cy0
    frame.alpha_composite(im, (x, y))

# ---------------------------------------------------------------- subtitles
FIX = {"risak": "result", "dokter": "doktor", "kesidupan": "kehidupan", "kecing": "kencing", "dia orang": "diorang"}
T = json.load(open(f"{S}/src/transcript.json"))
words = []
for sg in T:
    for w in sg["words"]:
        txt = w["w"].strip()
        if 163.3 <= w["s"] < 166.25: continue
        if txt.startswith("-") and words:   # "sangat-sangat", "bila-bila"
            words[-1]["w"] += txt; words[-1]["e"] = m(w["e"]); continue
        base = txt.strip(",.?!").lower()
        if base in FIX: txt = txt.lower().replace(base, FIX[base])
        words.append({"w": txt, "s": m(w["s"]), "e": m(w["e"])})

chunks, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    gap = words[i + 1]["s"] - w["e"] if i + 1 < len(words) else 9
    clen = sum(len(x["w"]) + 1 for x in cur)
    if len(cur) >= 3 or clen > 16 or w["w"][-1:] in ",.?!" or gap > 0.35:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
for i, c in enumerate(chunks):
    c0 = c[0]["s"]; nxt = chunks[i + 1][0]["s"] if i + 1 < len(chunks) else c[-1]["e"] + 0.4
    for x in c: pass
    chunks[i] = {"t0": c0, "t1": min(nxt, c[-1]["e"] + 0.6), "words": c}

SUBF = font("ExtraBold", 60)
_subcache = {}
def sub_img(ci, active):
    k = (ci, active)
    if k in _subcache: return _subcache[k]
    ws = [x["w"].strip(",.").upper() for x in chunks[ci]["words"]]
    sp = SUBF.getlength(" ")
    tw = int(sum(SUBF.getlength(x) for x in ws) + sp * (len(ws) - 1)); pad = 30
    im = Image.new("RGBA", (tw + pad * 2, 110), (0, 0, 0, 0))
    mask = Image.new("L", im.size, 0); md = ImageDraw.Draw(mask)
    x = pad
    for w in ws: md.text((x, 18), w, font=SUBF, fill=255, stroke_width=5, stroke_fill=255); x += SUBF.getlength(w) + sp
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(mask.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * .55)))
    im.alpha_composite(sh, (0, 4))
    st = Image.new("RGBA", im.size, (8, 12, 24, 0)); st.putalpha(mask.point(lambda v: int(v * .85)))
    im.alpha_composite(st)
    d = ImageDraw.Draw(im); x = pad
    for j, w in enumerate(ws):
        col = (255, 220, 60, 255) if j == active else (255, 255, 255, 255)
        d.text((x, 18), w, font=SUBF, fill=col); x += SUBF.getlength(w) + sp
    _subcache[k] = im
    return im

# ---------------------------------------------------------------- script / timeline (source times -> m())
def M(a, b): return m(a), m(b)
E = []          # overlay elements
HIDE_SUB = []   # ranges where subtitles hidden

def emph(a, b, small, big):
    t0, t1 = M(a, b); E.append(Emph(t0, t1, small, big)); HIDE_SUB.append((t0, t1))

emph(1.10, 5.62, "ramai tanya saya", "Makan ubat ke?")
emph(7.70, 9.51, "saya nak cuba", "Tukar lifestyle")
emph(32.9, 34.65, "dalam masa yang sama", "Ubah lifestyle")
emph(92.7, 93.77, "doktor pun", "Manusia")
emph(101.3, 104.77, "tak ada siapa yang", "Suka makan ubat")
emph(111.2, 112.75, "korang memang boleh", "Sembuh!")
emph(129.2, 132.89, "pastikan korang", "Maintain")
emph(158.75, 160.0, "sebab it's a", "Lifestyle")

# disclaimer badge at start
t0, t1 = M(1.1, 9.0); E.append(Badge(t0, t1, "Perkongsian pengalaman — bukan nasihat perubatan", 230))

# infographic: bacaan bahaya
t0, t1 = M(15.6, 28.2)
E.append(Card(t0, t1, "Kalau bacaan korang macam ni...", [
    ("Tekanan darah terlalu tinggi", "up", "pulse", m(17.1)),
    ("Gula HbA1c teruk", "up", "drop", m(19.4)),
    ("Uric acid tinggi", "up", "drop", m(22.55)),
    ("HDL terlalu rendah", "down", "drop", m(24.23)),
    ("Triglyceride melambung", "up", "drop", m(26.15))], label="ujian darah", icon="list"))

# full card: ikut nasihat doktor
t0, t1 = M(28.2, 31.6)
inner = Card(t0 + 0.3, t1 + 5, "Pelan sementara", [
    ("Makan ubat sekejap", "ok", "pill", t0 + 0.55),
    ("Ikut nasihat doktor", "ok", "steth", m(29.65) + 0.2)], icon="list", y=1000, width=660)
E.append(FullCard(t0, t1, "LANGKAH PERTAMA", "IKUT DOKTOR", inner=inner))

# card: cara yakinkan doktor (journey)
t0, t1 = M(40.9, 62.5)
E.append(Card(t0, t1, "Cara yakinkan doktor", [
    ("6 bulan — result makin baik", "ok", "cal", m(51.97)),
    ("Tak stop, teruskan lagi", "ok", "pulse", m(54.69)),
    ("1 tahun — back to normal", "ok", "cal", m(56.17)),
    ("Baru minta stop ubat", "ok", "pill", m(59.91))], label="pengalaman saya", icon="steth",
    progress=(m(44.3), m(62.0))))

# card: follow-up
t0, t1 = M(66.6, 86.8)
E.append(Card(t0, t1, "Appointment follow-up", [
    ("Repeat ujian darah", "ok", "drop", m(68.05)),
    ("Dalam keadaan tak makan ubat", "ok", "pill", m(78.15)),
    ("Result lebih baik dari sebelum", "ok", "pulse", m(82.9))], label="6–12 bulan", icon="cal"))

# full card: harapan sembuh
t0, t1 = M(113.0, 115.3)
E.append(FullCard(t0, t1, "UNTUK ORANG MUDA", "HARAPAN", big2="SANGAT BESAR"))

# compare infographic
t0, t1 = M(117.1, 124.7)
E.append(Compare(t0, t1, [
    ("Dapat penyakit", "± 10 tahun tabiat", 1.0, (225, 72, 72), m(117.4)),
    ("Ubah lifestyle & sembuh", "± 1 tahun", 0.16, (40, 190, 100), m(121.3))], "Masa: tabiat vs sembuh"))

# full card: metabolic syndrome
t0, t1 = M(137.0, 141.7)
E.append(FullCard(t0, t1, "SEBAB DIA ADALAH", "METABOLIC", big2="SYNDROME"))

# card: tak maintain
t0, t1 = M(141.75, 156.95)
E.append(Card(t0, t1, "Bila tak maintain...", [
    ("Patah balik", "bad", "warn", m(144.0)),
    ("Rosak balik", "bad", "warn", m(145.27)),
    ("Darah tinggi datang balik", "bad", "pulse", m(149.57)),
    ("Kencing manis datang balik", "bad", "drop", m(151.33))], label="metabolic syndrome", icon="warn"))

# card: ajak family
t0, t1 = M(177.2, 186.9)
E.append(Card(t0, t1, "Supaya kekal lama", [
    ("Ubah lifestyle", "ok", "pulse", m(177.3)),
    ("Ajak family sekali", "ok", "family", m(180.2)),
    ("Maintain lebih lama", "ok", "cal", m(183.6))], icon="family"))

# end card (appended after last spoken word)
END0 = DUR
END1 = DUR + 2.6
E.append(EndCard(END0, END1))
TOTAL = END1

FULL = [e for e in E if isinstance(e, (FullCard, EndCard))]
CARDS = [e for e in E if isinstance(e, (Card, Compare))]

def sub_y(t):
    return 1600 if any(c.t0 <= t < c.t1 for c in CARDS) else 1330

# ---------------------------------------------------------------- SFX
def make_sfx(path):
    sr = 48000; n = int(TOTAL * sr) + sr; out = np.zeros(n, np.float32)
    rng = np.random.default_rng(1)
    def pop():
        t = np.arange(int(0.09 * sr)) / sr
        f = 1100 * np.exp(-t * 18) + 500
        return 0.5 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 45)
    def whoosh():
        L = int(0.4 * sr); x = rng.normal(0, 1, L)
        # simple swept one-pole lowpass
        y = np.zeros(L); a = 0
        for i in range(L):
            c = 0.02 + 0.25 * math.sin(math.pi * i / L)
            a += c * (x[i] - a); y[i] = a
        env = np.sin(np.pi * np.arange(L) / L) ** 2
        return 0.9 * y * env / (np.abs(y).max() + 1e-6)
    def hit():
        t = np.arange(int(0.35 * sr)) / sr
        b = 0.8 * np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 25)) * t) * np.exp(-t * 9)
        return b + 0.35 * whoosh()[:len(t)] if len(t) <= int(0.4 * sr) else b
    lib = {"pop": pop(), "whoosh": whoosh(), "hit": hit()}
    for e in E:
        for kind, t in e.events():
            s = lib[kind]; i = int(t * sr)
            if 0 <= i < n - len(s): out[i:i + len(s)] += s
    out = np.clip(out, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())

# ---------------------------------------------------------------- main loop
_yy = np.linspace(0, 1, H)[:, None]
_sa = np.clip((_yy - 0.52) / 0.48, 0, 1) ** 1.4 * 150
SCRIM = np.zeros((H, W, 4), np.uint8); SCRIM[..., 3] = np.broadcast_to(_sa, (H, W)).astype(np.uint8)
SCRIM = Image.fromarray(SCRIM, "RGBA")
_r = np.exp(-(((np.mgrid[0:500, 0:W][1] - W / 2) / (W * .45)) ** 2 + ((np.mgrid[0:500, 0:W][0] - 250) / 190.0) ** 2)) * 150
EMPH_SCRIM = np.zeros((500, W, 4), np.uint8); EMPH_SCRIM[..., 3] = _r.astype(np.uint8); EMPH_SCRIM = Image.fromarray(EMPH_SCRIM, "RGBA")
def overlay(t):
    fr = SCRIM.copy()
    full = [e for e in FULL if e.t0 <= t < e.t1]
    if full:
        r = full[0].frame(t)
        if r: composite_el(fr, *r)
        if isinstance(full[0], EndCard) or (r and r[1] >= 0.999):
            return fr
    for e in E:
        if e in FULL: continue
        r = e.frame(t)
        if r: composite_el(fr, *r)
    if not any(a <= t < b for a, b in HIDE_SUB):
        for ci, c in enumerate(chunks):
            if c["t0"] <= t < c["t1"]:
                act = -1
                for j, w in enumerate(c["words"]):
                    if w["s"] <= t + 0.03: act = j
                im = sub_img(ci, act)
                k = ease_back((t - c["t0"]) / 0.16); sc = 0.9 + 0.1 * k
                composite_el(fr, im, 1.0, sc, ((W - im.size[0]) // 2, sub_y(t)))
                break
    return fr

if __name__ == "__main__":
    a = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    b = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
    if len(sys.argv) > 4 and sys.argv[4] == "stills":
        for tt in sys.argv[5:]:
            t = float(tt)
            vf = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(min(t, DUR - 0.05)), "-i", f"{S}/work/graded.mov", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture_output=True).stdout
            base = Image.frombytes("RGBA", (W, H), vf) if len(vf) == W * H * 4 else Image.new("RGBA", (W, H), (0, 0, 0, 255))
            base.alpha_composite(overlay(t)); base.convert("RGB").resize((540, 960)).save(f"{S}/work/still_{t:.1f}.jpg", quality=88)
        sys.exit()
    sfx = f"{S}/work/sfx.wav"; make_sfx(sfx)
    out = f"{S}/work/final.mp4" if len(sys.argv) <= 2 else f"{S}/work/test.mp4"
    # video: graded footage padded with end-card time; voice cleanup + sfx mix
    vf = f"[0:v]tpad=stop_mode=add:stop_duration={END1 - DUR + 0.2}:color=black,trim=start={a}:end={b},setpts=PTS-STARTPTS[bg];[bg][1:v]overlay=0:0:format=auto,format=yuv420p[v]"
    MUS = f"{S}/music/inspiration.mp3"
    voice = ("highpass=f=85,afftdn=nr=10:nf=-30,"
             "equalizer=f=220:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=9000:t=q:w=1:g=1.5,"
             "deesser=i=0.3,acompressor=threshold=-22dB:ratio=3:attack=4:release=150:makeup=3,"
             "loudnorm=I=-15:TP=-2:LRA=7")
    af = (f"[0:a]{voice},apad,atrim=start={a}:end={b},asetpts=PTS-STARTPTS,asplit=2[vo][key];"
          f"[3:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
          f"volume=0.11,afade=t=in:d=0.6,afade=t=out:st={max(0, (b - a) - 2.2):.2f}:d=2.2[mu];"
          f"[mu][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=450:makeup=1[mud];"
          f"[2:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,volume=0.2,aformat=channel_layouts=stereo[fx];"
          f"[vo]aformat=channel_layouts=stereo[vos];"
          f"[vos][mud][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=9,aresample=48000[a]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", f"{S}/work/graded.mov",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", sfx, "-i", MUS, "-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level:v", "4.2",
           "-maxrate", "28M", "-bufsize", "56M", "-g", "60", "-bf", "2", "-r", str(FPS),
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", str(b - a), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round((b - a) * FPS))
    for i in range(nf):
        t = a + i / FPS
        p.stdin.write(overlay(t).tobytes())
        if i % 300 == 0: print(f"frame {i}/{nf}", flush=True)
    p.stdin.close(); p.wait()
    print("done", out, "dur", TOTAL)
