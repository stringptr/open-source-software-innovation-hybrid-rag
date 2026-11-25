# **Checklist Tugas per Tahap dan per Orang**

Ini mengikuti **Workflow.md** (versi 14 hari, target selesai Selasa 8 Des, buffer Rabu 9 Des). Angka di Workflow \- IN PROGRESS.md (golden set 60-100, ekstraksi 2-5 ribu abstrak, 5× ulang untuk semua eksperimen) sudah digantikan versi 14 hari.

**Peran:** P1 \= Data & Vektor \+ format laporan · P2 \= Graph · P3 \= LLM & Evaluasi

---

## **Tahap 1 · Hari 1-2 (Rab 25 \- Kam 26 Nov): Fondasi**

**P1**

* \[ \] Buat repo Git dan struktur folder (`/ingest`, `/graph`, `/eval`, `/report`, `/docker`)  
* \[ \] Tulis skrip ambil data OpenAlex dengan cursor paging dan rekonstruksi `abstract_inverted_index`  
* \[ \] Simpan data mentah (JSONL) dan catat jumlah total karya  
* \[ \] Buat file `VERSIONS.md` berisi versi image, model, dan seed

✅ **Selesai jika:** data mentah tersimpan, jumlah karya dengan abstrak (\~14 ribu) terkonfirmasi, dan repo bisa di-clone ketiga anggota.

**P2**

* \[ \] Tulis `docker-compose.yml` (Neo4j dengan heap 2-4 GB, Qdrant, profil opsional Ollama)  
* \[ \] Verifikasi **T11675** (topik OpenAlex) cocok dengan tema OSS  
* \[ \] Draf skema graf lapis 1 dan 2 (node, relasi, constraint unik)  
* \[ \] Atur `.wslconfig` (12-14 GB untuk laptop 24GB) bila memakai Windows

✅ **Selesai jika:** `docker compose up` jalan di ≥2 laptop, Neo4j Browser dan Qdrant dashboard terbuka, serta T11675 terverifikasi.

**P3**

* \[ \] Putuskan LLM lokal vs API (jika API, tetapkan budget dan model untuk judge dan generasi)  
* \[ \] Pasang Ollama di host (bukan container) di laptop \#3 dan \#2, samakan versi model 7B Q4  
* \[ \] Tes satu panggilan ekstraksi dan satu jawaban dari model terpilih  
* \[ \] Buat outline laporan (BAB 1-5) dan bagi penulis per bab  
* \[ \] Kumpulkan referensi: ≥5 Sinta 2 \+ 1 buku (bagi tugas bersama; konfirmasi ke dosen apakah Scopus Q1-Q2 diterima)

✅ **Selesai jika:** keputusan LLM tercatat di `VERSIONS.md`, outline disepakati, dan daftar referensi awal ada.

---

## **Tahap 2 · Hari 3-4 (Jum 27 \- Sab 28 Nov): Data dan Graf Lapis 1**

**P1**

