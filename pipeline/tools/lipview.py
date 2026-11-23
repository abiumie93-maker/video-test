import sys, subprocess, numpy as np, wave
from PIL import Image, ImageDraw, ImageFont
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
model, f, wav, t0, t1, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
FR = 30
dur = t1 - t0
raw = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-i",f,"-t",str(dur),"-vf",f"scale=1080:1920,fps={FR}","-pix_fmt","rgb24","-f","rawvideo","-"],capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 1920, 1080, 3)
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.VIDEO, num_faces=1))
crops = []; opens = []
for k, im in enumerate(fr):
    r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(im)), int(k * 1000 / FR))
    if r.face_landmarks:
        L = r.face_landmarks[0]; cx = int(L[13].x * 1080); cy = int((L[13].y + L[14].y) / 2 * 1920)
        opens.append(abs(L[14].y - L[13].y) / abs(L[152].y - L[10].y))
    else: cx, cy = 540, 760; opens.append(0)
    crops.append(Image.fromarray(im).crop((cx - 70, cy - 45, cx + 70, cy + 45)))
w = wave.open(wav); sr = w.getframerate(); w.setpos(int(t0 * sr)); a = np.frombuffer(w.readframes(int(dur * sr)), np.int16).astype(float)
n = len(crops); CW = 140
img = Image.new("RGB", (n * CW, 90 + 140 + 80), "white"); g = ImageDraw.Draw(img)
env = np.array([np.abs(a[int(i * sr / FR):int((i + 1) * sr / FR)]).mean() for i in range(n)])
for i in range(n):
    img.paste(crops[i], (i * CW, 0))
    h = int(130 * env[i] / (env.max() + 1)); g.rectangle((i * CW + 20, 230 - h, i * CW + 60, 230), fill=(220, 40, 40))
    h2 = int(130 * opens[i] / (max(opens) + 1e-6)); g.rectangle((i * CW + 75, 230 - h2, i * CW + 115, 230), fill=(40, 40, 220))
    g.text((i * CW + 30, 240), f"{t0 + i / FR:.2f}", fill="black")
img.save(out)
