## **1\. Rumusan masalah (draft)**

Judul: **RANCANG BANGUN SISTEM GRAPH RAG UNTUK PENCARIAN DAN PENJELASAN LITERATUR INOVASI PERANGKAT LUNAK OPEN SOURCE DARI DATASET OPENALEX**

1. Bagaimana merancang graf pengetahuan dari data OpenAlex dan menghubungkannya dengan vector database?  
2. Apakah retrieval Graph atau Hybrid lebih baik dari Vector-only (Recall@K, MRR)?  
3. Bagaimana pengaruh jenis pertanyaan (single-hop vs multi-hop) terhadap akurasi jawaban?  
4. Bagaimana latency dan storage berubah seiring pertumbuhan graf dan kedalaman traversal?  
5. Seberapa akurat ekstraksi entitas/relasi, dan bagaimana kualitas jawaban generatifnya (RAGAS)?

## **2\. Arsitektur (Docker Compose, hanya 3–4 container)**

```
OpenAlex API ─► Ingestion (Python) ─► Neo4j  (graf)
                                  └─► Qdrant (vektor, payload: work_id)
Pertanyaan ─► Orchestrator ─┬─ Mode 1: Vector-only
                            ├─ Mode 2: Graph-only (entity linking + Cypher/fulltext)
                            └─ Mode 3: Hybrid (vector top-K → seed node → expand 1–2 hop → LLM)
```

* **Penghubung vektor ↔ graf:** `work_id` OpenAlex dipakai sebagai kunci di kedua sisi, sehingga hasil vektor bisa langsung jadi titik awal traversal.  
* **Alternatif:** Neo4j punya vector index bawaan. Itu lebih sederhana, tapi eksperimen "integrasi graph \+ vektor" jadi kurang bermakna. Saya sarankan Qdrant \+ Neo4j terpisah.  
* **LLM:** satu model untuk ekstraksi entitas, generasi jawaban, dan penilai RAGAS. Bisa Ollama lokal atau API murah. Satu model embedding saja, misalnya `bge-m3`, agar bisa menerima pertanyaan Indonesia.

## **3\. Desain graf (dua lapis)**

**Lapis 1, dari metadata OpenAlex (murah dan pasti benar):**

* Node: `Work`, `Author`, `Institution`, `Source` (jurnal/venue), `Topic`, `Keyword`  
* Relasi: `AUTHORED`, `AFFILIATED_WITH`, `PUBLISHED_IN`, `HAS_TOPIC`, `HAS_KEYWORD`, `CITES`

**Lapis 2, hasil ekstraksi LLM dari abstrak (relevan dengan tema transisi ke OSS):**

* Node: `Software` (Linux, LibreOffice, dst.), `License`, `Organization`, `Concept` (migrasi, vendor lock-in, adopsi)  
* Relasi: `MIGRATED_FROM/TO`, `USES`, `LICENSED_UNDER`, `STUDIES`  
* Lapis ini hanya dijalankan pada **subset 2–5 ribu abstrak** supaya biaya LLM terkendali.

Referensi (`referenced_works`) yang berada di luar topik cukup disimpan sebagai node ID-only. Abstrak direkonstruksi dari `abstract_inverted_index`.

## **4\. Golden set evaluasi (inti kualitas proyek)**

* 60–100 pertanyaan: ±50% single-hop dan ±50% multi-hop.  
* Tiap pertanyaan punya `relevant_work_ids` dan jawaban referensi.  
* Contoh single-hop: "Apa faktor adopsi OSS di organisasi publik?"  
* Contoh multi-hop: "Penulis mana yang meneliti migrasi OSS di pemerintahan, dan paper apa yang mereka sitasi?", yang butuh `AUTHORED` lalu `CITES`.  
* Generate semi-otomatis dengan LLM, lalu **validasi manual**. Pertanyaan harus bisa dijawab dari literatur, bukan dari katalog produk.  
* Tambahan: anotasi manual 50 abstrak sebagai gold untuk eksperimen ekstraksi entitas.

## **5\. Tujuh eksperimen (persis tabel dosen)**

| \# | Eksperimen | Cara | Metrik |
| ----- | ----- | ----- | ----- |
| 1 | Vector vs Graph vs Hybrid | Jalankan golden set di 3 mode, K \= 3/5/10 | Recall@K, MRR |
| 2 | Single-hop vs multi-hop | Pisahkan hasil per jenis pertanyaan dan mode | Answer accuracy |
| 3 | Graph traversal | Kedalaman 1, 2, 3 hop | Query latency (p50, p95) |
| 4 | Integrasi graph \+ vektor | Ukur dari pertanyaan sampai konteks siap, dengan rincian waktu embed, vector search, expand, rakit konteks | End-to-end retrieval latency |
| 5 | Pertumbuhan node dan edge | Snapshot 10%, 25%, 50%, 100% data | Latency, storage size |
| 6 | Ekstraksi entitas/relasi | Bandingkan hasil LLM dengan gold manual | Precision, recall |
| 7 | Jawaban generatif | Jawab golden set dengan tiap mode | RAGAS Faithfulness, Response Relevancy |

Aturan umum: ulang minimal 5 kali setelah warm-up, laporkan mean ± std, kunci seed dan versi image. Untuk Answer accuracy, gunakan LLM-judge yang dikalibrasi dengan pengecekan manual pada sampel.

# **6\. Risiko dan mitigasinya**

* **Graf tanpa nilai tambah:** kalau Hybrid tidak lebih baik dari Vector, itu tetap temuan yang sah. Karena itu golden set multi-hop harus benar-benar membutuhkan relasi.  
* **Kualitas ekstraksi LLM:** terapkan skema relasi yang tetap dan normalisasi nama software (misalnya "Libre Office" dan "LibreOffice" jadi satu node).  
* **Biaya LLM:** batasi ekstraksi ke subset dan RAGAS ke golden set.  
* **Sinta 2 untuk paper internasional:** tanyakan ke dosen apakah Scopus Q1–Q2 diterima sebagai padanan.

## **Yang perlu dikonfirmasi**

1. Deadline dan jumlah anggota?  
2. Spesifikasi laptop (RAM/GPU) dan akses API LLM?  
3. Apakah dosen mengizinkan satu vector DB tetap dipakai sebagai baseline, atau harus ada alasan khusus?

Langkah berikutnya bisa berupa `docker-compose.yml` (Neo4j \+ Qdrant), skema graf Cypher, atau skrip ingest OpenAlex. Mau mulai dari yang mana?
