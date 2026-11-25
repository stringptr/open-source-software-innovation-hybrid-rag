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
