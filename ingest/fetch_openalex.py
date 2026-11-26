#!/usr/bin/env python3
"""Fetch OpenAlex works for topic T11675 into JSONL, reconstructing abstracts.

Each output line is the raw OpenAlex work object plus an added "abstract" field.
"""
import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"
FILTER = "topics.id:T11675,has_abstract:true,type:article,language:en"
MAILTO = os.environ.get("OPENALEX_MAILTO", "satriampp@proton.me")
PER_PAGE = 200

# uv-managed Pythons ship no CA bundle, so verify against certifi when present.
try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


def load_api_key(env_path=".env"):
    key = os.environ.get("OPEN_ALEX_API_KEY")
    if key:
        return key
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            m = re.match(r"\s*OPEN_ALEX_API_KEY\s*=\s*(.*)\s*$", line)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    return ""


def reconstruct_abstract(inverted):
    if not inverted:
        return None
    positions = [(pos, word) for word, pos_list in inverted.items() for pos in pos_list]
    positions.sort()
    return " ".join(word for _, word in positions)


def get(url, params, retries=5):
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"{url}?{query}", headers={"User-Agent": f"openalex-ingest (mailto:{MAILTO})"}
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="stop after N works (0 = all)")
    parser.add_argument("--out", default="data/raw/openalex_works.jsonl")
    parser.add_argument("--filter", default=FILTER)
    args = parser.parse_args()

    api_key = load_api_key()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    # shortcut: no resume; a rerun overwrites and restarts, acceptable while the
    # full corpus is ~76 requests. Add checkpointing if the corpus grows.
    cursor = "*"
    written = 0
    total = None
    with open(args.out, "w", encoding="utf-8") as fh:
        while cursor:
            params = {
                "filter": args.filter,
                "per-page": PER_PAGE,
                "cursor": cursor,
                "mailto": MAILTO,
            }
            if api_key:
                params["api_key"] = api_key
            page = get(API, params)
            if total is None:
                total = page["meta"]["count"]
            for work in page["results"]:
                work["abstract"] = reconstruct_abstract(work.get("abstract_inverted_index"))
                fh.write(json.dumps(work, ensure_ascii=False) + "\n")
                written += 1
                if args.limit and written >= args.limit:
                    break
            cursor = page["meta"].get("next_cursor")
            print(f"\rwritten {written}/{total}", end="", file=sys.stderr)
            if args.limit and written >= args.limit:
                break
    print(file=sys.stderr)
    print(json.dumps({"written": written, "meta_count": total, "out": args.out}))


if __name__ == "__main__":
    main()
