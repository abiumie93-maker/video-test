#!/usr/bin/env python3
"""Style E "Papan Hijau Nota Lekat" renderer (9:16).  usage: renderE.py P  [TEST=t1,t2,..]"""
import sys, os, json, math, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
from cutout import Cutter, stylise
P = sys.argv[1]; W, H, FPS = 1080, 1920, 30
FD = f"{ROOT}/fontsE"
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        path = {"head": f"{FD}/ArchivoBlack.ttf", "marker": f"{FD}/PermanentMarker.ttf", "hand": f"{FD}/PatrickHand.ttf",
                "mono": f"{FD}/SpaceMono-Bold.ttf", "inter": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"}[name]
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]
YEL, INK, PAPER, RED, TICK = (255, 218, 76), (26, 26, 26), (239, 237, 232), (217, 58, 58), (30, 107, 74)

# ---------------------------------------------------------------- timeline mapping (clip, source t) -> edit t
ED = json.load(open(f"{P}/work/edit.json")); SEGS = ED["segs"]
def m(clip, t):
    best = None
    for sg in SEGS:
        if sg["clip"] != clip: continue
        if sg["a"] <= t < sg["b"]: return sg["t"] + (t - sg["a"])
        if t < sg["a"] and (best is None or sg["a"] < best["a"]): best = sg
    return best["t"] if best else SEGS[-1]["t"] + SEGS[-1]["n"] / FPS
DUR = SEGS[-1]["t"] + SEGS[-1]["n"] / FPS
END = 1.6; TOTAL = DUR + END

