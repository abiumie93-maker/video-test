# Video editing house style (Hyperframes)

The user approved this style on 2026-11-22 ("ingat terus style macam ni"). Use it by default for every new talking-head video
from this user, unless they ask for something different. The reference project is `edit/`. Its generator `edit/tools/gen.py` +
`edit/tools/draw.py` is the template to copy and adapt; read `edit/EDIT-NOTES.md` for a worked example.

Talk to the user in Bahasa Melayu (casual, "awak/korang"). Spell **"supplement"**, never "suplimen", in all on-screen text.

## Workflow (always in this order)
1. Download the source. Probe it. Re-encode to H.264 with a keyframe every 1 s (`-g 30`), or seeking freezes.
2. **Transcribe first**: `npx hyperframes transcribe <wav> --model medium --language ms`. Read the whole transcript before planning.
3. Check a 1 fps / 10 s contact sheet for burned-in captions or old graphics, and tell the user if you find any.
4. Plan the edit from the transcript:
   - **Hook**: cold-open with the single strongest line (a thesis or surprising claim, ~5–7 s), then cut to the start.
   - **Cut** repeated sentences, filler restarts, awkward/unfinished lines and the dead tail. Snap every cut to a real silence
     gap (`tools/gaps.py`), not Whisper timestamps, which drift 0.1–0.2 s. Verify each seam by re-transcribing ±1.8 s
     either side (`tools/seam.py`).
5. Build, then `npx hyperframes check` (0 errors) and `snapshot` the key moments, and look at them.
6. **Render a PREVIEW only** (`--quality draft`, then downscale to 540p with a "PREVIEW" mark) and send it. Never render the
   final until the user says so.
7. On approval: `npx hyperframes render --quality delivery`. Commit the project, not the footage or renders.

## Camera (zoom in / zoom out). The user asked for lots of it.
- Hard re-frame on every jump cut (alternate 1.0 / 1.1 / 1.08 / 1.0).
- Smooth zoom on almost every new sentence (min 2.2 s apart), 0.7 s `power2.inOut`, cycling scale 1.0–1.24 with small x drift.
- **Zoom slam** on key words (the disease, the shocking number, "tak logik"…): 1.26 in 0.22 s `expo.out`, with a whoosh on about half.
- While any lower card is on screen: scale ≥ 1.2 and lift the frame (`y = -(1113.6·(s-1) - 3)`, origin `50% 42%`) so the face
  always sits above the card. Never cover the face.
- Clamp |x| ≤ 540·(s-1) so no black edge shows.

## Graphics: two families, placed in the lower band (y ≈ 860–1245, x 120–780)
1. **Dark cards** for data and lists: `rgba(12,18,38,.86)`, radius 28, Montserrat 700–800, Archivo Black headlines,
   accent yellow `#FFC928`, red `#FF4D4D`, green `#3DDC84`. Use them for checklists ticked as each item is spoken,
   progress bars, a clock that spins through a daily routine, a struck-through chip, a "TAK LOGIK" stamp, a SHARE button.
2. **Hand-drawn paper cards** (the user loves these): cream `#FFF8E7` paper with a yellow tape strip, slight rotation,
   entering with `back.out(1.4)` at scale .86 (origin top). Ink strokes draw on (`pathLength=1`, dashoffset 1→0), and
   handwriting wipes in left to right. Fonts: Caveat 700 and Permanent Marker (in `assets/fonts/`).
   Ink colours: `#1d1d1f`, red `#E63434`, green `#1FA855`, blue `#1F5FD1`, highlighter `#F2B705`.
   Draw what is being said, e.g. a gauge spiking, pills, a bottle with "?", a calendar, an arrow into a circled word,
   stick figures crossed out, a mirror, a notebook with a magnifier and a red ring, an hourglass with falling sand,
   a smiling cell, a rising-then-falling health graph, numbered steps with underlines.
- **No stretch of the video may go without graphics.** Aim for a new card every ~8–15 s. Every element lands on the word that says it.
- Hook title: Archivo Black, white plus a yellow key word, with a drawn yellow underline and a bass impact.
- Lines must hold ≥ 0.5 s + 0.3 s per word. Do not add a second set of subtitles over burned-in ones.

## Sound
Use the bundled SFX only, few and exact: whoosh-short when a card enters, pop when an item or number lands, error on a
cross-out or a "wrong" beat, impact on the hook and stamps, a riser into the single biggest payoff. Peak one frame after the
visual. Target the mix at −15 LUFS, true peak ≤ −1 dBTP. No music unless the source is clean and the user asks.

## Delivery note
Always tell the user, in Malay: what was cut (with timestamps), where the hook came from, any factual or maths slip
heard in the audio (flag it, don't "fix" the voice), and whether the push worked.
