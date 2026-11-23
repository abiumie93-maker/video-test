# Video 2 — Cek kesihatan dari rumah (1:58)

- `cut2.py`: buang gagap/ulang (senarai EDITS), buang jeda, laju 1.128x, grading dalam rumah. Segmen di-cache.
- `render2.py`: kamera maya (punch-in setiap cut, zoom smooth/fast dengan motion blur, slow push-in, insert shot produk),
  B-roll 4K full-screen, kinetic typography, kad infografik, lower third, tag produk, CTA beg kuning, end card,
  SFX (whoosh, swish, slam, pop, tick, hit, ding), audio: NR + EQ + de-esser + compressor, muzik ducking, -14 LUFS.

Lesen aset:
- B-roll: Mixkit — Stock Video Free License (komersial dibenarkan, tiada kredit diperlukan). Senarai & semakan lesen dalam `BROLL_LICENSES.json`.
- Muzik: "Inspiration" — FreePD (CC0).

## v2 — pembetulan sync & suntingan ketat
- **Lip-sync:** rakaman asal ada audio ~0.61 s LEBIH AWAL daripada gambar (diukur dengan SyncNet di 4 bahagian: +600..+640 ms).
  `cut2.py` kini ambil video dari `a + AV_SHIFT` dan audio dari `a`. Hasil akhir SyncNet: -40 ms (1 frame) — bawah had kesan ITU (±125 ms).
- PTS video tidak di-reset per segmen (elak beralih ±1 frame 24fps); diuji dengan video kilat+bip (`tools/flash_beep_measure.py`).
- Buang jeda mikro (< -38 dBFS ≥ 0.17 s), serpihan tanpa suara, perkataan berganda/salah mula; titik potong hanya boleh bergerak ke SEBELUM perkataan.
- Laju kini 1.025x (hampir asli), tempoh 1:54.7.
- `tools/av_offset.py` perlukan model SyncNet (`syncnet_v2.model`, VGG Oxford) + MediaPipe face landmarker — tidak disimpan dalam repo.
