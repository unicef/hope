"""Consistency check run before ``migrate`` while the baseline migrations carry ``replaces``.

The old migration files are gone, so Django cannot apply them any more. A database that has only a
part of the old chain would silently lose the missing migrations: Django drops the baseline node
from the graph and reports that there is nothing to do. See docs/guide-dev/migrations-baseline.md.
"""

from collections.abc import Collection, Iterable, Mapping

from django.db.migrations import Migration

# Was on develop under this name for five days (PR #5914 to PR #5941) before it was renumbered,
# so the dev database may still hold the row.
TOLERATED_STRAY_ROWS = {("core", "0023_migration")}

PARTIAL_REMEDY = (
    "Check out the commit right before the baseline (the migrations-checkpoint tag, or the parent of "
    "the baseline merge commit), run migrate there and come back. A new database whose first migrate "
    "was interrupted or targeted at a single migration has to be dropped and rebuilt."
)
STRAY_REMEDY = (
    "The database is ahead of this code: deploy or check out the code that contains these migrations, "
    "or rebuild a local database."
)


def baseline_violations(
    disk_migrations: Mapping[tuple[str, str], Migration],
    applied: Iterable[tuple[str, str]],
    labels: Collection[str],
) -> list[str]:
    """Return one message per app whose ``django_migrations`` rows cannot be migrated safely.

    Only apps in ``labels`` are checked. Two states are refused: the old migrations replaced by the
    app's baseline files are applied in part (neither all nor none), or the app has an applied row
    that is neither on disk nor replaced by the baseline.
    """
    applied = set(applied)
    violations = []
    for label in sorted(labels):
        on_disk = {key for key in disk_migrations if key[0] == label}
        replaced = {replaced_key for key in on_disk for replaced_key in disk_migrations[key].replaces}
        applied_here = {key for key in applied if key[0] == label}
        missing = replaced - applied_here
        if missing and missing != replaced:
            violations.append(
                f"{label}: {len(missing)} of the {len(replaced)} migrations replaced by the baseline are not "
                f"applied in this database: {_names(missing)}. {PARTIAL_REMEDY}"
            )
        stray = applied_here - on_disk - replaced - TOLERATED_STRAY_ROWS
        if stray:
            violations.append(
                f"{label}: django_migrations has rows that are neither on disk nor replaced by the baseline: "
                f"{_names(stray)}. {STRAY_REMEDY}"
            )
    return violations


def _names(keys: Iterable[tuple[str, str]]) -> str:
    return ", ".join(f"{app_label}.{name}" for app_label, name in sorted(keys))
