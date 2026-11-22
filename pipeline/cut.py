import json, subprocess, sys, os
S=sys.argv[1]
T=json.load(open(f"{S}/src/transcript.json"))
sil=[tuple(map(float,l.split())) for l in open(f"{S}/work/sil.txt")]
DUR=188.4
rm=[]
for a,b in sil:
    a2=a+0.08 if a>0.5 else 0.0
    b2=b-0.10
    if b2-a2>0.08: rm.append([a2,b2])
rm.append([163.30,166.30]); rm.append([186.95,DUR])
rm.sort()
segs=[]; cur=0.0
for a,b in rm:
    if a>cur+0.15: segs.append([cur,a])
    cur=max(cur,b)
if cur<DUR-0.2: segs.append([cur,DUR])
# hard cut at the removed region
out=[]; t=0
for i,(a,b) in enumerate(segs):
    out.append({"a":round(a,3),"b":round(b,3),"t":round(t,3),"zoom":(1.0 if i%2==0 else 1.10)})
    t+=b-a
json.dump(out,open(f"{S}/work/segs.json","w"),indent=1)
print(len(out),"segments, new duration",round(t,2))
G="selectivecolor=greens='0 0 0.15 0':yellows='0.05 -0.08 0.1 0':cyans='0.1 0 -0.1 0':blues='0.05 0 -0.05 0',eq=contrast=1.1:saturation=0.95:gamma=0.96,colorbalance=rs=-0.05:bs=0.07:rh=0.04:bh=-0.03,curves=master='0/0.03 0.25/0.2 0.75/0.8 1/0.97',vignette=PI/4.5"
if len(sys.argv)>2:
    lst=open(f"{S}/work/segs/list.txt","w")
    for i,sg in enumerate(out):
        d=sg["b"]-sg["a"]; z=sg["zoom"]
        vf=f"scale=1080:1920,crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.35,scale=1080:1920:flags=lanczos,setsar=1,{G},fps=30"
        af=f"afade=t=in:d=0.02,afade=t=out:st={max(0,d-0.03):.3f}:d=0.03,aresample=48000"
        fn=f"{S}/work/segs/s{i:03d}.mp4"
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{sg['a']:.3f}","-i",f"{S}/src/raw.mp4","-t",f"{d:.3f}","-vf",vf,"-af",af,
          "-c:v","libx264","-preset","veryfast","-crf","16","-pix_fmt","yuv420p","-c:a","pcm_s16le",fn.replace(".mp4",".mov")],check=True)
        lst.write(f"file '{fn.replace('.mp4','.mov')}'\n")
    lst.close()
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{S}/work/segs/list.txt","-c:v","copy","-c:a","pcm_s16le",f"{S}/work/graded.mov"],check=True)
