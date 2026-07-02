"""Reconcile a shadow Elasticsearch cluster with Postgres after the bulk copy.

Records keep changing in Postgres while the ES Index copy runs, so the shadow cluster drifts. This command brings it back in sync.

Postgres is the source of truth. Both ES documents populate from
``Individual.all_merge_status_objects`` / ``Household.objects`` and both models have
an indexed ``updated_at`` (``auto_now=True``), so "what changed since T" is a cheap,
exact query. For every program that changed, we rebuild its per-program index on the
shadow cluster (delete + create + populate). A full per-program rebuild is idempotent
and re-runnable, and it mirrors Postgres exactly for that program -- so it inherently
covers inserts, updates, soft-deletes *and* hard-deletes within the touched programs.

Two modes, usually run in sequence:

``--since``     Delta mode. Rebuild only programs with a record changed at/after the
                given timestamp. Use the time the bulk copy *started* (T0), minus a
                small safety buffer. Run this once or twice until it reports ~0
                programs, i.e. the cluster has caught up.

``--reconcile`` Safety net. For every in-scope program, compare ES doc count vs DB
                row count and rebuild any mismatch. Catches the one case ``--since``
                cannot: a pure hard-delete in a program with no other change (a
                hard-delete does not bump any sibling ``updated_at``). This is the
                "run again to be sure all data are the same" pass.

Examples
--------
Bulk copy started at 2026-07-01T09:00Z. After it finishes, catch up the delta::

    python manage.py es_populate_delta --using v9 --since 2026-07-01T08:55Z --parallel --threads 8

Run it again right before cutover to shrink the window further::

    python manage.py es_populate_delta --using v9 --since 2026-07-01T11:30Z

Final convergence check across all programs (counts must match)::

    python manage.py es_populate_delta --using v9 --reconcile --verify

Dry-run (print which programs would be rebuilt, no writes)::

    python manage.py es_populate_delta --using v9 --since 2026-07-01T08:55Z --dry-run

"""

from datetime import datetime
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from hope.apps.household.services.index_management import (
    check_program_indexes,
    rebuild_program_indexes,
)


