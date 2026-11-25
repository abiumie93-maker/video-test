# Promo tapak kasut (insole), Versi 1 + Versi 2 (1080x1920)

Sumber: folder Drive, 5 klip (25 Nov 2026). Suara hanya ada dalam `073913` (cakap ke kamera) dan `074041` (suara + close-up);
`073758`, `073815`, `073827` senyap (b-roll). Footage dan `assets/a_*.wav` tak di-commit.

| Versi | Tempoh | Generator |
|---|---|---|
| Versi 1 (house style) | 0:35 | `tools/gen1.py` -> `v1/` |
| Versi 2 (gaya reference) | 0:36 | `tools/gen2.py` -> `v2/` |

Hook (kedua-dua): "Tapak kasut yang lama ni, korang boleh campak." (073913 0:00-0:04) + shot tapak lama dicampak (073827),
kemudian "Dapatkan yang baru."

Muzik: FreePD (CC0 / public domain) - bebas untuk kegunaan komersial (TikTok Shop / beg kuning, YouTube), tiada atribusi diperlukan.

```bash
python3 tools/gen1.py && python3 tools/gen2.py
(cd v1 && npx hyperframes@0.9.79 render --quality delivery -o ../renders/v1_video.mp4)
python3 tools/mix.py v1 renders/v1_video.mp4 renders/INSOLE_Versi1_1080x1920.mp4    # sama untuk v2
```
