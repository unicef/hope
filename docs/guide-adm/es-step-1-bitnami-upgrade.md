---
tags:
  - elasticsearch
  - migration
  - operations
---

# Elasticsearch Step 1 — Bitnami 8.14.0 → 8.18.0

This is the **first of two steps** in the upgrade path from Bitnami Elasticsearch 8.14.0 to official Elasticsearch 9.0.1.

| | Step 1 (this doc) | Step 2 (later) |
|---|---|---|
| What | Bitnami 8.14.0 → Bitnami 8.18.0 | Bitnami 8.18.0 → Official 9.0.1 |
| Operation | Image tag bump only | Vendor swap + UID/path workaround |
| Code change required | None | Yes (separate PR) |
| Downtime | 30 s – 2 min | 30 s – 5 min |

Step 2 is hard-gated by Elasticsearch's own policy: ES 9 will only open data directories written by ES 8.18.x. Step 1 unlocks Step 2.

## Why Step 1 is safe and small

- Same vendor (Bitnami), same image family, same UID 1001, same `/bitnami/elasticsearch/data` mount.
- A minor-version bump within the same major triggers ES's internal node-metadata upgrade — no data is rewritten.
- The Python `elasticsearch` client (still at 8.x on `develop`) is unaffected: 8.x client ↔ 8.18 server is a fully supported combination.
- No application code change required.

## Pre-flight checklist

- [ ] `bitnamilegacy/elasticsearch:8.18.0` is pullable from your registry mirror (verified: it exists on Docker Hub).
- [ ] ES snapshot repository configured and reachable from prod, and a fresh test snapshot completes successfully.
- [ ] Off-hours maintenance window scheduled. Expected search downtime: 30 s – 2 min.
- [ ] Celery workers can be paused for the duration of the restart (RDI imports, dedup, sanction-list checks all write to ES).

## Local rehearsal

The compose file in this PR sets `bitnamilegacy/elasticsearch:8.18.0` as the dev-default. To rehearse the actual 8.14 → 8.18 upgrade locally:

```bash
cd development_tools

# Wipe any existing 8.18-formatted state so we genuinely start from 8.14
docker compose down -v

# Start on 8.14 (the pre-upgrade state)
git stash  # if your branch has the 8.18 change
docker compose up -d
curl http://localhost:9200/ | jq '.version.number'   # → "8.14.0"

# (Optional) populate some test data via the UI or RDI

# Restore the 8.18 change and restart on the SAME data volume
git stash pop
docker compose down                                    # keep volume (no -v)
docker compose up -d
curl http://localhost:9200/ | jq '.version.number'   # → "8.18.0"
curl http://localhost:9200/_cluster/health           # → status: green
curl http://localhost:9200/_cat/indices?v            # data from 8.14 still present
```

Bitnami's 8.18 image reads 8.14's node-metadata file and upgrades it transparently. No data rewrite, no UID change, no path change — just the binary swap.

## Prod procedure

### 1. Take a baseline snapshot

```bash
curl -X PUT "$ES_PROD/_snapshot/<repo>/pre-step1-$(date +%Y%m%d-%H%M)?wait_for_completion=true" \
  -H 'Content-Type: application/json' \
  -d '{"indices":"*","include_global_state":true}'
```

The snapshot is restorable to either ES 8.x or ES 9.x — your rollback insurance.

### 2. Pause writes

Anything that writes to ES (RDI imports, dedup, sanction-list checks) goes through Celery:

```bash
kubectl scale deployment celery-worker --replicas=0
kubectl scale deployment celery-worker-periodic --replicas=0
kubectl scale deployment celery-beat --replicas=0
```

### 3. Bump the image tag in the prod ES manifest

```diff
- image: bitnamilegacy/elasticsearch:8.14.0
+ image: bitnamilegacy/elasticsearch:8.18.0
```

Apply via your normal deployment mechanism (`kubectl apply`, `helm upgrade`, or a GitOps push).

### 4. Wait for ES to come back up

```bash
kubectl rollout status statefulset/elasticsearch --timeout=300s
# or
kubectl wait --for=condition=ready pod -l app=elasticsearch --timeout=300s
```

### 5. Verify version + cluster health

```bash
curl -s "$ES_PROD/" | jq '.version.number'                 # → "8.18.0"
curl -s "$ES_PROD/_cluster/health" | jq '.status'          # → "green"
curl -s "$ES_PROD/_cat/indices?v" | wc -l                  # confirm all per-program indexes present
```

### 6. End-to-end app verification

Run a representative read through the backend (NOT directly to ES) — confirms the app + ES path still works:

```bash
TOKEN=$(curl -s -X POST "$APP_PROD/api/token-auth/" \
  -d 'username=...&password=...' | jq -r .token)
curl -H "Authorization: Token $TOKEN" \
  "$APP_PROD/api/rest/business-areas/<slug>/programs/<code>/households/?search=<known-HH-id>"
# Expected: 200 OK, same hits as before the upgrade, no 5xx in backend logs.
```

### 7. Resume Celery

```bash
kubectl scale deployment celery-worker --replicas=<N>
kubectl scale deployment celery-worker-periodic --replicas=<N>
kubectl scale deployment celery-beat --replicas=1
```

### 8. Soak

Run on 8.18.0 for **at least 24 hours** before starting Step 2. Watch:

- Sentry for any new ES-related exceptions
- ES cluster health stays green
- Run a real RDI import end-to-end (best smoke test)

## Rollback

ES 8.18 → ES 8.14 is supported within minutes of the upgrade (cluster state hasn't drifted). Revert the image tag and re-apply.

If the rollback window has closed (hours have passed and writes have happened on 8.18):

```bash
# Restore the pre-step-1 snapshot to a fresh 8.14 cluster
# (wipe the PVC first, then start the 8.14 pod, then restore)
curl -X POST "$ES/_snapshot/<repo>/pre-step1-<timestamp>/_restore" \
  -H 'Content-Type: application/json' \
  -d '{"indices":"*"}'
```

## What's NOT in scope of this PR

To keep the migration reviewable, Step 2 (the vendor swap to official ES 9.0.1) ships in a separate PR. That PR will include:

- Python `elasticsearch` client lib bump to 9.x
- The `_PreparedFieldsFix` mixin needed by `elasticsearch.dsl` 9.x
- `compose.yml` swap to the official ES image with the `path.data` + chown-init workaround
- The corresponding step-2 runbook

Do not start Step 2 until Step 1 has been in prod for the 24+ hour soak.
