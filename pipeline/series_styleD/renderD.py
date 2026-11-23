#!/usr/bin/env python3
"""Style D "Neon Yellow Stack" renderer.  usage: renderD.py VID_KEY  [env TEST=t1,t2]"""
import sys, os, json, math, subprocess, wave, re
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
from cutout import Cutter, grade
import d_videos as DV
KEY = sys.argv[1]; CFG = DV.V[KEY]
P = f"{ROOT}/p4"; SRC = f"{P}/src"; WORK = f"{P}/work/{KEY}"
W, H, FPS = 1080, 1920, 30
YEL = (249, 255, 35); ORA = (232, 158, 52)
FD = f"{ROOT}/fontsD"
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype({"anton": f"{FD}/Anton.ttf", "archivo": f"{FD}/ArchivoBlack.ttf", "serif": f"{FD}/PlayfairXB.ttf",
                                     "serifi": f"{FD}/PlayfairBI.ttf", "bebas": f"{FD}/BebasNeue.ttf"}[name], size)
    return _fc[k]
def full(c): return c if c.startswith("VID_") else f"VID_20261109_{c}"

# ---------------------------------------------------------------- timeline
ED = json.load(open(f"{WORK}/edit.json")); SEGS = ED["segs"]
def m(clip, t):
    clip = full(clip); best = None
    for sg in SEGS:
        if sg["clip"] != clip: continue
        if sg["a"] <= t < sg["b"]: return sg["t"] + (t - sg["a"])
        if t < sg["a"] and (best is None or sg["a"] < best["a"]): best = sg
    return best["t"] if best else None
DUR = SEGS[-1]["t"] + SEGS[-1]["n"] / FPS
def seg_at(t):
    """last segment starting at or before t (robust to the 4-decimal rounding in edit.json)"""
    i = 0
    for k, sg in enumerate(SEGS):
        if sg["t"] <= t + 1e-3: i = k
        else: break
    return i

# ---------------------------------------------------------------- words
def kept(clip, s, e):
    for sg in SEGS:
        if sg["clip"] != clip: continue
        if sg["a"] <= s + 0.03 < sg["b"]: return sg["t"] + max(0, s - sg["a"])
    for sg in SEGS:
        if sg["clip"] == clip and min(sg["b"], e) - max(sg["a"], s) >= 0.2: return sg["t"]
    return None
WORDS = []
for clip in sorted({sg["clip"] for sg in SEGS}):
    T = json.load(open(f"{SRC}/{clip}.json"))
    raw = []
    for sg in T:
        for w in sg["words"]:
            tx = w["w"].strip()
            if tx.startswith("-") and raw: raw[-1]["w"] += tx; raw[-1]["e"] = w["e"]; continue
            raw.append({"w": tx, "s": w["s"], "e": w["e"]})
    for w in raw:
        t = kept(clip, w["s"], w["e"])
        if t is None: continue
        core = w["w"].strip(",.?!").lower()
        txt = w["w"]
        if core in DV.FIX: txt = txt.lower().replace(core, DV.FIX[core])
        WORDS.append({"w": txt, "t": t, "end": t + (w["e"] - w["s"]), "clip": clip})
WORDS.sort(key=lambda x: x["t"])
# merge decimal/compound tokens like "3 -in -1"
for w in WORDS: w["w"] = w["w"].replace("-in-1", "-in-1")

# ---------------------------------------------------------------- phrases -> stacked blocks
KW = sorted([k.lower() for k in DV.KEYWORDS], key=len, reverse=True)
def norm(s): return re.sub(r"[^\w\-\.%/]", "", s.lower())
PH = []; cur = []
for i, w in enumerate(WORDS):
    cur.append(w)
    gap = WORDS[i + 1]["t"] - w["end"] if i + 1 < len(WORDS) else 9
    if len(cur) >= 5 or (w["w"][-1:] in ".?!" and len(cur) >= 2) or gap > 0.45 or (w["w"][-1:] == "," and len(cur) >= 3):
        PH.append(cur); cur = []
if cur: PH.append(cur)

