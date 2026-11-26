#!/usr/bin/env python3
"""Download cached full text (GROBID TEI XML) for the corpus works.

OpenAlex serves a cached TEI parse per work at content_urls.grobid_xml, for 5,515
of our 15,077 works; the other 9,498 have no cached full text at all. Each
download costs $0.01 and is metered against the API key's daily budget, so this
asks /rate-limit (free) how many files each key can still pay for, spends each
key to that cap, then rotates to the next one.

A work counts as done when its file exists and starts with a TEI root; files are
written under a temp name and renamed, so a killed run never leaves a truncated
file that looks complete. Reruns, shards and teammates therefore all share one
directory safely.
"""
import argparse
import csv
import gzip
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_openalex import MAILTO, SSL_CONTEXT
from tei_text import extract_text

DEFAULT_IN = "data/raw/openalex_works.jsonl"
DEFAULT_OUT = "data/fulltext"
DEFAULT_COST = 0.01
RATE_LIMIT = "https://api.openalex.org/rate-limit"
FIELDS = ["work_id", "file", "bytes", "text_chars", "status", "license", "downloaded_at"]


class Key:
    __slots__ = ("value", "left", "cooldown")

    def __init__(self, value, left):
        self.value = value
        self.left = left
        self.cooldown = 0.0


def load_keys(keys_file=None):
    if keys_file:
        keys = [line.strip() for line in open(keys_file, encoding="utf-8")
                if line.strip() and not line.lstrip().startswith("#")]
    else:
        keys = []
        for name in ("OPEN_ALEX_API_KEYS", "OPEN_ALEX_API_KEY"):
            raw = os.environ.get(name)
            if not raw and os.path.exists(".env"):
                for line in open(".env", encoding="utf-8"):
                    match = re.match(rf"\s*{name}\s*=\s*(.*)\s*$", line)
                    if match:
                        raw = match.group(1)
                        break
            if raw:
                keys += re.split(r"[,\s]+", raw.strip().strip("\"'"))
    seen, unique = set(), []
    for key in keys:
        key = key.strip().strip("\"'")
        if key and key not in seen:
            seen.add(key)
            unique.append(key)
    return unique


