#!/usr/bin/env python3
"""Embed OpenAlex works into vectors with a sentence-transformers model.

The embedded text is the title, a newline, then the reconstructed abstract
(see work_text). Vectors are written one chunk file per --chunk works, so an
interrupted run resumes at chunk granularity instead of starting over. A
chunk counts as done only once its .ids.jsonl exists; the vectors and the ids
are written together at the end of the chunk, so a crash cannot leave a chunk
that looks complete but is not. run.json pins the model configuration and
refuses to mix vectors of two models in one output directory.

Torch, numpy and pandas are imported inside functions: --help and --dry-run
must work on a machine that does not have the ML stack installed.
"""
import argparse
import json
import sys
import time
from pathlib import Path

DEFAULT_MODEL = "BAAI/bge-m3"
DEFAULT_IN = "data/raw/openalex_works.jsonl"
DEFAULT_OUT = "data/embeddings/bge-m3"
DEFAULT_BATCH = 16
DEFAULT_CHUNK = 1024
DEFAULT_MAX_SEQ = 512


def work_text(work):
    title = (work.get("title") or work.get("display_name") or "").strip()
    abstract = (work.get("abstract") or "").strip()
    return f"{title}\n{abstract}" if title else abstract


def iter_texts(path, limit=0):
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if limit and i >= limit:
                break
            work = json.loads(line)
            yield work.get("id"), work_text(work)


def count_works(path, limit=0):
    with open(path, "rb") as fh:
        n = sum(1 for line in fh if line.strip())
    return min(n, limit) if limit else n