def build_lines(ws):
    """returns list of lines: (kind 'big'|'small', [word dicts])"""
    toks = [norm(w["w"]) for w in ws]; used = [False] * len(ws); spans = []
    for k in KW:
        kt = k.split()
        for i in range(len(ws) - len(kt) + 1):
            if any(used[i:i + len(kt)]): continue
            if [norm(x) for x in kt] == toks[i:i + len(kt)] or (len(kt) == 1 and toks[i] == norm(k)):
                spans.append((i, i + len(kt))); used[i:i + len(kt)] = [True] * len(kt)
    if not spans:   # no keyword -> longest word becomes the big one
        cand = [(len(t), i) for i, t in enumerate(toks) if len(t) >= 4]
        if cand: i = max(cand)[1]; spans.append((i, i + 1))
    spans.sort(); lines = []; i = 0
    big_starts = {a: b for a, b in spans}
    small = []
    while i < len(ws):
        if i in big_starts:
            if small: lines.append(("small", small)); small = []
            lines.append(("big", ws[i:big_starts[i]])); i = big_starts[i]; continue
        small.append(ws[i]); i += 1
        if len(small) >= 3 or sum(len(x["w"]) for x in small) > 16: lines.append(("small", small)); small = []
    if small: lines.append(("small", small))
    # keep at most 2 big lines per block (others become small)
    nb = 0; out = []
    for kd, l in lines:
        if kd == "big":
            nb += 1
            if nb > 2: kd = "small"
        out.append((kd, l))
    return out

def glow_text(txt, font, color=YEL, glow=0.38, blur=14, stroke=None):
    asc, desc = font.getmetrics(); tw = int(font.getlength(txt)); pad = 40
    m_ = Image.new("L", (tw + pad * 2, asc + desc + pad * 2), 0); ImageDraw.Draw(m_).text((pad, pad), txt, font=font, fill=255)
    if stroke is None: stroke = max(3, int(font.size * 0.045))
    ms = Image.new("L", m_.size, 0); ImageDraw.Draw(ms).text((pad, pad), txt, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    out = Image.new("RGBA", m_.size, (0, 0, 0, 0))
    g = Image.new("RGBA", m_.size, color + (0,)); g.putalpha(m_.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * glow))); out.alpha_composite(g)
    sh = Image.new("RGBA", m_.size, (0, 0, 0, 0)); sh.putalpha(ms.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .55))); out.alpha_composite(sh, (0, 4))
    ol = Image.new("RGBA", m_.size, (12, 12, 12, 0)); ol.putalpha(ms); out.alpha_composite(ol)          # solid dark outline -> readable on any background
    body = Image.new("RGBA", m_.size, color + (0,)); body.putalpha(m_); out.alpha_composite(body)
    return out, pad

class Block:
    def __init__(self, ws, t1, side=0):
        self.t0 = ws[0]["t"] - 0.05; self.t1 = t1
        self.lines = build_lines(ws)
        self.items = []   # (img, x, y, t_word, layer) ; layer 'back' (behind person) or 'front'
        y = 0; zig = 0
        for kd, lws in self.lines:
            txt = " ".join(x["w"].strip(",.?!").upper() for x in lws)
            if kd == "big":
                fs = 160
                while F("anton", fs).getlength(txt) > W - 200 and fs > 70: fs -= 6
                f = F("anton", fs); color = YEL; lh = int(fs * 0.98); layer = "back"
            else:
                fs = 50; f = F("archivo", fs); color = (255, 255, 255); lh = int(fs * 1.25); layer = "front"
            lw = int(f.getlength(txt)); bb = f.getbbox(txt)      # real glyph box -> tight, non-overlapping leading
            off = 50 * (zig % 2)
            x0 = (90 + off) if side == 0 else (W - 90 - off - lw)     # compact stack anchored on one side, small zig-zag
            x0 = max(70, min(W - 70 - lw, x0))
            xx = x0
            for w in lws:
                wt = w["w"].strip(",.?!").upper()
                img, pad = glow_text(wt, f, color, glow=0.38 if kd == "big" else 0.0, blur=14)
                self.items.append((img, xx - pad, y - bb[1] - pad, w["t"], layer))
                xx += f.getlength(wt + " ")
            y += (bb[3] - bb[1]) + (14 if kd == "big" else 12); zig += 1
        self.h = y
    def render(self, t, ox, oy, rot):
        """returns (back_layer, front_layer) RGBA full-frame"""
        back = Image.new("RGBA", (W, self.h + 200), (0, 0, 0, 0)); front = Image.new("RGBA", (W, self.h + 200), (0, 0, 0, 0))
        for img, x, y, tw, layer in self.items:
            u = (t - tw + 0.03) / 0.2
            if u <= 0: continue
            e = 1 - (1 - min(1, u)) ** 3
            sc = 1.15 - 0.15 * e; bl = 12 * (1 - e)
            im = img
            if sc != 1: im = im.resize((int(im.size[0] * sc), int(im.size[1] * sc)), Image.BILINEAR)
            if bl > 0.5: im = im.filter(ImageFilter.GaussianBlur(bl))
            if e < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v, e=e: int(v * e)))
            tgt = back if layer == "back" else front
            tgt.alpha_composite(im, (int(x - (im.size[0] - img.size[0]) / 2), int(y + 100 - (im.size[1] - img.size[1]) / 2)) if x - (im.size[0] - img.size[0]) / 2 >= 0 else (0, int(y + 100)))
        outs = []
        for L in (back, front):
            if abs(rot) > 0.1: L = L.rotate(rot, resample=Image.BICUBIC, expand=False)
            full_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); full_.alpha_composite(L, (0, int(oy - 100)))
            outs.append(full_)
        return outs

