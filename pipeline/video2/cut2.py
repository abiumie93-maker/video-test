#!/usr/bin/env python3
"""Jump-cut + content edit + speed-up + colour grade.
Usage: cut.py SCRATCH [render]
Writes work/segs.json (source a..b -> edited t, all frame-exact) and work/graded.mov
"""
import json, subprocess, sys, wave, os
import numpy as np

S = sys.argv[1]
FPS = 30
TARGET = 116.0          # spoken part target (s); end card added after
SP_MIN, SP_MAX = 1.0, 1.2
DUR = 232.05

# --- content edits: stutters / repeats / filler (source seconds, word boundaries)
EDITS = [
    (0.0, 6.60),      # take pertama hook (diulang)
    (15.59, 17.12),   # "Gaut, kolesterol," (ulang)
    (30.53, 32.71),   # "Setiap hari saya jumpa pesakit dan" (ulang)
    (58.11, 70.51),   # "Yang mana saya rasa ... yang mana" (berbelit)
    (42.40, 52.61),   # senarai penyakit kali ke-2 (ada dalam kad)
    (73.21, 77.77),   # "Itu yang saya cuba buat ... nak capai"
    (88.71, 92.89),   # "Disebabkan itulah, saya rasa aku" (tersekat)
    (98.81, 105.53),  # "Apatah lagi orang yang ... penyakit-penyakit ini,"
    (108.39, 111.31), # "sebenarnya dapat disangkal ataupun" (salah sebut)
    (118.61, 120.63), # "So contoh lah, macam darah tinggi"
    (137.27, 143.89), # "saya sangat-sangat / Saya sangat," (gagap)
    (149.33, 153.73), # "Dan saya gunakan platform ini..." (ulang)
    (153.73, 155.89), # "Supaya korang tak jadi macam saya dan"
    (157.85, 168.0),  # "Dan kita semua InsyaAllah ... okey?" (ulang)
    (178.78, 180.60),
    (186.35, 190.60), # "yang mana semua barang-barang ... MDA approve" (ulang) # "Yang mana saya sendiri barang-barang ini," (gagap)
    (205.66, 207.65), # "So semua ini MDA approve dan" (ulang)
    (214.01, 220.51), # "Kalau korang nak tahu ... rumah" (ulang)
]

# --- audio for snapping cut points to the quietest spot
wf = wave.open(f"{S}/src/audio.wav"); SR = wf.getframerate()
AUD = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768
HOP = int(SR * 0.005)
env = np.sqrt(np.convolve(AUD ** 2, np.ones(HOP * 4) / (HOP * 4), mode="same"))[::HOP]
def snap(t, win=0.09):
    i0, i1 = int((t - win) / 0.005), int((t + win) / 0.005)
    i0 = max(0, i0); i1 = min(len(env) - 1, i1)
    return (i0 + int(np.argmin(env[i0:i1 + 1]))) * 0.005

# --- silences (from silencedetect) -> removal ranges
sil = [tuple(map(float, l.split())) for l in open(f"{S}/work/sil.txt")]
rm = []
for a, b in sil:
    a2 = a + 0.06 if a > 0.5 else 0.0
    b2 = b - 0.08
    if b2 - a2 > 0.06: rm.append([a2, b2])
for a, b in EDITS:
    rm.append([snap(a), snap(b)])
rm.append([228.75, DUR])
rm.sort()
segs, cur = [], 0.0
for a, b in rm:
    if a > cur + 0.12: segs.append([cur, a])
    cur = max(cur, b)
if cur < DUR - 0.2: segs.append([cur, DUR])

kept = sum(b - a for a, b in segs)
SP = 1.1277862068965527  # dikunci supaya segmen cache boleh diguna semula
# frame-exact segment lengths (output frames), so overlays never drift
out, t, z = [], 0.0, 0
for i, (a, b) in enumerate(segs):
    nfr = max(1, round((b - a) / SP * FPS))
    b = a + nfr / FPS * SP
    out.append({"a": round(a, 4), "b": round(b, 4), "t": round(t, 4), "n": nfr,
                "zoom": 1.0})
    t += nfr / FPS
    if nfr > 18: z += 1      # only flip zoom on segments that are long enough to read
json.dump({"speed": SP, "segs": out}, open(f"{S}/work/segs.json", "w"), indent=1)
print(f"{len(out)} segments, kept {kept:.2f}s, speed {SP:.3f}x, edited {t:.2f}s")

G = ("selectivecolor=yellows='0 0 0.08 0':whites='0 0 0.03 0',eq=contrast=1.12:saturation=1.08:gamma=0.95,"
     "colorbalance=rs=-0.04:gs=-0.01:bs=0.055:rm=0.02:rh=0.03:bh=-0.03,"
     "curves=master='0/0.02 0.25/0.2 0.75/0.8 1/0.97',vignette=PI/4.5")
if len(sys.argv) > 2:
    import concurrent.futures as cf
    def job(i):
        sg = out[i]; d = sg["b"] - sg["a"]; z = sg["zoom"]; dur_out = sg["n"] / FPS
        vf = (f"scale=1080:1920:flags=lanczos,crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.35,"
              f"scale=1080:1920:flags=lanczos,setsar=1,{G},setpts=(PTS-STARTPTS)/{SP},fps={FPS}")
        af = (f"asetpts=PTS-STARTPTS,atempo={SP},afade=t=in:d=0.012,"
              f"afade=t=out:st={max(0, dur_out - 0.02):.4f}:d=0.02,apad,atrim=end={dur_out:.5f}")
        fn = f"{S}/work/segs/c_{sg['a']:.4f}_{sg['b']:.4f}_{sg['n']}.mov"
        if os.path.exists(fn) and os.path.getsize(fn) > 1000: return fn
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sg['a']:.4f}", "-i", f"{S}/src/raw.mp4", "-t", f"{d + 0.1:.4f}",
                        "-vf", vf, "-af", af, "-frames:v", str(sg["n"]),
                        "-c:v", "libx264", "-preset", "fast", "-crf", "11", "-pix_fmt", "yuv420p",
                        "-c:a", "pcm_s16le", "-ar", "48000", fn], check=True)
        return fn
    with cf.ThreadPoolExecutor(2) as ex:
        fns = list(ex.map(job, range(len(out))))
    with open(f"{S}/work/segs/list.txt", "w") as lst:
        for fn in fns: lst.write(f"file '{fn}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{S}/work/segs/list.txt",
                    "-c", "copy", f"{S}/work/graded.mov"], check=True)
