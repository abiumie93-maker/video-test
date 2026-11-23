#!/usr/bin/env python3
"""Overlay renderer: subtitles, keyword emphasis, infographic cards, full-screen title cards.
Usage: render.py SCRATCH [preview_start preview_end]  -> writes work/final.mp4 (or work/test.mp4)
"""
import json, sys, math, subprocess, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]
ROOT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
ANTON = f"{ROOT}/fonts/Anton.ttf"
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

_r = np.exp(-(((np.mgrid[0:500, 0:W][1] - W / 2) / (W * .45)) ** 2 + ((np.mgrid[0:500, 0:W][0] - 250) / 190.0) ** 2)) * 150
EMPH_SCRIM = np.zeros((500, W, 4), np.uint8); EMPH_SCRIM[..., 3] = _r.astype(np.uint8); EMPH_SCRIM = Image.fromarray(EMPH_SCRIM, "RGBA")
# ================================================================ PROJECT 2 (camera + zoom + SFX)
# ---------------------------------------------------------------- subtitles
FIX = {"beryar-erya": "beria-ria", "kecil": "kencing", "kecing": "kencing", "gaut": "gout", "gaut,": "gout",
       "trigara": "trigliserida", "kesehatan": "kesihatan", "yaitu": "iaitu", "dia orang": "diorang"}
T = json.load(open(f"{S}/src/transcript.json"))
def kept_src(t):
    return any(sg["a"] <= t < sg["b"] for sg in SEGS)
def kept_word(s0, e0):
    """word survives the edit if >= 80 ms of it is inside a kept segment; returns the first kept instant"""
    if kept_src(s0 + 0.03): return s0
    for sg in SEGS:
        ov = min(sg["b"], e0) - max(sg["a"], s0)
        if ov >= 0.20: return max(sg["a"], s0)
    return None
words = []
for sg in T:
    for w in sg["words"]:
        txt = w["w"].strip()
        ks = kept_word(w["s"], w["e"])
        if ks is None: continue
        w = dict(w, s=ks)
        if txt.startswith("-") and words:
            words[-1]["w"] += txt; words[-1]["e"] = m(w["e"]); continue
        if txt.strip(",.?!").lower() == "serak" and words and "trigliserida" in words[-1]["w"].lower():
            words[-1]["e"] = m(w["e"]); continue
        words.append({"w": txt, "s": m(w["s"]), "e": m(w["e"])})
for w in words:
    core = w["w"].strip(",.?!"); low = core.lower()
    if low in FIX: w["w"] = w["w"].replace(core, FIX[low])

chunks, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    gap = words[i + 1]["s"] - w["e"] if i + 1 < len(words) else 9
    clen = sum(len(x["w"]) + 1 for x in cur)
    if len(cur) >= 3 or clen > 16 or w["w"][-1:] in ",.?!" or gap > 0.35:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
for i, c in enumerate(chunks):
    nxt = chunks[i + 1][0]["s"] if i + 1 < len(chunks) else c[-1]["e"] + 0.4
    chunks[i] = {"t0": c[0]["s"], "t1": min(nxt, c[-1]["e"] + 0.6), "words": c}

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

# ---------------------------------------------------------------- extra elements
class LowerThird:
    def __init__(self, t0, t1, name, role, y=1150):
        self.t0, self.t1, self.y = t0, t1, y
        f1, f2 = font("Bold", 46), font("Medium", 29)
        wd = int(max(f1.getlength(name), f2.getlength(role))) + 90
        im = rounded((wd, 140), 26, (18, 20, 26, 225), (255, 255, 255, 24))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((22, 28, 30, 112), 4, fill=BLUE_BOT + (255,))
        d.text((52, 22), name, font=f1, fill=(250, 250, 252))
        d.text((52, 80), role, font=f2, fill=(160, 168, 184))
        self.im = im
    def events(self): return [("swish", self.t0)]
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        k = ease_out((t - self.t0) / 0.4); ko = ease_out((self.t1 - t) / 0.3)
        x = int(60 - (1 - k) * 120 - (1 - ko) * 80)
        return self.im, min(k, ko), 1.0, (x, self.y)

