# Progress

Log of work on this project. Newest entries at the top. One entry per unit of work.

Entry header: `tanggal - time - title`, followed by commit, deskripsi, catatan, hasil, temuan, and file yang diubah.

## 2026-11-26 - 00:55 - Charts for the coverage, language, and cross-check cells

- **Commit:** _pending_
- **Deskripsi:** Menambahkan grafik pada tiga sel yang belum punya: sel ringkasan korpus (bar cakupan abstrak: total topik vs berabstrak vs korpus), sel Language (bar bahasa korpus), dan sel API cross-check (bar rasio cakupan 64,0% dan 31,2%, plus bar horizontal 10 bahasa teratas topic-wide). Helper `openalex()` dipindah dari sel cross-check ke sel setup agar sel ringkasan bisa memanggil API lebih dulu; variabel `total`, `with_abs`, dan `corpus` dihitung sekali di sel ringkasan lewat `corpus = len(df)` dan dipakai ulang di sel cross-check, sehingga tidak ada kueri ganda. Impor `FILTER` dihapus karena tidak lagi terpakai. Empat PNG baru: `abstract_coverage.png`, `language_corpus.png`, `coverage_rates.png`, `language_topic_wide.png`.
- **Catatan:** Bar cakupan korpus di sel 2 dan tabel cross-check di sel 12 memakai angka yang sama, jadi grafiknya dibedakan: sel 2 menampilkan jumlah absolut, sel 12 menampilkan rasio. Sel 8 hanya berisi satu batang (`en`) karena filter `language:en`; judulnya diberi keterangan filter agar tidak terlihat rusak. Konsekuensinya sel 2 kini melakukan dua panggilan API, jadi sel itu gagal bila API tidak terjangkau. Output notebook dikosongkan lagi.
- **Hasil:** Semua 7 code cell lolos compile, JSON valid, 0 output tersisa, tidak ada lagi referensi `FILTER`/`urlopen`/`Agg`/`plt.close`. Logika kueri diuji langsung ke `api.openalex.org` dengan urutan sel 2 lalu sel 12: total 75.472, berabstrak 48.320, korpus 15.077, rasio 64,0% dan 31,2%; 60 grup bahasa (English 37.490, 77,6%), 57 grup tahun.
- **Temuan:** `FILTER` menjadi yatim setelah `corpus = len(df)` menggantikan kueri `openalex(FILTER)`, jadi impornya dibuang. Notebook tetap tidak dapat dieksekusi di container ini (pandas/matplotlib tidak terpasang, `.venv` rusak), sehingga keempat PNG baru belum ada dan pemanggilan plot serta render inline belum diuji secara nyata; PNG lama di `report/figures/` belum tersentuh.
- **File yang diubah:** `eval/eda.ipynb`, `docs/PROGRESS.md`

## 2026-11-26 - 00:12 - Fix SSL certificate error under uv Python and render charts inline

- **Commit:** 95d061c fix(eda): fix TLS verification under uv Python, render charts inline
- **Deskripsi:** Memperbaiki `CERTIFICATE_VERIFY_FAILED` pada sel cross-check API dan menampilkan grafik inline di notebook. `ingest/fetch_openalex.py` sekarang membangun `SSL_CONTEXT` dari `certifi` (fallback ke context default bila `certifi` tidak ada) dan memakainya di `get()`. Notebook membuang helper `urlopen` sendiri dan memanggil `get()` bersama sehingga konteks SSL hanya didefinisikan sekali; `matplotlib.use("Agg")` dan `plt.close(fig)` dihapus agar grafik tampil inline setelah tabel teks. `certifi` ditambahkan sebagai dependensi eksplisit di `pyproject.toml` (di-relock). Output notebook dikosongkan, `.gitignore` mendapat `.ipynb_checkpoints/`, dan tiga PNG di `report/figures/` di-commit.
- **Catatan:** Penyebabnya bukan kode notebook: uv mengunduh CPython `python-build-standalone` (`~/.local/share/uv/python/cpython-3.12.13-...`) yang tidak membawa CA bundle, sedangkan Python sistem di container ini lolos verifikasi. `certifi` memang sudah ada di lock sebagai dependensi transitif jupyter, tetapi urllib tidak otomatis memakainya, jadi harus dideklarasikan dan dipakai eksplisit. Notebook tidak dapat dieksekusi di container ini (`.venv` rusak menunjuk interpreter container lain, dependensi belum dipasang), sehingga render inline belum diuji secara nyata.
- **Hasil:** `uv lock --check` lolos (109 paket, `certifi` kini dependensi top-level). Kedua cabang SSL diuji langsung ke `api.openalex.org`: path fallback (Python sistem, 148 CA) dan path certifi (disimulasikan dengan modul `certifi` yang menunjuk bundle CA), keduanya berhasil. Logika sel API diuji dengan `get()` bersama: total 75.472, berabstrak 48.320 (64,0%), korpus 15.077, 60 grup bahasa, 57 grup tahun. Semua 7 code cell notebook lolos compile, JSON valid, 0 output tersisa, tidak ada lagi referensi `Agg`/`plt.close`/`urlopen`.
- **Temuan:** Python hasil unduhan uv perlu CA bundle sendiri; ini juga akan menyerang `uv run python ingest/fetch_openalex.py`, jadi perbaikannya diletakkan di helper bersama, bukan di notebook. `matplotlib.use("Agg")` ternyata mematikan tampilan inline, bukan hanya memilih backend tanpa layar: grafik tidak pernah muncul dan tidak ada output `image/png` di notebook hasil eksekusi.
- **File yang diubah:** `ingest/fetch_openalex.py`, `eval/eda.ipynb`, `pyproject.toml`, `uv.lock`, `.gitignore`, `report/figures/*.png`, `docs/PROGRESS.md`

