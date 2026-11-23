"""Style E project: assemble speaker track from two clips (ranges), trim micro-pauses, fix A/V offset.
usage: cutE.py P [render]  -> P/work/edit.json, P/work/speaker.mov (1080x1920 30fps + audio)"""
import sys, os, json, subprocess, wave
import numpy as np
P = sys.argv[1]; FPS = 30
CLIP = {"A": "VID_20261123_201800", "B": "VID_20261123_201836"}
AV_SHIFT = -0.12          # SyncNet: audio ~120 ms late -> take video 120 ms earlier
RANGES = [  # (clip, start, end)  -- end = start of the next word we drop
    ("A", 3.00, 5.95),            # Guys, korang ingat tak, saya selalu promosikan Hinarin kan?
    ("A", 7.88, 11.95),           # ini adalah Travel Pack, 30ml. Pada saya memang tak cukup
    ("A", 12.41, 18.56),          # dan saya try ... dan my favourite adalah
    ("A", 19.07, 21.85),          # coconut oil and rice milk
    ("A", 23.61, 27.53),          # sebabkan itulah, tadaaa, saya ambil botol besar terus
    ("A", 34.71, 36.75),          # kita test bau dia, sama tak?
    ("A", 38.85, 39.71),          # memang sedap
    ("B", 0.05, 11.23),           # Lepas ni ... botol kecil ni kita buat untuk travel
    ("A", 46.63, 48.97),          # peach and mango ni pun sedap
    ("A", 51.61, 55.95),          # so yang ni bau dia manis-manis, bau-bau manis buah peach dengan mango
    ("A", 59.91, 63.57),          # tapi my nombor satu tetap coconut oil, kedua still peach and mango
    ("B", 16.63, 21.13),          # So korang guys, ... produk Malaysia, local made
    ("B", 23.62, 25.81),          # dia gunakan 95% bahan natural
    ("B", 25.81, 28.05),          # korang dapatkan terus dekat beg kuning
]
def load(c):
    w = wave.open(f"{P}/src/{CLIP[c]}.wav"); sr = w.getframerate()
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, sr
AUD = {c: load(c) for c in CLIP}
def pauses(c, a, b, thr=-33, minlen=0.25):
    x, sr = AUD[c]; hop = int(sr * 0.01); out = []; run = 0
    seg = x[int(a * sr):int(b * sr)]
    db = [20 * np.log10(np.sqrt((seg[i:i + hop] ** 2).mean()) + 1e-9) for i in range(0, len(seg) - hop, hop)]
    for k, v in enumerate(db + [0]):
        if v < thr: run += 1
        else:
            if run * 0.01 >= minlen: out.append((a + (k - run) * 0.01 + 0.08, a + k * 0.01 - 0.08))
            run = 0
    return out
# split ranges at micro-pauses
segs = []
for c, a, b in RANGES:
    cur = a
    for pa, pb in pauses(c, a, b):
        if pa - cur > 0.1: segs.append([c, cur, pa])
        cur = pb
    if b - cur > 0.1: segs.append([c, cur, b])
t = 0.0; out = []
for c, a, b in segs:
    n = max(1, round((b - a) * FPS)); b = a + n / FPS
    out.append({"clip": c, "a": round(a, 4), "b": round(b, 4), "t": round(t, 4), "n": n}); t += n / FPS
json.dump({"segs": out, "fps": FPS, "av_shift": AV_SHIFT}, open(f"{P}/work/edit.json", "w"), indent=1)
print(len(out), "segments, duration", round(t, 2))
if len(sys.argv) > 2:
    os.makedirs(f"{P}/work/segs", exist_ok=True)
    import concurrent.futures as cf
    def job(i):
        sg = out[i]; d = sg["b"] - sg["a"]; dur = sg["n"] / FPS
        src = f"{P}/src/{CLIP[sg['clip']]}.mp4"
        fn = f"{P}/work/segs/{sg['clip']}_{sg['a']:.4f}_{sg['n']}.mov"
        if os.path.exists(fn) and os.path.getsize(fn) > 1000: return fn
        subprocess.run(["ffmpeg", "-v", "error", "-y",
                        "-ss", f"{sg['a'] + AV_SHIFT:.4f}", "-t", f"{d + 0.1:.4f}", "-i", src,
                        "-ss", f"{sg['a']:.4f}", "-t", f"{d + 0.1:.4f}", "-i", src, "-map", "0:v", "-map", "1:a",
                        "-vf", f"scale=1080:1920:flags=lanczos,setsar=1,fps={FPS}:start_time=0",
                        "-af", f"asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0, dur - 0.02):.4f}:d=0.02,apad,atrim=end={dur:.5f}",
                        "-frames:v", str(sg["n"]), "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-pix_fmt", "yuv420p",
                        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1", fn], check=True)
        return fn
    with cf.ThreadPoolExecutor(3) as ex: fns = list(ex.map(job, range(len(out))))
    with open(f"{P}/work/segs/list.txt", "w") as f:
        for fn in fns: f.write(f"file '{fn}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{P}/work/segs/list.txt", "-c", "copy", f"{P}/work/speaker.mov"], check=True)
    # --- sample-exact audio rebuild: each segment's audio padded/trimmed to n * (48000/FPS) samples (no cumulative drift)
    spf = 48000 // FPS; chunks = []
    for sg, fn in zip(out, fns):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", fn, "-map", "0:a", "-f", "s16le", "-ac", "1", "-ar", "48000", "-"], capture_output=True).stdout
        a = np.frombuffer(raw, np.int16); need = sg["n"] * spf
        a = a[:need] if len(a) >= need else np.concatenate([a, np.zeros(need - len(a), np.int16)])
        chunks.append(a)
    with wave.open(f"{P}/work/speaker_audio.wav", "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000); wf.writeframes(np.concatenate(chunks).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{P}/work/speaker.mov", "-i", f"{P}/work/speaker_audio.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "pcm_s16le", f"{P}/work/speaker_fixed.mov"], check=True)
    os.replace(f"{P}/work/speaker_fixed.mov", f"{P}/work/speaker.mov")
