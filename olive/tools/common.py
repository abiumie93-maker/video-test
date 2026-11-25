"""Shared helpers for the Alooma promo edits (Hyperframes project + ffmpeg audio mix).

Picture: Hyperframes renders every clip muted. Sound: tools/mix.py builds the voice-over (cut from the
source audio), a CC0 music bed ducked under the voice, and the SFX, then muxes it onto the render.
All times here are OUTPUT seconds unless a name says src.
"""
import json, os, re

W, H = 1080, 1920
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = json.load(open(os.path.join(ROOT, "transcript.json")))

# Bundled SFX: where the loud part peaks, how much of the file to use, default gain.
PEAK = {"whoosh": .162, "whoosh-short": .162, "pop": .12, "impact-bass-1": .073, "riser": 3.472,
        "click-soft": .05, "notification": .229, "error": .745}
DUR = {"whoosh": .574, "whoosh-short": .574, "pop": .72, "impact-bass-1": 2.1, "riser": 3.6,
       "click-soft": .365, "notification": 1.5, "error": 1.0}
VOL = {"whoosh": .55, "whoosh-short": .45, "pop": .6, "impact-bass-1": .5, "riser": .28,
       "click-soft": .6, "notification": .4, "error": .55}

FONTS_CSS = """
  @font-face { font-family:'Caveat'; font-weight:700; src:url('assets/fonts/caveat-700.woff2') format('woff2'); }
  @font-face { font-family:'Permanent Marker'; src:url('assets/fonts/permanent-marker.woff2') format('woff2'); }
  @font-face { font-family:'Montserrat'; font-weight:100 900; src:url('assets/fonts/montserrat.woff2') format('woff2'); }
  @font-face { font-family:'Archivo Black'; src:url('assets/fonts/archivo-black.woff2') format('woff2'); }
  @font-face { font-family:'Plus Jakarta Sans'; font-weight:200 800; src:url('assets/fonts/plus-jakarta-sans.woff2') format('woff2'); }
"""


class Edit:
    def __init__(self):
        self.vo = []        # dict(name, src_in, src_out, out, dur)
        self.t = 0.0
        self.shots = []     # picture clips
        self.sfx = []       # (name, visual_hit_time, gain)
        self.js = []        # gsap lines on the main timeline
        self.html = []      # overlay markup
        self.css = []
        self.zoom = []      # (t, kind, scale, x)
        self.lift = []      # windows where a lower card is on screen
        self.music = []     # (t, level) music level keyframes
        self.n = 0
        self.cam_html = []  # markup that rides with the camera

    # ---- voice-over / timeline
    def say(self, name, a, b, gap=0.0, clip="073913"):
        self.t += gap
        seg = dict(name=name, src_in=a, src_out=b, out=round(self.t, 3), dur=round(b - a, 3), clip=clip,
                   audio=f"assets/a_{clip}.wav", video=f"assets/footage/{clip}.mp4")
        self.vo.append(seg)
        self.t = round(self.t + b - a, 3)
        return seg

    def hold(self, d):
        """Music-only stretch (no voice)."""
        a = self.t
        self.t = round(self.t + d, 3)
        return a

    def o(self, src, seg=None):
        """Source second -> output second (inside the voice segment that holds it)."""
        for s in self.vo:
            if seg and s["name"] != seg:
                continue
            if s["src_in"] - .2 <= src <= s["src_out"] + .2:
                src = min(max(src, s["src_in"]), s["src_out"])
                return round(s["out"] + src - s["src_in"], 3)
        raise ValueError(f"source {src} not in the voice edit")

    def w(self, text, near=None, seg=None):
        """Output time of a transcript word (first match, optionally near a source second). seg is required here."""
        clip = next(s["clip"] for s in self.vo if s["name"] == seg)
        c = [x for x in WORDS if text.lower() in x["text"].lower() and x["file"] == clip]
        if near is not None:
            c.sort(key=lambda x: abs(x["start"] - near))
        for x in c:
            try:
                return self.o(x["start"], seg)
            except ValueError:
                continue
        raise ValueError(text)

    # ---- picture
    def shot(self, start, dur, src, ms=0.0, kind="video", cls="", style=""):
        self.n += 1
        self.shots.append(dict(id=f"s{self.n}", start=round(start, 3), dur=round(dur, 3), src=src, ms=round(ms, 3),
                               kind=kind, cls=cls, style=style))
        return f"s{self.n}"

    def synced(self, seg, src=None, a=None, b=None):
        """Talking footage in lip-sync with a voice segment (optionally only part of it)."""
        a = seg["src_in"] if a is None else a
        b = seg["src_out"] if b is None else b
        src = src or seg["video"]
        return self.shot(self.o(a, seg["name"]), b - a, src, a)

    def cuts(self):
        return sorted({s["start"] for s in self.shots if s["kind"] in ("video", "img")})

    # ---- sound
    def fx(self, name, at, gain=None):
        self.sfx.append((name, round(at, 3), VOL[name] if gain is None else gain))

    # ---- motion
    def add(self, line):
        self.js.append(line)


