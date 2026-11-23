# Video 3 — hinarin (Style E: Papan Hijau Nota Lekat), 53 s

- `cutE.py`: pilih ayat dari 2 klip (RANGES), buang jeda mikro (< -33 dBFS ≥ 0.25 s), betulkan A/V (SyncNet: audio lewat 120 ms → video diambil 0.12 s lebih awal),
  dan **bina semula audio tepat ikut sampel** per segmen (elak drift bila concat — punca +110 ms sebelum ini).
- `renderE.py`: papan hijau bergrid, cut-out B&W bersticker (warna oren produk dikekalkan), label kuning, pita kertas, nota lekat + tick,
  polaroid video produk, polaroid gambar bahan (dari screenshot pengguna), badge 95%, CTA beg kuning, end card logo (crop dari screenshot pengguna). SFX disintesis.
- `cutout.py`: MediaPipe selfie segmenter + gaya B&W dengan warna produk.
- Fon: Archivo Black, Permanent Marker, Patrick Hand, Space Mono (@fontsource, OFL).

## v2 (berwarna)
- Cut-out kini **berwarna** dengan colour grade (`cutout.grade`: kontras 1.10, saturasi 1.14, highlight hangat / bayang sejuk halus).
- Zoom in/out pada penutur (`ZK` keyframes: punch-in laju 0.22 s pada perkataan kunci, zoom-out lembut 0.55 s), berpusat di atas kepala supaya tak menutup elemen papan.
- SFX tambahan: whoosh naik (zoom in) / turun (zoom out). Lubang kecil dalam mask (botol) ditampal.
