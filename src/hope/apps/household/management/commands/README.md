# ES blue-green tooling (Milestone 1: alias bootstrap)

Commands in this directory support the zero-downtime Elasticsearch blue-green scheme: the app
addresses every per-program index by a suffix-less name, which after bootstrap is an ALIAS onto a
versioned physical index (`individuals_<ba>_<code>` -> `individuals_<ba>_<code>_v1`). Future
mapping changes then build `_vN+1` next to the live index and swap the alias atomically.

| Command | What |
|---------|------|
| `es_bootstrap_aliases` | One-time clone-first bootstrap: per active program (individuals + households), write-block the bare index, `_clone` it to `<name>_v1` (hard links, seconds), atomically replace the index with an alias of the same name, then sweep the freeze-window writes with a delta pass. Resumable from ES state, self-healing, ES-index lock, `--status` / `--dry-run`. See the command docstring for the exact sequence and the accepted hard-delete-during-freeze risk. |
| `es_populate_delta` | Incremental Postgres -> ES catch-up: upserts documents changed since `--since` (including embedded Document/Identity/Household changes), deletes soft-removed docs by `_id`, never deletes an index. `--reconcile` prints a read-only ES-vs-DB count drift report. |
| `es_mutate_stream` | Dev/rehearsal-only change-stream generator: mutates households/individuals in a loop and logs every change to JSONL so ES state can be asserted against it. Refuses to run outside `DEBUG` without `--i-am-sure`; soft-deletes are opt-in (`--delete-every`). |

## Typical rehearsal flow (ephemeral env)

```bash
python manage.py es_bootstrap_aliases --all --status     # expect: BARE everywhere, no aliases
python manage.py es_bootstrap_aliases --program <id>     # canary
python manage.py es_mutate_stream --i-am-sure            # separate shell: live-write noise
python manage.py es_bootstrap_aliases --all              # the real thing
python manage.py es_bootstrap_aliases --all --status     # expect: ALIAS -> _v1, es == db
```

Production = the same steps without the mutate stream, canary -> business area -> `--all`.
