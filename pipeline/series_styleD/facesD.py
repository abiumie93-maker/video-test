"""per-segment face centre/height for a Style D work dir. usage: facesD.py WORKDIR"""
import sys, json, subprocess, numpy as np, os
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
ROOT = os.path.dirname(os.path.abspath(__file__))
WK = sys.argv[1]; E = json.load(open(f"{WK}/edit.json"))["segs"]
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=f"{ROOT}/models/face_landmarker.task"),
                                               running_mode=vision.RunningMode.VIDEO, num_faces=1))
res = []; k = 0
for sg in E:
    vals = []
    for f in (0.3, 0.7):
        t = sg["t"] + f * sg["n"] / 30
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", f"{WK}/speaker.mov", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) != 1080 * 1920 * 3: continue
        rgb = np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3)
        r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)), k * 100); k += 1
        if r.face_landmarks:
            L = r.face_landmarks[0]; xs = [p.x * 1080 for p in L]; ys = [p.y * 1920 for p in L]
            vals.append(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(ys) - min(ys)))
    res.append(list(np.mean(vals, 0)) if vals else None)
good = [r for r in res if r]
med = list(np.median(good, 0)) if good else [540, 700, 260]
res = [r if r else med for r in res]
json.dump(res, open(f"{WK}/faces.json", "w"))
print("faces:", len(res), "median", [round(x) for x in med])
