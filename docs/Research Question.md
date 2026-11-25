# Pertanyaan Relevan yang Dijawab Project Ini

Pertanyaan disusun berlapis: dari rumusan masalah resmi, turun ke pertanyaan penelitian per eksperimen, lalu pertanyaan teknis dan pertanyaan yang kemungkinan muncul saat tanya-jawab individu.

---

## A. Rumusan Masalah (dari draf judul)

1. Bagaimana merancang graf pengetahuan dari data OpenAlex dan menghubungkannya dengan vector database?
2. Apakah retrieval Graph atau Hybrid lebih baik dari Vector-only (Recall@K, MRR)?
3. Bagaimana pengaruh jenis pertanyaan (single-hop vs multi-hop) terhadap akurasi jawaban?
4. Bagaimana latency dan storage berubah seiring pertumbuhan graf dan kedalaman traversal?
5. Seberapa akurat ekstraksi entitas/relasi, dan bagaimana kualitas jawaban generatifnya (RAGAS)?

---

## B. Pertanyaan Penelitian per Eksperimen

**Eksperimen 1: Vector vs Graph vs Hybrid** (P1, P3)

- Mode mana yang punya Recall@3/5/10 dan MRR tertinggi pada golden set?
- Apakah selisih antar mode cukup besar untuk dianggap bermakna, atau hanya noise dari 50 soal?
- Pada K berapa keunggulan Hybrid mulai hilang atau justru membesar?
- Jika Hybrid tidak lebih baik dari Vector-only, apa penyebabnya (kualitas graf, kualitas seed, atau jenis soal)?

**Eksperimen 2: Single-hop vs multi-hop** (P3)

- Apakah keunggulan Graph/Hybrid muncul terutama pada soal multi-hop?
- Seberapa besar penurunan akurasi Vector-only dari single-hop ke multi-hop?
- Pada soal multi-hop mana setiap mode gagal, dan apa pola kegagalannya?

**Eksperimen 3: Graph traversal** (P2)

- Bagaimana p50 dan p95 latency naik dari 1 ke 2 ke 3 hop?
- Pada kedalaman berapa pertumbuhan jumlah node yang dikunjungi (fan-out) membuat latency tidak praktis?
- Apakah node dengan derajat tinggi (hub, misalnya jurnal atau topik populer) mendominasi latency?
- Apakah kedalaman tambahan masih menambah konteks relevan, atau hanya menambah noise?

**Eksperimen 4: Integrasi graph + vektor** (P1)

- Berapa total latency end-to-end retrieval Hybrid?
- Komponen mana yang paling dominan: embed query, vector search, expand graf, atau perakitan konteks?
- Berapa overhead Hybrid dibanding Vector-only, dan sepadankah dengan peningkatan kualitasnya?

**Eksperimen 5: Pertumbuhan node dan edge** (P2)

- Bagaimana latency dan ukuran storage berubah pada 10%, 25%, 50%, 100% data?
- Pertumbuhannya mendekati linear, atau ada titik patah (misalnya saat data tidak lagi muat di page cache)?
- Berapa kontribusi storage Neo4j dibanding Qdrant?

**Eksperimen 6: Ekstraksi entitas/relasi** (P3)

- Berapa precision dan recall ekstraksi `Software`, `License`, `Organization`, `Concept`?
- Tipe relasi mana (`MIGRATED_FROM/TO`, `USES`, `LICENSED_UNDER`, `STUDIES`) yang paling sulit diekstraksi?
- Seberapa besar normalisasi nama (misalnya "Libre Office" menjadi "LibreOffice") memperbaiki hasil?
- Apakah model 7B kuantisasi 4-bit cukup untuk tugas ini?

**Eksperimen 7: Jawaban generatif (RAGAS)** (P3)

- Mode retrieval mana yang menghasilkan Faithfulness dan Response Relevancy tertinggi?
- Apakah konteks graf tambahan membuat jawaban lebih lengkap, atau justru memicu halusinasi?
- Seberapa andal LLM-judge lokal dibanding pengecekan manual pada sampel?

