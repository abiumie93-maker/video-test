"""SyncNet (Chung & Zisserman) A/V offset. usage: av_offset.py FILE t0 dur [vshift]
Prints offset in ms: NEGATIVE = audio is LATE vs lips, POSITIVE = audio is EARLY."""
import sys, os, subprocess, numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from SyncNetModel import S as SNet
import python_speech_features
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f, t0, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); VS = int(sys.argv[4]) if len(sys.argv) > 4 else 15
FR = 25; W, H = 540, 960
p = subprocess.Popen(["ffmpeg","-v","error","-ss",str(t0),"-i",f,"-t",str(dur),"-vf",f"scale={W}:{H},fps={FR}","-pix_fmt","rgb24","-f","rawvideo","-"],stdout=subprocess.PIPE)
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=f"{ROOT}/models/face_landmarker.task"), running_mode=vision.RunningMode.VIDEO, num_faces=1))
crops = []; boxes = []; k = 0
from PIL import Image
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr)), int(k * 1000 / FR)); k += 1
    if r.face_landmarks:
        L = r.face_landmarks[0]; xs = [q.x * W for q in L]; ys = [q.y * H for q in L]
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    else:
        boxes.append(boxes[-1] if boxes else (W*.3, H*.3, W*.7, H*.6))
    crops.append(fr)
# smooth boxes, crop like syncnet_python (bs = half box size, cs = 0.4)
B = np.array(boxes); Bs = np.stack([np.convolve(np.pad(B[:, i], 6, mode="edge"), np.ones(13) / 13, mode="valid") for i in range(4)], 1)
ims = []
for fr, (x0, y0, x1, y1) in zip(crops, Bs):
    bs = max(x1 - x0, y1 - y0) / 2; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; cs = 0.4
    pad = int(bs * (1 + 2 * cs)) + 2
    P = np.pad(fr, ((pad, pad), (pad, pad), (0, 0)), constant_values=110)
    my, mx = cy + pad, cx + pad
    c = P[int(my - bs):int(my + bs * (1 + 2 * cs)), int(mx - bs * (1 + cs)):int(mx + bs * (1 + cs))]
    ims.append(np.array(Image.fromarray(c).resize((224, 224), Image.BILINEAR))[:, :, ::-1])   # BGR like cv2
a = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-i",f,"-t",str(dur),"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
audio = np.frombuffer(a, np.int16)
mfcc = np.stack([np.array(i) for i in zip(*python_speech_features.mfcc(audio, 16000))])
net = SNet(num_layers_in_fc_layers=1024); st = torch.load(f"{ROOT}/models/syncnet_v2.model", map_location="cpu")
net.load_state_dict(st if not hasattr(st, "state_dict") else st.state_dict(), strict=True) if isinstance(st, dict) else None
net.eval()
im = np.stack(ims, 3)[None].transpose(0, 3, 4, 1, 2).astype(np.float32)   # 1 x C x T x H x W
imtv = torch.from_numpy(im); cct = torch.from_numpy(mfcc[None, None].astype(np.float32))
n = min(len(ims), len(audio) // 640) - 5
imf, ccf = [], []
with torch.no_grad():
    for i in range(0, n, 20):
        idx = range(i, min(n, i + 20))
        imf.append(net.forward_lip(torch.cat([imtv[:, :, v:v + 5] for v in idx], 0)))
        ccf.append(net.forward_aud(torch.cat([cct[:, :, :, v * 4:v * 4 + 20] for v in idx], 0)))
imf = torch.cat(imf); ccf = torch.cat(ccf)
ccp = torch.nn.functional.pad(ccf, (0, 0, VS, VS))
d = torch.stack([torch.nn.functional.pairwise_distance(imf[[i]].repeat(2 * VS + 1, 1), ccp[i:i + 2 * VS + 1]) for i in range(len(imf))], 1)
md = d.mean(1); mv, mi = torch.min(md, 0)
off = VS - mi.item(); conf = (torch.median(md) - mv).item()
print(f"{os.path.basename(f)} t={t0:.0f}+{dur:.0f}: offset {off:+d} frames = {off*40:+d} ms (conf {conf:.2f})  [neg = audio late]")