class Command(BaseCommand):
    help = "Delta/reconcile per-program ES indexes on a shadow cluster against Postgres."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--using",
            default="v9",
            help="Connection alias from settings.ELASTICSEARCH_DSL (default: 'v9').",
        )
        parser.add_argument(
            "--since",
            default=None,
            help=(
                "ISO-8601 timestamp. Rebuild programs with an Individual/Household changed "
                "at/after this time. Use the bulk-copy start time minus a small buffer."
            ),
        )
        parser.add_argument(
            "--reconcile",
            action="store_true",
            help="Compare ES vs DB counts for all in-scope programs and rebuild mismatches.",
        )
        parser.add_argument(
            "--include-non-active",
            action="store_true",
            help="Include closed/finished programs (default: ACTIVE only).",
        )
        parser.add_argument(
            "--parallel",
            action="store_true",
            default=getattr(settings, "ELASTICSEARCH_POPULATE_PARALLEL", False),
            help="Use parallel_bulk for indexing.",
        )
        parser.add_argument(
            "--threads",
            type=int,
            default=getattr(settings, "ELASTICSEARCH_POPULATE_THREAD_COUNT", 4),
            help="Worker threads when --parallel is set.",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=getattr(settings, "ELASTICSEARCH_POPULATE_CHUNK_SIZE", 2000),
            help="Bulk chunk size.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only print the programs that would be rebuilt.",
        )
        parser.add_argument(
            "--verify",
            action="store_true",
            help="After each rebuild, run check_program_indexes() to confirm DB/ES counts match.",
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        using: str = opts["using"]
        if using not in settings.ELASTICSEARCH_DSL:
            raise CommandError(
                f"Connection alias '{using}' is not registered in settings.ELASTICSEARCH_DSL "
                f"(have: {list(settings.ELASTICSEARCH_DSL)}). "
                f"Set ELASTICSEARCH_HOST_V9 in env to register the 'v9' shadow cluster."
            )
        if not opts["since"] and not opts["reconcile"]:
            raise CommandError("Provide --since <timestamp> and/or --reconcile.")

        since = self._parse_since(opts["since"]) if opts["since"] else None

        from hope.models import Program

        scope = Program.objects.all() if opts["include_non_active"] else Program.objects.filter(status=Program.ACTIVE)
        code_by_id = dict(scope.values_list("id", "code"))
        scope_id_set = set(code_by_id)

        # 1) Programs changed since `since` (inserts / updates / soft-deletes).
        changed_ids = (self._changed_program_ids(since) & scope_id_set) if since is not None else set()
        if since is not None:
            self.stdout.write(f"Changed since {since.isoformat()}: {len(changed_ids)} program(s) in scope.")

        # 2) Programs whose ES vs DB counts disagree (catches hard-deletes).
        mismatch_ids = self._count_mismatch_ids(scope_id_set, using) if opts["reconcile"] else set()
        if opts["reconcile"]:
            self.stdout.write(f"Reconcile: {len(mismatch_ids)} program(s) need a rebuild (count/exists mismatch).")

        to_rebuild = changed_ids | mismatch_ids
        self.stdout.write(f"Target cluster: '{using}' -> {settings.ELASTICSEARCH_DSL[using]['hosts']}")
        self.stdout.write(f"Programs to rebuild: {len(to_rebuild)}")

        if opts["dry_run"]:
            self._print_dry_run(to_rebuild, changed_ids, mismatch_ids, code_by_id)
            return

        failures = self._rebuild_programs(to_rebuild, code_by_id, using, opts)
        if failures:
            raise CommandError(f"Done with {failures} failure(s) on cluster '{using}'.")
        self.stdout.write(self.style.SUCCESS(f"Done. Cluster '{using}' is in sync for the processed programs."))

    @staticmethod
    def _count_mismatch_ids(scope_id_set: set, using: str) -> set:
        return {pid for pid in scope_id_set if not check_program_indexes(str(pid), using=using)[0]}

    def _print_dry_run(self, to_rebuild: set, changed_ids: set, mismatch_ids: set, code_by_id: dict) -> None:
        for pid in sorted(to_rebuild, key=lambda p: code_by_id.get(p, "")):
            reasons = [r for r, group in (("changed", changed_ids), ("count-mismatch", mismatch_ids)) if pid in group]
            self.stdout.write(f"  - {code_by_id.get(pid)}  id={pid}  ({', '.join(reasons)})")

    def _rebuild_programs(self, to_rebuild: set, code_by_id: dict, using: str, opts: dict) -> int:
        failures = 0
        for pid in to_rebuild:
            self.stdout.write(f"==> Rebuilding {code_by_id.get(pid)} on '{using}' ...")
            ok, msg = rebuild_program_indexes(
                str(pid),
                batch_size=opts["chunk_size"],
                parallel=opts["parallel"],
                thread_count=opts["threads"],
                using=using,
            )
            line = self.style.SUCCESS if ok else self.style.ERROR
            self.stdout.write(line(f"    {msg or ('ok' if ok else 'failed')}"))
            if not ok:
                failures += 1
                continue
            if opts["verify"]:
                vok, vmsg = check_program_indexes(str(pid), using=using)
                self.stdout.write((self.style.SUCCESS if vok else self.style.WARNING)(f"    verify: {vmsg}"))
        return failures

    @staticmethod
    def _parse_since(raw: str) -> datetime:
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise CommandError(f"--since '{raw}' is not a valid ISO-8601 timestamp.") from exc
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    @staticmethod
    def _changed_program_ids(since: datetime) -> set:
        """Program ids with an Individual or Household changed at/after `since`.

        Uses the exact managers the ES documents populate from, so detection matches
        the index population set.
        """
        from hope.models import Household, Individual

        ind = (
            Individual.all_merge_status_objects.filter(updated_at__gte=since)
            .values_list("program_id", flat=True)
            .distinct()
        )
        hh = Household.objects.filter(updated_at__gte=since).values_list("program_id", flat=True).distinct()
        return {pid for pid in ind if pid is not None} | {pid for pid in hh if pid is not None}
