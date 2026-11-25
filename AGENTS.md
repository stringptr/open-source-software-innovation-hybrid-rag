# AGENTS.md

Working conventions for agents in this repository.

## Before coding

Think first. State your assumptions. If the request is unclear or has more than one reasonable reading, stop and ask instead of picking one silently. Surface tradeoffs and name a simpler approach when one exists.

## Goal-driven execution

Turn each task into a verifiable goal and loop until it passes ("add validation" becomes "make tests for invalid input pass"). For multi-step work, state the plan as `step → verify` before starting.

## Surgical changes

Touch only what the task needs. Match the surrounding style. Do not refactor, reformat, or "improve" adjacent code, and do not delete pre-existing dead code (mention it instead). Remove only the imports, variables, and functions your own change orphaned.

## Comments

Comment only the why the code cannot show, in one line. Explaining how a non-obvious block works is fine. No decorative separators or banner comments.

## Ponytail

Ponytail, lazy senior dev mode, is active at **full** level on every coding task. The skill is vendored as the `./.skills/ponytail` submodule and loaded through `opencode.json` `skills`.

## Commits

`<type>(scope): <description>`, for example `feat(ingest): ...` or `docs(progress): ...`. The body is required and explains what changed, why, and any notable decisions or side effects.

## Progress log

Record every unit of work in `docs/PROGRESS.md`: header `tanggal - time - title`, then commit, deskripsi, catatan, hasil, temuan, and file yang diubah.
