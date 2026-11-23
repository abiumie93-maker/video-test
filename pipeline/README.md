# Pipeline edit video (gaya talking-head + infografik)

1. `transcribe.py` – transkrip audio (faster-whisper, Bahasa Melayu) dengan timestamp setiap perkataan.
2. `cut.py` – buang jeda senyap (jump cut), zoom berselang-seli, colour grading (ffmpeg).
3. `render.py` – subtitle, teks kata kunci, kad infografik, kad tajuk penuh skrin, SFX, end card; mix audio & loudnorm.

Semua skrip ambil direktori kerja (scratch) sebagai argumen pertama.
Output preview: `preview_720p.mp4`.

## Versi 2 (±2 minit)
- Buang gagap / ayat berulang (senarai `EDITS` dalam `cut.py`), laju 1.17x (pitch kekal).
- Muzik: "Inspiration" dari FreePD.com (CC0 / public domain) — mirror archive.org `abook-music-freepd-cc0`, fail `fpd-878d4dee797d92ef.mp3`.
  Ducking automatik (sidechain) bila bercakap.
- Suara: noise reduction, EQ presence, de-esser, compressor; master -14 LUFS.
- Output final: 1080x1920, 30fps, H.264 High CRF16, AAC 320k.
