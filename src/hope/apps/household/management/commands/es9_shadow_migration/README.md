# ES8 → ES9 shadow-cluster migration

Zero-downtime move of the HOPE Elasticsearch data from the ES8 (Bitnami) cluster to a
fresh ES9 (official image) **shadow** cluster, then a fast cut-over. The app keeps
serving from ES8 the whole time; ES9 is populated in the background and reconciled with
Postgres via a per-program delta before the switch.

Commands live in `src/hope/apps/household/management/commands/`:
- `es_populate_delta` — reconcile the shadow cluster against Postgres (delta by `updated_at`, or `--reconcile` by count). Targets the shadow cluster via `--using v9`.
- `es_mutate_stream` — **dev/test only** change generator (proves the delta shrinks). Not run in prod.
- `_es_shadow.py` — registers the `v9` connection from `ELASTICSEARCH_HOST_V9` (keeps shadow wiring out of core `es.py`).

`es_migrate.py` here is the raw ES-level bulk copy (stdlib HTTP, ES8→ES9) used for the initial baseline.

## Procedure (8 steps)
1. ES8 populated; app on ES8; empty ES9 cluster ready.
2. **Baseline copy** ES8→ES9 — `es_migrate.py` (via `copy-job.yaml`). Record its start time as **T0**.
3. *(test only)* run `es_mutate_stream` to simulate live changes during the copy.
4. **Delta loop:** `es_populate_delta --using v9 --since <T0>`, re-run each pass from the previous pass's start time until it reports ~0 programs.
5. Scale Celery workers → 0 (blocks dedup; sync signal-writes to ES stay harmless).
6. Switch backend/Celery → ES9.
7. Final `es_populate_delta --using v9 --since <last pass ts>` (shrinks the window to seconds).
8. Scale Celery workers back up.

## Running it

### prod (once PR #6164 is merged and the image is built)
The commands are in the image — no file mounts needed. Set `ELASTICSEARCH_HOST_V9` to the
ES9 cluster and run, e.g. as a Job/pod on the backend image:
```
export ELASTICSEARCH_HOST_V9=http://<es9-service>:9200
django-admin es_populate_delta --using v9 --since <T0> --parallel --threads 8
django-admin es_populate_delta --using v9 --reconcile --verify   # final safety pass
```

### eph-1 rehearsal (old image — mount the files)
`shadow-pods.yaml` and `copy-job.yaml` are eph-1 specific (namespace `ictd-hope-eph-1`,
old image tag). Because that image predates the commands, they're mounted from ConfigMaps:
```
# copy job scripts
kubectl -n ictd-hope-eph-1 create configmap mig-scripts \
  --from-file=es_migrate.py --from-file=orchestrate.py
# shadow tooling (commands + v9 helper); es_mutate_stream.eph.py is the program-scoped variant
kubectl -n ictd-hope-eph-1 create configmap shadow-tools \
  --from-file=es_mutate_stream.py=es_mutate_stream.eph.py \
  --from-file=es_populate_delta.py=../../src/hope/apps/household/management/commands/es_populate_delta.py \
  --from-file=_es_shadow.py=../../src/hope/apps/household/management/commands/_es_shadow.py
kubectl -n ictd-hope-eph-1 apply -f copy-job.yaml     # step 2
kubectl -n ictd-hope-eph-1 apply -f shadow-pods.yaml  # runner pods for steps 3/4/7
```
Both pods write to the container stdout, so `kubectl logs shadow-delta` / `shadow-mutate` show live activity.

## Findings from the eph-1 rehearsal (relevant to prod)
- **`--since` keys off `updated_at`.** Any `save(update_fields=[...])` that omits `updated_at` will NOT bump it (Django does not auto-add `auto_now` fields), so such a change is invisible to the delta. Verify the app's write paths bump `updated_at`, or rely on the `--reconcile` count pass to catch the rest.
- Hard-deletes with no sibling `updated_at` change are only caught by `--reconcile` (count mismatch).
- `es_mutate_stream.eph.py` is program-scoped + unordered because `order_by("?")` over ~12M rows is unusably slow; the committed `es_mutate_stream` keeps the simpler form for small datasets.

## Files
| File | Purpose |
|---|---|
| `es_migrate.py` | raw ES8→ES9 bulk copy (baseline, step 2) |
| `copy-job.yaml` | eph-1 Job that runs `es_migrate.py` |
| `shadow-pods.yaml` | eph-1 runner pods (`shadow-delta`, `shadow-mutate`) |
| `es_mutate_stream.eph.py` | eph-scale (program-scoped) variant of the test change generator |