## 2026-11-25 - 23:50 - uv project initialization replaces requirements.txt

- **Commit:** f1b8ed2 chore(uv): initialize uv project, replacing requirements.txt
- **Deskripsi:** Menambahkan proyek uv: `.python-version` (3.12), `pyproject.toml` (deps `jupyter`, `matplotlib`, `pandas`), `uv.lock`, dan `README.md`; menghapus `requirements.txt`. `pyproject.toml` dijadikan aplikasi non-package (tanpa `[project.scripts]` dan `[build-system]`) karena skeleton `src/project` sudah dihapus dan kode berada di `ingest/` dan `eval/`.
- **Catatan:** `uv.lock` di-relock setelah build-system dihapus. `.venv` lama menunjuk interpreter yang tidak ada (sisa container lain); uv mengabaikannya dan akan membuat ulang saat `uv sync`.
- **Hasil:** `uv lock --check` lolos; `uv sync --dry-run` me-resolve 109 paket tanpa error. `uv build` sebelumnya gagal (README tidak ada dan nama module tidak cocok), sehingga README ditambahkan.
- **Temuan:** `pyproject.toml` hasil generate tidak dapat di-build: `readme = "README.md"` menunjuk berkas yang tidak ada, dan `uv_build` mencari module `src/open_source_software_innovation_hybrid_rag/` padahal skeleton bernama `src/project/` (lalu dihapus). uv 0.13.9.
- **File yang diubah:** `pyproject.toml`, `uv.lock`, `.python-version`, `README.md`, `docs/PROGRESS.md`; dihapus `requirements.txt`

## 2026-11-25 - 23:41 - Tahap 2 P1: EDA notebook (eval/eda.ipynb)

- **Commit:** 545369a feat(eda): add exploratory data analysis notebook
- **Deskripsi:** Menambahkan `eval/eda.ipynb` (EDA korpus: distribusi tahun, primary topic dan keyword, bahasa, panjang abstrak, persentase karya berabstrak, plus cross-check API topic-wide) dan `requirements.txt` (`jupyter`, `pandas`, `matplotlib`). Notebook mengekspor CSV ke `data/eda/` (gitignored) dan PNG ke `report/figures/`.
- **Catatan:** Requirements-only: dependensi belum diinstal di lingkungan ini, jadi notebook belum dieksekusi di sini. Verifikasi terbatas pada JSON notebook valid, semua code cell lolos compile, dan logika API diuji langsung. Jalankan `pip install -r requirements.txt` lalu `jupyter nbconvert --execute eval/eda.ipynb`.
- **Hasil:** Notebook EDA siap dijalankan; metrik korpus diverifikasi via stdlib: 15.077 karya, 100% berabstrak, tahun 1866-2027 (median 2016), 427 primary topic, panjang abstrak rata-rata 156 kata (median 146, p10 35, p90 257, min 1, max 4027).
- **Temuan:** Cross-check API: T11675 total 75.472 karya; 48.320 berabstrak (64,0%); korpus (article+en+abstrak) 15.077 = 31,2% dari yang berabstrak. Topic-wide bahasa Inggris hanya 77,6% (Spanyol 2.748, Prancis 1.993, dari 60 bahasa), jadi filter `language:en` membuang banyak karya. Outlier: tahun 1866 dan 2027, abstrak 1 kata dan 4.027 kata.
- **File yang diubah:** `eval/eda.ipynb`, `requirements.txt`, `docs/PROGRESS.md`

## 2026-11-25 - 23:13 - Add research question and stakeholder question docs

