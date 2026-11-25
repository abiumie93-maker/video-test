# Gaya edit video yang diluluskan: **Versi 1** dan **Versi 2**

Pengguna meluluskan kedua-dua gaya ini pada 2026-11-24 ("Aku suka sangat 2 2 versi ni... kekal versi ni").
Bila pengguna sebut **"Versi 1"** atau **"Versi 2"**, ikut gaya di bawah. Kalau dia minta "2 versi", buat kedua-duanya.
Projek rujukan: `promo/` (video promo Set Alooma Premium). Generator: `promo/tools/gen1.py` (Versi 1) dan
`promo/tools/gen2.py` (Versi 2), helper bersama `promo/tools/common.py`, mixer audio `promo/tools/mix.py`.
Salin dan sesuaikan generator ini untuk video baru; jangan tulis dari kosong.
Contoh kedua: `insole/` (promo tapak kasut, suara dari BEBERAPA klip). `insole/tools/common.py` + `mix.py` menyokong
`E.say(name, a, b, clip="<klip>")` (setiap segmen suara ada klip sendiri, audio `assets/a_<klip>.wav`), dan
`insole/tools/gen1.py` / `gen2.py` memuatkan rupa + helper terus dari `promo/tools/gen1.py` / `gen2.py` (satu sumber).
Guna `insole/tools/` sebagai titik mula untuk projek baru.

Cakap dengan pengguna dalam Bahasa Melayu santai ("awak/korang"). Dalam teks skrin, eja **"supplement"**, bukan "suplimen".

## Aliran kerja (kedua-dua versi)
1. Muat turun sumber (folder Drive yang dikongsi "anyone with link" boleh dimuat turun dengan
   `curl "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`).
   Probe. Tukar ke H.264 1080×1920 30fps dengan keyframe setiap 1 s (`-g 30`), klip senyap guna `-an`.
2. **Transcribe dulu** (`npx hyperframes@0.9.79 transcribe <wav> --model medium --language ms`; fail ditulis sebelah wav).
   Baca keseluruhannya. Betulkan ejaan jenama/perkataan dalam `transcript.json` (cth. Aloma→Alooma, Lapid→Lapik).
3. Contact sheet (0.5–1 fps) setiap klip: cari teks burned-in, inset, dan shot terbaik untuk hook/montaj.
   Semak spektrogram: bahagian yang hanya muzik (bukan suara) jangan guna audionya.
4. Pilih **hook** paling kuat (masalah/kejutan) dan letak di depan. Buang ayat berulang. Potong pada titik senyap
   (`tools/snap.py`), kemudian **sahkan setiap sambungan** dengan transcribe semula audio mix.
5. Jana, `hyperframes lint` (0 ralat), `snapshot --at ...` momen penting dan **tengok** hasilnya.
6. Render `--quality delivery`, kemudian `python3 tools/mix.py vN render.mp4 akhir.mp4`.
   Hantar fail (SendUserFile) dan PushNotification bila siap kalau pengguna minta.
7. Commit projek (bukan footage/render). Beritahu pengguna: apa dipotong (dengan masa), dari mana hook,
   perkataan audio yang tak pasti, dan sama ada push berjaya.

## Bunyi (kedua-dua versi)
- Semua `<video>` di Hyperframes `muted`; bunyi dibina oleh `tools/mix.py`: suara asal dipotong ikut edit (fade 25–35 ms),
  muzik latar CC0 (FreePD, `assets/music/`) rendah bawah suara (~0.14–0.16) dan naik masa montaj (~0.6), fade di hujung,
  SFX bundel (whoosh, pop, impact, error, notification, click, riser) dengan puncak 1 frame selepas visual.
- Target −15 LUFS, true peak ≤ −1.5 dBTP (loudnorm dua laluan). Jangan guna audio muzik dari footage sumber.
- **Muzik mesti selamat untuk komersial** (TikTok Shop / beg kuning dan YouTube — pengguna minta): guna hanya trek
  public domain / CC0 (FreePD dalam `promo/assets/music/`, `CREDITS.txt`). Jangan guna lagu popular atau muzik "free"
  yang bersyarat (cth. non-commercial, atau perlu atribusi yang mungkin terlupa).

---

## VERSI 1 — House style (zoom + kad gelap + kad lukisan tangan)
Rujukan: `promo/v1/`, hasil "ALOOMA_Versi1" (1:25).

**Struktur:** Hook masalah (cold open, ~6 s) → cut pantas ke penyelesaian ("Let's go!") → isi dengan suara asal →
montaj muzik dengan label besar → reveal **SIAP!** (riser + impact) → b-roll suasana ("MEWAH") → kad CTA.

**Hook:** gambar/klip masalah (cth. tilam bertompok) dengan Ken Burns, bulatan dakwat merah dilukis atas masalah + bunyi error,
tajuk Archivo Black di jalur bawah: baris pertama sudah ada pada frame 0 (thumbnail), kata kunci kuning, kata kejutan
merah besar ("PETA DUNIA?!") + garis bawah kuning dilukis + bass impact. Kemudian whoosh ke "Penyelesaian dia? SET ALOOMA".

