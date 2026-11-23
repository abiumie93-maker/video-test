#!/usr/bin/env python3
"""Generic multi-clip cutter (Style D series).
usage: cutD.py CONFIG.json [render]
config: {"src": dir, "work": dir, "ranges": [[clip, a, b], ...], "av_shift": {clip: s}, "thr": -33}
- trims micro-pauses inside ranges, drops fragments without speech
- per-clip A/V offset fix (video taken at a + av_shift)
- writes work/edit.json and work/speaker.mov (1080x1920, 30 fps, sample-exact mono 48k audio)"""
import sys, os, json, subprocess, wave
import numpy as np
C = json.load(open(sys.argv[1])); SRC, WORK = C["src"], C["work"]; FPS = 30
os.makedirs(WORK, exist_ok=True)
_aud = {}
def aud(c):
    if c not in _aud:
        w = wave.open(f"{SRC}/{c}.wav"); sr = w.getframerate()
        _aud[c] = (np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, sr)
    return _aud[c]
def db_series(c, a, b, hop_s=0.01):
    x, sr = aud(c); hop = int(sr * hop_s); seg = x[int(a * sr):int(b * sr)]
    return np.array([20 * np.log10(np.sqrt((seg[i:i + hop] ** 2).mean()) + 1e-9) for i in range(0, max(0, len(seg) - hop), hop)])
def pauses(c, a, b, thr, minlen=0.25):
    d = db_series(c, a, b); out = []; run = 0
    for k, v in enumerate(list(d) + [0]):
        if v < thr: run += 1
        else:
            if run * 0.01 >= minlen: out.append((a + (k - run) * 0.01 + 0.07, a + k * 0.01 - 0.07))
            run = 0
    return out
segs = []
for c, a, b in C["ranges"]:
    thr = C.get("thr", -33); cur = a
    for pa, pb in pauses(c, a, b, thr):
        if pa - cur > 0.1: segs.append([c, cur, pa])
        cur = pb
    if b - cur > 0.1: segs.append([c, cur, b])
segs = [s for s in segs if db_series(s[0], s[1], s[2], 0.02).max(initial=-99) > -26]   # keep only fragments with real speech
t = 0.0; out = []
for c, a, b in segs:
    n = max(1, round((b - a) * FPS)); b = a + n / FPS
    out.append({"clip": c, "a": round(a, 4), "b": round(b, 4), "t": round(t, 4), "n": n}); t += n / FPS
json.dump({"segs": out, "fps": FPS, "av_shift": C.get("av_shift", {})}, open(f"{WORK}/edit.json", "w"), indent=1)
print(len(out), "segments, duration", round(t, 2))
if len(sys.argv) > 2:
    os.makedirs(f"{WORK}/segs", exist_ok=True)
    import concurrent.futures as cf
    def job(i):
        sg = out[i]; d = sg["b"] - sg["a"]; sh = C.get("av_shift", {}).get(sg["clip"], 0.0)
        fn = f"{WORK}/segs/{sg['clip']}_{sg['a']:.4f}_{sg['n']}_{sh:+.3f}.mov"
        if os.path.exists(fn) and os.path.getsize(fn) > 1000: return fn
        src = f"{SRC}/{sg['clip']}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y",
                        "-ss", f"{max(0, sg['a'] + sh):.4f}", "-t", f"{d + 0.1:.4f}", "-i", src,
                        "-ss", f"{sg['a']:.4f}", "-t", f"{d + 0.1:.4f}", "-i", src, "-map", "0:v", "-map", "1:a",
                        "-vf", f"scale=1080:1920:flags=lanczos,setsar=1,fps={FPS}:start_time=0",
                        "-af", "aresample=48000", "-ac", "1",
                        "-frames:v", str(sg["n"]), "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-pix_fmt", "yuv420p",
                        "-c:a", "pcm_s16le", fn], check=True)
        return fn
    with cf.ThreadPoolExecutor(3) as ex: fns = list(ex.map(job, range(len(out))))
    with open(f"{WORK}/segs/list.txt", "w") as f:
        for fn in fns: f.write(f"file '{fn}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{WORK}/segs/list.txt", "-map", "0:v", "-c", "copy", f"{WORK}/video_only.mov"], check=True)
    # sample-exact audio (no cumulative drift), tiny fades at every cut
    spf = 48000 // FPS; chunks = []
    for sg, fn in zip(out, fns):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", fn, "-map", "0:a", "-f", "s16le", "-ac", "1", "-ar", "48000", "-"], capture_output=True).stdout
        a = np.frombuffer(raw, np.int16).astype(np.float32); need = sg["n"] * spf
        a = a[:need] if len(a) >= need else np.concatenate([a, np.zeros(need - len(a), np.float32)])
        f = min(480, len(a) // 4)
        if f > 0: a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        chunks.append(a.astype(np.int16))
    with wave.open(f"{WORK}/speaker_audio.wav", "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000); wf.writeframes(np.concatenate(chunks).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{WORK}/video_only.mov", "-i", f"{WORK}/speaker_audio.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "pcm_s16le", f"{WORK}/speaker.mov"], check=True)
    print("speaker.mov done")
