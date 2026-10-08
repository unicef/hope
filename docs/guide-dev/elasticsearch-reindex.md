# Elasticsearch reindex

[Elasticsearch](elasticsearch.md) explains how HOPE uses Elasticsearch: the index model,
the rules for mapping changes and feature flags. This guide covers only the hands-on part:
running the blue-green reindex on a deployed environment.

## Before you start

1. Your change follows every rule in [Elasticsearch](elasticsearch.md). In particular,
   every query that depends on the new mapping is behind an `ES_USE_<FEATURE>` flag that
   is still **OFF**.
2. The release containing the document changes is deployed on the environment you are
   about to reindex.
3. `IS_ELASTICSEARCH_ENABLED` is on. With it off, `es_reindex` refuses to run.

## Steps

### 1. Smoke-test the deployment

Open the environment and check that the deployed changes did not break anything. This
confirms that all breaking behaviour is properly guarded by your flag.

### 2. Create a dedicated pod

Run the reindex in its own pod. You could use a backend pod, but its memory limits can
kill a long reindex halfway through.

Save this as `es-reindex-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: adhoc-pod-for-es-reindex
spec:
  containers:
    - name: backend1
      command: ["/bin/sh"]
      args: ["-c", "sleep infinity"]
      image: unicef/hope-support-images:core-<sha>  # same image as the backend pods
      imagePullPolicy: Always
      envFrom:
        - secretRef:
            name: hope-core-backend
        - configMapRef:
            name: hope-core-backend
        - secretRef:
            name: keyvault-secret
  restartPolicy: Never
```

The pod **must** run the same image as the backend pods, otherwise it reindexes with a
different mapping. The image changes with every deploy, so update it each time. Read the image from a running backend pod:

```bash
kubectl get pod <backend-pod> -o jsonpath='{.spec.containers[0].image}'
```

Then create the pod and open a shell in it:

```bash
kubectl apply -f es-reindex-pod.yaml
kubectl exec -it adhoc-pod-for-es-reindex -- bash
```

### 3. Check the current state

```bash
django-admin es_reindex --all --status
```

Expected output:

```text
1--i  individuals_afghanistan_1--i: ALIAS -> individuals_afghanistan_1--i_v1  versions=[1]  es=24 db=24
1--i  households_afghanistan_1--i: ALIAS -> households_afghanistan_1--i_v1  versions=[1]  es=24 db=24
1231  individuals_afghanistan_1231: ALIAS -> individuals_afghanistan_1231_v1  versions=[1]  es=10 db=10
1231  households_afghanistan_1231: ALIAS -> households_afghanistan_1231_v1  versions=[1]  es=10 db=10
```

| Part | Meaning |
|---|---|
| `1--i` | Program code |
| `individuals_afghanistan_1--i` | Alias, the name the application uses |
| `individuals_afghanistan_1--i_v1` | Physical index the alias currently points at |
| `versions=[1]` | Physical versions that exist for this alias |
| `es=24 db=24` | Documents in the live index vs. rows in Postgres |

!!! warning "Every line must say `ALIAS`"
    A line with `NOT AN ALIAS (run es_bootstrap_aliases)` means that program is still on
    a bare index. Stop and run `django-admin es_bootstrap_aliases` before you continue.

### 4. Check shard capacity

Every reindexed program adds a new index pair. The old `_vN` indexes stay open as the
rollback target until step 10, so nothing is freed during the run. A `--all` run needs
free shards for **every** program it reindexes. With the default settings (1 shard,
0 replicas) that is 2 per program.

`es_reindex` checks this itself (steps 5 and 6) and stops before touching anything.
Still worth a manual look, to see the headroom left after the run:

```bash
django-admin shell -c "
from elasticsearch.dsl import connections
es = connections.get_connection()
print(es.cluster.health(filter_path='number_of_data_nodes,active_shards,unassigned_shards'))
print(es.cluster.get_settings(include_defaults=True, flat_settings=True, filter_path='**.cluster.max_shards_per_node'))
"
```

- **Limit** = `cluster.max_shards_per_node` × `number_of_data_nodes`. If the setting
  appears in more than one section, `transient` wins over `persistent`, and `persistent`
  wins over `defaults`.
- **Open** = `active_shards` + `unassigned_shards`.
- **Free** = limit − open. It must be at least 2 × the number of programs the dry run
  marks `REINDEX`.

