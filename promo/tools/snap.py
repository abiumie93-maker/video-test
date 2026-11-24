"""Snap cut points to the quietest 10 ms frame near a target (source audio)."""
import numpy as np, wave, sys
w = wave.open(sys.argv[1]); sr = w.getframerate(); ch = w.getnchannels()
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
a = a.reshape(-1, ch).mean(1)
hop = sr // 100; n = len(a) // hop
db = 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12))
for t in map(float, sys.argv[2:]):
    i0, i1 = int((t - .15) * 100), int((t + .15) * 100)
    k = i0 + int(np.argmin(db[i0:i1]))
    print(f"{t:7.2f} -> {k/100:7.2f}  ({db[k]:.1f} dB, at target {db[int(t*100)]:.1f})")