BLOCKS = []
for i, ph in enumerate(PH):
    t1 = PH[i + 1][0]["t"] - 0.05 if i + 1 < len(PH) else DUR
    t1 = min(t1, ph[-1]["end"] + 1.2)
    BLOCKS.append(Block(ph, t1, side=i % 2))
HOOK_Q = PH[0][-1]["w"].endswith("?") if PH else False

# ---------------------------------------------------------------- giant words / broll / wide (source -> edit times)
GIANT = []
for c, a, b, wd in CFG.get("giant", []):
    t0 = m(c, a); t1 = m(c, b)
    if t0 is not None and t1 is not None and t1 > t0: GIANT.append((t0, t1, wd))
WIDE = []
for c, a, b in CFG.get("wide", []):
    t0, t1 = m(c, a), m(c, b - 0.02)
    if t0 is not None and t1 is not None: WIDE.append((t0, t1 + 0.02))
BROLL = []
for c, a, d, kind, asset in CFG.get("broll", []):
    t0 = m(c, a)
    if t0 is not None: BROLL.append({"t0": t0, "t1": min(DUR, t0 + d), "kind": kind, "asset": asset})

def lavender_bg():
    yy = np.linspace(0, 1, H)[:, None, None]
    c0 = np.array([192, 145, 244], np.float32); c1 = np.array([155, 107, 240], np.float32)
    bg = (c0 * (1 - yy) + c1 * yy) * np.ones((1, W, 1))
    rng = np.random.default_rng(2); bg += rng.normal(0, 4, bg.shape)
    dots = np.zeros((H, W), np.float32); dots[::14, ::14] = 1; dots = cv2.GaussianBlur(dots, (0, 0), 1.2) * 60
    bg += dots[..., None] * 0.25
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
LAV = None
_img_cache = {}
def card_img(asset):
    if asset not in _img_cache:
        p = f"{SRC}/img/{asset}"
        if not os.path.exists(p) or asset.endswith(".avif"):
            pp = p + ".png"
            if not os.path.exists(pp): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, pp])
            p = pp
        im = Image.open(p).convert("RGB")
        # trim phone status/nav bars on screenshots
        if asset.startswith("s_shop"): w_, h_ = im.size; im = im.crop((0, int(h_ * 0.12), w_, int(h_ * 0.86)))
        sc_ = min(860 / im.size[0], 1180 / im.size[1]); im = im.resize((int(im.size[0] * sc_), int(im.size[1] * sc_)), Image.LANCZOS)   # fill the card (up- or down-scale)
        r = 34; mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), r, fill=255)
        card = Image.new("RGBA", (im.size[0] + 24, im.size[1] + 24), (255, 255, 255, 255))
        mk2 = Image.new("L", card.size, 0); ImageDraw.Draw(mk2).rounded_rectangle((0, 0, card.size[0] - 1, card.size[1] - 1), r + 10, fill=255); card.putalpha(mk2)
        rgba = im.convert("RGBA"); rgba.putalpha(mask); card.alpha_composite(rgba, (12, 12))
        sh = Image.new("RGBA", (card.size[0] + 80, card.size[1] + 80), (0, 0, 0, 0)); a = Image.new("L", sh.size, 0); a.paste(card.getchannel("A"), (40, 52))
        sh.putalpha(a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * .45))); sh.alpha_composite(card, (40, 40))
        _img_cache[asset] = sh
    return _img_cache[asset]