If it is tight, first drop the old versions left over from a previous reindex
(`django-admin es_drop_old_index_versions --all`, see step 10). If that isn't enough,
raise `cluster.max_shards_per_node` or reindex one business area at a time
(`--business-area <slug>`).

### 5. Dry run

```bash
django-admin es_reindex --all --dry-run
```

This is read-only. It exits with an error if the cluster lacks the shards the run needs.
Expected output:

```text
y1t1: REINDEX ['individuals_afghanistan_y1t1_v1', 'households_afghanistan_y1t1_v1'] -> _v2, then swap both aliases
y58h: REINDEX ['individuals_afghanistan_y58h_v1', 'households_afghanistan_y58h_v1'] -> _v2, then swap both aliases
yfhz: REINDEX ['individuals_afghanistan_yfhz_v1', 'households_afghanistan_yfhz_v1'] -> _v2, then swap both aliases
Shard capacity: need 6, free 940 (60/1000 open)
```

| Line | Meaning |
|---|---|
| `REINDEX [...] -> _v2, then swap both aliases` | A new `_v2` pair is built and both aliases move to it |
| `... (will RESUME an existing dark leftover)` | A previous run crashed here and is picked up where it stopped |
| `up-to-date [...] - would skip` | Already built from the current mapping, so nothing to do |
| `SKIP - not an alias yet` | Needs `es_bootstrap_aliases` first (see step 3) |
| `Shard capacity: need N, free M (open/limit open)` | Shards this run adds vs. shards the cluster still allows (see step 4) |

- Some programs may be on a higher version than others (e.g. `_v3 -> _v4`). That is
  expected; each program pair gets its own next version.
- If your deploy changed **only** analyzers or index settings, every program shows
  `up-to-date`. See the
  [analyzer warning](elasticsearch.md#changing-the-mapping) and add
  `--force`.

!!! tip
    Paste the dry-run output to an AI agent or a teammate and confirm it matches what you
    expect before running the real thing.

### 6. Run the reindex

```bash
PYTHONUNBUFFERED=1 nohup django-admin es_reindex --all --chunk-size 1000 > /tmp/reindex.log 2>&1 &
tail -f /tmp/reindex.log
```

- `nohup` keeps the reindex running if your `kubectl exec` session drops. Reattach with
  `kubectl exec` and `tail -f /tmp/reindex.log` again.
- `PYTHONUNBUFFERED=1` writes progress to the log immediately.
- On large environments this can take hours.

Each program ends with a summary line, `[n/total] <code>: reindexed ...` or
`[n/total] <code>: FAILED - ...`. A failed program does not stop the rest of the fleet.
Its alias is never moved, so search keeps working on the old version.

### 7. Verify

```bash
django-admin es_reindex --all --status
```

Every alias must now point at the new version (e.g. `_v2`), and `es` must equal `db` on
every line.

### 8. Turn the flag on

Only once step 7 is clean, flip your `ES_USE_<FEATURE>` flag **ON** in the Django admin
**Config** (constance) page, then test the new behaviour on the environment.

!!! danger
    Flipping the flag before every program is reindexed returns silently wrong (often
    empty) search results for the programs that were not reindexed yet.

### 9. Delete the reindex pod

```bash
kubectl delete pod adhoc-pod-for-es-reindex
```

### 10. Drop old versions after the sanity window

The old `_vN` indexes stay as an instant rollback target. After the sanity window
(1–3 days), list them and then drop them:

```bash
django-admin es_drop_old_index_versions --all            # list only
django-admin es_drop_old_index_versions --all --confirm  # delete
```

Then remove the flag and the old query path in code.

## Rollback

!!! todo
    Document how to roll back a reindexed program: atomically move both aliases of the
    pair back to the previous `_vN` during the sanity window.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Another reindex run holds the lock` | Make sure no other run is active, then re-run with `--force-unlock`. |
| Run crashed or the pod died midway | Re-run the same command. Finished programs are skipped and a half-done pair is resumed. |
| `verify failed ... re-run with --sweep-wrecks` | A resumed pair was incomplete. Re-run with `--sweep-wrecks` for a clean rebuild of it. |
| `Not enough shard capacity: need N, free M ...` | Nothing was touched. Free shards (see step 4) and re-run. |
| Want to try one program first | `django-admin es_reindex --program <uuid-or-code>` (or `--business-area <slug>`). |
