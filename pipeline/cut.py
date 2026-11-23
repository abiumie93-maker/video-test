#!/usr/bin/env python3
"""Jump-cut + content edit + speed-up + colour grade.
Usage: cut.py SCRATCH [render]
Writes work/segs.json (source a..b -> edited t, all frame-exact) and work/graded.mov
"""
import json, subprocess, sys, wave
import numpy as np

S = sys.argv[1]
FPS = 30
TARGET = 117.3          # spoken part target (s); end card added after
SP_MIN, SP_MAX = 1.0, 1.22
DUR = 188.4

# --- content edits: stutters / repeats / filler (source seconds, word boundaries)
EDITS = [
    (0.0, 1.75),      # "dan" di awal
    (14.17, 15.77),   # "untuk buat masa ni"
    (90.17, 92.13),   # "dan ke arah yang lebih baik"
    (17.09, 17.97),   # "yang memang darah tinggi tu"
    (34.65, 35.97),   # "tukar lifestyle tu" (ulang)
    (45.87, 47.23),   # "itulah cara dia" (ulang)
    (48.77, 50.19),   # "saya sendiri," (gagap)
    (64.27, 65.77),   # "dalam masa yang sama,"
    (71.47, 77.87),   # "ataupun keadaan saya, maksudnya kita kita ... darah tu" (berbelit)
    (98.25, 102.27),  # "diorang sendiri pun ... sama je,"
    (108.99, 111.23), # "nasihat saya untuk orang-orang yang muda" (ulang)
    (115.31, 117.11), # "sangat-sangat mudah untuk sembuh"
    (129.25, 130.45), # "korang maintain" (gagap)
    (138.99, 141.09), # "so bila metabolic syndrome ni maksudnya"
    (146.63, 149.21), # "dia akan jadi balik" (tersekat)
    (154.41, 155.41), # "korang dah normal" (ulang)
    (163.30, 166.29), # "dan once korang dah ubah dia," (salah mula)
    (173.41, 177.23), # "so it's a lifestyle ... nak sembuh" (ulang)
    (179.23, 180.45), # "korang bawa juga," (gagap)
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
rm.append([186.95, DUR])
rm.sort()
segs, cur = [], 0.0
for a, b in rm:
    if a > cur + 0.12: segs.append([cur, a])
    cur = max(cur, b)
if cur < DUR - 0.2: segs.append([cur, DUR])

kept = sum(b - a for a, b in segs)
SP = min(SP_MAX, max(SP_MIN, kept / TARGET))
# frame-exact segment lengths (output frames), so overlays never drift
out, t, z = [], 0.0, 0
for i, (a, b) in enumerate(segs):
    nfr = max(1, round((b - a) / SP * FPS))
    b = a + nfr / FPS * SP
    out.append({"a": round(a, 4), "b": round(b, 4), "t": round(t, 4), "n": nfr,
                "zoom": (1.0 if z % 2 == 0 else 1.10)})
    t += nfr / FPS
    if nfr > 18: z += 1      # only flip zoom on segments that are long enough to read
json.dump({"speed": SP, "segs": out}, open(f"{S}/work/segs.json", "w"), indent=1)
print(f"{len(out)} segments, kept {kept:.2f}s, speed {SP:.3f}x, edited {t:.2f}s")

G = ("selectivecolor=greens='0 0 0.15 0':yellows='0.05 -0.08 0.1 0':cyans='0.1 0 -0.1 0':blues='0.05 0 -0.05 0',"
     "eq=contrast=1.1:saturation=0.95:gamma=0.96,colorbalance=rs=-0.05:bs=0.07:rh=0.04:bh=-0.03,"
     "curves=master='0/0.03 0.25/0.2 0.75/0.8 1/0.97',vignette=PI/4.5")
if len(sys.argv) > 2:
    import concurrent.futures as cf
    def job(i):
        sg = out[i]; d = sg["b"] - sg["a"]; z = sg["zoom"]; dur_out = sg["n"] / FPS
        vf = (f"scale=1080:1920:flags=lanczos,crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.35,"
              f"scale=1080:1920:flags=lanczos,setsar=1,{G},setpts=(PTS-STARTPTS)/{SP},fps={FPS}")
        af = (f"asetpts=PTS-STARTPTS,atempo={SP},afade=t=in:d=0.012,"
              f"afade=t=out:st={max(0, dur_out - 0.02):.4f}:d=0.02,apad,atrim=end={dur_out:.5f}")
        fn = f"{S}/work/segs/s{i:03d}.mov"
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