**Kamera (banyak zoom in/out — pengguna minta):**
- Re-frame keras pada setiap cut (1.0 / 1.08 / 1.04 / 1.1).
- Zoom lancar pada hampir setiap ayat baru (≥2.2 s jarak), 0.7 s `power2.inOut`, skala 1.0–1.22 dengan sedikit drift x.
- **Zoom slam** 1.28 dalam 0.22 s `expo.out` pada kata kunci (jenama, harga/mahal, "tak cantik", "waterproof", "bersih",
  "wajib", "go"), whoosh pada separuh daripadanya.
- Bila kad bawah di skrin: skala ≥1.2 dan angkat frame supaya muka di atas kad. Montaj/b-roll: slow push 1.1–1.15 setiap shot.

**Grafik (jalur bawah, y ≈ 880–1400, x 120–960):**
1. **Kad gelap** `rgba(12,18,38,.88)`, radius 28, Montserrat 800, tajuk Archivo Black, kuning `#FFC928`, merah `#FF4D4D`,
   hijau `#3DDC84`: senarai item ditanda ✓ ikut sebutan, chip (cth. WATERPROOF / NON-WATERPROOF, yang ditolak dipangkah),
   **cop** bersudut (cth. "ALOOMA!" pop setiap kali jenama disebut, "PILIH INI!"), "WAJIB PAKAI!" + perisai dilukis.
2. **Kad kertas lukisan tangan** (pengguna suka): kertas `#FFF8E7` + pita kuning, masuk `back.out(1.4)`, garisan dilukis
   (`pathLength=1`), tulisan Caveat / Permanent Marker dilap kiri ke kanan. Lukis apa yang disebut (orang lidi + belon cakap,
   swatch warna dipangkah/ditanda, kalendar "2-3 bulan" → tilam berkilau).
- Tiada bahagian tanpa grafik: kad baru setiap ~5–10 s, setiap elemen mendarat pada perkataannya.
- Montaj: label Archivo Black 124px tengah bawah (putih + kata kuning), masuk scale 1.5→1 + blur, whoosh setiap cut.
- CTA: kad gelap "Nak bilik cantik macam ni?" + butang kuning bulat dengan ikon beg **TEKAN BEG KUNING** (berdenyut, click)
  + "Komen 1 hingga 5". Fade keluar 0.4 s.

---

## VERSI 2 — Gaya video reference (motion design moden, kanvas bersih)
Rujukan: `promo/v2/`, hasil "ALOOMA_Versi2" (1:08). Diilhamkan oleh klip contoh pengguna
("NAK EDIT VIDEO GUNA AI TAPI TAK TAHU NAK START").

**Fon & warna:** Plus Jakarta Sans 600–800. Neon lime `#C8FF2E` dengan glow berlapis, biru `#2347FF` untuk kata kunci,
merah `#E5383B`, teks gelap `#12131A`, kanvas `#F3F3F0`.

**Elemen tetap:**
- **Pill atas** gelap lut sinar (blur), tengah atas, 2 baris: soalan kecil + tajuk tebal (cth. "Nak bilik cantik macam hotel?" /
  "1 SET ALOOMA"). Muncul bila hook mengecil masuk ke dalamnya, kekal sampai akhir.
- Pemusatan guna `left:0; right:0; margin:0 auto; width:fit-content` (jangan `translateX(-50%)` — GSAP scale merosakkannya).

**Struktur & teknik:**
1. **Hook:** nombor neon gergasi (cth. "6") + "ITEM / 1 SET SAHAJA" putih dengan kata neon, di atas footage;
   **karusel 3D** kad produk (gambar dipotong dari footage, sudut bulat, bingkai putih) berpusing di separuh bawah;
   pill putih kecil ("guys, tengok ni!"). Hujung hook: tajuk mengecil ke pill atas.
2. **Footage bercakap:** nama item putih tebal besar (96px) di bawah, masuk scale 1.25→1 + blur; **pill putih kecil** dengan
   kata kunci biru (cth. "jenama? **ALOOMA** ✓", bunyi notification).
3. **Transisi blur → neon:** footage blur 36px + gelap, label kecil ("brand dia dipanggil"), kata neon gergasi (ALOOMA) + impact,
   pill kaca kecil di bawah.
4. **Scene kanvas putih** (dot grid + blob lavender & lime kabur): lencana seksyen kiri atas (petak putih huruf biru + label),
   **kad kaca** putih dengan gambar, chip lime "✓ cadangan", kad yang ditolak jadi kelabu/kecil, kapsyen tebal hitam
   dengan kata kunci biru di bawah; **petak persamaan** (Lapik + 2–3 bulan = ✓ biru) diikuti kad bukti bergambar.
5. **Masalah:** latar gambar kabur gelap + kad kaca bergambar di tengah, kapsyen putih kata merah, **tag merah** terapung
   ("✗ tompok", "✗ kotor", "✗ peta dunia") + bunyi error, kad bergegar sedikit.
6. **Montaj:** cut 1.6 s dengan pill putih huruf kecil ("pasang cadar"), "LET'S GO!" neon, slow push setiap shot.
7. **Reveal:** "SIAP!" neon + tag kaca terapung "LEMBUT +", "CANTIK +", "PREMIUM +".
8. **Kad akhir:** latar footage kabur, kad kaca putih bergambar produk + nama + senarai isi, **butang pill biru** bercahaya
   "TEKAN BEG KUNING SEKARANG" (click, berdenyut), "klik beg kuning ↓", pill "komen 1 hingga 5".
- Kamera tetap zoom in/out (re-frame pada cut, zoom lancar 1.0–1.16, punch 1.24 pada kata kunci) tapi tiada angkat-frame.
