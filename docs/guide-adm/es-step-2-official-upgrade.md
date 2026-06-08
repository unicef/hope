---
tags:
  - elasticsearch
  - migration
  - operations
---

# Elasticsearch Step 2 — Bitnami 8.18.0 → Official 9.0.1

This is the **second of two steps** in the ES 8 → 9 migration. Step 1 (Bitnami 8.14 → 8.18) must have been in prod for at least 24 hours before this is started.

| | Step 1 (prerequisite) | Step 2 (this doc) |
|---|---|---|
| What | Bitnami 8.14.0 → Bitnami 8.18.0 | Bitnami 8.18.0 → Official 9.0.1 |
| Operation | Image tag bump only | Vendor swap + UID/path workaround |
| Python deps | unchanged | bumped to ES 9.x |
| Downtime | 30 s – 2 min | 30 s – 5 min |

## Why this can't be a simple tag bump

ES 9 enforces an upgrade-source check: it will only open data directories written by ES 8.18.x. That's why Step 1 had to land first.

There are also two image differences that have to be handled in the manifest:

| | Bitnami 8.18.0 | Official Elastic 9.0.1 |
|---|---|---|
| Process UID | 1001 | 1000 |
| Default data path | `/bitnami/elasticsearch/data` | `/usr/share/elasticsearch/data` |
| Plugin install | `ELASTICSEARCH_PLUGINS` env | `bin/elasticsearch-plugin install` at boot |
| `xpack.security` | implicit | must set `xpack.security.enabled=false` |

This PR resolves both incompatibilities **without moving data**:

- An **init container** chowns the existing volume from UID 1001 to UID 1000 before ES starts.
- The official ES 9 image is configured with `path.data=/bitnami/elasticsearch/data`, so it reads the Bitnami-formatted indexes in place.
- The phonetic plugin is installed by a boot-time `command:` wrapper.

## What's in this PR

```
 development_tools/compose.yml                                   | 37 +++-
 pyproject.toml                                                  |  7 +-
 uv.lock                                                         | 59 +++---
 src/hope/apps/administration/panels/es.py                       |  4 +-
 src/hope/apps/core/es_analyzers.py                              |  2 +-
 src/hope/apps/household/documents.py                            | 25 ++-
 src/hope/apps/household/services/index_management.py            |  6 +-
 src/hope/apps/utils/elasticsearch_utils.py                      |  2 +-
 src/hope/config/fragments/es.py                                 |  2 +-
 stubs/factory/__init__.pyi                                      |  3 +
 tests/e2e/registration_data_import/test_registration_data_import.py |  2 +-
 tests/unit/apps/administration/test_admin.py                    | 17 ++
 tests/unit/conftest.py                                          |  2 +-
```

### Code changes summary

- **`documents.py` — `_PreparedFieldsFix` mixin**: works around a behavior change in `elasticsearch.dsl` 9.x where `AttrDict.__setattr__` routes `_prepared_fields` assignments to `_d_`, while reads still hit the class-level `[]`. Without this, every doc written under ES 9 has an empty `_source` and search returns nothing.
- **Import path migration**: `elasticsearch_dsl` → `elasticsearch.dsl`. The DSL is bundled into the `elasticsearch` package in 9.x (the standalone `elasticsearch-dsl` package no longer has a 9.x release).
- **`panels/es.py` — `conn.info().body`**: the ES 9.x client wraps responses in `ObjectApiResponse`; accessing `.body` gets the raw dict.
- **`tests/unit/apps/administration/test_admin.py`**: new test exercising the admin ES panel info action.

## Pre-flight checklist

- [ ] Step 1 (Bitnami 8.14 → 8.18) is live in prod and soaked for ≥ 24 hours.
- [ ] `docker.elastic.co/elasticsearch/elasticsearch:9.0.1` is pullable from your registry mirror.
- [ ] ES snapshot taken on Bitnami 8.18 immediately before this deploy.
- [ ] Off-hours maintenance window scheduled. Expected search downtime: 30 s – 5 min.
- [ ] Celery workers can be paused for the duration.

## Local rehearsal

```bash
cd development_tools

# Start from clean 8.14 state, simulate Step 1, then apply Step 2.
docker compose down -v
git checkout develop                                  # 8.14 baseline
docker compose up -d
# ... write some test data (RDI, household creation, etc.) ...

git checkout es_migration_step_1                      # Step 1: Bitnami 8.18
docker compose down                                   # KEEP volumes
docker compose up -d
curl http://localhost:9200/ | jq '.version.number'    # → "8.18.0"
# Verify data from develop is still searchable

git checkout es_migration_step_2                      # Step 2: official ES 9.0.1
docker compose down                                   # KEEP volumes
docker compose build backend                          # picks up the ES 9 client lib bump
docker compose up -d                                  # elasticsearch-init chowns, then ES 9 boots
curl http://localhost:9200/ | jq '.version.number'    # → "9.0.1"
# Verify data is STILL searchable from the ES 8.x era
```

