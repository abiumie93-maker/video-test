"""Build the sound for a rendered edit: voice-over cut from the source audio, ducked CC0 music bed, SFX.
Usage: python3 tools/mix.py v1 [render.mp4 out.mp4]
Writes <proj>/mix.wav (-15 LUFS, true peak <= -1.5 dBTP); with a render, muxes it to out.mp4."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PEAK, DUR, ROOT

proj = os.path.join(ROOT, sys.argv[1])
plan = json.load(open(os.path.join(proj, "edit-plan.json")))
total = plan["total"]
A = os.path.join(ROOT, "assets")
inputs = ["-i", os.path.join(A, "main_audio.wav"), "-stream_loop", "-1", "-i", os.path.join(ROOT, plan["music_file"])]
fc, labels = [], []
for i, s in enumerate(plan["vo"]):
    d = s["dur"]; ms = int(s["out"] * 1000)
    fc.append(f"[0:a]atrim={s['src_in']}:{s['src_out']},asetpts=PTS-STARTPTS,afade=t=in:d=0.025,"
              f"afade=t=out:st={d - .035:.3f}:d=0.035,volume=1.0,adelay={ms}|{ms}[v{i}]")
    labels.append(f"[v{i}]")

# music: piecewise-linear level from keyframes
kf = plan["music"]
expr = "0"
for (t0, l0), (t1, l1) in reversed(list(zip(kf, kf[1:]))):
    seg = f"({l0}+({l1}-{l0})*(t-{t0})/{max(t1 - t0, 1e-3)})"
    expr = f"if(between(t,{t0},{t1}),{seg},{expr})"
fc.append(f"[1:a]atrim=0:{total},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo:sample_rates=48000,"
          f"volume='{expr}':eval=frame[mus]")
labels.append("[mus]")

n = 2
for j, (name, hit, gain) in enumerate(plan["sfx"]):
    start = max(hit + 1 / 30 - PEAK[name], 0)
    inputs += ["-i", os.path.join(A, "sfx", f"{name}.mp3")]
    ms = int(start * 1000)
    fc.append(f"[{n}:a]atrim=0:{DUR[name]},afade=t=out:st={DUR[name] - .08:.3f}:d=0.08,"
              f"aformat=channel_layouts=stereo:sample_rates=48000,volume={gain},adelay={ms}|{ms}[x{j}]")
    labels.append(f"[x{j}]")
    n += 1
fc.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:dropout_transition=0,atrim=0:{total}[pre]")

raw = os.path.join(proj, "mix_raw.wav")
script = os.path.join(proj, "mix_filter.txt")
open(script, "w").write(";\n".join(fc))
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex_script", script, "-map", "[pre]",
                "-ar", "48000", "-c:a", "pcm_s16le", raw], check=True)
# two-pass loudness
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json",
                    "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r, re.S).group(0))
out = os.path.join(proj, "mix.wav")
af = (f"loudnorm=I=-15:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", "48000", out], check=True)
print("mix", out, "input", m["input_i"], "LUFS")
if len(sys.argv) > 3:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", sys.argv[2], "-i", out, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", sys.argv[3]], check=True)
    print("muxed", sys.argv[3])
