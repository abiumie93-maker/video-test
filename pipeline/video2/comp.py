#!/usr/bin/env python3
"""Before/after comparison video (promo). usage: comp.py P  -> P/work/compare.mp4"""
import sys, os, subprocess, json, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
P = sys.argv[1]
ROOT = os.path.dirname(os.path.abspath(__file__))
# reuse helpers/classes from render2 (fonts, text styles, cards...)
sys.argv = ["render2", P]; __file__r = f"{ROOT}/render2.py"
_g = {"__file__": __file__r, "__name__": "r2"}
exec(open(__file__r).read().split("if __name__")[0], _g)
globals().update({k: v for k, v in _g.items() if not k.startswith("__")})
SEGS2 = SEGS; SP2 = SP
AV_SHIFT = 0.61
RAW = f"{P}/src/raw.mp4"; FIN = f"{P}/work/final.mp4"

# ---------------------------------------------------------------- timeline
SPLIT_T0 = 85.8; SPLIT_LEN = 6.2           # a long uncut segment in the edit (Sinocare box)
seg = [s for s in SEGS2 if abs(s["t"] - SPLIT_T0) < 0.05][0]
HOOK_T0 = 67.67                            # "bermotivasi" close-up
hook_seg = [s for s in SEGS2 if abs(s["t"] - HOOK_T0) < 0.05][0]
SECTIONS = [  # (name, start, dur)
    ("hook", 0.0, 3.0), ("before", 3.0, 9.0), ("trans", 12.0, 1.0), ("after", 13.0, 15.2),
    ("split", 28.2, SPLIT_LEN), ("stats", 28.2 + SPLIT_LEN, 5.2)]
TOTAL = SECTIONS[-1][1] + SECTIONS[-1][2]
def section(t):
    for n, a, d in SECTIONS:
        if a <= t < a + d: return n, t - a
    return "stats", t - SECTIONS[-1][1]
BEFORE_SRC = 0.6   # raw 0.6..9.6: question, 3 s of silence, then the same take again

# ---------------------------------------------------------------- frame sources
class Src:
    def __init__(self, f, t0, dur, vf="scale=1080:1920"):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur + 0.5:.3f}", "-i", f,
                                   "-vf", f"{vf},fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None
    def next(self):
        b = self.p.stdout.read(1080 * 1920 * 3)
        if len(b) == 1080 * 1920 * 3: self.last = Image.frombytes("RGB", (1080, 1920), b)
        return self.last
SRC = {
    "hook_raw": Src(RAW, hook_seg["a"] + AV_SHIFT, 3.0), "hook_fin": Src(FIN, HOOK_T0, 3.0),
    "before": Src(RAW, BEFORE_SRC + AV_SHIFT * 0, 9.0),      # 'before' keeps the original (unsynced) recording on purpose
    "after": Src(FIN, 0.0, 15.2),
    "split_raw": Src(RAW, seg["a"] + AV_SHIFT, SPLIT_LEN * SP2 + 0.3, vf=f"scale=1080:1920,setpts=PTS/{SP2}"),
    "split_fin": Src(FIN, SPLIT_T0, SPLIT_LEN),
}

