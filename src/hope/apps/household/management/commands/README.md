# ES blue-green tooling

Commands in this directory support the zero-downtime Elasticsearch blue-green scheme: the app
addresses every per-program index by a suffix-less name, which after bootstrap is an ALIAS onto a
versioned physical index (`individuals_<ba>_<code>` -> `individuals_<ba>_<code>_v1`). Mapping
changes then build `_vN+1` next to the live index and swap the alias atomically.

| Command | What |
|---------|------|
| `es_bootstrap_aliases` | One-time clone-first bootstrap: per active program (individuals + households), write-block the bare index, `_clone` it to `<name>_v1` (hard links, seconds), atomically replace the index with an alias of the same name, then sweep the freeze-window writes with a delta pass. Resumable from ES state, self-healing, ES-index lock, `--status` / `--dry-run`. See the command docstring for the exact sequence and the accepted hard-delete-during-freeze risk. |
| `es_reindex` | The recurring blue-green reindex (requires bootstrap done): per program, create a dark `_vN+1` pair from the code mapping (one lockstep version for both indexes), full-populate, one delta `--target-suffix` catch-up pass, count-verify vs Postgres (one retry delta, abort before swap on mismatch), ONE atomic 4-action alias swap (`must_exist` + postcondition), two post-swap delta passes. The old version stays unaliased as an instant rollback target. Crash recovery = rebuild: dark wrecks newer than the alias target are deleted and their number reused (contents of a wreck are never trusted). |
| `es_drop_old_index_versions` | Sweep unaliased `_vN` leftovers days after a reindex (old versions past their sanity window, dark wrecks of crashed runs). Never touches the alias target or anything aliased; prints-only unless `--confirm`. |
| `es_populate_delta` | Incremental Postgres -> ES catch-up: upserts documents changed since `--since` (including embedded Document/Identity/Household changes), deletes soft-removed docs by `_id`, never deletes an index. `--target-suffix vN` writes into a dark `_vN` pair instead of through the alias (missing target = error). `--reconcile` prints a read-only ES-vs-DB count drift report. Normally called internally by the two commands above; stays usable standalone for ad-hoc drift fixes. |
| `es_mutate_stream` | Dev/rehearsal-only change-stream generator: mutates households/individuals in a loop and logs every change to JSONL so ES state can be asserted against it. Refuses to run outside `DEBUG` without `--i-am-sure`; soft-deletes are opt-in (`--delete-every`). |

## Typical rehearsal flow (ephemeral env)

```bash
# Milestone 1 - bootstrap (one-time)
django-admin es_bootstrap_aliases --all --status     # expect: BARE everywhere, no aliases
django-admin es_bootstrap_aliases --program <id>     # canary
django-admin es_mutate_stream --i-am-sure            # separate shell: live-write noise
django-admin es_bootstrap_aliases --all              # the real thing
django-admin es_bootstrap_aliases --all --status     # expect: ALIAS -> _v1, es == db

# Milestone 2 - reindex (recurring, after any mapping change)
django-admin es_reindex --all --status               # expect: ALIAS -> _vN everywhere
django-admin es_reindex --program <id>               # canary
django-admin es_reindex --all                        # the real thing
# ... 24-72h sanity window (old _vN = instant rollback: flip the alias back) ...
django-admin es_drop_old_index_versions --all        # list leftovers
django-admin es_drop_old_index_versions --all --confirm
```

Production = the same steps without the mutate stream, canary -> business area -> `--all`.