class Tag:
    """Blue product label pill."""
    def __init__(self, t0, t1, txt, y=1180, icon=None):
        self.t0, self.t1, self.y = t0, t1, y
        f = font("Bold", 38); tw = int(f.getlength(txt))
        im = Image.new("RGBA", (tw + 100, 92), (0, 0, 0, 0))
        g = Image.new("L", im.size, 0); ImageDraw.Draw(g).rounded_rectangle((8, 8, im.size[0] - 8, 84), 38, fill=255)
        gl = Image.new("RGBA", im.size, GLOW + (0,)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .6)))
        im.alpha_composite(gl)
        body = Image.new("RGBA", im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(body)
        bd.rounded_rectangle((12, 12, im.size[0] - 12, 80), 34, fill=BLUE_BOT + (255,), outline=(140, 180, 255, 255), width=2)
        im.alpha_composite(body)
        ImageDraw.Draw(im).text((50, 20), txt, font=f, fill="white")
        self.im = im
    def events(self): return [("pop", self.t0)]
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        k = ease_back((t - self.t0) / 0.32); ko = ease_out((self.t1 - t) / 0.2)
        return self.im, min(1, ko), max(0.05, 0.6 + 0.4 * k) * (0.85 + 0.15 * ko), ((W - self.im.size[0]) // 2, self.y)

def bag_icon(d=150):
    s = 4; D = d * s; im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    g.arc((D * .3, D * .05, D * .7, D * .5), 180, 360, fill=(255, 196, 0, 255), width=int(D * .07))
    g.rounded_rectangle((D * .12, D * .28, D * .88, D * .95), D * .1, fill=(255, 196, 0, 255))
    g.rounded_rectangle((D * .12, D * .28, D * .88, D * .4), D * .05, fill=(255, 214, 60, 255))
    g.ellipse((D * .3, D * .36, D * .38, D * .44), fill=(150, 100, 0, 255)); g.ellipse((D * .62, D * .36, D * .7, D * .44), fill=(150, 100, 0, 255))
    return im.resize((d, d), Image.LANCZOS)

class CTA:
    def __init__(self, t0, t1, y=1310):
        self.t0, self.t1, self.y = t0, t1, y
        self.bag = bag_icon(170)
        self.l1 = shadow_text("NAK DAPATKAN SEMUA NI?", font("SemiBold", 40), tracking=4, shadow=190, blur=8)
        self.l2 = gradient_text("TEKAN BEG KUNING", font("Anton", 130), top=(255, 230, 90), bot=(255, 170, 0), glow=False)
        g = Image.new("RGBA", self.l2.size, (0, 0, 0, 0))
        m_ = self.l2.getchannel("A").filter(ImageFilter.GaussianBlur(16))
        g2 = Image.new("RGBA", self.l2.size, (255, 170, 0, 0)); g2.putalpha(m_.point(lambda v: int(v * .7)))
        self.l2 = Image.alpha_composite(g2, self.l2)
    def events(self): return [("ding", self.t0), ("pop", self.t0 + 0.35)]
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        im = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
        im.alpha_composite(EMPH_SCRIM.resize((W, 520)))
        kb = ease_back((t - self.t0) / 0.45)
        bob = math.sin((t - self.t0) * 2 * math.pi * 1.2) * 10
        if kb > 0:
            b = self.bag.resize((max(1, int(170 * kb)), max(1, int(170 * kb))), Image.BICUBIC)
            im.alpha_composite(b, ((W - b.size[0]) // 2, int(10 + bob + (170 - b.size[1]) / 2)))
        im.alpha_composite(self.l1, ((W - self.l1.size[0]) // 2, 190))
        k2 = ease_back((t - self.t0 - 0.3) / 0.35)
        if k2 > 0:
            sc = 0.7 + 0.3 * k2
            l2 = self.l2.resize((int(self.l2.size[0] * sc), int(self.l2.size[1] * sc)), Image.BICUBIC)
            im.alpha_composite(l2, ((W - l2.size[0]) // 2, 210 + (self.l2.size[1] - l2.size[1]) // 2))
        a = min(ease_out((t - self.t0) / 0.2), ease_out((self.t1 - t) / 0.2))
        return im, a, 1.0, (0, self.y)

class EndCard2(EndCard):
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.l1 = shadow_text("JAGA KESIHATAN. MULAKAN", font("SemiBold", 34), tracking=6, shadow=0, fill=(170, 178, 195))
        self.big = gradient_text("DARI RUMAH", font("Anton", 190))
        bar = rounded((700, 110), 55, (255, 255, 255, 255)); bd = ImageDraw.Draw(bar)
        bar.alpha_composite(bag_icon(76), (24, 17))
        bd.text((116, 30), "Tekan beg kuning sekarang", font=font("Bold", 38), fill=(30, 32, 40))
        self.bar = bar
        self.disc = shadow_text("Peranti saringan di rumah tidak menggantikan pemeriksaan & nasihat doktor.", font("Medium", 24), fill=(130, 136, 150), shadow=0)
    def events(self): return [("hit", self.t0)]

class KText:
    """Kinetic typography: words slam in one by one (scale 1.6->1, fade), staggered."""
    def __init__(self, t0, t1, lines, y=None, icon=None, stagger=0.12, scrim=True, max_slams=3):
        self.t0, self.t1, self.icon, self.stagger, self.scrim, self.max_slams = t0, t1, icon, stagger, scrim, max_slams
        self.rows = []
        for txt, kind in lines:
            ws = txt.split()
            if kind == "s":
                f = font("SemiBold", 46); imgs = [shadow_text(w.upper(), f, tracking=5, shadow=200, blur=8) for w in ws]; gap = 22; trim = 30
            else:
                fs = 190 if kind != "m" else 150
                while text_w(txt.upper(), font("Anton", fs)) + 30 * len(ws) > W - 110: fs -= 6
                f = font("Anton", fs)
                if kind == "a": imgs = [gradient_text(w.upper(), f) for w in ws]; trim = 60
                else: imgs = [shadow_text(w.upper(), f, shadow=210, blur=12) for w in ws]; trim = 30
                gap = int(fs * 0.26)
            self.rows.append((imgs, gap, trim, kind))
        hs = [max(i.size[1] - 2 * tr for i in imgs) for imgs, g, tr, k in self.rows]
        tot = sum(hs) + 10 * (len(hs) - 1)
        self.cy = y if y is not None else H // 2 - 40
        yy = self.cy - tot // 2
        self.place = []; k = 0
        for (imgs, gap, tr, kind), h in zip(self.rows, hs):
            wsum = sum(i.size[0] - 2 * tr for i in imgs) + gap * (len(imgs) - 1)
            x = (W - wsum) // 2
            for im in imgs:
                self.place.append((im, x - tr, yy - tr + (h - (im.size[1] - 2 * tr)) // 2, k)); x += im.size[0] - 2 * tr + gap; k += 1
            yy += h + 10
        self.top = self.cy - tot // 2
        self.n = k
        self.ic = icon_status(icon, 120) if icon else None
    def events(self):
        ev = [("slam", self.t0 + 0.05 + i * self.stagger) for i in range(min(self.n, self.max_slams))]
        if self.ic is not None: ev.append(("pop", self.t0 + 0.05 + self.n * self.stagger))
        return ev
    def frame(self, t):
        if not (self.t0 <= t < self.t1): return None
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if self.scrim:
            a0 = min(ease_out((t - self.t0) / 0.2), ease_out((self.t1 - t) / 0.2))
            sc = EMPH_SCRIM.resize((W, 760)); sc.putalpha(sc.getchannel("A").point(lambda v: int(v * a0 * 1.15)))
            fr.alpha_composite(sc, (0, max(0, self.cy - 380)))
        out_k = ease_out((self.t1 - t) / 0.18)
        for im, x, y, k in self.place:
            u = (t - self.t0 - 0.05 - k * self.stagger) / 0.22
            if u <= 0: continue
            e = ease_out(u); sc = (1.6 - 0.6 * e) * (1 + 0.06 * (1 - out_k))
            al = min(1, u * 2) * out_k
            if al <= 0.01: continue
            w2, h2 = max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))
            jm = im.resize((w2, h2), Image.BICUBIC) if sc != 1 else im.copy()
            if al < 0.999: jm.putalpha(jm.getchannel("A").point(lambda v, al=al: int(v * al)))
            composite_el(fr, jm, 1.0, 1.0, (x - (w2 - im.size[0]) // 2, y - (h2 - im.size[1]) // 2))
        if self.ic is not None:
            kb = ease_back((t - self.t0 - 0.05 - self.n * self.stagger) / 0.3)
            if kb > 0:
                d = max(2, int(120 * kb)); ic = self.ic.resize((d, d), Image.LANCZOS)
                composite_el(fr, ic, out_k, 1.0, ((W - d) // 2, self.top - 150 + (120 - d) // 2))
        return fr, 1.0, 1.0, (0, 0)

# ---------------------------------------------------------------- B-roll (Mixkit, Stock Video Free License)
BR_DIR = f"{ROOT}/broll"
BROLL = []   # dicts: t0, t1, id, fx (crop centre 0..1), off (clip start s)
def broll(a, b, vid, fx=0.5, off=0.5):
    t0, t1 = M(a, b); BROLL.append({"t0": t0, "t1": t1, "id": vid, "fx": fx, "off": off})
GRADE_BR = ("eq=contrast=1.06:saturation=0.95:gamma=0.98,colorbalance=rs=-0.03:bs=0.04:rh=0.02:bh=-0.02,"
            "curves=master='0/0.02 0.25/0.21 0.75/0.79 1/0.97',vignette=PI/4.5")
def prep_broll():
    os.makedirs(f"{S}/work/broll", exist_ok=True)
    for b in BROLL:
        n = int(round((b["t1"] - b["t0"]) * FPS)) + 3
        b["file"] = f"{S}/work/broll/{b['id']}_{b['off']}_{b['fx']}_{n}.mov"; b["n"] = n
        if os.path.exists(b["file"]): continue
        vf = (f"crop=ih*9/16:ih:(iw-ih*9/16)*{b['fx']}:0,scale=1080:1920:flags=lanczos,setsar=1,fps={FPS},{GRADE_BR}")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(b["off"]), "-i", f"{BR_DIR}/{b['id']}.mp4", "-vf", vf, "-frames:v", str(n), "-an",
                        "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-pix_fmt", "yuv420p", b["file"]], check=True)

# ---------------------------------------------------------------- script (source times -> m())
def M(a, b): return m(a), m(b)
E = []; HIDE_SUB = []
def emph(a, b, small, big):
    t0, t1 = M(a, b); E.append(KText(t0, t1, [(small, "s"), (big, "a")], y=1290, stagger=0.1)); HIDE_SUB.append((t0, t1))
def ktext(a, b, lines, icon=None, y=None):
    t0, t1 = M(a, b); E.append(KText(t0, t1, lines, y=y, icon=icon)); HIDE_SUB.append((t0, t1))
def card(a, b, title, items, **kw):
    t0, t1 = M(a, b)
    E.append(Card(t0, t1, title, [(x[0], x[1], x[2], m(x[3])) for x in items], **kw))
def full(a, b, cap, big, big2=None, inner=None):
    t0, t1 = M(a, b); E.append(FullCard(t0, t1, cap, big, big2=big2, inner=inner)); return t0, t1

emph(6.70, 9.30, "Khalid, kenapa kau", "Beria-ria sangat?")
card(9.31, 19.0, "Topik yang saya kongsi", [
    ("Darah tinggi", "", "pulse", 9.51), ("Kencing manis", "", "drop", 10.49), ("Gout", "", "drop", 11.51),
    ("Total kolesterol tinggi", "", "drop", 12.79), ("Buah pinggang", "", "list", 17.12)], label="setiap hari", icon="list")
emph(19.05, 20.1, "apa yang", "Kau dapat?")
broll(25.40, 27.47, "4795", fx=0.72, off=0.3)
ktext(25.40, 27.47, [("sebagai seorang", "s"), ("Petugas kesihatan", "a")])
t0, t1 = M(27.48, 32.6); E.append(LowerThird(t0, t1, "Khalid", "Petugas kesihatan · bekas pesakit"))
emph(32.70, 35.2, "saya perasan satu trend yang", "Menakutkan")
broll(35.23, 38.05, "4766", fx=0.55, off=1.0)
ktext(35.23, 38.05, [("pesakit", "s"), ("Semakin ramai", "a")], icon="up")
emph(38.11, 42.35, "pesakit juga semakin", "Muda")
emph(70.45, 73.1, "kita boleh bantu dengan", "Kesedaran awal")
full(78.70, 80.95, "SAYA SENDIRI", "BEKAS PESAKIT")
card(80.95, 88.6, "Bacaan saya dulu", [
    ("Darah tinggi", "bad", "pulse", 81.35), ("Kencing manis", "bad", "drop", 82.53),
    ("Uric acid melampau", "up", "drop", 83.49), ("Trigliserida melambung", "up", "drop", 85.95)], label="pengalaman", icon="steth")
emph(95.70, 98.3, "orang kesihatan pun kena", "Pada usia 30")
full(105.50, 107.5, "INI DIPANGGIL", "PENYAKIT", big2="METABOLIK")
emph(111.30, 113.6, "sebenarnya dapat", "Dicegah awal")
broll(113.70, 115.57, "40531", fx=0.5, off=2.0)
ktext(113.70, 115.57, [("sekiranya kita", "s"), ("Ambil tahu", "b")])
broll(115.59, 118.6, "722", fx=0.5, off=4.0)
ktext(115.59, 118.6, [("dan", "s"), ("Ambil tindakan", "a")], icon="ok")
emph(120.60, 121.68, "contoh", "Darah tinggi")
broll(121.70, 125.35, "4701", fx=0.62, off=1.0)
ktext(121.70, 125.35, [("bukan sebab", "s"), ("Stres semalam", "b")], icon="bad")
broll(128.30, 132.6, "44096", fx=0.5, off=0.5)
ktext(128.30, 132.6, [("tapi gaya hidup", "s"), ("3-4 tahun", "a"), ("ke belakang", "s")])
broll(132.90, 134.02, "25592", fx=0.45, off=1.5)
ktext(132.90, 134.02, [("Stres", "b")])
broll(134.05, 135.15, "31414", fx=0.35, off=2.0)
ktext(134.05, 135.15, [("Tidur", "b")])
broll(135.17, 136.95, "26092", fx=0.66, off=1.0)
ktext(135.17, 136.95, [("Tak jaga", "s"), ("Makan", "a")])
emph(155.85, 157.85, "supaya korang tak jadi", "The next patient")
emph(170.0, 172.0, "tapi macam mana", "Korang nak cek?")
t0, t1 = full(182.20, 186.3, "SEMUA PRODUK DI SINI", "MDA", big2="APPROVED", inner=None)
E[-1].inner = Card(t0 + 0.35, t1 + 5, "Medical Device Authority", [("Lulus kelulusan MDA", "ok", "list", t0 + 0.7)], icon="steth", y=1080, width=680)
card(190.69, 196.75, "Sinocare 3 dalam 1", [
    ("Uric acid", "ok", "drop", 194.01), ("Blood glucose", "ok", "drop", 194.87), ("Total cholesterol", "ok", "drop", 195.93)],
    label="1 meter, 3 ujian", icon="pulse")
t0, t1 = M(197.45, 199.5); E.append(Tag(t0, t1, "Blood glucose meter"))
t0, t1 = M(199.6, 205.5); E.append(Tag(t0, t1, "BP monitor · hitam & putih"))
emph(207.60, 209.4, "harga sangat-sangat", "Mampu milik")
emph(211.70, 213.6, "korang boleh cek", "Dari rumah")
card(220.50, 223.1, "Mulakan dengan", [("Diri sendiri", "ok", "list", 221.45), ("Keluarga", "ok", "list", 222.23)], icon="list")
t0, t1 = M(223.17, 228.9); E.append(CTA(t0, t1)); HIDE_SUB.append((t0, t1))

END0 = DUR; END1 = DUR + 2.6
E.append(EndCard2(END0, END1))
TOTAL = END1
FULL = [e for e in E if isinstance(e, (FullCard, EndCard))]
CARDS = [e for e in E if isinstance(e, Card)]
def sub_y(t):
    return 1600 if any(c.t0 <= t < c.t1 for c in CARDS) or any(isinstance(e, (LowerThird, Tag)) and e.t0 <= t < e.t1 for e in E) else 1330

# ---------------------------------------------------------------- camera
WIDE, MED, CLOSE, PROD, XCLOSE = (1.0, 540, 960), (1.28, 540, 860), (1.6, 540, 760), (1.3, 560, 800), (1.85, 540, 720)
KEYS = [  # (source time, preset, move)  move: cut | smooth | fast
    (6.6, CLOSE, "cut"), (9.31, MED, "smooth"), (19.05, CLOSE, "fast"), (24.27, MED, "cut"),
    (32.70, CLOSE, "smooth"), (35.23, MED, "smooth"), (52.61, CLOSE, "smooth"), (70.45, MED, "smooth"),
    (78.0, CLOSE, "smooth"), (80.95, MED, "cut"), (92.89, CLOSE, "smooth"), (105.5, MED, "cut"),
    (111.30, CLOSE, "fast"), (113.70, MED, "smooth"), (143.89, CLOSE, "smooth"), (155.85, XCLOSE, "fast"),
    (170.0, MED, "smooth"), (172.5, WIDE, "smooth"),
    (176.40, (2.0, 200, 1005), "cut"), (177.10, (2.1, 500, 1230), "cut"), (177.80, (2.0, 810, 1095), "cut"), (178.60, WIDE, "cut"),
    (180.73, MED, "smooth"), (190.69, PROD, "smooth"),
(207.60, CLOSE, "fast"), (209.93, MED, "smooth"), (223.17, WIDE, "smooth"),
]
CAM = sorted([(m(a), p, mv) for a, p, mv in KEYS], key=lambda x: x[0])
# punch-in alternation only flips on segments long enough to read (short ones keep the previous framing)
CUTS = []; _par = 0
for sg in SEGS:
    if sg["n"] / FPS >= 1.0: _par ^= 1
    CUTS.append((sg["t"], _par))
def seg_index(t):
    i = 0
    for c, par in CUTS:
        if c <= t: i = par
    return i
def cam(t):
    prev = (0.0, MED, "cut"); cur = CAM[0] if CAM[0][0] <= t else None
    idx = -1
    for k, c in enumerate(CAM):
        if c[0] <= t: idx = k
    if idx < 0:
        z, cx, cy = MED; since = t
    else:
        tk, p, mv = CAM[idx]
        pz, pcx, pcy = CAM[idx - 1][1] if idx > 0 else MED
        dur = {"cut": 0.0, "smooth": 0.55, "fast": 0.28}[mv]
        u = 1.0 if dur == 0 else min(1, (t - tk) / dur)
        e = u * u * (3 - 2 * u) if mv == "smooth" else 1 - (1 - u) ** 3
        z = math.exp(math.log(pz) + (math.log(p[0]) - math.log(pz)) * e)
        cx = pcx + (p[1] - pcx) * e; cy = pcy + (p[2] - pcy) * e
        since = t - tk - dur
    # slow push-in (Ken Burns) + punch alternation at jump cuts (hidden by the cut itself)
    z *= 1 + 0.012 * min(max(since, 0), 5)
    if z > 1.05 and seg_index(t) % 2 == 1: z *= 1.05
    return z, cx, cy

def crop_box(z, cx, cy):
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h)
    return (x0, y0, x0 + w, y0 + h)

def moving(t):
    for tk, p, mv in CAM:
        dur = {"cut": 0.0, "smooth": 0.55, "fast": 0.28}[mv]
        if dur and tk <= t < tk + dur: return True
    return False

def render_cam(src, t):
    """src: PIL RGB full graded frame. Returns reframed RGB with motion blur during moves."""
    if moving(t):
        acc = None
        for k, dt in enumerate((-1 / 90, 0, 1 / 90)):
            fr = src.resize((W, H), Image.BICUBIC, box=crop_box(*cam(t + dt)))
            acc = fr if acc is None else Image.blend(acc, fr, 1 / (k + 1))
        return acc
    return src.resize((W, H), Image.BICUBIC, box=crop_box(*cam(t)))

# ---------------------------------------------------------------- SFX
def make_sfx(path):
    sr = 48000; n = int((TOTAL + 1) * sr); out = np.zeros(n, np.float32)
    rng = np.random.default_rng(7)
    def env_ad(L, a, d):
        e = np.ones(L); ai = int(a * sr); e[:ai] = np.linspace(0, 1, ai); e[ai:] = np.exp(-np.arange(L - ai) / (d * sr)); return e
    def noise_sweep(L, f0, f1, q=0.25):
        x = rng.normal(0, 1, L); y = np.zeros(L); lp = 0.0; bp = 0.0
        for i in range(L):
            f = f0 + (f1 - f0) * (i / L); c = min(0.99, 2 * math.sin(math.pi * f / sr))
            hp = x[i] - lp - q * bp; bp += c * hp; lp += c * bp; y[i] = bp
        return y / (np.abs(y).max() + 1e-9)
    def whoosh(L=0.45, up=True):
        N = int(L * sr); y = noise_sweep(N, 300 if up else 2600, 2600 if up else 300)
        e = np.sin(np.pi * np.arange(N) / N) ** (1.5 if up else 2.5)
        return 0.9 * y * e
    def pop():
        t = np.arange(int(0.09 * sr)) / sr; f = 1100 * np.exp(-t * 18) + 500
        return 0.55 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 45)
    def tick():
        t = np.arange(int(0.05 * sr)) / sr
        return 0.45 * np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120) + 0.25 * np.sin(2 * np.pi * 3300 * t) * np.exp(-t * 160)
    def hit():
        t = np.arange(int(0.5 * sr)) / sr
        b = 0.9 * np.sin(2 * np.pi * (55 + 90 * np.exp(-t * 22)) * t) * np.exp(-t * 7)
        w = whoosh(0.5, False)[:len(t)] * 0.35
        return b + w
    def ding():
        t = np.arange(int(0.9 * sr)) / sr
        return 0.35 * (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t) + 0.25 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 4)
    def slam():
        t = np.arange(int(0.32 * sr)) / sr
        return 0.85 * np.sin(2 * np.pi * (48 + 70 * np.exp(-t * 30)) * t) * np.exp(-t * 14) + 0.25 * rng.normal(0, 1, len(t)) * np.exp(-t * 60)
    lib = {"slam": slam(), "pop": pop(), "whoosh": whoosh(0.45, True), "whoosh_out": whoosh(0.55, False), "fast": whoosh(0.3, True),
           "swish": 0.6 * whoosh(0.3, True), "tick": tick(), "hit": hit(), "ding": ding()}
    ev = []
    for e in E:
        for kind, t in e.events():
            ev.append(("tick" if kind == "pop" and isinstance(e, Card) else kind, t))
    for e in E:   # cards: whoosh -> softer swish
        if isinstance(e, Card): ev = [(("swish" if (k == "whoosh" and abs(t - e.t0) < 1e-6) else k), t) for k, t in ev]
    for i, (tk, p, mv) in enumerate(CAM):
        if i == 0: continue
        if mv == "cut":
            if p[0] >= 1.9 or CAM[i - 1][1][0] >= 1.9: ev.append(("swish", tk - 0.03))
            continue
        pz = CAM[i - 1][1][0]
        if p[0] < pz: ev.append(("whoosh_out", tk - 0.05))
        elif mv == "fast": ev.append(("fast", tk - 0.04))
        else: ev.append(("whoosh", tk - 0.08))
    for b in BROLL: ev.append(("whoosh", b["t0"] - 0.12))
    for kind, t in ev:
        s = lib[kind]; i = int(max(0, t) * sr)
        if i < n - len(s): out[i:i + len(s)] += s
    out = np.clip(out * 0.9, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())

# ---------------------------------------------------------------- compositing
_yy = np.linspace(0, 1, H)[:, None]
_sa = np.clip((_yy - 0.52) / 0.48, 0, 1) ** 1.4 * 150
SCRIM = np.zeros((H, W, 4), np.uint8); SCRIM[..., 3] = np.broadcast_to(_sa, (H, W)).astype(np.uint8)
SCRIM = Image.fromarray(SCRIM, "RGBA")
def overlay(t):
    fr = SCRIM.copy()
    full_ = [e for e in FULL if e.t0 <= t < e.t1]
    if full_:
        r = full_[0].frame(t)
        if r: composite_el(fr, *r)
        if isinstance(full_[0], EndCard) or (r and r[1] >= 0.999):
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

def active_broll(t):
    for b in BROLL:
        if b["t0"] <= t < b["t1"]: return b
    return None
_brdec = {}
def broll_frame(b, t):
    """sequential decode of the prepared B-roll clip; returns PIL RGB with slow push-in + quick zoom-in entry"""
    k = id(b)
    if k not in _brdec:
        for kk in list(_brdec):
            _brdec[kk][0].kill(); del _brdec[kk]
        _brdec[k] = [subprocess.Popen(["ffmpeg", "-v", "error", "-i", b["file"], "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE), None]
    proc, last = _brdec[k]
    buf = proc.stdout.read(W * H * 3)
    img = Image.frombytes("RGB", (W, H), buf) if len(buf) == W * H * 3 else last
    _brdec[k][1] = img
    u = t - b["t0"]; dur = b["t1"] - b["t0"]
    z = 1.0 + 0.07 * (u / max(dur, 0.1)) + 0.14 * (1 - ease_out(u / 0.22))
    w, h = W / z, H / z
    return img.resize((W, H), Image.BICUBIC, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2))

def compose(src_rgb, t):
    b = active_broll(t)
    if b is not None:
        base = broll_frame(b, t).convert("RGBA")
    else:
        base = render_cam(src_rgb, t).convert("RGBA") if src_rgb is not None else Image.new("RGBA", (W, H), (0, 0, 0, 255))
    base.alpha_composite(overlay(t))
    return base.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "stills":
        prep_broll()
        for tt in sys.argv[3:]:
            _brdec.clear()
            t = float(tt)
            vf = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(min(t, DUR - 0.05)), "-i", f"{S}/work/graded.mov", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            src = Image.frombytes("RGB", (W, H), vf) if len(vf) == W * H * 3 else None
            compose(src, t).resize((540, 960)).save(f"{S}/work/still_{t:.1f}.jpg", quality=88)
        sys.exit()
    prep_broll()
    sfx = f"{S}/work/sfx.wav"; make_sfx(sfx)
    out = f"{S}/work/final.mp4"
    MUS = f"{ROOT}/music/inspiration.mp3"
    voice = ("highpass=f=85,afftdn=nr=8:nf=-35,"
             "equalizer=f=220:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=9000:t=q:w=1:g=1.5,"
             "deesser=i=0.3,acompressor=threshold=-22dB:ratio=3:attack=4:release=150:makeup=3,"
             "loudnorm=I=-15:TP=-2:LRA=7")
    a, b = 0.0, TOTAL
    af = (f"[1:a]{voice},apad,atrim=start={a}:end={b},asetpts=PTS-STARTPTS,asplit=2[vo][key];"
          f"[3:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
          f"volume=0.11,afade=t=in:d=0.6,afade=t=out:st={max(0, (b - a) - 2.2):.2f}:d=2.2[mu];"
          f"[mu][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=450:makeup=1[mud];"
          f"[2:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,volume=0.24,aformat=channel_layouts=stereo[fx];"
          f"[vo]aformat=channel_layouts=stereo[vos];"
          f"[vos][mud][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=9,aresample=48000[a]")
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", f"{S}/work/graded.mov", "-i", sfx, "-i", MUS,
           "-filter_complex", "[0:v]format=yuv420p[v];" + af, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level:v", "4.2",
           "-maxrate", "28M", "-bufsize", "56M", "-g", "60", "-bf", "2", "-r", str(FPS),
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{b - a:.3f}", out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"{S}/work/graded.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    nf = int(round((b - a) * FPS)); FB = W * H * 3
    for i in range(nf):
        t = a + i / FPS
        buf = dec.stdout.read(FB) if t < DUR else b""
        src = Image.frombytes("RGB", (W, H), buf) if len(buf) == FB else None
        enc.stdin.write(compose(src, t).tobytes())
        if i % 300 == 0: print(f"frame {i}/{nf}", flush=True)
    enc.stdin.close(); enc.wait(); dec.kill()
    print("done", out, "dur", TOTAL)
