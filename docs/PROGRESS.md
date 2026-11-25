# Progress

Log of work on this project. Newest entries at the top. One entry per unit of work.

Entry header: `tanggal - time - title`, followed by commit, deskripsi, catatan, hasil, temuan, and file yang diubah.

## 2026-11-25 - 15:13 - Bootstrap conventions and ponytail submodule

- **Commit:** ab246c4 chore(repo): bootstrap conventions, ponytail submodule, progress log
- **Deskripsi:** Menyiapkan konvensi kerja proyek: `AGENTS.md` (think-first, goal-driven, surgical changes, komentar, format commit, log progress), `docs/PROGRESS.md`, dan skill ponytail sebagai submodule.
- **Catatan:** Ponytail tidak di-inline; dipasang sebagai submodule `./.skills/ponytail` dan dimuat lewat `opencode.json` (`skills: ["./.skills/ponytail/skills"]`). Submodule dikloning shallow (`--depth 1`) karena repo besar.
- **Hasil:** Repo memiliki aturan kerja yang berlaku lintas sesi, skill ponytail tersedia, dan progress log mulai dicatat.
- **Temuan:** Config V2 OpenCode memakai key `skills` berupa array berisi direktori skill; `AGENTS.md` dimuat otomatis.
- **File yang diubah:** `AGENTS.md`, `opencode.json`, `.gitmodules`, `.skills/ponytail` (submodule), `docs/PROGRESS.md`