def camera_js(ed, total, card_lift=True, origin_y=.42, lift_scale=1.2):
    """House-style camera: hard re-frame on each cut, eased zooms, fast punches, lift above lower cards."""
    ev = list(ed.zoom)
    for a_, b_ in ed.lift:
        ev += [(round(a_, 3), "keep", None, None), (round(b_, 3), "keep", None, None)]
    order = {"set": 0, "keep": 1, "ease": 2, "slow": 2, "punch": 3}
    ev.sort(key=lambda e: (e[0], order[e[1]]))
    cuts = ed.cuts()

    def lifted(t):
        return card_lift and any(a_ <= t < b_ for a_, b_ in ed.lift)

    def frame(s_, x_, t):
        y_ = 0
        if lifted(t + .01):
            s_ = round(max(lift_scale, 1.2 + (s_ - 1.0) * .5), 3)
            y_ = -round(H * (1 - origin_y) * .9 * (s_ - 1.0) - 3, 1)
        lim = 540 * (s_ - 1.0)
        return s_, round(max(-lim, min(lim, x_)), 1), y_

    out, cur = {}, (1.0, 0)
    times = [e[0] for e in ev]
    for n, (t_, kind, s_, x_) in enumerate(ev):
        if s_ is not None:
            cur = (s_, x_)
        fs, fx, fy = frame(cur[0], cur[1], t_)
        nxt = next((tt for tt in times[n + 1:] if tt > t_ + 1e-6), total)
        if kind == "set" or (kind == "keep" and any(abs(t_ - c) < .05 for c in cuts)):
            out[t_] = f'tl.set("#cam", {{scale:{fs}, x:{fx}, y:{fy}}}, {t_});'
            continue
        d = .22 if kind == "punch" else (.5 if kind == "keep" else .7)
        if kind == "slow":
            d = 99
        d = round(min(d, nxt - t_ - .02), 3)
        if d < .12:
            out[t_] = f'tl.set("#cam", {{scale:{fs}, x:{fx}, y:{fy}}}, {t_});'
        else:
            ease = {"punch": "expo.out", "slow": "sine.inOut"}.get(kind, "power2.inOut")
            out[t_] = f'tl.to("#cam", {{scale:{fs}, x:{fx}, y:{fy}, duration:{d}, ease:"{ease}"}}, {t_});'
    return [out[k] for k in sorted(out)]


def write_project(ed, proj, total, extra_css="", origin_y=.42, card_lift=True, lift_scale=1.2, bg="#000"):
    os.makedirs(proj, exist_ok=True)
    clips = []
    for s in ed.shots:
        base = (f'id="{s["id"]}" class="clip {s["cls"]}" data-start="{s["start"]}" data-duration="{s["dur"]}" '
                f'data-track-index="0"')
        st = f'position:absolute; left:0; top:0; width:{W}px; height:{H}px; object-fit:cover; {s["style"]}'
        if s["kind"] == "video":
            clips.append(f'        <video {base} src="{s["src"]}" muted playsinline data-media-start="{s["ms"]}" style="{st}"></video>')
        else:
            clips.append(f'        <img {base} src="{s["src"]}" style="{st}" />')
    cam = camera_js(ed, total, card_lift, origin_y, lift_scale)
    html = f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
{FONTS_CSS}
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:{W}px; height:{H}px; overflow:hidden; background:{bg}; }}
      body {{ font-family:"Montserrat", sans-serif; }}
      #cam {{ position:absolute; inset:0; transform-origin:50% {int(origin_y*100)}%; }}
      .ov {{ position:absolute; opacity:0; }}
{extra_css}
{chr(10).join(ed.css)}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
      <div id="cam">
{chr(10).join(clips)}
{chr(10).join(ed.cam_html)}
      </div>
{chr(10).join(ed.html)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join('      ' + l for l in cam)}
{chr(10).join('      ' + l for l in ed.js)}
      tl.set({{}}, {{}}, {total});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(proj, "index.html"), "w").write(html)
    plan = dict(total=total, vo=ed.vo, shots=ed.shots, sfx=ed.sfx, music=ed.music, zoom=ed.zoom)
    json.dump(plan, open(os.path.join(proj, "edit-plan.json"), "w"), indent=1)
    print(proj, "total", total, "shots", len(ed.shots), "sfx", len(ed.sfx), "zoom", len(ed.zoom))
