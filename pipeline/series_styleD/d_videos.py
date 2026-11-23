"""Style D series v2 — 5 videos, ~1:20-1:35 each, repeats removed, full sentences.
Source times are each clip's own timeline (s).
broll: (clip, t, dur, kind, asset)   kind: img | clip
giant: (clip, t0, t1, WORD)
wide:  (clip, t0, t1)
cards: (title, clip, t_in, t_out, [(row_text, status, clip, t_row)])   status: ok | bad | up | info"""
V = {}
V["v1"] = dict(
    title="Kenapa cek di rumah?",
    ranges=[("152508", 1.25, 2.0), ("152508", 4.05, 11.65), ("152508", 11.9, 15.35), ("152508", 15.45, 20.2),
            ("152508", 20.2, 28.1), ("152508", 28.1, 40.3), ("152508", 40.4, 44.8), ("152508", 44.85, 51.05),
            ("152508", 51.05, 59.6), ("152508", 59.7, 63.9), ("152508", 65.45, 67.55), ("152508", 69.2, 75.95),
            ("152508", 75.95, 80.9), ("152508", 81.0, 87.15)],
    broll=[("152508", 10.4, 1.2, "img", "gout_bengkak.webp"), ("152508", 57.3, 1.4, "img", "s_pdf_165330.jpg"),
           ("152508", 66.3, 1.2, "clip", "VID_20261109_160054.mp4@20"), ("152508", 78.2, 1.4, "img", "p_ca93.webp"),
           ("152508", 83.0, 1.5, "img", "s_shop_080722.jpg")],
    giant=[("152508", 72.9, 73.9, "KLINIK")],
    wide=[("152508", 15.45, 20.2), ("152508", 51.05, 54.3)],
    cards=[("Kenapa cek di rumah?", "152508", 22.2, 28.0, [("Bacaan lebih stabil", "ok", "152508", 24.49), ("Bacaan lebih dipercayai", "ok", "152508", 26.35)]),
           ("Faktor luar buat bacaan naik", "152508", 30.3, 40.2, [("Takut doktor", "bad", "152508", 31.51), ("Takut nurse", "bad", "152508", 32.87),
                                                                    ("Takut hospital", "bad", "152508", 37.91), ("Suasana klinik", "bad", "152508", 39.11)]),
           ("Apa perlu buat?", "152508", 60.5, 75.9, [("Cek sendiri di rumah", "ok", "152508", 60.99), ("Catat bacaan", "ok", "152508", 63.47),
                                                       ("Sentiasa tinggi? Bawa ke klinik", "up", "152508", 71.29)])],
)
V["v2"] = dict(
    title="Hitam atau putih?",
    ranges=[("153809", 0.25, 7.55), ("153809", 7.75, 12.3), ("153809", 12.7, 19.2), ("153809", 19.3, 29.0),
            ("153809", 33.85, 40.6), ("155958", 0.3, 4.9), ("153809", 44.5, 52.4), ("153809", 52.35, 60.0),
            ("154207", 1.3, 7.4), ("154207", 7.6, 13.3), ("154207", 14.4, 25.2), ("154207", 31.2, 36.4),
            ("154207", 36.7, 41.9), ("154207", 42.3, 46.45), ("153809", 63.9, 67.05), ("153809", 69.9, 71.45), ("153809", 71.9, 74.45)],
    broll=[("153809", 25.0, 1.3, "img", "s_shop_080741.jpg"), ("153809", 47.6, 1.4, "img", "s_shop_080805.jpg"),
           ("154207", 9.6, 1.4, "img", "s_tt_202256.jpg"), ("154207", 39.3, 1.4, "img", "p_ca93.webp"), ("153809", 72.6, 1.3, "img", "s_pdf_165811.jpg")],
    giant=[("153809", 14.1, 15.5, "SAMA")],
    wide=[("153809", 7.75, 12.3), ("154207", 14.4, 21.4)],
    cards=[("Hitam vs Putih", "153809", 13.0, 19.2, [("Semua sama, identikal", "ok", "153809", 13.44), ("Dua-dua MDA approved", "ok", "153809", 16.2),
                                                     ("Beza hanya warna", "info", "153809", 17.74)]),
           ("Dalam kotak", "153809", 34.0, 40.6, [("Bateri", "ok", "153809", 35.66), ("Cuff", "ok", "153809", 37.88), ("Manual", "ok", "153809", 40.18)]),
           ("Pilihan kombo", "154207", 15.0, 25.2, [("BP set + glukometer", "ok", "154207", 17.97), ("BP set + 3-in-1", "ok", "154207", 20.63),
                                                    ("3-in-1 lebih berbaloi", "up", "154207", 24.61)])],
)
V["v3"] = dict(
    title="Barang murah boleh percaya ke?",
    ranges=[("154605", 0.75, 4.1), ("154605", 12.4, 14.6), ("154605", 14.8, 19.5), ("154605", 20.0, 25.6), ("154605", 27.2, 27.9),
            ("154605", 29.3, 38.1), ("154605", 38.3, 42.55), ("154605", 44.4, 49.1), ("154605", 49.4, 51.0), ("154605", 51.8, 54.95),
            ("154605", 58.6, 60.45), ("154605", 60.8, 63.5), ("154605", 70.95, 71.4), ("154605", 74.5, 77.35),
            ("153938", 16.15, 21.3), ("153938", 21.8, 23.9), ("153938", 30.1, 35.9), ("153938", 36.1, 36.95), ("153938", 41.0, 43.1),
            ("153938", 43.5, 51.7), ("153938", 52.2, 57.25), ("153938", 57.4, 63.2), ("153938", 69.8, 74.5)],
    broll=[("154605", 22.9, 1.4, "img", "s_chrome_165504.jpg"), ("154605", 39.9, 1.3, "clip", "VID_20261109_160054.mp4@14"),
           ("153938", 33.4, 1.4, "img", "p_ca93.webp"), ("153938", 47.0, 1.5, "img", "p_my820lb.avif"), ("153938", 72.9, 1.4, "img", "chatgpt.png")],
    giant=[("153938", 19.5, 20.9, "MAHAL"), ("154605", 59.0, 60.3, "KONSISTEN")],
    wide=[("154605", 14.8, 19.5)],
    cards=[("2 poin saya", "154605", 13.0, 19.4, [("Semua MDA approved", "ok", "154605", 18.62)]),
           ("Dulu vs sekarang", "153938", 16.5, 43.0, [("Dulu: harga mahal", "bad", "153938", 19.57), ("Dulu: tak banyak pilihan", "bad", "153938", 22.95),
                                                       ("Sekarang: harga berbaloi", "ok", "153938", 35.33), ("Masih MDA approved", "ok", "153938", 42.29)])],
)
V["v4"] = dict(
    title="Kau berya sebab nak jual je?",
    ranges=[("154842", 0.4, 6.3), ("154842", 7.1, 11.1), ("154842", 11.4, 15.3), ("154842", 18.2, 20.9), ("154842", 21.3, 26.1),
            ("154842", 26.45, 32.05), ("154842", 34.7, 38.95), ("154842", 39.2, 46.2), ("154842", 49.95, 52.6), ("154842", 52.9, 56.1),
            ("154842", 56.2, 61.8), ("154842", 62.1, 67.4), ("154842", 67.9, 72.8), ("154842", 73.1, 79.5), ("154842", 79.9, 84.8),
            ("154842", 84.85, 88.0), ("154842", 91.1, 92.3), ("154842", 92.5, 98.5), ("154842", 98.7, 100.75), ("154842", 101.1, 105.3),
            ("154842", 109.9, 110.4)],
    broll=[("154842", 22.5, 1.3, "img", "p_899b.webp"), ("154842", 47.0, 1.3, "img", "s_pdf_165330.jpg"),
           ("154842", 75.2, 1.6, "img", "p_my820le.jpeg"), ("154842", 95.5, 1.3, "img", "p_ca93.webp")],
    giant=[("154842", 3.3, 4.5, "JUAL?"), ("154842", 70.6, 72.4, "RM10-20")],
    wide=[("154842", 49.95, 52.6)],
    cards=[("Saya dah guna sendiri", "154842", 26.6, 38.9, [("BP set · lebih 2 tahun", "ok", "154842", 28.92), ("Glucometer · lebih 2 tahun", "ok", "154842", 31.58),
                                                             ("3-in-1 · lebih 1 tahun", "ok", "154842", 38.54)]),
           ("Dalam set 3-in-1", "154842", 77.6, 88.0, [("Uric acid · 10 pieces", "info", "154842", 78.88), ("Total kolesterol · 5 pieces", "info", "154842", 81.92),
                                                       ("Gula · 25 pieces", "info", "154842", 84.04)])],
)
V["v5"] = dict(
    title="Macam mana nak tahu ada darah tinggi?",
    ranges=[("154425", 0.3, 2.2), ("154425", 4.35, 6.4), ("154425", 7.0, 10.4), ("154425", 10.85, 12.6), ("154425", 15.95, 25.3),
            ("154425", 25.35, 27.3), ("154425", 27.7, 32.4), ("154425", 33.35, 33.8), ("154425", 37.2, 40.1), ("154425", 42.9, 49.7),
            ("154425", 50.45, 54.6), ("154425", 54.75, 67.6), ("154425", 68.7, 80.3), ("154425", 80.4, 89.3), ("154425", 89.5, 97.4),
            ("154425", 97.9, 98.3), ("154425", 102.45, 103.9), ("154425", 104.2, 110.6), ("154207", 48.3, 53.3)],
    broll=[("154425", 8.8, 1.2, "clip", "VID_20261109_160054.mp4@10"), ("154425", 44.4, 1.2, "img", "s_shop_080741.jpg"),
           ("154425", 46.3, 1.2, "img", "s_shop_080821.jpg"), ("154425", 48.4, 1.2, "img", "s_shop_080736.jpg"),
           ("154425", 85.0, 1.4, "clip", "VID_20261109_160054.mp4@26")],
    giant=[("154207", 49.8, 51.0, "PENYAKIT")],
    wide=[("154425", 42.9, 49.7)],
    cards=[("Soalan saya balik", "154425", 16.0, 25.3, [("Tekanan darah?", "info", "154425", 16.41), ("Bacaan glukos?", "info", "154425", 20.43),
                                                        ("Uric acid?", "info", "154425", 22.69), ("Total kolesterol?", "info", "154425", 24.53)]),
           ("Contoh bacaan", "154425", 55.5, 80.2, [("Gula lepas makan: 11", "info", "154425", 57.47), ("Gula bangun tidur: 12", "info", "154425", 62.01),
                                                    ("BP di rumah: 150/100", "up", "154425", 70.17), ("Sebelum tidur: 110/80", "info", "154425", 74.87)])],
)
KEYWORDS = ["darah tinggi", "tekanan darah", "kencing manis", "uric acid", "total kolesterol", "kolesterol", "gula", "glukos",
            "glukometer", "gout", "buah pinggang", "jantung", "MDA", "approved", "approval", "medical device authority",
            "rumah", "klinik", "doktor", "nurse", "hospital", "takut", "stabil", "dipercayai", "catat", "bacaan", "beg kuning",
            "promosi", "harga", "murah", "mahal", "berbaloi", "jimat", "kombo", "combo", "3-in-1", "3 in 1", "BP set",
            "hitam", "putih", "warna", "color", "sama", "identikal", "percaya", "support", "RM10", "RM20", "pieces", "tahun",
            "normal", "tinggi", "penyakit", "sendiri", "Sinocare", "Dr Beat", "manual", "bateri", "cuff", "lab", "konsisten",
            "tak lari", "mesra pocket", "pilihan", "keluarga", "luar", "simptom", "ujian", "11.11", "150", "100", "110", "80",
            "11", "12", "2 tahun", "1 tahun", "10", "5", "25", "poin", "pertama", "kedua", "bayangan", "check up", "checkup"]
FIX = {"kula": "gula", "risak": "result", "glukus": "glukos", "toto": "total", "kolesrol": "kolesterol", "komburkan": "kombokan",
       "cekup": "checkup", "khaled": "Khalid", "berya": "beria", "beats": "Beat", "terteri": "tertera", "hadakan": "adakan",
       "kaff": "cuff", "kerap": "kena", "bag": "beg", "dia orang": "diorang"}
