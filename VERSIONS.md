# VERSIONS

Pin every image, model, and seed here. Update when a decision is final; leave undecided items as TBD with the owner.

## Seed

| Item | Value |
|------|-------|
| Global seed | 42 |

## Data

| Item | Value |
|------|-------|
| Source | OpenAlex API, `https://api.openalex.org/works` |
| Corpus filter | `topics.id:T11675,has_abstract:true,type:article,language:en` |
| Works fetched | 15077 |
| Fetch date | 2026-11-25 |
| Raw file | `data/raw/openalex_works.jsonl` (gitignored) |
| Full text source | OpenAlex content API, `content_urls.grobid_xml` (GROBID TEI XML), $0.01 per file |
| Full text coverage | 5515 of 15077 works (36.6%); the other 9498 have no cached full text |
| Full text cache | `data/fulltext/{work_id}.xml` + `manifest.csv` (gitignored) |

## Services (Docker images)

| Service | Image | Owner |
|---------|-------|-------|
| Neo4j | TBD | P2 |
| Qdrant | TBD | P2 |
| Ollama (optional) | TBD | P3 |

## Models

| Purpose | Model | Owner |
|---------|-------|-------|
| Embedding | bge-m3 (`BAAI/bge-m3`, 1024 dim, fp16 on CUDA, max_seq 512, no query prefix) | P1 |
| LLM extract/generate/judge | TBD | P3 |

Embedding config lives in `data/embeddings/bge-m3/meta.json` after a run: model,
HF revision, dimension, device, batch actually used, and the embedded text
template (`title` + newline + `abstract`). Fallback if bge-m3 does not fit VRAM:
`multilingual-e5-small` (384 dim, needs `query:`/`passage:` prefixes and a new
output directory, since the dimension differs).