- **Commit:** d499896 docs(eval): add research questions and stakeholder question set
- **Deskripsi:** Menambahkan `docs/Research Question.md` (pertanyaan per rumusan masalah, per eksperimen 1-7, desain/metodologi, validitas, reproduksibilitas, dan tanya-jawab dosen) dan `docs/Stakeholder Question.md` (kandidat pertanyaan pengguna untuk golden set, berlabel [SH]/[MH]/[AGG], dibagi A-H termasuk uji penolakan).
- **Catatan:** Kedua dokumen bersifat rencana/evaluasi; belum ada kode. `Stakeholder Question.md` langsung menyuplai kandidat golden set untuk Tahap 2 (P3).
- **Hasil:** Daftar pertanyaan penelitian dan kandidat golden set terdokumentasi di repo.
- **Temuan:** Target golden set final 50 soal (25 single-hop + 25 multi-hop) plus 2-3 soal penolakan; soal agregasi [AGG] dipakai untuk demo/kualitatif, bukan Recall@K.
- **File yang diubah:** `docs/Research Question.md`, `docs/Stakeholder Question.md`, `docs/PROGRESS.md`

## 2026-11-25 - 22:44 - Tahap 1 P1: OpenAlex ingest, raw data, VERSIONS.md

- **Commit:** b215a2b feat(ingest): fetch OpenAlex corpus with cursor paging and abstract reconstruction
- **Deskripsi:** Menambahkan `ingest/fetch_openalex.py` (cursor paging, api key dari `.env`, retry/backoff, rekonstruksi `abstract_inverted_index`), `.gitignore` (menyamarkan `.env` dan `data/`), `.env.example`, dan `VERSIONS.md`. Menjalankan ingest penuh: 15.077 karya ke `data/raw/openalex_works.jsonl`.
- **Catatan:** Filter korpus `topics.id:T11675,has_abstract:true,type:article,language:en`; T11675 = "Open Source Software Innovations" (terverifikasi). Api key dibaca dari `.env` (`OPEN_ALEX_API_KEY`). Tidak ada resume: rerun menimpa, cukup untuk ~76 request.
- **Hasil:** Data mentah tersimpan sebagai JSONL; tiap baris = record OpenAlex utuh + field `abstract` hasil rekonstruksi. Jumlah total karya tercatat: 15.077 (== `meta.count`). File 245 MB, masuk `.gitignore`.
- **Temuan:** Sebagian record (2/400 saat smoke test) punya `abstract_inverted_index` dengan celah posisi (satu token tak terindeks); rekonstruksi sort-and-join tetap kanonik dan lolos cek jumlah token == jumlah posisi terindeks. Record utuh besar (~16 KB/karya). OpenAlex kini memakai budget harian per-IP bila tanpa key, diperbesar lewat API key.
- **File yang diubah:** `ingest/fetch_openalex.py`, `.gitignore`, `.env.example`, `VERSIONS.md`, `docs/PROGRESS.md` (data mentah `data/raw/openalex_works.jsonl` tidak dikomit)

## 2026-11-25 - 15:26 - Add project definition and task checklist docs

- **Commit:** 8eec098 docs(project): add project definition and task checklist
- **Deskripsi:** Menambahkan dua dokumen perencanaan. `docs/Project Definition.md` memuat rumusan masalah, arsitektur GraphRAG hybrid (OpenAlex -> Neo4j + Qdrant), desain graf dua lapis, golden set evaluasi, tujuh eksperimen, dan risiko. `docs/Task and Stage Checklist.md` memuat checklist per tahap dan per orang (14 hari, peran P1/P2/P3).
- **Catatan:** Kedua dokumen sudah distage sebelum commit ini; isinya rencana, belum ada kode. Ikuti aturan di `AGENTS.md` (think-first, surgical, goal-driven, ponytail full).
- **Hasil:** Rencana proyek dan pembagian tugas terdokumentasi di repo.
- **Temuan:** Proyek adalah GraphRAG hybrid untuk literatur inovasi perangkat lunak open source dari OpenAlex; stack Neo4j (graf) + Qdrant (vektor, payload `work_id`), embedding `bge-m3`.
- **File yang diubah:** `docs/Project Definition.md`, `docs/Task and Stage Checklist.md`, `docs/PROGRESS.md`

## 2026-11-25 - 15:13 - Bootstrap conventions and ponytail submodule

- **Commit:** ab246c4 chore(repo): bootstrap conventions, ponytail submodule, progress log
- **Deskripsi:** Menyiapkan konvensi kerja proyek: `AGENTS.md` (think-first, goal-driven, surgical changes, komentar, format commit, log progress), `docs/PROGRESS.md`, dan skill ponytail sebagai submodule.
- **Catatan:** Ponytail tidak di-inline; dipasang sebagai submodule `./.skills/ponytail` dan dimuat lewat `opencode.json` (`skills: ["./.skills/ponytail/skills"]`). Submodule dikloning shallow (`--depth 1`) karena repo besar.
- **Hasil:** Repo memiliki aturan kerja yang berlaku lintas sesi, skill ponytail tersedia, dan progress log mulai dicatat.
- **Temuan:** Config V2 OpenCode memakai key `skills` berupa array berisi direktori skill; `AGENTS.md` dimuat otomatis.
- **File yang diubah:** `AGENTS.md`, `opencode.json`, `.gitmodules`, `.skills/ponytail` (submodule), `docs/PROGRESS.md`
