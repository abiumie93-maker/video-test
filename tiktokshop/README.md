# TikTok Shop awareness (affiliate), gaya video contoh pengguna (1080x1920, 1:54)

Sumber (folder Drive, 26 Nov 2026): `VID_20261126_074607` (cakap ke kamera, 1:55), rakaman skrin `SVID_..._073404`
(install TikTok Shop dari Play Store), `SVID_..._073509` (buka app, search produk), `SVID_..._073827` (profil @khalidkacak).
Video contoh: `df22d424ef945d66e197ad5cfa8e768f.mp4` (TikTok Shop app, gaya krim/emas).

Gaya (`tools/gen_ref.py`): footage hangat + vignette, tajuk emas Anton atas kepala, sari kata serif (Playfair) dengan kata kunci
emas italic, scene kanvas krim (tajuk Montserrat italic + bar emas, mockup telefon main rakaman skrin, kad putih/oren, cop),
ikon TikTok -> TikTok Shop, carta sales, voucher, LIVE, bar undian A/B, end card bar carian @khalidkacak.
Bukan promosi produk: tiada CTA beg kuning. Muzik: "Be Chillin" (FreePD, CC0).

Potongan: 0:52.0-0:55.5 (ulangan "dan sekarang ni pun kita dah start rasa dah. Dan sekarang ni pun").

```bash
python3 tools/gen_ref.py
(cd v1 && npx hyperframes@0.9.79 render --quality delivery -o ../renders/v1_video.mp4)
python3 tools/mix.py v1 renders/v1_video.mp4 renders/TIKTOKSHOP_Awareness_1080x1920.mp4
```
