# open-source-software-innovation-hybrid-rag

Hybrid GraphRAG system for searching and explaining open-source software innovation literature from the OpenAlex dataset (topic `T11675`).

## Setup

```sh
uv sync
```

Creates `.venv` and installs dependencies from `pyproject.toml` / `uv.lock`.

## Ingest

```sh
uv run python ingest/fetch_openalex.py
```

Fetches the corpus to `data/raw/openalex_works.jsonl` (gitignored). Requires `OPEN_ALEX_API_KEY` in `.env` (see `.env.example`).

## Full text

```sh
uv run python ingest/download_fulltext.py --dry-run   # coverage and today's key budget
uv run python ingest/download_fulltext.py             # download what is missing
uv run python ingest/download_fulltext.py --shard 1/3 # one slice per teammate
```

Downloads the cached GROBID TEI XML from OpenAlex's content API for the works that
have it (5,515 of 15,077; `content_urls.grobid_xml`) to `data/fulltext/{work_id}.xml`,
with a `manifest.csv` recording size, extracted characters, status and licence
(gitignored). A work is skipped when its file already exists and looks like TEI, so
reruns, shards and teammates share one directory safely.

Each file costs $0.01 against the key's daily budget, so the script asks `/rate-limit`
how many files each key can still pay for, spends each key to that cap and rotates;
a `daily_budget` 429 retires the key, any other 429 cools it down for `Retry-After`.
Keys come from `OPEN_ALEX_API_KEYS` in `.env` (comma or newline separated) or
`--keys-file`. `ingest/tei_text.py` turns the files into plain text (both TEI shapes,
bibliography dropped); `python ingest/tei_text.py FILE` prints its size and the
no-argument form runs the shape checks.

## EDA

```sh
uv run jupyter nbconvert --execute eval/eda.ipynb
```

Writes CSVs to `data/eda/` (gitignored) and charts to `report/figures/`.

## Embed

```sh
uv run python ingest/embed_bge_m3.py                 # bge-m3 over every abstract
uv run python ingest/embed_bge_m3.py --dry-run       # print the plan, no torch needed
uv run jupyter nbconvert --execute eval/embed.ipynb  # stats and charts for the vectors
```

Embeds `title` + newline + `abstract` with bge-m3 (`--limit N` for a smoke test,
`--batch` halved automatically on CUDA OOM). Vectors are written chunk by chunk,
so an interrupted run resumes instead of restarting; the result is
`data/embeddings/bge-m3/embeddings.npy` plus `work_ids.jsonl` (row order) and
`meta.json` (gitignored, ready for the Qdrant load with payload `work_id`).