# ---------------------------------------------------------------- easing
def eo(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def eb(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------------------------------------------------------------- board background
def make_board():
    bg = np.zeros((H, W, 3), np.float32); bg[:] = (19, 105, 77)
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.35 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
    bg *= np.clip(vig, 0.55, 1)[..., None]
    im = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(grid)
    cell = 64; ox, oy = (W % cell) // 2, (H % cell) // 2
    for k, x in enumerate(range(ox, W, cell)):
        g.line([(x, 0), (x, H)], fill=(79, 143, 120, 150 if k % 4 == 0 else 80), width=3 if k % 4 == 0 else 1)
    for k, y in enumerate(range(oy, H, cell)):
        g.line([(0, y), (W, y)], fill=(79, 143, 120, 150 if k % 4 == 0 else 80), width=3 if k % 4 == 0 else 1)
    im.alpha_composite(grid)
    return im
BOARD = make_board()
rng = np.random.default_rng(5)
GRAIN = [Image.fromarray(np.clip(rng.normal(0, 7, (H // 2, W // 2)) + 128, 0, 255).astype(np.uint8)).resize((W, H)) for _ in range(6)]

# ---------------------------------------------------------------- paper element factories (return RGBA)
def drop_shadow(im, off=(8, 12), blur=10, alpha=0.45, pad=40):
    out = Image.new("RGBA", (im.size[0] + pad * 2, im.size[1] + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); a = Image.new("L", out.size, 0); a.paste(im.getchannel("A"), (pad + off[0], pad + off[1]))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha)))
    out.alpha_composite(sh); out.alpha_composite(im, (pad, pad)); return out

def headline(txt, size=120, bg=YEL, fg=INK):
    f = F("head", size); tw = int(f.getlength(txt)); asc, desc = f.getmetrics()
    im = Image.new("RGBA", (tw + 70, asc + desc + 30), bg + (255,))
    ImageDraw.Draw(im).text((35, 12), txt, font=f, fill=fg)
    return drop_shadow(im, (6, 10), 8, 0.5)

def torn(txt, size=52):
    f = F("marker", size); tw = int(f.getlength(txt)); h = size + 40; w = tw + 80
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = np.random.default_rng(len(txt))
    zl = [(0 + r.uniform(0, 14), y) for y in range(0, h + 1, 10)]; zr = [(w - r.uniform(0, 14), y) for y in range(h, -1, -10)]
    d.polygon(zl + zr, fill=PAPER + (255,))
    d.text((40, 12), txt, font=f, fill=INK)
    return drop_shadow(im, (4, 7), 6, 0.4)

def sticky(lines, size=50, w=330, tick=False, color="yellow"):
    f = F("hand", size); lh = int(size * 1.08); h = max(w, 60 + lh * len(lines) + 40)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    base = np.zeros((h, w, 4), np.uint8)
    top, bot = ((242, 208, 74), (227, 192, 62)) if color == "yellow" else ((250, 250, 248), (236, 236, 232))
    for y in range(h):
        k = y / h; base[y, :, :3] = [int(top[i] * (1 - k) + bot[i] * k) for i in range(3)]
    base[..., 3] = 255
    im = Image.fromarray(base, "RGBA")
    # curled corner shade
    cs = Image.new("L", (w, h), 0); ImageDraw.Draw(cs).polygon([(w, h - 70), (w, h), (w - 70, h)], fill=90)
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0)); shade.putalpha(cs.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(shade)
    d = ImageDraw.Draw(im)
    y = (h - lh * len(lines)) // 2 - 6
    for ln in lines:
        tw = f.getlength(ln); d.text(((w - tw) / 2, y), ln, font=f, fill=(34, 34, 34)); y += lh
    out = drop_shadow(im, (6, 12), 10, 0.45)
    # tape strip on top
    tp = Image.new("RGBA", (150, 46), (255, 255, 255, 120))
    tp = tp.rotate(-6, expand=True, resample=Image.BICUBIC)
    out.alpha_composite(tp, (out.size[0] // 2 - tp.size[0] // 2, 22))
    return out

def tick_layer(size=120):
    """returns function(k)->RGBA green hand-drawn tick drawn progressively"""
    pts = [(0.08, 0.55), (0.38, 0.85), (0.95, 0.12)]
    def draw(k):
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); tot = (L1 + L2) * k
        p = [(x * size, y * size) for x, y in pts]
        if tot <= 0: return im
        if tot <= L1:
            e = tot / L1; d.line([p[0], (p[0][0] + (p[1][0] - p[0][0]) * e, p[0][1] + (p[1][1] - p[0][1]) * e)], fill=TICK + (255,), width=size // 7)
        else:
            d.line([p[0], p[1]], fill=TICK + (255,), width=size // 7); e = (tot - L1) / L2
            d.line([p[1], (p[1][0] + (p[2][0] - p[1][0]) * e, p[1][1] + (p[2][1] - p[1][1]) * e)], fill=TICK + (255,), width=size // 7)
        return im
    return draw

def redtag(txt, size=30):
    f = F("mono", size); tw = int(f.getlength(txt))
    im = Image.new("RGBA", (tw + 34, size + 22), RED + (255,)); ImageDraw.Draw(im).text((17, 6), txt, font=f, fill="white")
    return drop_shadow(im, (3, 5), 4, 0.4, pad=16)

def monotag(txt, size=34):
    f = F("mono", size); tw = int(f.getlength(txt) + 3 * len(txt))
    im = Image.new("RGBA", (tw + 40, size + 26), (26, 26, 26, 255)); d = ImageDraw.Draw(im); x = 20
    for ch in txt: d.text((x, 8), ch, font=f, fill="white"); x += f.getlength(ch) + 3
    return drop_shadow(im, (3, 6), 5, 0.4, pad=16)

def marker_text(txt, size=72, underline=True):
    f = F("marker", size); tw = int(f.getlength(txt)); asc, desc = f.getmetrics()
    im = Image.new("RGBA", (tw + 40, asc + desc + (40 if underline else 10)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((20, 0), txt, font=f, fill="white")
    if underline:
        y = asc + desc + 8; d.line([(24, y + 6), (tw * 0.5, y), (tw + 10, y + 4)], fill="white", width=6, joint="curve")
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * .35)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, 0)); out.alpha_composite(im)
    return out

def badge(lines, d=270):
    s = 3; D = d * s; im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    g.ellipse((0, 0, D - 1, D - 1), fill=YEL + (255,)); g.ellipse((D * .06, D * .06, D * .94, D * .94), outline=INK + (255,), width=s * 4)
    im = im.resize((d, d), Image.LANCZOS); dd = ImageDraw.Draw(im)
    sizes = [int(d * 0.30), int(d * 0.11), int(d * 0.11)]
    tot = sum(sizes[:len(lines)]) + 8 * (len(lines) - 1); y = (d - tot) / 2 - 6
    for ln, sz in zip(lines, sizes):
        f = F("head", sz); tw = f.getlength(ln); dd.text(((d - tw) / 2, y), ln, font=f, fill=INK); y += sz + 8
    return drop_shadow(im, (5, 9), 8, 0.45)

def polaroid_frame(inner_w, inner_h, caption=None):
    pad, bottom = 22, (86 if caption else 46)
    im = Image.new("RGBA", (inner_w + pad * 2, inner_h + pad + bottom), (250, 250, 247, 255))
    if caption:
        f = F("hand", 46); tw = f.getlength(caption)
        ImageDraw.Draw(im).text(((im.size[0] - tw) / 2, inner_h + pad + 12), caption, font=f, fill=(40, 40, 40))
    return im, pad

def bag_icon(d=120):
    s = 4; D = d * s; im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    g.arc((D * .3, D * .05, D * .7, D * .5), 180, 360, fill=(255, 196, 0, 255), width=int(D * .07))
    g.rounded_rectangle((D * .12, D * .28, D * .88, D * .95), D * .1, fill=(255, 196, 0, 255), outline=INK + (255,), width=s * 3)
    return im.resize((d, d), Image.LANCZOS)

# ---------------------------------------------------------------- video polaroid sources
class Clip:
    def __init__(self, f, w, h, start=0.0, crop_y=0.5):
        n = int(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout) * FPS) - 1
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", f, "-vf",
                              f"scale={w}:-2,crop={w}:{h}:0:(ih-{h})*{crop_y},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        self.frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3); self.w, self.h = w, h
    def get(self, u):
        i = int(u * FPS); n = len(self.frames)
        i = i % (2 * n - 2) if n > 1 else 0
        if i >= n: i = 2 * n - 2 - i          # ping-pong loop
        return Image.fromarray(self.frames[i])

# ---------------------------------------------------------------- element
class El:
    """generic paper element: pops in at t0 (scale 1.15->1, rotation settle), flies off at scene end"""
    def __init__(self, t0, img, x, y, rot=0.0, sfx="slap", live=None, write=False, tick_at=None, tick_pos=None, tagimg=None, front=False):
        self.front = front
        self.t0, self.img, self.x, self.y, self.rot, self.sfx, self.live, self.write = t0, img, x, y, rot, sfx, live, write
        self.tick_at, self.tick_pos, self.tagimg = tick_at, tick_pos, tagimg
        self.tick = tick_layer(130) if tick_at is not None else None
        self.t1 = None
    def render(self, t):
        u = t - self.t0
        if u < 0: return None
        im = self.live(u) if self.live else self.img.copy()
        if self.write:   # left-to-right write-on
            k = eo(u / 0.45); wcut = int(im.size[0] * k)
            mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).rectangle((0, 0, wcut, im.size[1]), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(6)); a = Image.fromarray((np.array(im.getchannel("A")).astype(np.float32) * np.array(mask) / 255).astype(np.uint8)); im.putalpha(a)
        if self.tick is not None and t >= self.tick_at:
            tk = self.tick(eo((t - self.tick_at) / 0.35)); im.alpha_composite(tk, self.tick_pos)
        if self.tagimg is not None and self.tick_at is not None and t >= self.tick_at + 0.1:
            im.alpha_composite(self.tagimg, (im.size[0] - self.tagimg.size[0] - 4, 0))
        k = eb(u / 0.22) if not self.write else 1.0
        sc = 1.15 - 0.15 * k if not self.write else 1.0
        rot = self.rot + (1 - eo(u / 0.3)) * 5
        alpha = min(1, u / 0.12)
        dx = 0
        if self.t1 is not None and t > self.t1 - 0.22:   # fly off
            e = eo((t - (self.t1 - 0.22)) / 0.22); dx = (1 if self.x + im.size[0] / 2 > W / 2 else -1) * e * 900
        return im, sc, rot, alpha, dx

def paste(fr, im, cx, cy, sc=1.0, rot=0.0, alpha=1.0):
    if sc != 1.0: im = im.resize((max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))), Image.BICUBIC)
    if abs(rot) > 0.05: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999: im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)
    if x >= W or y >= H or x + im.size[0] <= 0 or y + im.size[1] <= 0: return
    cx0, cy0 = max(0, -x), max(0, -y)
    im = im.crop((cx0, cy0, min(im.size[0], W - x), min(im.size[1], H - y)))
    fr.alpha_composite(im, (x + cx0, y + cy0))

class Scene:
    def __init__(self, t0, t1, side):
        self.t0, self.t1, self.side, self.els = t0, t1, side, []
    def add(self, t0, img, x, y, rot=0.0, **kw):
        if callable(img): kw["live"] = img; img = None
        e = El(max(self.t0 + 0.05, t0), img, x, y, rot, **kw); e.t1 = self.t1; self.els.append(e); return e

# ---------------------------------------------------------------- script
A, B = "A", "B"
def tA(t): return m(A, t)
def tB(t): return m(B, t)
def tAe(t): return m(A, t - 0.02) + 0.02     # scene END at the last word of a range (must not jump to the next range)
def tBe(t): return m(B, t - 0.02) + 0.02
SC = []
def scene(a, b, side): s = Scene(a, b, side); SC.append(s); return s
Q = lambda s: marker_text(s, 110, underline=False)

# polaroid live sources (prepared lazily)
CLIPS = {}
def clip(name, w, h, **kw):
    if name not in CLIPS: CLIPS[name] = Clip(f"{P}/src/{name}.mp4", w, h, **kw)
    return CLIPS[name]
def live_polaroid(name, w, h, caption=None, **kw):
    frame, pad = polaroid_frame(w, h, caption)
    def f(u):
        im = frame.copy(); im.paste(clip(name, w, h, **kw).get(u), (pad, pad))
        im = drop_shadow(im, (8, 14), 12, 0.5)
        tp = Image.new("RGBA", (170, 50), (255, 255, 255, 130)).rotate(4, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(tp, (im.size[0] // 2 - tp.size[0] // 2, 18)); return im
    return f
def still_polaroid(path, w, h, caption=None):
    frame, pad = polaroid_frame(w, h, caption)
    frame.paste(Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS), (pad, pad))
    im = drop_shadow(frame, (8, 14), 12, 0.5)
    tp = Image.new("RGBA", (170, 50), (255, 255, 255, 130)).rotate(-5, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(tp, (im.size[0] // 2 - tp.size[0] // 2, 18)); return im

# S1 hook
s = scene(0.0, tA(7.0), "C")
s.add(tA(3.0), headline("INGAT TAK?", 128), 540, 190, -2)
s.add(tA(3.6), Q("?"), 150, 560, -10, sfx="pop"); s.add(tA(3.75), Q("?"), 930, 520, 8, sfx="pop")
s.add(tA(4.09), torn("SAYA SELALU PROMOSI"), 560, 370, 2)
s.add(tA(4.99), marker_text("HINARIN!", 96), 540, 545, -4, write=True, sfx="write")
# S2 travel pack
s = scene(tA(7.88), tA(12.2), "L")
s.add(tA(8.85), torn("TRAVEL PACK"), 290, 150, -2)
s.add(tA(8.95), live_polaroid("VID_20261028_124821", 420, 380, "travel pack", crop_y=0.55), 770, 390, 4)
s.add(tA(10.13), headline("30ml", 150), 270, 360, 3)
s.add(tA(11.45), marker_text("TAK CUKUP!", 84), 300, 560, -3, write=True, sfx="write")
# S3 test bau
s = scene(tA(12.41), tAe(21.85) + 0.25, "R")
s.add(tA(13.03), headline("TEST BAU", 120), 540, 150, -2)
s.add(tA(15.45), sticky(["Coconut Oil", "& Rice Milk"], 44, 300), 190, 440, -4, tick_at=tA(17.59), tick_pos=(190, 200), tagimg=redtag("FAVOURITE", 26))
s.add(tA(15.67), sticky(["Peach", "& Mango"], 48, 290), 540, 450, 3)
s.add(tA(15.87), sticky(["Olive", "& Argan Oil"], 44, 290), 890, 440, -2)
s.add(tA(19.07), torn("MY FAVOURITE"), 300, 690, -3)
# S4 botol besar
s = scene(tA(23.61), tAe(27.53) + 0.25, "L")
s.add(tA(25.09), headline("TADAAA!", 104), 300, 160, -2)
s.add(tA(25.4), live_polaroid("VID_20261123_201903", 360, 440, "botol besar", crop_y=0.45), 820, 430, 4)
s.add(tA(26.55), torn("BOTOL BESAR TERUS"), 320, 380, -2)
# S5 test bau sama tak / memang sedap
s = scene(tA(34.71), tAe(39.71) + 0.3, "R")
s.add(tA(35.27), monotag("TEST BAU"), 540, 140, 0)
s.add(tA(36.45), marker_text("SAMA TAK?", 92), 540, 300, -3, write=True, sfx="write")
s.add(tA(38.87), headline("MEMANG SEDAP!", 104), 540, 500, -2)
# S6a botol besar = puas-puas
s = scene(tB(0.05), tB(7.55), "L")
s.add(tB(1.77), headline("PAKAI PUAS-PUAS", 96), 540, 170, -2)
s.add(tB(3.45), torn("DAH ADA BOTOL BESAR"), 560, 350, 2)
s.add(tB(4.41), marker_text("SELAMA NI...", 76), 330, 530, -3, write=True, sfx="write")
s.add(tB(5.49), sticky(["botol kecil", "je"], 46, 270), 170, 860, 4, front=True)
s.add(tB(6.61), sticky(["berjimat", "cermat"], 46, 270), 910, 860, -3, front=True)
# S6b big = rumah, small = travel
s = scene(tB(7.55), tBe(11.23) + 0.3, "R")
s.add(tB(7.97), monotag("CARA SAYA GUNA"), 540, 140, 0)
s.add(tB(8.35), sticky(["Botol besar", "= di rumah"], 44, 320), 250, 430, -3)
s.add(tB(9.47), marker_text("vs", 90, underline=False), 540, 430, 0, sfx="pop")
s.add(tB(9.63), sticky(["Botol kecil", "= travel"], 44, 320), 830, 430, 3, tick_at=tB(10.73), tick_pos=(210, 220))
# S7 peach & mango
s = scene(tA(46.63), tAe(55.95) + 0.3, "L")
s.add(tA(46.63), headline("PEACH & MANGO", 100), 540, 160, 2)
s.add(tA(47.0), still_polaroid(f"{P}/work/peach.png", 360, 340, "Peach Extract"), 300, 480, -4)
s.add(tA(48.33), redtag("PUN SEDAP"), 560, 320, 6, sfx="pop")
s.add(tA(52.73), sticky(["bau manis-", "manis"], 48, 300), 800, 500, 3, tick_at=tA(54.3), tick_pos=(190, 210))
# S8 ranking
s = scene(tA(59.91), tAe(63.57) + 0.3, "R")
s.add(tA(60.71), headline("#1", 170), 170, 190, -4)
s.add(tA(61.0), still_polaroid(f"{P}/work/coconut.png", 340, 320, "Coconut Oil"), 470, 420, 3)
s.add(tA(62.13), headline("#2", 120, bg=PAPER), 820, 260, 3)
s.add(tA(62.4), sticky(["Peach", "& Mango"], 46, 270), 860, 560, -3)
# S9 produk Malaysia
s = scene(tB(16.63), tB(25.81), "L")
s.add(tB(18.0), monotag("PERCAYAKAN SAYA"), 540, 130, 0)
s.add(tB(19.43), headline("PRODUK MALAYSIA", 90), 540, 270, -2)
s.add(tB(20.53), torn("LOCAL MADE"), 300, 440, 3)
s.add(tB(24.21), badge(["95%", "BAHAN", "NATURAL"], 300), 820, 520, -6)
# S10 CTA
s = scene(tB(25.81), DUR, "R")
s.add(tB(26.35), marker_text("DAPATKAN TERUS", 80), 540, 170, -3, write=True, sfx="write")
s.add(tB(27.39), headline("BEG KUNING", 128), 470, 350, 2)
s.add(tB(27.39) + 0.05, bag_icon(150), 930, 340, 8, sfx="pop")

for _i in range(len(SC) - 1):            # scenes never overlap
    SC[_i].t1 = min(SC[_i].t1, SC[_i + 1].t0)
    for _e in SC[_i].els: _e.t1 = SC[_i].t1
# ---------------------------------------------------------------- speaker cut-out (live)
CUT = Cutter(f"{ROOT}/models/selfie_segmenter.tflite")
SPK_DY = 620
def speaker_layer(rgb):
    mk = clean_mask(CUT.mask(rgb))
    sty = stylise(rgb)
    h2, w2 = H // 2, W // 2
    ms2 = cv2.resize(mk, (w2, h2), interpolation=cv2.INTER_AREA)
    hard = (ms2 > 0.5).astype(np.uint8) * 255
    dil = cv2.dilate(hard, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    dil = cv2.resize(cv2.GaussianBlur(dil, (0, 0), 0.8), (W, H), interpolation=cv2.INTER_LINEAR)
    af = mk[..., None]
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = (sty * af + 255 * (1 - af)).astype(np.uint8); out[..., 3] = np.maximum(dil, (mk * 255).astype(np.uint8))
    return Image.fromarray(out, "RGBA")
def clean_mask(mk):
    hard = (mk > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(hard, 8)
    if n <= 2: return mk
    big = stats[1:, cv2.CC_STAT_AREA].max()
    keep = np.zeros(n, bool); keep[1:] = stats[1:, cv2.CC_STAT_AREA] > big * 0.08
    return mk * keep[lab]
_SH = None
def shadow_of(sp):
    a = sp.getchannel("A").resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(4)).resize((W, H))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * .5))); return sh
def scene_at(t):
    for s in SC:
        if s.t0 <= t < s.t1: return s
    return None

# ---------------------------------------------------------------- end card
LOGO = None
def end_card(u):
    global LOGO
    fr = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    if LOGO is None:
        lg = Image.open(f"{P}/work/logo.png").convert("RGBA"); sc = 620 / lg.size[0]
        LOGO = lg.resize((620, int(lg.size[1] * sc)), Image.LANCZOS)
    k = eb(u / 0.35); paste(fr, LOGO, W / 2, H / 2 - 40, 0.85 + 0.15 * k, 0, min(1, u / 0.15))
    if u > 0.35:
        t = Image.new("RGBA", (700, 80), (0, 0, 0, 0)); f = F("mono", 34); tx = "cek beg kuning"; tw = f.getlength(tx)
        ImageDraw.Draw(t).text(((700 - tw) / 2, 20), tx, font=f, fill=(90, 90, 90))
        paste(fr, t, W / 2, H / 2 + 110, 1, 0, min(1, (u - 0.35) / 0.25))
    return fr

# ---------------------------------------------------------------- frame compose
def compose(t, spk_rgb):
    if t >= DUR: return end_card(t - DUR).convert("RGB")
    fr = BOARD.copy()
    s = scene_at(t)
    if s:
        for e in s.els:
            if e.front: continue
            r = e.render(t)
            if r:
                im, sc, rot, al, dx = r
                hw = im.size[0] / 2; cx = min(max(e.x, 50 + hw), W - 50 - hw) if hw < W / 2 - 50 else W / 2
                paste(fr, im, cx + dx, e.y, sc, rot, al)
    if spk_rgb is not None and s:
        sp = speaker_layer(spk_rgb)
        u_in = t - s.t0; u_out = s.t1 - t
        k_in = eb(u_in / 0.28); k_out = eo(u_out / 0.2) if u_out < 0.2 else 1.0
        idx = SC.index(s); xoff = (-40 if idx % 2 else 40); zs = 1.0 if idx % 2 else 1.05
        dy = SPK_DY + (1 - min(k_in, 1.0)) * 500 + (1 - k_out) * 700 - (min(k_in, 1.06) - 1) * 300
        sc = zs * (1 + 0.025 * min(1, u_in / max(0.1, s.t1 - s.t0)))
        spr = sp.resize((int(W * sc), int(H * sc)), Image.BILINEAR) if sc != 1 else sp
        x0 = int((W - spr.size[0]) / 2 + xoff); y0 = int(dy)
        sh = shadow_of(spr)
        fr.alpha_composite(sh.crop((0, 0, min(sh.size[0], W - max(0, x0 + 12)), max(1, H - y0 - 16))) if False else sh, (max(0, x0 + 12), min(H - 1, y0 + 16))) if y0 + 16 < H and x0 + 12 >= 0 else None
        paste(fr, spr, x0 + spr.size[0] / 2, y0 + spr.size[1] / 2, 1.0, 0, min(1, u_in / 0.06))
        for e in s.els:
            if e.front:
                r = e.render(t)
                if r: im, sc2, rot, al, dx = r; paste(fr, im, e.x + dx, e.y, sc2, rot, al)
    g = GRAIN[int(t * FPS) % 6]
    out = Image.blend(fr.convert("RGB"), Image.merge("RGB", (g, g, g)), 0.05)
    return out

# ---------------------------------------------------------------- audio
def build_audio(out):
    sr = 48000; n = int((TOTAL + 1) * sr); fx = np.zeros(n, np.float32); r = np.random.default_rng(9)
    def slap():
        L = int(0.12 * sr); x = r.normal(0, 1, L) * np.exp(-np.arange(L) / (0.018 * sr)); t = np.arange(L) / sr
        return 0.5 * x + 0.5 * np.sin(2 * np.pi * (140 + 120 * np.exp(-t * 40)) * t) * np.exp(-t * 30)
    def pop():
        t = np.arange(int(0.09 * sr)) / sr; f = 1000 * np.exp(-t * 18) + 420; return 0.55 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 45)
    def write():
        L = int(0.4 * sr); x = r.normal(0, 1, L); y = np.convolve(x, np.ones(6) / 6, "same"); return 0.18 * y * (0.6 + 0.4 * np.sin(np.arange(L) / sr * 2 * np.pi * 9))
    def tick():
        t = np.arange(int(0.03 * sr)) / sr; return 0.4 * np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90)
    def whoosh():
        L = int(0.3 * sr); x = r.normal(0, 1, L); y = np.convolve(x, np.ones(18) / 18, "same"); return 0.5 * y * np.sin(np.pi * np.arange(L) / L) ** 2
    def ding():
        t = np.arange(int(0.7 * sr)) / sr; return 0.3 * (np.sin(2 * np.pi * 1318 * t) + 0.6 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 5)
    lib = {"slap": slap(), "pop": pop(), "write": write(), "tick": tick(), "whoosh": whoosh(), "ding": ding()}
    def add(k, t):
        s = lib[k]; i = int(t * sr)
        if 0 <= i < n - len(s): fx[i:i + len(s)] += s
    for s in SC:
        add("whoosh", s.t0 - 0.05)
        for e in s.els:
            add(e.sfx, e.t0)
            if e.tick_at is not None: add("tick", e.tick_at + 0.1)
    add("ding", DUR + 0.05)
    with wave.open(f"{P}/work/sfxE.wav", "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
    voice = "highpass=f=70,afftdn=nr=8:nf=-35,equalizer=f=3000:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000"
    fc = (f"[0:a]{voice},apad,atrim=end={TOTAL},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo[v];"
          f"[1:a]volume=0.35,aformat=channel_layouts=stereo[f];[v][f]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{P}/work/speaker.mov", "-i", f"{P}/work/sfxE.wav", "-filter_complex", fc,
                    "-map", "[a]", "-c:a", "pcm_s16le", out], check=True)

if __name__ == "__main__":
    test = [float(x) for x in os.environ.get("TEST", "").split(",") if x]
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"{P}/work/speaker.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    FB = W * H * 3
    if test:
        tiles = []; i = 0; want = sorted(test)
        while want:
            t = i / FPS; buf = dec.stdout.read(FB) if t < DUR else b""
            rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3) if len(buf) == FB else None
            if rgb is not None: CUT.mask(rgb) if abs(t - want[0]) > 0.5 / FPS else None
            if abs(t - want[0]) < 0.5 / FPS:
                tiles.append(compose(t, rgb).resize((540, 960))); want.pop(0)
            i += 1
            if t > TOTAL: break
        cols = 4; rows = (len(tiles) + cols - 1) // cols
        sh = Image.new("RGB", (540 * cols, 960 * rows))
        for k, im in enumerate(tiles): sh.paste(im, ((k % cols) * 540, (k // cols) * 960))
        sh.save(f"{P}/work/testE.jpg", quality=85); dec.kill(); sys.exit()
    aud = f"{P}/work/audioE.wav"; build_audio(aud)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", aud, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", f"{P}/work/finalE.mp4"], stdin=subprocess.PIPE)
    nf = int(round(TOTAL * FPS))
    for i in range(nf):
        t = i / FPS; buf = dec.stdout.read(FB) if t < DUR else b""
        rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3) if len(buf) == FB else None
        enc.stdin.write(compose(t, rgb).tobytes())
        if i % 300 == 0: print(f"frame {i}/{nf}", flush=True)
    enc.stdin.close(); enc.wait(); dec.kill(); print("done", TOTAL)
