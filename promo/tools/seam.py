import sys, numpy as np, wave
from faster_whisper import WhisperModel
w=wave.open(sys.argv[1]); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
m=WhisperModel('small',device='cpu',compute_type='int8')
def tx(s,e):
    seg,_=m.transcribe(a[int(s*sr):int(e*sr)],language='ms',beam_size=5,vad_filter=False,condition_on_previous_text=False)
    return ' '.join(x.text.strip() for x in seg)
for t in map(float,sys.argv[2:]):
    print(f'{t:7.2f}  BEFORE: ...{tx(t-1.8,t)!r}   AFTER: {tx(t,t+1.8)!r}...',flush=True)
