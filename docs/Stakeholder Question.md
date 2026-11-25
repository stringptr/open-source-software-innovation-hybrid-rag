# Pertanyaan/Task untuk Pengguna RAG (Hasil Project)

Ini adalah pertanyaan yang diajukan **pengguna sistem** (mahasiswa, peneliti, praktisi, pengambil kebijakan) kepada Graph RAG, bukan pertanyaan penelitian. Semuanya bisa jadi bahan **kandidat golden set** (ingat: golden set final 50 soal, 25 single-hop dan 25 multi-hop, dan harus divalidasi manual terhadap data yang benar-benar ada di korpus).

Label: **[SH]** single-hop (cukup satu abstrak/dokumen), **[MH]** multi-hop (butuh relasi graf), **[AGG]** agregasi/eksplorasi. Kolom "Mode yang diuntungkan" adalah hipotesis, bukan kesimpulan.

---

## A. Pemahaman Konsep dan Faktor (umumnya [SH], Vector kuat)

1. Apa faktor-faktor yang memengaruhi adopsi perangkat lunak open source di organisasi publik?
2. Apa hambatan utama migrasi dari perangkat lunak proprietary ke open source?
3. Apa itu vendor lock-in dan bagaimana kaitannya dengan keputusan migrasi ke OSS?
4. Bagaimana total cost of ownership (TCO) OSS dibandingkan perangkat lunak proprietary menurut literatur?
5. Apa peran kebijakan pemerintah dalam mendorong penggunaan OSS?
6. Bagaimana aspek keamanan OSS dibahas dalam literatur (misalnya transparansi kode sumber)?
7. Apa saja tantangan pelatihan dan resistensi pengguna saat migrasi ke OSS?
8. Bagaimana pengaruh lisensi (GPL, MIT, Apache) terhadap keputusan adopsi?

## B. Pencarian Literatur (Vector/Hybrid)

1. Cari paper tentang migrasi sistem perkantoran ke LibreOffice di instansi pemerintah.
2. Paper apa yang membahas adopsi Linux di desktop pemerintah daerah?
3. Carikan studi kasus migrasi OSS di sektor pendidikan.
4. Literatur apa yang membahas OSS di negara berkembang, khususnya Asia Tenggara?
5. Paper mana yang paling relevan untuk topik "kesiapan organisasi mengadopsi OSS"?
6. Bagaimana tren penelitian transisi ke OSS dari tahun ke tahun? [AGG]

## C. Relasi Penulis, Institusi, dan Venue ([MH], Graph/Hybrid diharapkan unggul)

1. Penulis mana yang meneliti migrasi OSS di pemerintahan, dan paper apa yang mereka sitasi?
2. Institusi mana yang paling produktif meneliti adopsi OSS?
3. Siapa saja rekan penulis (co-author) dari peneliti X yang juga meneliti OSS?
4. Jurnal atau venue mana yang paling sering memuat penelitian transisi ke OSS?
5. Peneliti dari institusi Y mempublikasikan paper apa saja tentang OSS, dan di jurnal mana?
6. Penulis mana yang bekerja lintas dua topik, misalnya OSS dan keamanan perangkat lunak?

## D. Relasi Sitasi dan Pengaruh ([MH])

1. Paper mana yang paling banyak disitasi oleh studi-studi migrasi OSS?
2. Paper apa saja yang mengutip paper X, dan apa kesimpulan mereka terhadapnya?
3. Karya fondasional apa yang sering dirujuk bersama oleh paper adopsi OSS di pemerintahan?
4. Dari paper X, telusuri dua tingkat sitasi: paper apa yang dirujuk oleh paper yang dirujuk X?
5. Apakah ada kelompok penelitian yang saling mengutip dalam topik OSS?

## E. Pertanyaan Berbasis Entitas Lapis 2 (hasil ekstraksi LLM, [MH])

1. Perangkat lunak apa saja yang dibahas dalam studi migrasi dari Microsoft Office?
2. Organisasi mana yang bermigrasi dari software proprietary ke Linux, dan studi apa yang melaporkannya?
3. Software OSS apa yang menggunakan lisensi GPL dan dipelajari dalam literatur adopsi?
4. Konsep apa yang paling sering muncul bersama "vendor lock-in" dalam abstrak?
5. Studi mana yang membahas migrasi dari X ke Y, dan faktor apa yang disebutkan?
6. Organisasi mana yang menggunakan LibreOffice menurut literatur?

## F. Tugas Sintesis dan Penjelasan (generatif, dinilai RAGAS)

1. Ringkas temuan utama literatur tentang hambatan adopsi OSS di pemerintahan, sebutkan paper pendukungnya.
2. Bandingkan alasan migrasi ke OSS di sektor pemerintah dan pendidikan.
3. Jelaskan hubungan antara kebijakan pemerintah, vendor lock-in, dan keputusan migrasi, berdasarkan literatur.
4. Apa kesenjangan penelitian (research gap) yang terlihat dari literatur OSS di korpus ini?
5. Buatkan ringkasan literatur (related work) singkat tentang adopsi OSS, lengkap dengan sitasi.
6. Mengapa studi X dan studi Y menyimpulkan hal berbeda tentang biaya OSS?

## G. Pertanyaan Lintas Bahasa (menguji bge-m3)

1. Apa saja penelitian tentang penggunaan OSS di pemerintah Indonesia? (pertanyaan Indonesia, abstrak Inggris)
2. Faktor apa yang membuat organisasi enggan beralih dari perangkat lunak berbayar?
3. Jelaskan dalam bahasa Indonesia hasil studi tentang migrasi ke Linux di sekolah.

## H. Pertanyaan yang Seharusnya Ditolak/Dijawab "Tidak Ada" (uji kejujuran sistem)

1. Berapa harga lisensi Microsoft Office tahun ini? (katalog produk, bukan literatur)
2. Apa fitur terbaru Linux kernel versi terbaru? (di luar korpus)
3. Paper apa tentang migrasi OSS di organisasi yang tidak ada di data? (entitas fiktif)
4. Siapa pemenang pemilu terakhir? (di luar domain)

Sistem yang baik menjawab "tidak ditemukan dalam korpus" dan tidak mengarang (menguji Faithfulness).

---

## Cara Memakai Daftar Ini

- **Pilih 50 soal final:** ambil kurang lebih 25 [SH] dari bagian A, B, F dan 25 [MH] dari C, D, E. Tambahkan 2-3 soal bagian H sebagai uji penolakan (di luar hitungan Recall).
- **Validasi tiap soal:** pastikan ada jawabannya di korpus, isi `relevant_work_ids`, dan tulis jawaban referensi. Buang soal yang tidak punya jawaban di data (misalnya penulis atau software yang ternyata tidak ada).
- **Sesuaikan entitas:** contoh nama (LibreOffice, Linux, GPL) harus diganti dengan entitas yang benar-benar muncul setelah EDA dan ekstraksi lapis 2.
- **Soal multi-hop sejati:** uji dengan pertanyaan "bisakah dijawab dari satu abstrak saja?" Jika ya, itu single-hop.
- **Soal agregasi [AGG]** (14, 16, 18, 21) bagus untuk demo, tetapi sulit dinilai dengan Recall@K karena tidak punya daftar relevan yang pasti. Pakai sebagai demo atau uji kualitatif, bukan metrik utama.
