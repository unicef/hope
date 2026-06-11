---
tags:
  - elasticsearch
  - migration
  - operations
---

# Elasticsearch 8 → 9 Migration Runbook

This runbook covers the upgrade from **Bitnami Elasticsearch 8.14.0** to **official Elasticsearch 9.4.2** for the HOPE deployment.

## Migration status

| Stage | Local dev | Prod |
|---|---|---|
| Step 1: Bitnami 8.14.0 → Bitnami 8.18.0 | ✅ applied | ✅ pending |
| Step 2: Bitnami 8.18.0 → Official 9.0.1 | ✅ applied (compose cleaned up) | ☐ pending |
| Step 3: Official 9.0.1 → Official 9.4.2 | ✅ applied (compose now at 9.4.2) | ☐ pending (tag bump only) |

After all three rows are ✅ in prod, this runbook becomes historical.

## Constraints

The upgrade has two binding constraints that shape the entire procedure:

1. **Elasticsearch policy**: ES 9 will only open data directories written by ES 8.18.x. A direct 8.14 → 9.0 upgrade hard-fails on boot with `cannot upgrade a node from version [8.14.0] directly to version [9.0.1]`.
2. **Vendor change**: We are leaving the Bitnami image (UID 1001, `/bitnami/elasticsearch/data`) for the official Elastic image (UID 1000, `/usr/share/elasticsearch/data`). The volume layout is the same on disk, but file ownership and the in-container path differ.

## Chosen path: three-step in-place upgrade

```
Step 1:  Bitnami 8.14.0   →   Bitnami 8.18.0    (same image family, tag bump)
Step 2:  Bitnami 8.18.0   →   Official 9.0.1    (vendor swap; UID + path workaround)
Step 3:  Official 9.0.1   →   Official 9.4.2    (same-major tag bump; no data changes)
```

> **Why not 8.18 → 9.4.2 directly?** Elastic's upgrade matrix only supports 8.18 → 9.0.x as the cross-major hop.
> 8.19 → 9.4.x is also supported but 8.19 was not available in the registry. 8.18 → 9.4.2 in a single step
> is untested by Elastic and risks Lucene codec and transport-protocol incompatibilities with no rollback path.

Why this path:

- Keeps the vendor swap as the **last** step, so if Step 2 fails you fall back to "we're on Bitnami 8.18.0", which is still a fully working production state.
- Step 1 is a low-risk same-vendor tag bump.
- Avoids the long bulk-reindex window that a from-scratch repopulate would require.

Alternative paths considered:

