# "Pizza buatan Pia" - video KENANGAN keluarga, Versi 1 (1080x1920, 0:56)

Sumber: folder Drive, 4 klip (24 Nov 2026): `101515` (Pia buat pizza, perbualan dengan ayah), `101558` (susun pepperoni,
tiada suara jelas), `102643` (pizza atas foil -> masuk air fryer oven), `103829` (0.25 s, pizza siap -> `assets/img/pizza_siap.jpg`).

Hook: "Kalau sedap boleh jual tak? / Tak boleh! / Sebab ini Pia buat." (101515 0:18.6-0:26.4) atas gambar pizza siap.
Bukan promosi: tiada CTA / beg kuning. Penutup = kad kenangan lukisan tangan ("Kenangan manis, Pizza buatan PIA,
24 November 2026, Ayah sayang Pia") atas shot Pia rasa sos.

```bash
python3 tools/gen1.py
(cd v1 && npx hyperframes@0.9.79 render --quality delivery -o ../renders/v1_video.mp4)
python3 tools/mix.py v1 renders/v1_video.mp4 renders/PIZZA_Kenangan_Versi1_1080x1920.mp4
```
