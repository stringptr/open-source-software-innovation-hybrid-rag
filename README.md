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