_clip_cache = {}
def clip_frame(asset, u):
    name, off = asset.split("@"); off = float(off)
    k = (name, off)
    if k not in _clip_cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(off), "-t", "2.2", "-i", f"{SRC}/{name}", "-vf",
                              f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        _clip_cache[k] = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    fr = _clip_cache[k]; i = min(len(fr) - 1, int(u * FPS))
    return Image.fromarray(grade(fr[i], warm=0.03, sat=1.1, contrast=1.08, lift=4))

# ---------------------------------------------------------------- camera (face-centred crops, punch alternation)
FACES = json.load(open(f"{WORK}/faces.json"))
NOFACE = {"VID_20261109_155958", "VID_20261109_160054", "VID_20261109_160431"}   # per segment: [cx, cy, fh] in 1080x1920 source coords
def cam(t):
    i = seg_at(t); sg = SEGS[i]; cx, cy, fh = FACES[i]
    if sg["clip"] in NOFACE:                       # product close-up clips: show the full frame
        return (0, 0, W, H), 1.0
    zb = min(2.0, max(1.25, 0.24 * H / max(fh, 80)))
    par = 1.0 if i % 2 == 0 else 1.10
    u = t - sg["t"]; push = 1 + 0.025 * min(1, u / max(0.5, sg["n"] / FPS))
    z = zb * par * push
    for a, b in WIDE:
        if a <= t < b:
            k = min(1, (t - a) / 0.35); k = k * k * (3 - 2 * k)
            z = z + (1.0 - z) * k; break
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - 0.44 * h, 0), H - h)
    return (x0, y0, x0 + w, y0 + h), z

CUT = Cutter(f"{ROOT}/models/selfie_segmenter.tflite")
def person_mask(rgb):
    mk = CUT.mask(rgb)
    return Image.fromarray((np.clip(mk, 0, 1) * 255).astype(np.uint8))

def giant_layer(t):
    for a, b, wd in GIANT:
        if a <= t < b:
            u = t - a; e = 1 - (1 - min(1, u / 0.25)) ** 3
            fs = 560
            while F("anton", fs).getlength(wd) > W * 1.15 and fs > 200: fs -= 20
            img, pad = glow_text(wd, F("anton", fs), YEL, glow=0.45, blur=24)
            sc = 1.5 - 0.5 * e
            im = img.resize((int(img.size[0] * sc), int(img.size[1] * sc)), Image.BILINEAR)
            if u < 0.12: im = im.filter(ImageFilter.BoxBlur(10 * (1 - u / 0.12)))
            out = (b - t) / 0.15
            if out < 1: im.putalpha(im.getchannel("A").point(lambda v, o=out: int(v * max(0, o))))
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L.alpha_composite(im, (int(W / 2 - im.size[0] / 2), int(H * 0.36 - im.size[1] / 2)))
            return L
    return None

