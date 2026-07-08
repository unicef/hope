# ES 8 → ES 9 shadow-cluster migration runbook

Zero-ish-downtime cutover from the ES 8 (Bitnami) cluster to a fresh ES 9 cluster.

The trick: bulk-copy ES 8 → ES 9 up front, then keep catching ES 9 up to Postgres with an
**incremental, DB-based delta** while the app still serves from ES 8. When ES 9 is within seconds
of the DB, flip the backend to ES 9 and run one final delta to close the last gap.


**Two pods, two ES targets** (from `reindex-delta.yml` / `mutate-data.yml`):

- `adhoc-reindex-delta` overrides `ELASTICSEARCH_HOST` → ES 9 (`hope-es-search-master:9200`), so its
  `default` connection writes to ES 9. **The delta runs here.** No alias to pass — just `--since ...`;
  the command prints host + ES version on startup so you can confirm ES 9 before anything writes.
- `adhoc-mutate-data` does **not** override it → its `default` is ES 8 (the app cluster). **The
  generator runs here**, so its `post_save` signal writes land in ES 8, not ES 9 — ES 9 is touched
  only by the delta. That isolation is the whole point: it proves the delta, not the signals.

## Steps

| # | Step | Owner | Env | What |
|---|------|-------|-----|------|
| 1 | Initial state | Valeriya | rehearsal only | ES 8 populated from the DB (ES is empty after a dump restore), backend/Celery point at ES 8, empty ES 9 ready. On the real cutover ES 8 is already populated — no dump-restore step there. |
| 2 | Bulk copy ES 8 → ES 9 | Valeriya | both | `copy-job.yaml` runs `es_migrate.py`. Note its **start time `T0`** — the first `--since` for the delta. |
| 3 | Generate a change stream | Jan | rehearsal only | On `adhoc-mutate-data`, run `es_mutate_stream`. Realistic logged stream to prove the delta shrinks each pass. On the real cutover, live traffic is the stream — skip. |
| 4 | Delta catch-up loop | Jan | both | On `adhoc-reindex-delta` (`default` = ES 9), run `es_populate_delta --since <T>` in a loop, **each pass from the previous pass's start** (overlapping windows). Repeat until a pass reports ~0 work. Shrinks the step 7 gap to seconds. |
| 5 | Scale Celery to 0 | Valeriya | both | Blocks dedup, no code change. Web still writes to ES via HOPE's `post_save` signals — harmless: before switch → ES 8, after → ES 9. Search slightly stale for minutes, acceptable. |
| 6 | Switch backend/Celery to ES 9 | Valeriya | both | Flip the app's ES connection to ES 9. |
| 7 | Final delta | Jan | both | Immediately re-run `es_populate_delta --since <start of the last pass from step 4>`. Catches everything written to ES 8 in the gap between the last delta and the switch. |
| 8 | Scale Celery back up | Valeriya | both | Restore workers. |

## Tooling (this directory)

| File | Owner | What |
|------|-------|------|
| `es8_to_es9_migration/es_migrate.py` + `copy-job.yaml` | Valeriya | Bulk ES 8 → ES 9 copy (raw-HTTP, idempotent by `_id`). |
| `es_populate_delta.py` | Jan | Incremental DB → ES 9 catch-up. Loops in-scope programs, upserts only changed docs, deletes soft-removed docs by `_id`, full-populates only programs whose index does not exist. Never deletes an index. |
| `es_mutate_stream.py` | Jan | **Ephemeral rehearsal only.** Mutates households/individuals in a loop (`given_name`, household `residence_status`, soft-deletes) and logs every change to JSONL so ES output can be asserted against it. |
| `reindex-delta.yml` | Jan | Pod `adhoc-reindex-delta`, `ELASTICSEARCH_HOST` → ES 9. |
| `mutate-data.yml` | Jan | Pod `adhoc-mutate-data`, `default` = ES 8 (rehearsal only). |

## Commands

### Deploy the command files (generator → mutate pod, delta → delta pod)

Management commands are picked up from any installed app's `management/commands/`, so drop Jan's
files under `core` in each pod. Run from the repo root:

```bash
kubectl cp src/hope/apps/household/management/commands/es_mutate_stream.py \
  adhoc-mutate-data:/app/.venv/lib/python3.14/site-packages/hope/apps/core/management/commands/es_mutate_stream.py

kubectl cp src/hope/apps/household/management/commands/es_populate_delta.py \
  adhoc-reindex-delta:/app/.venv/lib/python3.14/site-packages/hope/apps/core/management/commands/es_populate_delta.py
```

### Step 3 — generate changes (rehearsal only, on `adhoc-mutate-data` → ES 8)

```bash
# continuous stream (Ctrl+C to stop); log is flushed per record
kubectl exec -it adhoc-mutate-data -- \
  django-admin es_mutate_stream --passes 1 --batch 500 --delete-every 0 --sleep 0 --log /tmp/mutate_log.jsonl
```

### Step 4 & 7 — delta catch-up (on `adhoc-reindex-delta` → ES 9)

`--since` is a plain ISO-8601 UTC timestamp — pass it literally. The first pass uses `T0`, the
bulk-copy start time (example below: `2026-07-08T12:00:50Z`).

```bash
# dry-run first: per-program delta, no writes
kubectl exec -it adhoc-reindex-delta -- \
  django-admin es_populate_delta --since 2026-07-08T12:00:50Z --dry-run

# real pass
kubectl exec -it adhoc-reindex-delta -- \
  django-admin es_populate_delta --since 2026-07-08T12:00:50Z --parallel --threads 8
```


For step 7, `--since` = the time you noted for the **last** step-4 pass. Each run prints the target
cluster + ES version up front (confirm ES 9), then per program:
`[n/total] <code> id=...: <status> -- ind +N/-M hh +N/-M`.

### Read-only drift check (any time)

```bash
kubectl exec -it adhoc-reindex-delta -- django-admin es_populate_delta --reconcile
```
