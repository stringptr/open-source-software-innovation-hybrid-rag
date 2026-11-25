# Progress

Log of work on this project. Newest entries at the top. One entry per unit of work.

Entry header: `tanggal - time - title`, followed by commit, deskripsi, catatan, hasil, temuan, and file yang diubah.

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
