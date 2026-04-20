"""
Migrate pre-alias concretes to the aliased `_v1` shape.

Run from Django shell:
    from hope.one_time_scripts.migrate_to_aliased_v1 import migrate_to_aliased_v1
    migrate_to_aliased_v1()

Per program and document kind:
    Expected:   concrete named `<base>` (pre-alias state).
    Outcome:    concrete cloned to `<base>_v1`, old concrete removed, alias
                `<base>` now points at `<base>_v1`. Data preserved — clone
                is a segment-level copy, not a reindex.

States handled:
    - already migrated (alias exists, points at `<base>_v1`)  → skip
    - alias exists pointing elsewhere                          → warn, leave alone
    - no concrete and no clone                                 → skip (program never indexed)
    - concrete exists without alias                            → migrate
    - partial (clone exists but swap didn't complete)          → finish the swap

Idempotent; re-run after partial failure completes the work.

Per-index migration briefly blocks writes on the source during clone + swap
(seconds for small indices, minutes for very large ones). HOPE signal
handlers log and swallow write errors during this window; affected rows
re-sync on next save.
"""

from django.conf import settings
from elasticsearch import Elasticsearch

from hope.apps.household.documents import (
    get_household_alias_name,
    get_individual_alias_name,
    initial_concrete_for_alias,
)
from hope.models import Program


def _migrate_one(es: Elasticsearch, alias_name: str) -> str:
    concrete_v1 = initial_concrete_for_alias(alias_name)

    if es.indices.exists_alias(name=alias_name):
        backing = list(es.indices.get_alias(name=alias_name).keys())
        if backing == [concrete_v1]:
            return "already"
        print(f"[WARN] alias {alias_name} points at {backing}, expected [{concrete_v1}] — skipping")
        return "mismatch"

    source_exists = es.indices.exists(index=alias_name)
    clone_exists = es.indices.exists(index=concrete_v1)

    if not source_exists and not clone_exists:
        return "missing"

    if source_exists and not clone_exists:
        es.indices.put_settings(index=alias_name, settings={"index.blocks.write": True})
        es.indices.clone(index=alias_name, target=concrete_v1, timeout="60s")

    es.indices.put_settings(index=concrete_v1, settings={"index.blocks.write": False})

    if source_exists:
        es.indices.update_aliases(actions=[
            {"remove_index": {"index": alias_name}},
            {"add": {"index": concrete_v1, "alias": alias_name}},
        ])
    else:
        es.indices.put_alias(index=concrete_v1, name=alias_name)

    print(f"migrated {alias_name} -> {concrete_v1}")
    return "migrated"


def migrate_to_aliased_v1() -> None:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    counts = {"migrated": 0, "already": 0, "mismatch": 0, "missing": 0}

    for program in Program.objects.all().select_related("business_area"):
        for alias_name in (get_individual_alias_name(program), get_household_alias_name(program)):
            counts[_migrate_one(es, alias_name)] += 1

    print(
        f"Done: migrated={counts['migrated']} already={counts['already']} "
        f"mismatch={counts['mismatch']} missing={counts['missing']}"
    )
