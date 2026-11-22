# Edit: "Darah tinggi? Catat lifestyle dulu" (Hyperframes)

Sumber: `2026-11-11-084705352.mp4` (4:54, 1080×1920). Hasil edit: **4:41.7**.
Status: **PREVIEW v2 sahaja, final belum dirender.**

## v2: apa yang berubah
- **Zoom in/out lancar** pada setiap permulaan ayat (1.0×–1.3×, ease 0.7s), **zoom slam** pantas pada kata kunci
  (penyakit, FOMO, rehat 3 jam, berhutang, 6 bulan, tak logik, tak bodoh, sakit semula, silap), dan re-frame keras pada setiap jump cut.
  Bila kad di skrin, kamera zoom ≥1.2× dan angkat frame supaya muka sentiasa di atas kad. Ini juga menolak sebahagian besar subtitle lama ke luar frame.
- **8 kad infografik gaya lukisan tangan** (kertas + pita, garis dilukis atas skrin, tulisan tangan Caveat/Permanent Marker):
  | Masa | Lukisan |
  |---|---|
  | 0:07–0:15 | Meter tekanan darah naik ke merah, 3 biji ubat, botol supplement "?" |
  | 0:48–1:00 | Kalendar "10 tahun", Lifestyle → anak panah → Penyakit (dibulatkan) |
  | 1:32–1:44 | 3 orang dipangkah ("Semua orang salah?"), cermin diri, ✓ Terima salah, ✓ Perbaiki |
  | 1:45–1:52 | Buku nota rutin dengan kanta pembesar, bulatan merah "Oh! Aku salah kat sini!" |
  | 3:39–3:45 | Jam pasir (pasir turun), "Bagi badan MASA untuk adapt & repair" |
  | 3:45–3:53 | Sel badan tersenyum, "BIJAK!", ✓ ramai sembuh |
  | 3:53–4:01 | Graf kesihatan naik (sihat 3–4 bulan) lalu jatuh "Boleh sakit semula!" |
  | 4:08–4:23 | Langkah 1-2-3: Catat → Cari silap → Baru bincang supplement / rawatan / lifestyle |
- Ejaan **"suplimen" → "supplement"** dalam semua grafik dan transcript.

## Hook (cold open, 0:00–0:06)
Ayat paling kuat diletak di depan:
> "Saya percaya, penyakit yang kita dapat hari ini daripada lifestyle yang kita kekalkan selama 10 tahun ke belakang."

Tajuk di skrin: **PENYAKIT HARI INI = LIFESTYLE 10 TAHUN LEPAS**, dengan bunyi impact, dan whoosh masuk ke soalan follower.

## Potongan (buang ulangan dan ayat janggal)
| Sumber | Dibuang |
|---|---|
| 0:53.5–1:03.2 | Ulang "apa yang saya dapat umur 30… 10 tahun ke belakang" |
| 1:24.2–1:25.2 | "Buat yang itu dulu" (kali ke-3) |
| 1:48.6–1:49.9 | "Cuba buat yang itu dulu" (kali ke-4) |
| 2:56.2–2:58.3 | "Pukul itu pukul 2 pagi baru nak tidur" (berulang) |
| 4:15.5–4:17.6 | "Dan dekat situlah pentingnya kat sini" (janggal) |
| 4:51.2–akhir | Senyap di hujung |

Setiap potongan diletak dalam celah senyap sebenar (bukan ikut timestamp Whisper sahaja), dan disemak dengan transcribe semula audio di kedua-dua belah potongan.
Setiap jump cut ada punch-in (1.0× ↔ 1.08×). Ada juga zoom penekanan pada "rehat 3 jam", "Tak logik" dan lain-lain.

## Motion graphics (ikut transcript)
| Masa (output) | Grafik |
|---|---|
| 0:00 | Tajuk hook |
| 0:17–0:47 | Kad "Langkah 1: Catat rutin harian", 6 item ditanda ✓ ikut apa yang disebut |
| 1:00–1:09 | Umur 20 → 30, bar "10 tahun lifestyle → penyakit" |
| 1:09–1:18 | Chip ~~UBAT~~ ~~SUPPLEMENT~~ dan "Tahu dulu di mana salah" |
| 1:22–1:32 | "FOMO?" dengan gelembung "Supplement ni bagus!"… |
| 1:52–3:00 | Jam rutin harian: Pagi → 10PG → 1TGH → Petang → 8–9MLM → 12MLM → 2–3PG → **REHAT 3 jam** |
| 3:02–3:39 | Bar hutang tidur (8 jam lawan 4 jam), "Setahun berhutang = 6 BULAN", cop **TAK LOGIK** |
| 4:01–4:08 | PENTINGNYA: LIFESTYLE / KONSISTEN / DISIPLIN |
| 4:23–4:28 | "Setiap badan tak sama" |
| 4:29–4:41 | Butang SHARE dan "Semoga kembali sihat & sembuh" |

SFX (70 bunyi yang dibundel): whoosh, pop, click, error, notification, impact, riser. Setiap satu ada sebab di skrin, dengan puncak bunyi 1 frame selepas visual.

## Perlu keputusan awak
1. **Video sumber dah ada subtitle burned-in** (teks kuning/putih di atas) dan beberapa grafik lama (cth. simbol 🚫). Sebab tu saya **tak tambah satu lagi set subtitle**, nanti bertindih. Kalau nak subtitle gaya baru, hantar footage mentah (tanpa teks) dan saya akan bina caption ikut perkataan dari `transcript.json`.
2. **Matematik dalam audio:** "perlukan 8 jam, tidur 4 jam, berhutang **3 jam**". Sepatutnya 4 jam. Grafik tunjuk bar 8 lawan 4 tanpa angka hutang supaya tak bercanggah dengan suara.
3. Tiada muzik latar ditambah, sebab audio sumber dah ada bunyi latar dan tak senyap.

## Cara edit / render
```bash
cd edit
# letak footage (H.264, keyframe setiap 1s) di assets/footage.mp4:
ffmpeg -i SUMBER.mp4 -c:v libx264 -crf 19 -g 30 -pix_fmt yuv420p -c:a aac assets/footage.mp4
python3 tools/gen.py .          # jana semula index.html + compositions/ (guna tools/draw.py)
npx hyperframes preview         # Studio
npx hyperframes render --quality delivery -o final.mp4   # FINAL (bila dah lulus)
```