- **Snapshot/restore**: take a snapshot on 8.14, restore on 9.0. Officially supported by ES (N-1 restore). Requires a working snapshot repository (S3 or shared filesystem). Use this if 8.18 turns out to be unavailable in your registry.
- **Reindex from Postgres** (shadow cluster): bypasses ES entirely; stand up a fresh ES 9 cluster, repopulate every per-program index from Postgres via `es_shadow_populate`. Slowest but most defensible. Keep as the fallback if either in-place step fails. Tooling already lives in [src/hope/apps/household/management/commands/es_shadow_populate.py](https://github.com/unicef/hope/blob/develop/src/hope/apps/household/management/commands/es_shadow_populate.py).

## Pre-flight checklist (before touching prod)

- [ ] `bitnamilegacy/elasticsearch:8.18.0` is pullable from your registry mirror.
- [ ] `docker.elastic.co/elasticsearch/elasticsearch:9.0.1` is pullable (Step 2 intermediate).
- [ ] `docker.elastic.co/elasticsearch/elasticsearch:9.4.2` is pullable (Step 3 final target).
- [ ] Snapshot repository configured and verified (`PUT /_snapshot/<repo>` + a successful test snapshot exists).
- [ ] Backend code carries the [`_PreparedFieldsFix`](https://github.com/unicef/hope/blob/develop/src/hope/apps/household/documents.py) mixin (required by elasticsearch.dsl 9.x to populate `_source` correctly on writes).
- [ ] Off-hours maintenance window scheduled. Per-step downtime estimate:
  - Step 1: 30 s – 2 min
  - Step 2: 30 s – 2 min
- [ ] Active programs counted; `rebuild_search_index` smoke-tested in staging.
- [ ] Celery `RDI` / sanction / dedup workers can be paused for the duration.

## Local rehearsal — verify the mechanics before prod

The repo's [`development_tools/compose.yml`](https://github.com/unicef/hope/blob/develop/development_tools/compose.yml) defines two profiles that mirror prod's two upgrade hops.

### Rehearse Step 1 (Bitnami 8.14 → Bitnami 8.18)

The `legacy` profile uses `bitnamilegacy/elasticsearch:${ES_LEGACY_VERSION:-8.18.0}`. The default reflects the current local state (post-step-1). To re-rehearse the actual 8.14 → 8.18 hop, set the env var explicitly:

```bash
cd development_tools

# Wipe any 8.18-formatted data first so we start clean from 8.14
docker compose --profile legacy down
docker volume rm development_tools_data_es

# Start on 8.14 (the pre-upgrade state)
ES_LEGACY_VERSION=8.14.0 docker compose --profile legacy up -d
# Wait for green:
curl http://localhost:9201/_cluster/health
# Verify version:
curl http://localhost:9201/ | jq '.version.number'   # → "8.14.0"
# (optionally write a marker doc here to prove data survives the hop)

# Stop, drop the env override, restart on the SAME volume — this triggers
# the in-place upgrade (Bitnami 8.18 reads 8.14's node metadata and migrates it)
docker compose --profile legacy down
docker compose --profile legacy up -d                  # default: 8.18.0

# Verify version
curl http://localhost:9201/ | jq '.version.number'   # → "8.18.0"

# Verify pre-upgrade data is intact
curl http://localhost:9201/_cat/indices
```

Bitnami's 8.18 image reads 8.14's node-metadata file and upgrades it transparently. No data rewrite, no UID change, no path change — just the binary swap.

### Rehearse Step 2 (Bitnami 8.18 → Official 9.0.1)

After Step 1, the same `data_es` Docker volume now contains 8.18-formatted data and Bitnami's UID 1001 ownership. Step 2 uses the `inplace` profile, which:

1. Spins up a busybox `elasticsearch-inplace-init` container that runs `chown -R 1000:0` on the volume.
2. Spins up the official `elasticsearch:9.0.1` image with `path.data=/bitnami/elasticsearch/data` so it reads from where Bitnami wrote.
3. Waits for the init container via `depends_on: condition: service_completed_successfully`.

```bash
# Stop the Bitnami container
docker compose --profile legacy down

# Boot the official ES 9 against the same volume (with chown init)
docker compose --profile inplace up -d

# Verify version
curl http://localhost:9202/ | jq '.version.number'   # → "9.0.1" (step 2 intermediate)

# Verify pre-upgrade data is intact (the bitnami 8.18 data ES 9 now reads)
curl http://localhost:9202/_cat/indices
```

If you skipped Step 1 and try to run Step 2 directly on 8.14 data, ES 9 will refuse to boot with the version-upgrade error — that is the intended check.

## Prod procedure

### Step 1 — Bitnami 8.14 → Bitnami 8.18 (~30 s – 2 min search downtime)

1. **Take a baseline ES snapshot** to your snapshot repo. Restorable to 8.x or 9.x.

      ```bash
      curl -X PUT "$ES/_snapshot/<repo>/pre-step1-$(date +%Y%m%d-%H%M)?wait_for_completion=true"
      ```

2. **Pause writes**. Scale Celery to 0:

      ```bash
      kubectl scale deployment celery-worker --replicas=0
      kubectl scale deployment celery-worker-periodic --replicas=0
      kubectl scale deployment celery-beat --replicas=0
      ```

3. **Bump the ES image tag** in the prod manifest:

      ```diff
      - image: bitnamilegacy/elasticsearch:8.14.0
      + image: bitnamilegacy/elasticsearch:8.18.0
      ```

4. **Apply the manifest** (rolling-restart the ES pod). The PVC is the same; ES 8.18 reads ES 8.14's data and upgrades node metadata internally.

5. **Wait for green**:

      ```bash
      curl -s "$ES/_cluster/health?wait_for_status=green&timeout=120s"
      curl -s "$ES/" | jq '.version.number'   # → "8.18.0"
      ```

6. **Verify search end-to-end** via a representative API call from the backend. Restore Celery once verified.

7. **Soak**. Run on 8.18 for at least 24 hours before starting Step 2. This window lets any subtle 8.x version-bump issues surface while you're still on a same-vendor, same-major version where rollback is trivial.

### Step 2 — Bitnami 8.18 → Official 9.0.1 (~30 s – 5 min search downtime)

> After Step 2 is confirmed stable in prod, remove the `initContainers` block and the `path.data` env override
> from the Helm chart in a follow-up PR (same cleanup already applied to `compose.yml` on this branch).

1. **Take a second snapshot** (insurance against the vendor swap).

2. **Pause writes** (Celery to 0, same as Step 1).

3. **Update the manifest** — three coordinated changes:

      - Replace the image:

         ```diff
         - image: bitnamilegacy/elasticsearch:8.18.0
         + image: docker.elastic.co/elasticsearch/elasticsearch:9.0.1
         ```

      - Add an init container that fixes file ownership from Bitnami's UID 1001 to the official image's UID 1000:

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

      - Point ES 9 at the Bitnami path via env (so we don't have to migrate the data dir):

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
         ```

      - Install the `analysis-phonetic` plugin at boot (Bitnami did this via `ELASTICSEARCH_PLUGINS`; the official image needs an explicit install):

         ```yaml
         command:
           - bash
           - -c
           - |
             bin/elasticsearch-plugin install analysis-phonetic --batch --silent 2>/dev/null || true &&
             exec /usr/local/bin/docker-entrypoint.sh eswrapper
         ```

4. **Apply**. The init container chowns the volume, exits, and the main ES 9 container starts.

5. **Wait for green**:

      ```bash
      curl -s "$ES/_cluster/health?wait_for_status=green&timeout=180s"
      curl -s "$ES/" | jq '.version.number'   # → "9.0.1"
      ```

6. **Verify search end-to-end**, especially the codepaths that rely on:
      - `match_phrase_prefix` queries (household / individual search by ID/name)
      - The scripted similarity `return (1.0/doc.length)*query.boost` (sanction list scoring) — verify it compiled on the new cluster
      - The phonetic analyzer (name fuzzy matching)

7. **Resume Celery**.

8. **Soak** for 48 hours before starting Step 3.

### Step 3 — Official 9.0.1 → Official 9.4.2 (~30 s downtime, rolling-restart)

This is a same-major same-vendor tag bump. No index format changes, no UID changes, no data-path changes.
No breaking changes between 9.0 and 9.4 affect HOPE (TSDB and dense-vector changes are irrelevant).

**Step 3a — tag bump (required, low risk):**

1. **Bump the image tag** in the Helm chart:

      ```diff
      - image: docker.elastic.co/elasticsearch/elasticsearch:9.0.1
      + image: docker.elastic.co/elasticsearch/elasticsearch:9.4.2
      ```

2. **Remove the `initContainers` block** (Step 2 one-time chown is already done; volume is now owned by 1000:0).

3. **Keep `path.data=/bitnami/elasticsearch/data`** and the PVC mount at `/bitnami/elasticsearch/data` unchanged for now.
   The data files are at the volume root regardless of the mount path — no data migration is needed,
   but the mount path and `path.data` must be changed **atomically** (see Step 3b). Doing it in the same
   manifest as the tag bump risks a partial apply that would start ES against an empty path.

**Step 3b — path cleanup (optional, separate PR):**

Change the PVC mountPath and remove `path.data` **in the same manifest apply**:

```diff
  volumeMounts:
-   - mountPath: /bitnami/elasticsearch/data
+   - mountPath: /usr/share/elasticsearch/data
      name: data
  env:
-   - name: path.data
-     value: /bitnami/elasticsearch/data
```

Why this is safe: `data_es` (or the PVC) stores ES data at its root (`nodes/0/...`).
Changing the container mount point from `/bitnami/elasticsearch/data` to `/usr/share/elasticsearch/data`
does not move any files — it is a pure path alias change. ES will find its data at the new path immediately.

4. **Apply and wait for green**:

      ```bash
      curl -s "$ES/_cluster/health?wait_for_status=green&timeout=120s"
      curl -s "$ES/" | jq '.version.number'   # → "9.4.2"
      ```

5. **Run verification queries** (see below).

6. **Soak** for 24 hours then decommission the Step-2 snapshot.

## Rollback

### Rollback Step 1 (Bitnami 8.18 → Bitnami 8.14)

ES 8 supports downgrade within a major version IF the cluster state hasn't been upgraded too far. Generally safe to revert image tag back to 8.14.0 if you catch problems within minutes.

If too much time has passed:

```bash
# Restore the pre-step-1 snapshot to a fresh 8.14 cluster (or to the same volume after wiping it)
curl -X POST "$ES/_snapshot/<repo>/pre-step1-<timestamp>/_restore"
```

### Rollback Step 2 (Official 9.0.1 → Bitnami 8.18)

This is harder because once ES 9 has written cluster state to the volume, ES 8.18 cannot read it. Rollback requires:

1. Restore the pre-Step-2 snapshot to a fresh Bitnami 8.18 cluster:

      ```bash
      # Wipe the data volume on the rolled-back node, restart on 8.18.0
      # Then:
      curl -X POST "$ES/_snapshot/<repo>/pre-step2-<timestamp>/_restore"
      ```

2. Re-point the backend at the rolled-back cluster.

The snapshot from Step 2 is the ONLY safe rollback path; do not attempt to mount the ES-9-touched volume on Bitnami 8.18.

## Verification queries

Run these from the backend to confirm the upgrade landed cleanly:

```python
# Python shell
from elasticsearch.dsl import connections
es = connections.get_connection()
print("version:", es.info().body["version"]["number"])           # → "9.4.2"
print("health:", es.cluster.health().body["status"])             # → "green"
print("indices:", len(es.cat.indices(format="json").body))       # → > 0
print("phonetic plugin:", any(
    p["component"] == "analysis-phonetic"
    for n in es.cat.plugins(format="json").body
    for p in [n]
))
```

Or via HTTP:

```bash
curl -s "$ES/" | jq '.version.number'                            # → "9.4.2"
curl -s "$ES/_cluster/health" | jq '.status'                     # → "green"
curl -s "$ES/_cat/indices?v"                                     # all per-program indexes present
curl -s "$ES/_cat/plugins?v"                                     # analysis-phonetic present on every node
```

App-level verification — exercise the codepaths that depend on ES 9-specific behavior:

- Search a household by `unicef_id` (`GET /api/.../households/?search=<HH-ID>`)
- Search an individual by name (`GET /api/.../individuals/?search=<full name>`) — exercises phonetic analyzer
- Trigger an RDI dedup with intentional near-duplicates — exercises fuzzy match (`AUTO:3,6`) + scripted similarity
- Confirm a sanction-list flagged ticket gets created for a matching individual

## What happens if Step 2 fails because of the version check

If Step 2 fails with `cannot upgrade a node from version [...] directly to version [9.0.1]`, it means Step 1 did not actually complete or was applied to the wrong cluster. Check `node.lock` / cluster-state `node_version` on the volume before troubleshooting Step 2.

## Tooling reference

| Concern | Code | Notes |
|---|---|---|
| Admin "rebuild all indexes" action | [`hope.apps.administration.panels.es.ElasticsearchPanel`](https://github.com/unicef/hope/blob/develop/src/hope/apps/administration/panels/es.py) | Available from `/<admin>/~console/es/` |
| Per-program rebuild | [`hope.apps.household.services.index_management.rebuild_program_indexes`](https://github.com/unicef/hope/blob/develop/src/hope/apps/household/services/index_management.py) | Drops + recreates + populates from Postgres |
| Shadow-cluster populate (fallback path C) | [`python manage.py es_shadow_populate`](https://github.com/unicef/hope/blob/develop/src/hope/apps/household/management/commands/es_shadow_populate.py) | Supports `--shard N --of M` for sharded parallel populate across multiple worker pods |
| The `_prepare_fields` fix required by ES 9 dsl | [`_PreparedFieldsFix` mixin in `documents.py`](https://github.com/unicef/hope/blob/develop/src/hope/apps/household/documents.py) | Without this, doc writes under ES 9 produce empty `_source` |
| Local-dev compose | [`development_tools/compose.yml`](https://github.com/unicef/hope/blob/develop/development_tools/compose.yml) | Now runs `elasticsearch:9.4.2` on a clean volume; migration scaffolding (`elasticsearch-init`, `path.data`, Bitnami path) removed |

## Open considerations

- **`number_of_replicas: 0`** in [`hope.apps.household.documents`](https://github.com/unicef/hope/blob/develop/src/hope/apps/household/documents.py) means a single-node deployment has no HA. If prod ever moves to multi-node, bump this to 1 (or 2) at the same time as the migration.
- **Closed/finished programs**: [`rebuild_search_index`](https://github.com/unicef/hope/blob/develop/src/hope/apps/utils/elasticsearch_utils.py) only iterates `Program.objects.filter(status=ACTIVE)`. Non-active programs' indexes are still searched by the cross-program endpoints. If you ever run a rebuild as a recovery action, pass `include_non_active=True` or use `es_shadow_populate --include-non-active`.
- **Bitnami image lifecycle**: `bitnamilegacy/*` images are the archived versions of Bitnami's previous public catalog. They will not receive further updates. Pin to exact tags (`8.14.0`, `8.18.0`) and assume no patch releases.
