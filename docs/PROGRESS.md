# Progress

Log of work on this project. Newest entries at the top. One entry per unit of work.

Entry header: `tanggal - time - title`, followed by commit, deskripsi, catatan, hasil, temuan, and file yang diubah.

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