If ES 9 boots green and existing search hits still work, the migration logic is validated.

## Prod procedure

### 1. Take a snapshot on Bitnami 8.18

```bash
curl -X PUT "$ES_PROD/_snapshot/<repo>/pre-step2-$(date +%Y%m%d-%H%M)?wait_for_completion=true" \
  -H 'Content-Type: application/json' \
  -d '{"indices":"*","include_global_state":true}'
```

This is the rollback insurance. Step 2 is NOT reversible by image tag alone — once ES 9 writes cluster state to the volume, ES 8 cannot read it.

### 2. Pause writes

```bash
kubectl scale deployment celery-worker --replicas=0
kubectl scale deployment celery-worker-periodic --replicas=0
kubectl scale deployment celery-beat --replicas=0
```

### 3. Update the prod ES manifest — three coordinated changes

```diff
- image: bitnamilegacy/elasticsearch:8.18.0
+ image: docker.elastic.co/elasticsearch/elasticsearch:9.0.1
```

Add an init container that runs before the main ES container:

```yaml
initContainers:
  - name: fix-data-perms
    image: busybox:1.36
    command: ['sh', '-c', 'chown -R 1000:0 /bitnami/elasticsearch/data && chmod -R g+rwX /bitnami/elasticsearch/data']
    securityContext:
      runAsUser: 0
    volumeMounts:
      - name: data
        mountPath: /bitnami/elasticsearch/data
```

Update the main ES container's env to point at the Bitnami path and install the plugin at boot:

```yaml
env:
  - name: path.data
    value: /bitnami/elasticsearch/data
  - name: discovery.type
    value: single-node
  - name: xpack.security.enabled
    value: "false"
  - name: xpack.security.http.ssl.enabled
    value: "false"
command:
  - bash
  - -c
  - |
    bin/elasticsearch-plugin install analysis-phonetic --batch --silent 2>/dev/null || true &&
    exec /usr/local/bin/docker-entrypoint.sh eswrapper
```

### 4. Deploy the backend at the same time

The backend pod also needs to be updated to pick up the ES 9.x Python client (from this PR's `pyproject.toml` + `uv.lock` changes). Roll the backend deployment after the ES pod is ready, so the new client doesn't try to call into the old ES.

### 5. Verify

```bash
curl -s "$ES_PROD/" | jq '.version.number'                # → "9.0.1"
curl -s "$ES_PROD/_cluster/health" | jq '.status'         # → "green"
curl -s "$ES_PROD/_cat/indices?v" | wc -l                 # all per-program indexes present
curl -s "$ES_PROD/_cat/plugins?v"                         # analysis-phonetic visible
```

App-level — exercise the codepaths that use ES 9-specific behavior:

```bash
# Phonetic name matching
curl -H "Authorization: Token $TOKEN" \
  "$APP_PROD/api/rest/business-areas/<slug>/programs/<code>/individuals/?search=<full name>"

# match_phrase_prefix queries (household ID search)
curl -H "Authorization: Token $TOKEN" \
  "$APP_PROD/api/rest/business-areas/<slug>/programs/<code>/households/?search=<HH-id>"

# Scripted similarity (sanction-list scoring) — verify a sanction-match RDI flow end-to-end
```

### 6. Resume Celery

```bash
kubectl scale deployment celery-worker --replicas=<N>
kubectl scale deployment celery-worker-periodic --replicas=<N>
kubectl scale deployment celery-beat --replicas=1
```

### 7. Soak

48 hours minimum before decommissioning the snapshot from step 1 of this procedure.

## Rollback

ES 9 → ES 8.18 cannot be done by image tag alone — the cluster state on disk has been written by ES 9. Rollback requires a snapshot restore:

```bash
# 1. Wipe the data volume on a freshly-deployed Bitnami 8.18 pod
# 2. Restore the pre-Step-2 snapshot to the empty cluster:
curl -X POST "$ES/_snapshot/<repo>/pre-step2-<timestamp>/_restore" \
  -H 'Content-Type: application/json' \
  -d '{"indices":"*","include_global_state":true}'

# 3. Re-point the backend at the rolled-back cluster and revert the
#    backend image to the pre-Step-2 build (which still has the 8.x Python client)
```

Do not attempt to mount the ES-9-touched volume on Bitnami 8.18 — it will fail.

## Open considerations

- **`number_of_replicas: 0`** (defined in `src/hope/apps/household/documents.py`) means a single-node deployment has no HA. If prod moves to multi-node later, bump this to 1.
- **Closed/finished programs**: `rebuild_search_index` only iterates `Program.objects.filter(status=ACTIVE)`. Non-active programs' indexes are still searched by the cross-program endpoints. If a recovery rebuild becomes needed post-migration, run it across all programs explicitly.
- **Index format conversion in the background**: ES 9 reads 8.18 indexes natively, but new writes use ES 9 segment format. Over time, segment merges will rewrite all data to the 9.x format. No action needed; just be aware that disk usage may shift during the first few days.
