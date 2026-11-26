# Pokok olive tiruan 1.5 m - gaya TikTok Shop (video contoh pengguna) (1080x1920, 1:38)

Sumber (folder Drive, 26 Nov 2026): `lv_0_20261105164437.mp4` (rakaman asal, 1:48) - digunakan.
`lv_0_20261105163721.mp4` ialah versi CapCut yang sudah ada muzik - tidak digunakan.

Gaya sama dengan `tiktokshop/` (rupa + helper dimuat dari `tiktokshop/tools/gen_ref.py`).
Hook: "Guys tengoklah wife saya beli apa... dia tengah marah... sebab pokok dia saya letak kat atas, jadi dia beli pokok sendiri".
CTA: "...saya letak dekat beg kuning, korang terus checkout dekat beg kuning sekarang". Muzik: "Be Chillin" (FreePD, CC0).
Potongan: 0:35.9-0:38.7 ("boleh satu ha? sekali sekali ya?"), 1:04.3-1:07.9 (senyap, jalan ke dinding).

```bash
python3 tools/gen_ref.py
(cd v1 && npx hyperframes@0.9.79 render --quality delivery -o ../renders/v1_video.mp4)
python3 tools/mix.py v1 renders/v1_video.mp4 renders/POKOK_OLIVE_1080x1920.mp4
```
