#!/usr/bin/env python3
"""Migrate HOPE indices from cluster A (ES8) -> cluster B (ES9).

Raw HTTP (stdlib only) so it talks to ES8 (read) and ES9 (write) with plain
JSON — no client version / compat-header issues. Idempotent: bulk index by _id,
so re-running only overwrites/adds (delta pass).

Env:
  SRC          source base url   (default cluster A: http://hope-elasticsearch:9200)
  DST          dest base url     (default cluster B: http://hope-es-search:9200)
  CONC         parallel indices  (default 6)
  SCROLL_SIZE  docs per scroll   (default 2000)
  INDEX_GLOB   comma globs        (default households_*,individuals_*)
"""
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC = os.environ.get("SRC", "http://hope-elasticsearch:9200").rstrip("/")
DST = os.environ.get("DST", "http://hope-es-search:9200").rstrip("/")
CONC = int(os.environ.get("CONC", "6"))
SCROLL_SIZE = int(os.environ.get("SCROLL_SIZE", "2000"))
INDEX_GLOB = os.environ.get("INDEX_GLOB", "households_*,individuals_*")


def req(method, url, data=None, ndjson=False):
    headers = {"Content-Type": "application/x-ndjson" if ndjson else "application/json"}
    body = None
    if data is not None:
        body = data.encode() if isinstance(data, str) else json.dumps(data).encode()
    r = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=180) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def strip_boost(obj):
    """ES9 removed the `boost` mapping param — remove it recursively."""
    if isinstance(obj, dict):
        obj.pop("boost", None)
        for v in obj.values():
            strip_boost(v)
    elif isinstance(obj, list):
        for v in obj:
            strip_boost(v)
    return obj


def list_indices(base, globs):
    out = []
    for g in globs.split(","):
        g = g.strip()
        try:
            data = req("GET", f"{base}/_cat/indices/{g}?h=index&format=json")
            out += [d["index"] for d in data]
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
    return sorted({i for i in out if not i.startswith(".")})


def create_dest_index(index):
    meta = req("GET", f"{SRC}/{index}")[index]
    mappings = strip_boost(meta.get("mappings", {}) or {})
    src_idx = (meta.get("settings", {}) or {}).get("index", {}) or {}
    settings = {"number_of_shards": src_idx.get("number_of_shards", "1"), "number_of_replicas": "0"}
    if "analysis" in src_idx:                    # carry over custom/phonetic analyzers
        settings["analysis"] = src_idx["analysis"]
    body = {"settings": {"index": settings}, "mappings": mappings}
    try:
        req("PUT", f"{DST}/{index}", body)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        if e.code == 400 and "resource_already_exists" in detail:
            return
        raise RuntimeError(f"create {index} failed: {e.code} {detail[:200]}")


def migrate_index(index):
    t0 = time.time()
    create_dest_index(index)
    total = 0
    r = req("POST", f"{SRC}/{index}/_search?scroll=5m",
            {"size": SCROLL_SIZE, "query": {"match_all": {}}, "sort": ["_doc"]})
    sid = r.get("_scroll_id")
    hits = r["hits"]["hits"]
    while hits:
        lines = []
        for h in hits:
            lines.append(json.dumps({"index": {"_index": index, "_id": h["_id"]}}))
            lines.append(json.dumps(h["_source"]))
        resp = req("POST", f"{DST}/_bulk", "\n".join(lines) + "\n", ndjson=True)
        if resp.get("errors"):
            for it in resp["items"]:
                err = it.get("index", {}).get("error")
                if err:
                    return index, total, time.time() - t0, "BULK_ERR:" + json.dumps(err)[:160]
        total += len(hits)
        r = req("POST", f"{SRC}/_search/scroll", {"scroll": "5m", "scroll_id": sid})
        sid = r.get("_scroll_id")
        hits = r["hits"]["hits"]
    try:
        req("DELETE", f"{SRC}/_search/scroll", {"scroll_id": [sid]})
    except Exception:
        pass
    return index, total, time.time() - t0, "OK"


def main():
    indices = list_indices(SRC, INDEX_GLOB)
    print(f"START migrate {len(indices)} indices SRC={SRC} DST={DST} conc={CONC} size={SCROLL_SIZE}", flush=True)
    t0 = time.time()
    grand = done = fails = 0
    with ThreadPoolExecutor(max_workers=CONC) as ex:
        futs = {ex.submit(migrate_index, i): i for i in indices}
        for f in as_completed(futs):
            idx = futs[f]
            try:
                idx, total, el, status = f.result()
            except Exception as e:
                done += 1
                fails += 1
                print(f"[{done}/{len(indices)}] {idx} EXC {str(e)[:160]}", flush=True)
                continue
            grand += total
            done += 1
            if status != "OK":
                fails += 1
            print(f"[{done}/{len(indices)}] {idx} docs={total} {el:.1f}s {status} | cum_docs={grand} cum_s={time.time()-t0:.0f}", flush=True)
    print(f"DONE indices={len(indices)} docs={grand} fails={fails} total_s={time.time()-t0:.0f}", flush=True)


if __name__ == "__main__":
    main()
