"""Full-length side-by-side: left = plain cut (no grade/zoom/subs/effects), right = final edit. Same audio."""
import sys, os, subprocess
P = sys.argv[1]; ROOT = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["render2", P]; _g = {"__file__": f"{ROOT}/render2.py", "__name__": "r2"}
exec(open(f"{ROOT}/render2.py").read().split("if __name__")[0], _g)
globals().update({k: v for k, v in _g.items() if not k.startswith("__")})
from PIL import Image, ImageDraw, ImageFilter
PW, PH, PY = 510, 907, 520; LX, RX = 20, 550
# background
bg = Image.new("RGBA", (W, H), (10, 12, 20, 255))
g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse((40, 420, 1040, 1520), fill=120)
gl = Image.new("RGBA", (W, H), (30, 70, 200, 0)); gl.putalpha(g.filter(ImageFilter.GaussianBlur(190))); bg = Image.alpha_composite(bg, gl)
for x in (LX, RX):   # panel shadows
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((x, PY + 14, x + PW, PY + PH + 14), 30, fill=170)
    s2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); s2.putalpha(sh.filter(ImageFilter.GaussianBlur(22))); bg.alpha_composite(s2)
bg.convert("RGB").save(f"{P}/work/sbs_bg.png")
# foreground (titles + labels)
fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
t1 = shadow_text("AYAT SAMA · SUARA SAMA", font("SemiBold", 38), tracking=6, shadow=0, fill=(185, 193, 210))
t2 = gradient_text("SEBELUM vs SELEPAS", font("Anton", 118))
fg.alpha_composite(t1, ((W - t1.size[0]) // 2, 150)); fg.alpha_composite(t2, ((W - t2.size[0]) // 2, 190))
def pill(txt, col, size=36):
    f = font("Bold", size); tw = int(f.getlength(txt)); h = size + 30
    im = Image.new("RGBA", (tw + 80, h + 20), (0, 0, 0, 0))
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((8, 8, im.size[0] - 8, h + 8), h // 2, fill=255)
    gg = Image.new("RGBA", im.size, col + (0,)); gg.putalpha(m.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .55))); im.alpha_composite(gg)
    ImageDraw.Draw(im).rounded_rectangle((10, 10, im.size[0] - 10, h + 6), (h - 4) // 2, fill=col + (255,))
    ImageDraw.Draw(im).text((40, 10 + (h - 4 - size) // 2 - 4), txt, font=f, fill="white"); return im
for txt, col, x in (("SEBELUM", (229, 72, 77), LX), ("SELEPAS", BLUE_BOT, RX)):
    p = pill(txt, col); fg.alpha_composite(p, (x + (PW - p.size[0]) // 2, PY - p.size[1] - 8))
s1 = shadow_text("Mentah: tiada subtitle, zoom, B-roll atau grading", font("Medium", 27), shadow=0, fill=(150, 158, 175))
fg.alpha_composite(s1, ((W - s1.size[0]) // 2, PY + PH + 30))
c1 = shadow_text("Diedit sepenuhnya oleh", font("SemiBold", 38), shadow=0, fill=(200, 206, 220))
c2 = gradient_text("CLAUDE AI", font("Anton", 150), top=(255, 190, 150), bot=(217, 119, 87))
fg.alpha_composite(c1, ((W - c1.size[0]) // 2, 1500)); fg.alpha_composite(c2, ((W - c2.size[0]) // 2, 1525))
fg.save(f"{P}/work/sbs_fg.png")
m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 1, PH - 1), 30, fill=255); m.save(f"{P}/work/sbs_mask.png")
fin_dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{P}/work/final.mp4"], capture_output=True, text=True).stdout)
pad = fin_dur - DUR + 0.1
fc = (f"[1:v]scale={PW}:{PH}:flags=lanczos,tpad=stop_mode=clone:stop_duration={pad:.2f},format=rgba[lv];"
      f"[2:v]scale={PW}:{PH}:flags=lanczos,format=rgba[rv];"
      f"[4:v]format=gray,split=2[m1][m2];[lv][m1]alphamerge[l];[rv][m2]alphamerge[r];"
      f"[0:v][l]overlay={LX}:{PY}:shortest=0[b1];[b1][r]overlay={RX}:{PY}:shortest=0[b2];[b2][3:v]overlay=0:0,format=yuv420p[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", f"{P}/work/sbs_bg.png",
                "-i", f"{P}/work/plain.mov", "-i", f"{P}/work/final.mp4", "-loop", "1", "-framerate", "30", "-i", f"{P}/work/sbs_fg.png",
                "-loop", "1", "-framerate", "30", "-i", f"{P}/work/sbs_mask.png",
                "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                "-profile:v", "high", "-r", "30", "-c:a", "copy", "-t", f"{fin_dur:.3f}", "-movflags", "+faststart",
                f"{P}/work/side_by_side.mp4"], check=True)
print("done", fin_dur)