* \[ \] EDA: distribusi tahun, topik, bahasa, panjang abstrak, % karya dengan abstrak  
* \[ \] Jalankan embedding bge-m3 pada \~14 ribu abstrak (laptop \#1, batch kecil; jika OOM, turunkan batch atau pakai multilingual-e5-small)  
* \[ \] Muat vektor ke Qdrant dengan payload `work_id`  
* \[ \] Mulai draf BAB 3 (metodologi, termasuk daftar pemotongan skup)

✅ **Selesai jika:** jumlah titik di Qdrant sama dengan jumlah abstrak dan query sampel mengembalikan hasil masuk akal.

**P2**

* \[ \] Tulis skrip loader lapis 1: `Work`, `Author`, `Institution`, `Source`, `Topic`, `Keyword`  
* \[ \] Muat relasi `AUTHORED`, `AFFILIATED_WITH`, `PUBLISHED_IN`, `HAS_TOPIC`, `HAS_KEYWORD`, `CITES` (referensi luar topik sebagai node ID-only)  
* \[ \] Buat index dan constraint, serta fulltext index untuk entity linking  
* \[ \] Mulai draf BAB 2 (teori graph dan GraphRAG)

✅ **Selesai jika:** jumlah node dan edge per tipe tercatat, dan query Cypher `Author → Work → CITES` mengembalikan hasil.

**P3**

* \[ \] Draf golden set 30 soal (15 single-hop, 15 multi-hop) dengan `relevant_work_ids` dan jawaban referensi  
* \[ \] Pastikan soal multi-hop benar-benar butuh relasi graf (`AUTHORED` lalu `CITES`, dan sebagainya)  
* \[ \] Buat template golden set (CSV/JSON) dan skrip hitung Recall@K dan MRR  
* \[ \] Draf BAB 1 (latar belakang, rumusan masalah, tujuan)

✅ **Selesai jika:** 30 soal tervalidasi manual oleh minimal 1 orang lain, dan skrip metrik lolos tes dengan data dummy.

---

## **Tahap 3 · Hari 5-6 (Min 29 \- Sen 30 Nov): Tiga Mode Retrieval \+ Ekstraksi**

**P1**

* \[ \] Implementasi retrieval **Vector-only** (top-K dari Qdrant, kembalikan `work_id`)  
* \[ \] Bungkus dengan antarmuka yang sama seperti mode lain (`retrieve(query, k) → list[work_id]`)  
* \[ \] Siapkan subset 1.000-1.500 abstrak untuk ekstraksi (bersama P3)

✅ **Selesai jika:** Vector-only berjalan pada seluruh draf golden set dan menghasilkan Recall@K awal.

**P2**

* \[ \] Implementasi **Graph-only** (entity linking \+ Cypher/fulltext)  
* \[ \] Implementasi **Hybrid** (vector top-K → seed node → expand 1-2 hop → rakit konteks)  
* \[ \] Buat orchestrator yang memanggil 3 mode lewat satu antarmuka

✅ **Selesai jika:** ketiga mode menjawab pertanyaan yang sama end-to-end tanpa error.

**P3**

* \[ \] Rancang skema relasi tetap lapis 2: `Software`, `License`, `Organization`, `Concept`; relasi `MIGRATED_FROM/TO`, `USES`, `LICENSED_UNDER`, `STUDIES`  
* \[ \] Tulis prompt ekstraksi (output JSON), normalisasi nama (mis. "Libre Office" → "LibreOffice"), temperature 0, seed tetap  
* \[ \] Uji pada 20 abstrak, perbaiki prompt  
* \[ \] **Mulai ekstraksi semalam di laptop \#3** (Sen 30 Nov malam). Tidak ada benchmark yang berjalan bersamaan.

✅ **Selesai jika:** ekstraksi berjalan, ada log progres dan checkpoint hasil per batch. Jika terlalu lambat, turunkan ke 800 abstrak atau pakai API.

---

## **Tahap 4 · Hari 7 (Sel 1 Des): Checkpoint 1**

**Semua**

* \[ \] Demo end-to-end tiga mode di depan semua anggota  
* \[ \] Tinjau golden set bersama dan **bekukan di 50 soal** (25 single-hop, 25 multi-hop)

**P3**

* \[ \] Anotasi manual gold 30-40 abstrak dari subset ekstraksi (untuk eksperimen 6\)  
* \[ \] Pilot eksperimen 1-2 pada golden set final

**P1/P2**

* \[ \] Perbaiki bug yang ditemukan saat demo

✅ **Selesai jika:** golden set final dibekukan (jangan diubah lagi), hasil pilot eksperimen 1-2 ada, dan daftar bug sudah ditutup atau dijadwalkan.

---

## **Tahap 5 · Hari 8-9 (Rab 2 \- Kam 3 Des): Eksperimen 6, 3, 4, 5**

**P3**

* \[ \] Muat hasil ekstraksi lapis 2 ke graf (koordinasi dengan P2 untuk skema)  
* \[ \] **Eksperimen 6:** bandingkan hasil LLM dengan gold manual → precision dan recall (entitas dan relasi)  
* \[ \] Tulis analisis eksperimen 6

**P2** (di laptop \#3, **tanpa LLM berjalan**)

* \[ \] **Eksperimen 3:** latency traversal kedalaman 1, 2, 3 hop (p50, p95; 5× ulang setelah warm-up)  
* \[ \] **Eksperimen 5:** snapshot 10%, 25%, 50%, 100% → latency dan ukuran storage  
* \[ \] Simpan hasil mentah (CSV) per eksperimen

**P1** (di laptop \#3, **tanpa LLM berjalan**)

* \[ \] **Eksperimen 4:** latency end-to-end dengan rincian waktu embed, vector search, expand, dan rakit konteks (5× ulang)  
* \[ \] Eksperimen 1 (sisi vektor) final: Recall@K dan MRR untuk K \= 3/5/10  
* \[ \] Simpan hasil mentah (CSV)

✅ **Selesai jika:** semua CSV hasil eksperimen 1, 3, 4, 5, 6 ada, mean ± std terhitung, dan angka latency/storage berasal dari laptop \#3.

---

## **Tahap 6 · Hari 10 (Jum 4 Des): RAGAS**

**P3**

* \[ \] **Eksperimen 7:** jawab 50 soal dengan 3 mode, nilai RAGAS Faithfulness dan Response Relevancy (1 run, temperature 0, seed tetap), jalankan semalam  
* \[ \] Kalibrasi LLM-judge dengan cek manual pada sampel kecil  
* \[ \] Hitung answer accuracy per jenis soal (eksperimen 2\)

**P1/P2**

* \[ \] Review script dan log run, siapkan cadangan di laptop \#2 jika laptop \#3 bermasalah

✅ **Selesai jika:** run selesai tanpa crash dan **hasil dibekukan Sabtu 5 Des pagi**. Setelah itu tidak ada run ulang.

---

## **Tahap 7 · Hari 11-12 (Sab 5 \- Min 6 Des): Analisis dan Penulisan**

**P1**

* \[ \] Grafik dan tabel eksperimen 1 dan 4  
* \[ \] Tulis BAB 3 final (termasuk batasan skup) dan analisis eksperimen 1, 4  
* \[ \] Siapkan template Word: styles, caption, daftar isi/tabel/gambar otomatis

**P2**

* \[ \] Grafik dan tabel eksperimen 3 dan 5  
* \[ \] Tulis BAB 2 final dan analisis eksperimen 3, 5

**P3**

* \[ \] Grafik dan tabel eksperimen 2, 6, 7  
* \[ \] Tulis BAB 1, BAB 5, dan analisis eksperimen 2, 6, 7

**Semua**

* \[ \] **Saling-uji tanya-jawab 20 menit (hari 12):** tiap orang menjelaskan seluruh pipeline

✅ **Selesai jika:** semua bab dan analisis punya draf lengkap dan setiap anggota bisa menjelaskan pipeline end-to-end tanpa melihat catatan.

---

## **Tahap 8 · Hari 13 (Sen 7 Des): Integrasi Laporan**

**P1**

* \[ \] Gabung semua bab ke satu dokumen, cek styles, caption, nomor halaman, daftar isi/tabel/gambar  
* \[ \] Selesaikan daftar pustaka (≥5 Sinta 2 \+ 1 buku, format konsisten)

**P2/P3**

* \[ \] Baca silang bab milik orang lain, cek konsistensi angka antara tabel, teks, dan CSV  
* \[ \] Cek detektor AI **per bab** (target \<25%); tulis ulang dengan kata sendiri bila perlu

✅ **Selesai jika:** laporan satu file lengkap, semua bab \<25% di detektor AI, dan angka konsisten.

---

## **Tahap 9 · Hari 14 (Sel 8 Des): Pengumpulan**

**P1**

* \[ \] Tes `docker compose up` di mesin bersih (atau clone baru) sesuai README  
* \[ \] Pastikan README memuat langkah menjalankan, versi image, dan seed

**P2**

* \[ \] Rapikan repo, hapus data atau kredensial sensitif, tag rilis akhir

**P3**

* \[ \] Buat slide dan latihan presentasi bersama (semua anggota ikut berbicara)

**Semua**

* \[ \] **Kumpulkan** laporan, repo/konfigurasi Docker, dan slide

✅ **Selesai jika:** compose berjalan dari nol, paket terkirim, dan bukti pengumpulan tersimpan.

---

## **Buffer · Rab 9 Des**

Hanya untuk cadangan jika ada masalah (telat dikenai −5 per hari). **Jangan dijadwalkan untuk pekerjaan.**

---

## **Checklist Lintas Tahap (selalu dicek)**

* \[ \] Versi image, model, dan seed selalu tercatat di `VERSIONS.md`  
* \[ \] Tidak ada ekstraksi LLM bersamaan dengan benchmark di laptop \#3  
* \[ \] Semua pemotongan skup ditulis jujur sebagai batasan di BAB 3  
* \[ \] Laporan ditulis bertahap sejak hari 3, bukan di akhir

Mau saya buatkan ini sebagai dokumen (Word/Doc) atau spreadsheet tracker dengan kolom status, PIC, dan tanggal?

