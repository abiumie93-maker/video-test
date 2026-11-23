import sys, subprocess, numpy as np
f = sys.argv[1]
v = subprocess.run(["ffmpeg","-v","error","-i",f,"-vf","fps=240,scale=64:64,format=gray","-f","rawvideo","-"],capture_output=True).stdout
fps = 240
V = np.frombuffer(v,np.uint8).reshape(-1,64*64).mean(1)
a = subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","48000","-f","s16le","-"],capture_output=True).stdout
A = np.abs(np.frombuffer(a,np.int16).astype(float))
vt = [i/fps for i in range(1,len(V)) if V[i]>100 and V[i-1]<=100]
on = A > 3000; idx = np.flatnonzero(on); at = [idx[0]/48000] + [idx[k]/48000 for k in range(1,len(idx)) if idx[k]-idx[k-1] > 4800] if len(idx) else []
d = []
for t in vt:
    k = np.argmin([abs(x-t) for x in at]) if at else None
    if k is not None and abs(at[k]-t) < 0.5: d.append((t, (t-at[k])*1000))
arr=np.array([x[1] for x in d]); print(f"{f.split(chr(47))[-1]}: n={len(arr)} mean={arr.mean():+.1f}ms min={arr.min():+.0f} max={arr.max():+.0f}")
