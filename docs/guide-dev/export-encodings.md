---
title: Export encodings
---

# Export encodings (`export_encodings`)

One-shot management command that encodes Country Office (CO) face photos via the
[Deduplication Engine](../components/hde.md) (`encode_only`) and requests a zip of
embeddings as a **signed URL**. Progress is tracked in a JSON state file in Django
default storage so every mode is idempotent and safe to re-run.

There is no admin UI, Celery task, or REST route in HOPE for this flow — only this command.

## Prerequisites

- Deduplication Engine reachable over HTTP with Token auth.
- Individuals in the target business area(s) with a non-empty `photo`, not withdrawn/duplicate/removed.
- Engine image registration uses **filename mode**: HOPE sends
  `{reference_pk: individual.id, filename: individual.photo.name}`. The engine must be able to
  open that blob key in its Hope storage (shared Azure/Azurite, or filenames that already exist there).
- `--dedup-url` and `--dedup-token` are **required** on every run (not read from env).

## Command

```bash
python manage.py export_encodings \
  --mode submit|status|export \
  --state-file encodings/<run-name>.json \
  --dedup-url https://dedup.example.org/ \
  --dedup-token <token> \
  [--business-areas afghanistan,ukraine] \
  [--chunk-size 10000] \
  [--upload-batch-size 5000] \
  [--export-format npy|jsonl]
```

| Flag | Required | Notes |
|------|----------|--------|
| `--mode` | yes | `submit`, `status`, or `export` |
| `--state-file` | yes | Key in Django **default storage** (not a host path). Local default: `/data/uploads/<key>` |
| `--dedup-url` | yes | Engine base URL (trailing slash optional) |
| `--dedup-token` | yes | `Authorization: Token …` value |
| `--business-areas` | submit only | Comma-separated BA slugs |
| `--chunk-size` | no | Default `10000`. Pinned in the state file on first submit |
| `--upload-batch-size` | no | Default `5000`. Pinned on first submit; changing it on resume aborts |
| `--export-format` | export only | `npy` (default) or `jsonl` |

### Where is the state file?

`--state-file` is a storage key. With local `FileSystemStorage`:

```text
/data/uploads/encodings/<run-name>.json
```

In Docker:

```bash
docker exec <hope-backend> cat /data/uploads/encodings/<run-name>.json
```

## Typical workflow

Run the three modes in order. Re-run `status` / `export` until finished.

```bash
# 1) Create sets, register images, start encode_only
python manage.py export_encodings \
  --mode submit \
  --state-file encodings/run1.json \
  --business-areas afghanistan \
  --chunk-size 10000 \
  --dedup-url https://dedup.example.org/ \
  --dedup-token "$TOKEN"

# 2) Poll set states (safe while encoding is still running)
python manage.py export_encodings \
  --mode status \
  --state-file encodings/run1.json \
  --dedup-url https://dedup.example.org/ \
  --dedup-token "$TOKEN"

# 3) Request zip / poll signed URL (only when all chunks of a CO are Encoded+)
python manage.py export_encodings \
  --mode export \
  --state-file encodings/run1.json \
  --export-format npy \
  --dedup-url https://dedup.example.org/ \
  --dedup-token "$TOKEN"
```

### Mode: `submit`

For each business area, selects individuals with photos (ordered by `id`), slices them into
`--chunk-size` groups, and for each unfinished chunk:

1. `POST deduplication_sets/` — group reference id `enc-{ba}-{run_id}-{index:05d}`
2. `POST {set}/images/` in batches of `--upload-batch-size`
3. `POST {set}/ready/` then `POST {set}/process/?encode_only=true`
4. Updates the state file after each step (`uploaded_batches` enables resume mid-upload)

Use a **new** `--state-file` if you change `--chunk-size` or `--upload-batch-size` for a new run
(those values are locked in an existing state file).

### Mode: `status`

For each submitted chunk, `GET deduplication_sets/{id}/` and refresh `engine_state` in the state file.
Prints a per-CO summary (e.g. `Encoding in progress=3, Encoded=8`).

### Mode: `export`

Runs only for COs whose chunks are all in an exportable engine state:
`Encoded`, `Deduplicated`, or `Approved`.

Export slots in the state file are keyed by `{co_slug}:{format}` (so `npy` and `jsonl` are independent).

#### Does `export` POST or GET?

Yes — same `--mode export`, two engine calls depending on state-file contents:

| State file for `{co}:{format}` | Engine call | Purpose |
|--------------------------------|-------------|---------|
| No entry, or `key` missing/null | **`POST /encodings_exports/`** | Start zip job; store returned blob `key` as `pending` |
| `key` is set | **`GET /encodings_exports/status/?key=…`** | Poll / renew signed URL |

Details for the GET path:

- `ready` → store `url` + `expires_at` (re-running renews the SAS URL; no re-zip)
- `failed` → clear `key` so the next export run POSTs again
- `pending` → wait; if older than 2 hours, clear and POST under a new key

## State file shape (summary)

```json
{
  "run_id": "a1b2c3d4",
  "chunk_size": 10000,
  "upload_batch_size": 5000,
  "business_areas": ["afghanistan"],
  "chunks": [
    {
      "reference_id": "enc-afghanistan-a1b2c3d4-00000",
      "set_id": "uuid",
      "image_count": 10000,
      "step": "processed",
      "engine_state": "Encoded"
    }
  ],
  "exports": {
    "afghanistan:npy": {
      "key": "exports/1/afghanistan/afghanistan-….npy.zip",
      "format": "npy",
      "state": "ready",
      "url": "https://…",
      "expires_at": "…"
    }
  }
}
```

The deliverable is the signed `url` (plus `manifest.json` inside the zip).

## Chunking and scale

Each chunk is its own Dedup set **group**, so engine workers can encode chunks in parallel.
Smaller `--chunk-size` (e.g. `2` in local tests) creates more sets and exercises multi-chunk
status/export; production typically uses `10000`.

## Local notes

- From inside the HOPE backend container, `127.0.0.1:8000` is HOPE itself. Point `--dedup-url`
  at a host/network address that reaches the Dedup API (or a local forwarder).
- Filename-only testing: seed `Individual.photo.name` to blob keys that already exist in Dedup’s
  Hope storage; the command never opens photo bytes in HOPE.