---

## C. Pertanyaan Desain dan Metodologi

**Data**

- Apakah topik T11675 benar-benar mewakili literatur transisi ke OSS?
- Berapa persen karya memiliki abstrak, dan apakah yang tanpa abstrak bias ke tahun atau bahasa tertentu?
- Apakah pemotongan korpus ke ~14 ribu karya dengan abstrak mengubah kesimpulan?

**Graf**

- Apakah skema dua lapis cukup ekspresif untuk menjawab soal multi-hop di golden set?
- Bagaimana menangani referensi di luar topik (node ID-only) tanpa membuat traversal melebar?
- Bagaimana entity linking dari pertanyaan ke node dilakukan (fulltext, exact match, atau LLM)?

**Vektor**

- Apakah bge-m3 menangani pertanyaan berbahasa Indonesia terhadap abstrak berbahasa Inggris dengan baik?
- Berapa K awal untuk seed node di Hybrid, dan berapa hop yang optimal?

**Golden set**

- Apakah setiap soal multi-hop benar-benar membutuhkan relasi graf dan tidak bisa dijawab satu abstrak saja?
- Seberapa lengkap `relevant_work_ids` (risiko: dokumen relevan yang tidak terlabel dihitung salah)?
- Apakah komposisi 25 single-hop dan 25 multi-hop cukup untuk perbandingan?

**Evaluasi**

- Bagaimana menjamin perbandingan adil (LLM, prompt, dan seed sama di semua mode)?
- Apakah 1 run dengan temperature 0 cukup untuk eksperimen LLM, dan bagaimana mengakuinya sebagai batasan?

---

## D. Pertanyaan Validitas dan Batasan (untuk BAB 3 dan BAB 5)

- Pemotongan skup apa saja yang dilakukan, dan bagaimana dampaknya pada generalisasi hasil?
- Apakah hasil latency dari satu mesin (laptop #3) dapat dibawa ke lingkungan lain?
- Apakah LLM lokal kecil sebagai penilai RAGAS membuat skor bias?
- Apakah ekstraksi pada 1.000-1.500 abstrak cukup mewakili 14 ribu karya?
- Jika Hybrid tidak unggul, apakah itu keterbatasan metode atau keterbatasan data dan skema?

---

## E. Pertanyaan Reproduksibilitas dan Pengiriman

- Apakah `docker compose up` berjalan dari nol di mesin bersih?
- Apakah versi image, model, dan seed tercatat sehingga hasil bisa diulang?
- Apakah README cukup bagi dosen untuk menjalankan sistem tanpa bantuan?

---

## F. Pertanyaan yang Mungkin Diajukan Dosen (tanya-jawab individu)

Setiap anggota harus bisa menjawab semuanya, bukan hanya bagiannya.

1. Mengapa memakai Qdrant dan Neo4j terpisah, bukan vector index bawaan Neo4j?
2. Mengapa `work_id` OpenAlex dipilih sebagai penghubung dua database?
3. Jelaskan alur Hybrid dari pertanyaan sampai jawaban. Apa yang terjadi di tiap langkah?
4. Mengapa Recall@K dan MRR dipilih, dan apa kelemahannya?
5. Bagaimana Anda tahu soal multi-hop benar-benar multi-hop?
6. Mengapa graf dibuat dua lapis, dan apa risiko lapis 2 yang berasal dari LLM?
7. Apa arti p95 latency, dan mengapa dilaporkan selain rata-rata?
8. Mengapa eksperimen latency diulang 5× sedangkan eksperimen LLM hanya 1×?
9. Apa arti Faithfulness dan Response Relevancy di RAGAS, dan apa kelemahan LLM-judge?
10. Apa yang akan Anda ubah jika punya waktu dan sumber daya dua kali lipat?
11. Jika hasilnya Hybrid tidak lebih baik dari Vector-only, apa kesimpulan Anda?
12. Mengapa benchmark tidak boleh berjalan bersamaan dengan ekstraksi LLM?