def serif_hook(t):
    """question hook: white serif line + bigger orange serif line at chest height"""
    if not HOOK_Q: return None
    b = BLOCKS[0]
    if not (b.t0 <= t < b.t1): return None
    ws = PH[0]; n = len(ws); k = max(1, n // 2)
    l1 = " ".join(w["w"] for w in ws[:k]); l2 = " ".join(w["w"] for w in ws[k:])
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for j, (txt, f, col, y, ts) in enumerate(((l1, F("serif", 64), (255, 255, 255), 1180, ws[0]["t"]), (l2, F("serifi", 92), ORA, 1265, ws[k]["t"] if k < n else ws[-1]["t"]))):
        u = (t - ts) / 0.25
        if u <= 0: continue
        e = 1 - (1 - min(1, u)) ** 3
        tw = f.getlength(txt)
        while tw > W - 140: f = ImageFont.truetype(f.path, f.size - 4); tw = f.getlength(txt)
        im = Image.new("RGBA", (int(tw) + 60, f.size + 70), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
        dd.text((30, 20), txt, font=f, fill=(0, 0, 0, 160)); im = im.filter(ImageFilter.GaussianBlur(6)); ImageDraw.Draw(im).text((30, 16), txt, font=f, fill=col + (255,))
        im.putalpha(im.getchannel("A").point(lambda v, e=e: int(v * e)))
        L.alpha_composite(im, (int(W / 2 - im.size[0] / 2), int(y + (1 - e) * 30)))
    return L

# ---------------------------------------------------------------- infographic cards (dark glass + status icons, like the earlier videos)
def status_icon(kind, d=46):
    s_ = 4; D = d * s_; im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    col = {"ok": (34, 197, 94), "bad": (239, 68, 68), "up": (239, 68, 68), "info": YEL}[kind]
    g.ellipse((0, 0, D - 1, D - 1), fill=col + (255,)); c = D / 2; w_ = 5 * s_
    ink = (20, 20, 20) if kind == "info" else (255, 255, 255)
    if kind == "ok": g.line([(c - 9 * s_, c), (c - 2.5 * s_, c + 7 * s_), (c + 10 * s_, c - 7 * s_)], fill=ink, width=w_, joint="curve")
    elif kind == "bad":
        g.line([(c - 8 * s_, c - 8 * s_), (c + 8 * s_, c + 8 * s_)], fill=ink, width=w_); g.line([(c + 8 * s_, c - 8 * s_), (c - 8 * s_, c + 8 * s_)], fill=ink, width=w_)
    elif kind == "up":
        g.polygon([(c, c - 11 * s_), (c - 10 * s_, c + 1 * s_), (c + 10 * s_, c + 1 * s_)], fill=ink); g.rectangle((c - 3.5 * s_, c, c + 3.5 * s_, c + 11 * s_), fill=ink)
    else:
        g.ellipse((c - 4 * s_, c - 4 * s_, c + 4 * s_, c + 4 * s_), fill=ink)
    return im.resize((d, d), Image.LANCZOS)
FI = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 36)
class InfoCard:
    ROWH, HEAD, WD = 84, 96, 860
    def __init__(self, title, t0, t1, rows):
        self.t0, self.t1, self.rows = t0, t1, rows
        self.head = Image.new("RGBA", (self.WD, self.HEAD), (0, 0, 0, 0)); d = ImageDraw.Draw(self.head)
        d.rounded_rectangle((32, 34, 42, 66), 4, fill=YEL + (255,))
        d.text((60, 26), title, font=F("archivo", 38), fill=(250, 250, 250))
        self.rimgs = []
        for txt, kind, tr in rows:
            r = Image.new("RGBA", (self.WD - 44, self.ROWH - 12), (0, 0, 0, 0)); rd = ImageDraw.Draw(r)
            rd.rounded_rectangle((0, 0, r.size[0] - 1, r.size[1] - 1), 18, fill=(255, 255, 255, 16))
            rd.text((26, (r.size[1] - 36) // 2 - 4), txt, font=FI, fill=(238, 240, 245))
            self.rimgs.append((r, status_icon(kind)))
    def render(self, t):
        if not (self.t0 <= t < self.t1): return None
        vis = sum(1 - (1 - min(1, max(0, (t - tr + 0.05) / 0.3))) ** 3 for _, _, tr in self.rows)
        h = int(self.HEAD + max(vis, 0.4) * self.ROWH + 14)
        im = Image.new("RGBA", (self.WD, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, self.WD - 1, h - 1), 32, fill=(18, 20, 26, 232), outline=(255, 255, 255, 30), width=2)
        im.alpha_composite(self.head)
        for i, ((txt, kind, tr), (r, ic)) in enumerate(zip(self.rows, self.rimgs)):
            k = 1 - (1 - min(1, max(0, (t - tr) / 0.28))) ** 3
            if k <= 0: continue
            rr = r.copy()
            kb = min(1, max(0, (t - tr - 0.1) / 0.25))
            if kb > 0:
                sz = max(2, int(46 * (0.6 + 0.4 * kb))); rr.alpha_composite(ic.resize((sz, sz)), (rr.size[0] - 26 - sz // 2 - 23, (rr.size[1] - sz) // 2))
            rr.putalpha(rr.getchannel("A").point(lambda v, k=k: int(v * k)))
            y = self.HEAD + i * self.ROWH
            if y + rr.size[1] <= h: im.alpha_composite(rr, (22 + int((1 - k) * 40), y))
        a_in = 1 - (1 - min(1, (t - self.t0) / 0.3)) ** 3; a_out = min(1, (self.t1 - t) / 0.25)
        a = min(a_in, a_out)
        im.putalpha(im.getchannel("A").point(lambda v, a=a: int(v * a)))
        return im, int((W - self.WD) / 2), int(1190 + (1 - a_in) * 70)
CARDS = []
for title, c, a, b, rows in CFG.get("cards", []):
    t0, t1 = m(c, a), m(c, b - 0.02)
    rr = [(txt, kind, m(cc, tr)) for txt, kind, cc, tr in rows if m(cc, tr) is not None]
    if t0 is not None and t1 is not None and rr: CARDS.append(InfoCard(title, t0, t1 + 0.02, rr))

def broll_at(t):
    for b in BROLL:
        if b["t0"] <= t < b["t1"]: return b
    return None

# ---------------------------------------------------------------- frame compose
def compose(rgb, t):
    global LAV
    br = broll_at(t)
    if br is not None:
        u = t - br["t0"]
        if br["kind"] == "img":
            if LAV is None: LAV = lavender_bg()
            fr = LAV.copy(); cd = card_img(br["asset"])
            e = 1 - (1 - min(1, u / 0.25)) ** 3; c1 = 1.70158
            pop = 1 + (c1 + 1) * (min(1, u / 0.3) - 1) ** 3 + c1 * (min(1, u / 0.3) - 1) ** 2
            sc = (0.75 + 0.25 * pop) * (1 + 0.04 * u)
            im = cd.resize((int(cd.size[0] * sc), int(cd.size[1] * sc)), Image.BILINEAR).rotate(-3 + 3 * e, resample=Image.BICUBIC, expand=True)
            fr.alpha_composite(im, (int(W / 2 - im.size[0] / 2), int(H * 0.56 - im.size[1] / 2)))
        else:
            fr = clip_frame(br["asset"], u).convert("RGBA")
            z = 1.0 + 0.05 * u + 0.12 * (1 - min(1, u / 0.2))
            w_, h_ = W / z, H / z
            fr = fr.resize((W, H), Image.BICUBIC, box=((W - w_) / 2, (H - h_) / 2, (W + w_) / 2, (H + h_) / 2))
        blk = next((b for b in BLOCKS if b.t0 <= t < b.t1), None)
        if blk is not None and not (HOOK_Q and blk is BLOCKS[0]):
            back, front = blk.render(t, 0, 150, -5); fr.alpha_composite(back); fr.alpha_composite(front)
        return fr.convert("RGB")
    box, z = cam(t)
    base = Image.fromarray(rgb).resize((W, H), Image.BICUBIC, box=box)
    # zoom-blur punch on the first frames after every cut
    i = seg_at(t); u = t - SEGS[i]["t"]
    if i > 0 and u < 0.1:
        k = 1 - u / 0.1; s = 1 + 0.1 * k
        big = base.resize((int(W * s), int(H * s)), Image.BILINEAR).crop((int((W * s - W) / 2), int((H * s - H) / 2), int((W * s - W) / 2) + W, int((H * s - H) / 2) + H))
        base = Image.blend(base, big.filter(ImageFilter.GaussianBlur(6 * k)), 0.6 * k)
    g = grade(np.array(base), warm=0.03, sat=1.10, contrast=1.08, lift=4)
    fr = Image.fromarray(g).convert("RGBA")
    pm = person_mask(g)
    person = Image.fromarray(g).convert("RGBA"); person.putalpha(pm)
    gl = giant_layer(t)
    blk = next((b for b in BLOCKS if b.t0 <= t < b.t1), None)
    if gl is not None:
        fr.alpha_composite(gl); fr.alpha_composite(person)
    elif blk is not None and not (HOOK_Q and blk is BLOCKS[0]):
        back, front = blk.render(t, 0, 150, -5)
        fr.alpha_composite(back); fr.alpha_composite(person); fr.alpha_composite(front)
    sh = serif_hook(t)
    if sh is not None: fr.alpha_composite(sh)
    for cd_ in CARDS:
        r_ = cd_.render(t)
        if r_: fr.alpha_composite(r_[0], (r_[1], r_[2]))
    return fr.convert("RGB")

# ---------------------------------------------------------------- audio
def build_audio(out):
    sr = 48000; n = int((DUR + 1) * sr); fx = np.zeros(n, np.float32); r = np.random.default_rng(4)
    def pop():
        t = np.arange(int(0.08 * sr)) / sr; f = 1000 * np.exp(-t * 20) + 420; return 0.42 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 50)
    def whoosh(L=0.28):
        N = int(L * sr); x = r.normal(0, 1, N); y = np.convolve(x, np.ones(14) / 14, "same"); return 0.45 * y * np.sin(np.pi * np.arange(N) / N) ** 2
    def boom():
        t = np.arange(int(0.6 * sr)) / sr; return 0.9 * np.sin(2 * np.pi * (50 + 70 * np.exp(-t * 18)) * t) * np.exp(-t * 6)
    def ding():
        t = np.arange(int(0.6 * sr)) / sr; return 0.3 * (np.sin(2 * np.pi * 1318 * t) + 0.6 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 6)
    def tick():
        t = np.arange(int(0.03 * sr)) / sr; return 0.25 * np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90)
    lib = {"pop": pop(), "whoosh": whoosh(), "swish": whoosh(0.22) * 0.6, "boom": boom(), "ding": ding(), "tick": tick()}
    def add(k, t, g=1.0):
        s = lib[k] * g; i = int(t * sr)
        if 0 <= i < n - len(s): fx[i:i + len(s)] += s
    for b in BLOCKS:
        for img, x, y, tw, layer in b.items:
            add("pop" if layer == "back" else "tick", tw, 0.9 if layer == "back" else 0.6)
    for i, sg in enumerate(SEGS[1:], 1):
        if i % 2 == 0: add("swish", sg["t"] - 0.08, 0.7)
    for b in BROLL: add("whoosh", b["t0"] - 0.1)
    for a, b_, wd in GIANT: add("boom", a)
    for cd_ in CARDS:
        add("swish", cd_.t0 - 0.05, 0.9)
        for _, _, tr in cd_.rows: add("tick", tr + 0.1, 1.4)
    for w in WORDS:
        if norm(w["w"]) in ("kuning", "kuning."): add("ding", w["t"] + 0.1)
    with wave.open(f"{WORK}/sfx.wav", "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
    voice = "highpass=f=70,afftdn=nr=8:nf=-35,equalizer=f=3000:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000"
    fc = (f"[0:a]{voice},apad,atrim=end={DUR},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo[v];"
          f"[1:a]volume=0.38,aformat=channel_layouts=stereo[f];[v][f]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{WORK}/speaker.mov", "-i", f"{WORK}/sfx.wav", "-filter_complex", fc, "-map", "[a]", "-c:a", "pcm_s16le", out], check=True)

if __name__ == "__main__":
    test = [float(x) for x in os.environ.get("TEST", "").split(",") if x]
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"{WORK}/speaker.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    FB = W * H * 3
    if test:
        tiles = []; i = 0; want = sorted(test)
        while want:
            t = i / FPS; buf = dec.stdout.read(FB)
            if len(buf) < FB: break
            rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            if abs(t - want[0]) < 0.5 / FPS: tiles.append(compose(rgb, t).resize((540, 960))); want.pop(0)
            i += 1
        cols = 4; rows = (len(tiles) + cols - 1) // cols
        sh = Image.new("RGB", (540 * cols, 960 * rows))
        for k, im in enumerate(tiles): sh.paste(im, ((k % cols) * 540, (k // cols) * 960))
        sh.save(f"{WORK}/test.jpg", quality=85); dec.kill(); sys.exit()
    aud = f"{WORK}/audio.wav"; build_audio(aud)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", aud, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{DUR:.3f}", f"{WORK}/final.mp4"], stdin=subprocess.PIPE)
    nf = int(round(DUR * FPS))
    for i in range(nf):
        buf = dec.stdout.read(FB)
        rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3) if len(buf) == FB else None
        if rgb is None: break
        enc.stdin.write(compose(rgb, i / FPS).tobytes())
        if i % 300 == 0: print(KEY, f"frame {i}/{nf}", flush=True)
    enc.stdin.close(); enc.wait(); dec.kill(); print("done", KEY, DUR)
