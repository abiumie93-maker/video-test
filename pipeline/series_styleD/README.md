# Siri 5 video — Style D (Neon Yellow Stack)

| Fail | Tajuk | Sumber | Tempoh |
|---|---|---|---|
| D1 | Kenapa cek di rumah? | VID_152508 | 1:09 |
| D2 | Hitam atau putih? | VID_153809 + 155958 + 154207 | 1:11 |
| D3 | Barang murah boleh percaya ke? | VID_154605 + 153938 | 1:05 |
| D4 | Kau berya sebab nak jual je? | VID_154842 | 1:12 |
| D5 | Macam mana nak tahu ada darah tinggi? | VID_154425 + 154207 | 1:19 |

Pipeline: `buildD.py KEY` → `cutD.py p4/work/KEY/cut.json render` → `facesD.py p4/work/KEY` → `renderD.py KEY`.
- A/V offset diukur per klip dengan SyncNet (antara -200 ms hingga +840 ms) dan dibetulkan per klip; hasil akhir -40 ms (1 frame) untuk semua.
- Teks: blok bertindan kuning neon #F9FF23 (Anton) + lead-in putih (Archivo Black), perkataan dimunculkan ikut masa sebutan (blur-in + scale),
  keyword besar di BELAKANG kepala (segmentasi orang), perkataan gergasi memenuhi frame, punch-zoom + zoom-blur setiap cut,
  B-roll kad lavender (gambar pengguna) & klip demo BP, SFX pop/tick/swish/whoosh/boom/ding.

## v2 (maklum balas)
- Potongan tak lagi memotong hujung ayat: hujung setiap range dilanjutkan ikut tenaga suara (maks +0.35 s, tak melepasi perkataan seterusnya), jeda dipendekkan (≥0.38 s → dikekalkan ~0.2 s).
- Ayat berulang dibuang (senarai range ditulis semula untuk setiap video). Tempoh 1:21–1:39.
- Semua tulisan ada garisan luar gelap (stroke) supaya jelas walau di belakang kepala.
- Kad infografik gelap (✓ ✗ ↑ •) muncul ikut sebutan, macam format video sebelum ini.
