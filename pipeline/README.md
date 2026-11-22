# Pipeline edit video (gaya talking-head + infografik)

1. `transcribe.py` – transkrip audio (faster-whisper, Bahasa Melayu) dengan timestamp setiap perkataan.
2. `cut.py` – buang jeda senyap (jump cut), zoom berselang-seli, colour grading (ffmpeg).
3. `render.py` – subtitle, teks kata kunci, kad infografik, kad tajuk penuh skrin, SFX, end card; mix audio & loudnorm.

Semua skrip ambil direktori kerja (scratch) sebagai argumen pertama.
Output preview: `preview_720p.mp4`.
