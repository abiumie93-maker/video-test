import numpy as np, wave, sys
w=wave.open(sys.argv[1]); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
hop=sr//100; n=len(a)//hop; db=20*np.log10(np.sqrt((a[:n*hop].reshape(n,hop)**2).mean(1)+1e-12))
q=db<-25.5; gaps=[]; i=0
while i<n:
    if q[i]:
        j=i
        while j<n and q[j]: j+=1
        if j-i>=5: gaps.append((i/100,j/100))
        i=j
    else: i+=1
for t in map(float,sys.argv[2:]):
    c=sorted(gaps,key=lambda g:min(abs(g[0]-t),abs(g[1]-t)))[:3]
    print(t, ' | '.join(f'{g[0]:.2f}-{g[1]:.2f}' for g in c))
