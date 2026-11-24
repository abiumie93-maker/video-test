# Promo Set Alooma Premium (2 video, 1080x1920)

Sumber: folder Drive (1 video utama 1:58 + 6 klip bilik). Footage tak di-commit (`assets/footage/`, gitignore).

| Video | Gaya | Tempoh | Generator |
|---|---|---|---|
| **Versi 1** | House style (zoom in/out, zoom slam, kad gelap + kad lukisan tangan) | 1:25 | `tools/gen1.py` -> `v1/` |
| **Versi 2** | Gaya video reference (pill atas, neon + karusel kad, blur -> neon, kanvas putih, tag kaca, butang CTA) | 1:08 | `tools/gen2.py` -> `v2/` |

Hook Versi 1: "Sayang lah, tilam korang beli mahal. Tiba-tiba banyak tompok-tompok, peta-peta dunia" (sumber 0:59.8) atas gambar tilam lama.
Hook Versi 2: "6 ITEM, 1 SET SAHAJA" + karusel kad produk atas "Guys, mari sini... tengoklah ini".

Bunyi: suara asal (0:00-1:09 sumber) dipotong ikut titik senyap; muzik latar CC0 (FreePD, `assets/music/CREDITS.txt`)
rendah bawah suara, naik masa montaj; SFX (Pixabay). Mix -15 LUFS, true peak <= -1.5 dBTP.

```bash
# letak footage dalam assets/footage/ (H.264, -g 30), dan assets/main_audio.wav (48k stereo dari video utama)
python3 tools/gen1.py && python3 tools/gen2.py
(cd v1 && npx hyperframes@0.9.79 render --quality delivery -o ../renders/v1_video.mp4)
python3 tools/mix.py v1 renders/v1_video.mp4 renders/ALOOMA_Video1.mp4     # sama untuk v2
```