def chunk_bounds(n_works, chunk):
    """(index, start, stop) for every chunk, covering all works exactly once."""
    assert chunk > 0, "chunk must be positive"
    bounds = [(i, i * chunk, min((i + 1) * chunk, n_works)) for i in range(-(-n_works // chunk))]
    assert sum(stop - start for _, start, stop in bounds) == n_works, "chunks must cover every work"
    return bounds


def chunk_paths(out_dir, index):
    base = Path(out_dir) / f"chunk_{index:04d}"
    return base.with_suffix(".npy"), base.with_suffix(".ids.jsonl")


def chunk_done(out_dir, index, expected):
    npy, ids = chunk_paths(out_dir, index)
    if not (npy.exists() and ids.exists()):
        return False
    with open(ids, encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip()) == expected


def save_chunk(out_dir, index, vectors, ids):
    import numpy as np

    npy, ids_path = chunk_paths(out_dir, index)
    np.save(npy, vectors)
    with open(ids_path, "w", encoding="utf-8") as fh:
        for work_id in ids:
            fh.write(json.dumps(work_id) + "\n")


def resolve_device(requested="auto"):
    if requested != "auto":
        return requested
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def load_model(name, device, max_seq):
    """Load the sentence-transformer; fp16 on CUDA to fit a small VRAM budget."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(name, device=device)
    model.max_seq_length = max_seq
    if device.startswith("cuda"):
        model.half()
    return model


def model_revision(model):
    """HF snapshot hash, when the weights came from a hub cache snapshot."""
    path = str(getattr(model.tokenizer, "name_or_path", ""))
    return path.split("snapshots/")[-1].split("/")[0] if "snapshots/" in path else None


def encode(model, texts, batch, device):
    """Encode texts, halving the batch on CUDA OOM. Returns (vectors, batch used)."""
    import numpy as np

    while True:
        try:
            vectors = model.encode(
                texts, batch_size=batch, convert_to_numpy=True,
                normalize_embeddings=False, show_progress_bar=False,
            )
            return vectors.astype(np.float32), batch
        except RuntimeError as err:
            if batch == 1 or "out of memory" not in str(err).lower():
                raise
            batch = max(1, batch // 2)
            print(f"\nCUDA OOM, retrying with batch_size={batch}", file=sys.stderr)
            if device.startswith("cuda"):
                import torch

                torch.cuda.empty_cache()


def combine(out_dir, n_works, args, bounds, extra):
    """Join the chunks into embeddings.npy + work_ids.jsonl + meta.json."""
    import numpy as np

    out_dir = Path(out_dir)
    expected = {i: stop - start for i, start, stop in bounds}
    done = sum(1 for i, size in expected.items() if chunk_done(out_dir, i, size))
    if done != len(bounds):
        return {**extra, "chunks_done": done, "chunks": len(bounds), "combined": False}

    vectors = np.concatenate([np.load(chunk_paths(out_dir, i)[0]) for i in expected])
    ids = [json.loads(line) for i in expected
           for line in open(chunk_paths(out_dir, i)[1], encoding="utf-8") if line.strip()]
    if len(vectors) != n_works or len(ids) != n_works:
        raise SystemExit(f"row mismatch: {len(vectors)} vectors, {len(ids)} ids, expected {n_works}")
    if not np.isfinite(vectors).all():
        print("warning: embeddings contain non-finite values", file=sys.stderr)

    np.save(out_dir / "embeddings.npy", vectors)
    with open(out_dir / "work_ids.jsonl", "w", encoding="utf-8") as fh:
        for work_id in ids:
            fh.write(json.dumps(work_id) + "\n")
    meta = {
        "model": args.model, "dim": int(vectors.shape[1]), "works": n_works,
        "dtype": str(vectors.dtype), "max_seq": args.max_seq, "chunk": args.chunk,
        "text_template": "title + newline + abstract", **extra,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    for npy, ids_path in (chunk_paths(out_dir, i) for i in expected):
        npy.unlink()
        ids_path.unlink()
    return {**extra, "dim": meta["dim"], "combined": True, "chunks_done": done, "chunks": len(bounds)}


def run(args):
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    n_works = count_works(args.inp, args.limit)
    bounds = chunk_bounds(n_works, args.chunk)
    expected = {i: stop - start for i, start, stop in bounds}
    stops = {i: stop for i, _, stop in bounds}
    config = {"model": args.model, "chunk": args.chunk, "max_seq": args.max_seq, "input": str(args.inp)}
    run_file = out_dir / "run.json"
    meta_file = out_dir / "meta.json"

    if args.dry_run:
        done = [i for i, size in expected.items() if chunk_done(out_dir, i, size)]
        return {
            "works": n_works, "chunks": len(bounds), "works_per_chunk": args.chunk,
            "done": done, "missing": [i for i in expected if i not in done],
            "run_json": json.loads(run_file.read_text()) if run_file.exists() else None,
            "meta": json.loads(meta_file.read_text()) if meta_file.exists() else None,
            "sample_text": next((t for _, t in iter_texts(args.inp, 1)), ""),
        }

    if meta_file.exists() and not args.force:
        meta = json.loads(meta_file.read_text())
        if meta.get("works") == n_works and meta.get("model") == args.model and meta.get("chunk") == args.chunk:
            return {**meta, "already_combined": True}

    if run_file.exists() and json.loads(run_file.read_text()) != config and not args.force:
        raise SystemExit(f"{run_file} holds {json.loads(run_file.read_text())}; pass --force or another --out-dir")
    run_file.write_text(json.dumps(config, indent=2) + "\n")

    missing = {i for i, size in expected.items() if args.force or not chunk_done(out_dir, i, size)}
    if not missing:
        return combine(out_dir, n_works, args, bounds, {})

    import numpy as np
    import torch
    import sentence_transformers

    device = resolve_device(args.device)
    model = load_model(args.model, device, args.max_seq)
    todo = sum(expected[i] for i in missing)
    print(f"device={device} dim={model.get_sentence_embedding_dimension()} batch={args.batch} "
          f"chunks={len(missing)}/{len(bounds)} works={todo}", file=sys.stderr)

    started = time.time()
    batch_used = args.batch
    written = 0
    current = None
    chunk_vectors, chunk_ids, buffer = [], [], []
    for pos, (work_id, text) in enumerate(iter_texts(args.inp, args.limit)):
        index = pos // args.chunk
        if index not in missing:
            continue
        if index != current:
            current = index
            chunk_vectors, chunk_ids, buffer = [], [], []
        buffer.append(text)
        chunk_ids.append(work_id)
        last_of_chunk = pos == stops[index] - 1
        if len(buffer) < args.batch and not last_of_chunk:
            continue
        encoded, batch_used = encode(model, buffer, batch_used, device)
        chunk_vectors.append(encoded)
        buffer = []
        written += len(encoded)
        rate = written / max(time.time() - started, 1e-9)
        if last_of_chunk:
            save_chunk(out_dir, index, np.concatenate(chunk_vectors), chunk_ids)
            chunk_vectors, chunk_ids = [], []
            print(f"\rchunk {index + 1}/{len(bounds)} saved  {written}/{todo} works  {rate:.1f} works/s",
                  file=sys.stderr)
        else:
            print(f"\rwrote {written}/{todo}  {rate:.1f} works/s", end="", file=sys.stderr)

    extra = {
        "device": device, "batch_requested": args.batch, "batch_used": batch_used,
        "revision": model_revision(model), "torch": torch.__version__,
        "sentence_transformers": sentence_transformers.__version__,
        "seconds": round(time.time() - started, 1),
    }
    return combine(out_dir, n_works, args, bounds, extra)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="inp", default=DEFAULT_IN, help="input JSONL of OpenAlex works")
    parser.add_argument("--out-dir", default=DEFAULT_OUT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH, help="encode batch size (halved on CUDA OOM)")
    parser.add_argument("--chunk", type=int, default=DEFAULT_CHUNK, help="works per chunk file")
    parser.add_argument("--max-seq", type=int, default=DEFAULT_MAX_SEQ, help="token truncation length")
    parser.add_argument("--device", default="auto", help="auto | cpu | cuda")
    parser.add_argument("--limit", type=int, default=0, help="embed only the first N works")
    parser.add_argument("--force", action="store_true", help="ignore existing chunks and a mismatched run.json")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit, without torch")
    args = parser.parse_args()
    started = time.time()
    result = run(args)
    result["seconds"] = result.get("seconds", round(time.time() - started, 1))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