def candidates(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            work = json.loads(line)
            url = (work.get("content_urls") or {}).get("grobid_xml")
            if not url:
                continue
            work_id = url.rsplit("/", 1)[-1].split(".")[0]
            yield work_id, url, (work.get("best_oa_location") or {}).get("license") or ""


def file_path(out_dir, work_id):
    return Path(out_dir) / f"{work_id}.xml"


def is_tei(head):
    return len(head) > 200 and (b"<TEI" in head or b"<tei" in head)


def already(path):
    if not path.exists():
        return False
    with open(path, "rb") as fh:
        return is_tei(fh.read(2048))


def save(path, raw):
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(raw)
    tmp.replace(path)


def request(url, api_key=None, timeout=120):
    if api_key:
        url += ("&" if "?" in url else "?") + "api_key=" + urllib.parse.quote(api_key)
    req = urllib.request.Request(url, headers={"User-Agent": f"openalex-fulltext (mailto:{MAILTO})"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
            return resp.status, resp.read(), resp.headers
    except urllib.error.HTTPError as err:
        return err.code, err.read(), err.headers
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        return 0, str(err).encode(), {}


def daily_capacity(api_key, fallback_cost):
    status, body, _ = request(RATE_LIMIT, api_key)
    if status != 200:
        return 0, f"/rate-limit HTTP {status}"
    try:
        limit = json.loads(body)["rate_limit"]
    except (ValueError, KeyError):
        return 0, "/rate-limit unreadable"
    cost = (limit.get("endpoint_costs_usd") or {}).get("content") or fallback_cost
    left = float(limit.get("daily_remaining_usd") or 0)
    return int(left // cost), f"${left:.2f} left"


def parse_shard(value):
    try:
        index, count = (int(part) for part in value.split("/"))
    except ValueError:
        raise SystemExit(f"--shard wants i/N, got {value!r}")
    if count < 1 or not 1 <= index <= count:
        raise SystemExit(f"--shard {value!r}: need 1 <= i <= N")
    return index - 1, count


def text_chars(raw):
    try:
        return len(extract_text(raw))
    except Exception:
        return 0  # a parse failure still leaves a usable file on disk


def pick_key(keys):
    while True:
        now = time.monotonic()
        ready = [k for k in keys if k.left > 0 and k.cooldown <= now]
        if ready:
            return ready[0]
        waiting = [k for k in keys if k.left > 0]
        if not waiting:
            return None
        time.sleep(min(max(min(k.cooldown for k in waiting) - now, 1), 600))


def read_manifest(path):
    if not path.exists():
        return set()
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["work_id"] for row in csv.DictReader(fh)}


def write_manifest(path, work_id, file, size, chars, status, license, out_dir):
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        writer.writerow({
            "work_id": work_id,
            "file": str(Path(file).relative_to(out_dir)) if size else "",
            "bytes": size,
            "text_chars": chars,
            "status": status,
            "license": license,
            "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })


def run(args):
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    keys = load_keys(args.keys_file)
    index, count = parse_shard(args.shard)
    total = list(candidates(args.inp))
    shard = total[index::count]
    missing = [c for c in shard if not already(file_path(out_dir, c[0]))]
    todo = missing[: args.limit] if args.limit else missing

    key_objects = []
    for key in keys:
        capacity, note = daily_capacity(key, args.cost)
        key_objects.append(Key(key, capacity))
        print(f"key ...{key[-4:]}: {capacity} files today ({note})", file=sys.stderr)

    if args.dry_run:
        return {
            "candidates": len(total),
            "shard": args.shard,
            "in_shard": len(shard),
            "already": len(shard) - len(missing),
            "missing": len(missing),
            "will_fetch": len(todo),
            "keys": len(keys),
            "capacity_today": sum(k.left for k in key_objects),
        }

    if not key_objects:
        raise SystemExit("no API keys: pass --keys-file or set OPEN_ALEX_API_KEYS")

    manifest = out_dir / "manifest.csv"
    recorded = read_manifest(manifest)
    downloaded = missing_now = 0
    bytes_total = 0
    failures = 0
    started = time.time()

    while todo and any(k.left > 0 for k in key_objects):
        key = pick_key(key_objects)
        if key is None:
            break
        work_id, url, license = todo[0]
        status, body, headers = request(url, key.value)
        if status == 200:
            raw = gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body
            if not is_tei(raw[:2048]):
                write_manifest(manifest, work_id, "", 0, 0, "bad_payload", license, out_dir)
                todo.pop(0)
                key.left -= 1
                continue
            save(file_path(out_dir, work_id), raw)
            chars = text_chars(raw)
            write_manifest(manifest, work_id, file_path(out_dir, work_id), len(raw), chars,
                           "ok" if chars else "no_text", license, out_dir)
            recorded.add(work_id)
            downloaded += 1
            bytes_total += len(raw)
            key.left -= 1
            todo.pop(0)
            failures = 0
            print(f"\r[{downloaded}/{len(todo) + downloaded}] {work_id} {len(raw)}B "
                  f"{chars} chars  key ...{key.value[-4:]} ({key.left} left)  "
                  f"{downloaded / max(time.time() - started, 1e-9):.1f} files/s", file=sys.stderr)
        elif status == 429:
            reason, retry = error_reason(body), retry_after(headers)
            if reason == "daily_budget":
                key.left = 0
                print(f"\nkey ...{key.value[-4:]} is out for today", file=sys.stderr)
            else:
                key.cooldown = time.monotonic() + retry
                print(f"\nkey ...{key.value[-4:]} cooling {retry:.0f}s ({reason or 'rate limited'})",
                      file=sys.stderr)
        elif status in (401, 403):
            key.left = 0
            print(f"\nkey ...{key.value[-4:]} rejected (HTTP {status}); is it activated?",
                  file=sys.stderr)
        elif status in (404, 410):
            write_manifest(manifest, work_id, "", 0, 0, "missing", license, out_dir)
            todo.pop(0)
        elif status == 0 or status >= 500:
            failures += 1
            if failures >= args.retries:
                write_manifest(manifest, work_id, "", 0, 0, f"http_{status}", license, out_dir)
                todo.pop(0)
                failures = 0
            else:
                time.sleep(2 ** failures)
        else:
            write_manifest(manifest, work_id, "", 0, 0, f"http_{status}", license, out_dir)
            todo.pop(0)

    # works whose file survived an earlier killed run but never reached the manifest
    for work_id, _, license in missing:
        if work_id not in recorded and already(file_path(out_dir, work_id)):
            path = file_path(out_dir, work_id)
            raw = path.read_bytes()
            write_manifest(manifest, work_id, path, len(raw), text_chars(raw), "backfilled",
                           license, out_dir)
            missing_now += 1

    return {
        "candidates": len(total),
        "shard": args.shard,
        "already": len(shard) - len(missing),
        "downloaded": downloaded,
        "backfilled": missing_now,
        "remaining": len(missing) - downloaded,
        "bytes": bytes_total,
        "keys_left": sum(k.left for k in key_objects),
        "usd_est": round(downloaded * args.cost, 2),
    }


def error_reason(body):
    try:
        return json.loads(body).get("reason") or ""
    except ValueError:
        return ""


def retry_after(headers):
    try:
        return min(max(float(headers.get("Retry-After") or 5), 1), 600)
    except (TypeError, ValueError):
        return 5


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="inp", default=DEFAULT_IN)
    parser.add_argument("--out-dir", default=DEFAULT_OUT)
    parser.add_argument("--keys-file", help="one API key per line; defaults to OPEN_ALEX_API_KEYS in the environment or .env")
    parser.add_argument("--shard", default="1/1", help="i/N: download only slice i of N candidates")
    parser.add_argument("--limit", type=int, default=0, help="stop after N downloads in this run")
    parser.add_argument("--retries", type=int, default=4, help="network retries per work before recording an error")
    parser.add_argument("--cost", type=float, default=DEFAULT_COST, help="fallback price per file when /rate-limit omits it")
    parser.add_argument("--dry-run", action="store_true", help="report the plan and today's per-key budget, download nothing")
    args = parser.parse_args()
    started = time.time()
    result = run(args)
    result["seconds"] = round(time.time() - started, 1)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