# ---------------------------------------------------------------- graphics
RED = (229, 72, 77); GRN = (34, 197, 94)
def pill(txt, col, size=40, icon=None, pad=34):
    f = font("Bold", size); tw = int(f.getlength(txt)); ih = size + 30
    iw = ih - 16 if icon else 0
    im = Image.new("RGBA", (tw + pad * 2 + (iw + 14 if icon else 0), ih + 20), (0, 0, 0, 0))
    g = Image.new("L", im.size, 0); ImageDraw.Draw(g).rounded_rectangle((8, 8, im.size[0] - 8, ih + 8), ih // 2, fill=255)
    gl = Image.new("RGBA", im.size, col + (0,)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .55))); im.alpha_composite(gl)
    ImageDraw.Draw(im).rounded_rectangle((10, 10, im.size[0] - 10, ih + 6), (ih - 4) // 2, fill=col + (255,))
    x = 10 + pad
    if icon:
        ic = icon_status(icon, iw); bg = Image.new("RGBA", ic.size, (255, 255, 255, 0))
        im.alpha_composite(ic, (x - 10, 10 + (ih - 4 - iw) // 2)); x += iw + 4
    ImageDraw.Draw(im).text((x, 10 + (ih - 4 - size) // 2 - 4), txt, font=f, fill="white")
    return im

def callout(txt, kind):
    """dark pill with red ✗ / green ✓"""
    f = font("SemiBold", 34); tw = int(f.getlength(txt)); h = 78
    im = rounded((tw + 120, h), h // 2, (14, 16, 22, 225), (255, 255, 255, 30))
    im.alpha_composite(icon_status("bad" if kind == "x" else "ok", 46), (18, (h - 46) // 2))
    ImageDraw.Draw(im).text((80, (h - 34) // 2 - 4), txt, font=f, fill=(240, 242, 246))
    return im

LBL_BEFORE = pill("SEBELUM EDIT", RED, 44)
LBL_AFTER = pill("SELEPAS EDIT", BLUE_BOT, 44)
LBL_B_SMALL = pill("SEBELUM", RED, 34); LBL_A_SMALL = pill("SELEPAS", BLUE_BOT, 34)

ISSUES = [(0.4, "Mulut & suara tak sync"), (1.2, "Tiada subtitle"), (3.4, "Senyap lama"), (6.3, "Ulang take / tersasul")]
FEATS = [(0.4, "Senyap & take ulang dibuang"), (2.6, "Subtitle + infografik"), (9.4, "Zoom dinamik + SFX"),
         (11.0, "B-roll 4K"), (13.0, "Mulut & suara sync")]
_cache = {}
def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]

def stack(fr, items, u, x=40, y=210, kind="x"):
    yy = y
    for t0, txt in items:
        k = ease_back((u - t0) / 0.35)
        if k <= 0: continue
        im = cached((txt, kind), lambda: callout(txt, kind))
        composite_el(fr, im, min(1, k * 1.5), 0.6 + 0.4 * k, (x, yy)); yy += 92

def panel(img, label, x, y):
    """540x960 panel with rounded corners + label"""
    p = img.resize((480, 853), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.size[0] - 1, p.size[1] - 1), 28, fill=255)
    p.putalpha(m)
    return p

BG = None
def bg_dark():
    global BG
    if BG is None:
        b = Image.new("RGBA", (W, H), (10, 12, 20, 255))
        g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse((90, 460, 990, 1460), fill=110)
        gl = Image.new("RGBA", (W, H), (30, 70, 200, 0)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(180)))
        BG = Image.alpha_composite(b, gl)
    return BG.copy()

def split_frame(raw_img, fin_img, u, title=None):
    fr = bg_dark()
    for img, x, lbl in ((raw_img, 40, LBL_B_SMALL), (fin_img, 560, LBL_A_SMALL)):
        if img is None: continue
        pn = panel(img, None, x, 0)
        sh = Image.new("RGBA", (pn.size[0] + 60, pn.size[1] + 60), (0, 0, 0, 0))
        sm = Image.new("L", sh.size, 0); sm.paste(pn.getchannel("A"), (30, 30)); sh.putalpha(sm.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * .6)))
        fr.alpha_composite(sh, (x - 30, 560 - 30 + 14)); fr.alpha_composite(pn, (x, 560))
        fr.alpha_composite(lbl, (x + (480 - lbl.size[0]) // 2, 470))
    # arrow between panels
    d = ImageDraw.Draw(fr); cx, cy = 540, 560 + 426
    d.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), fill=(255, 255, 255, 255))
    d.polygon([(cx - 12, cy - 18), (cx + 18, cy), (cx - 12, cy + 18)], fill=BLUE_BOT + (255,))
    return fr

HOOK_KT = None
def frame_at(t):
    global HOOK_KT
    name, u = section(t)
    if name == "hook":
        fr = split_frame(SRC["hook_raw"].next(), SRC["hook_fin"].next(), u)
        if HOOK_KT is None:
            HOOK_KT = KText(0.0, 3.0, [("sebelum vs selepas", "s"), ("Edit guna Claude", "a")], y=290, stagger=0.14, scrim=False)
        r = HOOK_KT.frame(u)
        if r: composite_el(fr, *r)
        cap = cached("cap1", lambda: shadow_text("Video mentah ±4 minit → siap untuk post", font("SemiBold", 36), shadow=0, fill=(190, 198, 215)))
        fr.alpha_composite(cap, ((W - cap.size[0]) // 2, 1460))
        return fr
    if name == "before":
        img = SRC["before"].next().convert("RGBA")
        fr = img
        k = ease_back(u / 0.35)
        composite_el(fr, LBL_BEFORE, 1.0, 0.6 + 0.4 * max(0, k), ((W - LBL_BEFORE.size[0]) // 2, 90))
        stack(fr, ISSUES, u, kind="x")
        if 3.0 <= u < 6.1:   # silence meter
            secs = u - 3.0
            tag = cached(f"sil{int(secs * 10)}", lambda: pill(f"senyap… {secs:0.1f}s", (60, 64, 76), 34))
            fr.alpha_composite(tag, ((W - tag.size[0]) // 2, 1500))
        return fr
    if name == "trans":
        last = SRC["before"].last
        base = last.filter(ImageFilter.GaussianBlur(4 + 30 * u)).convert("RGBA") if last else bg_dark()
        dark = Image.new("RGBA", (W, H), (8, 10, 18, int(200 * min(1, u * 3)))); base.alpha_composite(dark)
        kt = cached("tkt", lambda: KText(0.0, 1.0, [("lepas", "s"), ("Claude edit", "a")], y=900, stagger=0.1, scrim=False))
        r = kt.frame(u)
        if r: composite_el(base, *r)
        return base
    if name == "after":
        fr = SRC["after"].next().convert("RGBA")
        k = ease_back(u / 0.35)
        composite_el(fr, LBL_AFTER, 1.0, 0.6 + 0.4 * max(0, k), ((W - LBL_AFTER.size[0]) // 2, 90))
        stack(fr, FEATS, u, kind="ok")
        return fr
    if name == "split":
        fr = split_frame(SRC["split_raw"].next(), SRC["split_fin"].next(), u)
        t1 = cached("st1", lambda: shadow_text("SAAT YANG SAMA", font("SemiBold", 40), tracking=6, shadow=0, fill=(190, 198, 215)))
        t2 = cached("st2", lambda: gradient_text("BANDINGKAN", font("Anton", 150)))
        fr.alpha_composite(t1, ((W - t1.size[0]) // 2, 150)); fr.alpha_composite(t2, ((W - t2.size[0]) // 2, 200))
        return fr
    # stats / CTA
    fr = bg_dark()
    big = cached("big", lambda: gradient_text("3:52 → 1:54", font("Anton", 170)))
    l1 = cached("l1", lambda: shadow_text("VIDEO MENTAH  →  SIAP POST", font("SemiBold", 36), tracking=5, shadow=0, fill=(170, 178, 195)))
    k = ease_back(u / 0.4)
    fr.alpha_composite(l1, ((W - l1.size[0]) // 2, 250))
    if k > 0: composite_el(fr, big, 1.0, 0.7 + 0.3 * k, ((W - big.size[0]) // 2, 300))
    rows = [(f"{len(SEGS2) - 1} jump cut automatik", 0.3), (f"{len(BROLL)} klip B-roll 4K", 0.5), ("Sync mulut dibetulkan (0.6 s)", 0.7),
            ("Subtitle, infografik, zoom, SFX, muzik", 0.9)]
    y = 640
    for txt, t0 in rows:
        kk = ease_out((u - t0) / 0.3)
        if kk > 0:
            im = cached(("r", txt), lambda: callout(txt, "ok"))
            composite_el(fr, im, kk, 1.0, ((W - im.size[0]) // 2 + int((1 - kk) * 60), y))
        y += 100
    kc = ease_back((u - 1.4) / 0.4)
    if kc > 0:
        c1 = cached("c1", lambda: shadow_text("Diedit sepenuhnya oleh", font("SemiBold", 40), shadow=0, fill=(200, 206, 220)))
        c2 = cached("c2", lambda: gradient_text("CLAUDE AI", font("Anton", 190), top=(255, 190, 150), bot=(217, 119, 87)))
        fr.alpha_composite(c1, ((W - c1.size[0]) // 2, 1110))
        composite_el(fr, c2, 1.0, 0.7 + 0.3 * kc, ((W - c2.size[0]) // 2, 1140))
    kf = ease_out((u - 2.2) / 0.4)
    if kf > 0:
        f = cached("f", lambda: pill("Follow untuk tips edit dengan AI", (40, 44, 56), 34))
        composite_el(fr, f, kf, 1.0, ((W - f.size[0]) // 2, 1480))
    return fr

# ---------------------------------------------------------------- audio
def build_audio(out):
    sr = 48000; n = int((TOTAL + 1) * sr)
    sfx = np.zeros(n, np.float32); rng = np.random.default_rng(3)
    def noise_sweep(L, f0, f1, q=0.25):
        x = rng.normal(0, 1, L); y = np.zeros(L); lp = bp = 0.0
        for i in range(L):
            f = f0 + (f1 - f0) * (i / L); c = min(0.99, 2 * math.sin(math.pi * f / sr))
            hp = x[i] - lp - q * bp; bp += c * hp; lp += c * bp; y[i] = bp
        return y / (np.abs(y).max() + 1e-9)
    def whoosh(L, up=True):
        N = int(L * sr); y = noise_sweep(N, 300 if up else 2600, 2600 if up else 300); return 0.9 * y * np.sin(np.pi * np.arange(N) / N) ** 1.5
    def hit():
        t = np.arange(int(0.5 * sr)) / sr; return 0.9 * np.sin(2 * np.pi * (55 + 90 * np.exp(-t * 22)) * t) * np.exp(-t * 7)
    def pop():
        t = np.arange(int(0.09 * sr)) / sr; f = 1100 * np.exp(-t * 18) + 500; return 0.55 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 45)
    def buzz():   # "wrong" buzzer for issues
        t = np.arange(int(0.22 * sr)) / sr; return 0.35 * np.sign(np.sin(2 * np.pi * 140 * t)) * np.exp(-t * 9)
    def ding():
        t = np.arange(int(0.6 * sr)) / sr; return 0.3 * (np.sin(2 * np.pi * 1568 * t) + 0.5 * np.sin(2 * np.pi * 3136 * t)) * np.exp(-t * 6)
    def add(s, t):
        i = int(t * sr)
        if 0 <= i < n - len(s): sfx[i:i + len(s)] += s
    add(hit(), 0.02); add(0.8 * pop(), 0.15); add(0.8 * pop(), 0.3)
    for t0, _ in ISSUES: add(buzz(), 3.0 + t0)
    add(whoosh(0.9), 11.6); add(hit(), 12.2)
    for t0, _ in FEATS: add(ding(), 13.0 + t0)
    add(whoosh(0.4), 28.05); add(hit(), TOTAL - 5.2 + 0.02)
    for k in (0.3, 0.5, 0.7, 0.9): add(ding() * 0.8, TOTAL - 5.2 + k)
    add(hit() * 0.8, TOTAL - 5.2 + 1.45)
    with wave.open(f"{P}/work/comp_sfx.wav", "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((np.clip(sfx, -1, 1) * 32767).astype(np.int16).tobytes())
    MUS = f"{ROOT}/music/inspiration.mp3"
    sp = seg["a"]
    fc = (
        # raw 'before' audio, lightly normalised so it is audible (still un-cleaned on purpose)
        f"[0:a]atrim=start={BEFORE_SRC}:end={BEFORE_SRC + 9.0},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2,aresample=48000,aformat=channel_layouts=stereo,adelay=3000|3000,apad=whole_dur={TOTAL}[bef];"
        f"[1:a]atrim=start=0:end=15.2,asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,adelay=13000|13000,apad=whole_dur={TOTAL}[aft];"
        f"[1:a]atrim=start={SPLIT_T0}:end={SPLIT_T0 + SPLIT_LEN},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,afade=t=in:d=0.05,adelay={int(28200)}|{int(28200)},apad=whole_dur={TOTAL}[spl];"
        f"[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start=20:end={20 + TOTAL},asetpts=PTS-STARTPTS,"
        f"volume='if(lt(t,3),0.30,if(lt(t,12),0.0,if(lt(t,13),0.30,if(lt(t,{TOTAL - 5.2}),0.0,0.32))))':eval=frame,afade=t=out:st={TOTAL - 1.2}:d=1.2[mus];"
        f"[3:a]aformat=channel_layouts=stereo,volume=0.6[fx];"
        f"[bef][aft][spl][mus][fx]amix=inputs=5:duration=first:normalize=0,atrim=end={TOTAL},alimiter=limit=0.89[a]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", RAW, "-i", FIN, "-i", MUS, "-i", f"{P}/work/comp_sfx.wav",
                    "-filter_complex", fc, "-map", "[a]", "-ar", "48000", "-c:a", "pcm_s16le", out], check=True)

if __name__ == "__main__":
    aud = f"{P}/work/comp_audio.wav"; build_audio(aud)
    out = f"{P}/work/compare.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                            "-i", aud, "-map", "0:v", "-map", "1:a", "-af", "loudnorm=I=-14:TP=-1.2:LRA=9",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", out], stdin=subprocess.PIPE)
    nf = int(round(TOTAL * 30))
    stills = [float(x) for x in os.environ.get("STILLS", "").split()] if os.environ.get("STILLS") else []
    for i in range(nf):
        t = i / 30
        fr = frame_at(t)
        enc.stdin.write(fr.convert("RGB").tobytes())
        for s in stills:
            if abs(t - s) < 1 / 60: fr.convert("RGB").resize((360, 640)).save(f"{P}/work/cmp_{s:.1f}.jpg")
    enc.stdin.close(); enc.wait()
    print("done", out, TOTAL)
