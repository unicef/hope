"""
Add `_rw` aliases over existing per-program ES concretes.

Run from Django shell:
    from hope.one_time_scripts.setup_rw_aliases import setup_rw_aliases
    setup_rw_aliases()

Semantics per program (Individual and Household):
    - alias already points at the expected concrete → skip
    - alias exists but points elsewhere → print warning, leave alone
    - alias missing, historical concrete exists → create alias → concrete
    - alias missing and no backing concrete → skip silently

Idempotent and safe to re-run after a partial failure.
"""

from django.conf import settings
from elasticsearch import Elasticsearch

from hope.apps.household.documents import (
    get_historical_household_concrete_name,
    get_historical_individual_concrete_name,
    get_household_alias_name,
    get_individual_alias_name,
)
from hope.models import Program


def _ensure_alias_over_existing_concrete(es: Elasticsearch, alias_name: str, historical_concrete: str) -> str:
    if es.indices.exists_alias(name=alias_name):
        backing = list(es.indices.get_alias(name=alias_name).keys())
        if backing == [historical_concrete]:
            return "already"
        print(f"[WARN] alias {alias_name} points at {backing}, expected [{historical_concrete}] — skipping")
        return "mismatch"

    if not es.indices.exists(index=historical_concrete):
        return "missing_concrete"

    es.indices.put_alias(index=historical_concrete, name=alias_name)
    return "created"


def setup_rw_aliases() -> None:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    counts = {"created": 0, "already": 0, "mismatch": 0, "missing_concrete": 0}

    for program in Program.objects.all().select_related("business_area"):
        pairs = (
            (get_individual_alias_name(program), get_historical_individual_concrete_name(program)),
            (get_household_alias_name(program), get_historical_household_concrete_name(program)),
        )
        for alias_name, historical_concrete in pairs:
            outcome = _ensure_alias_over_existing_concrete(es, alias_name, historical_concrete)
            counts[outcome] += 1
            if outcome == "created":
                print(f"created alias {alias_name} -> {historical_concrete}")

    print(
        f"Done: created={counts['created']} already={counts['already']} "
        f"mismatch={counts['mismatch']} missing_concrete={counts['missing_concrete']}"
    )
