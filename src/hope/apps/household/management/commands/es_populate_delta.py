"""Catch up a shadow Elasticsearch cluster with Postgres after the bulk copy, incrementally.

Records keep changing in Postgres while the ES bulk copy runs, so the shadow cluster drifts.
This command closes that gap **without ever deleting an index**: it loops the in-scope programs
and, for each one that has a delta since ``--since``, writes only the changed documents into the
existing per-program index (upsert changed, delete the docs of soft-removed records). A program
whose index does not exist yet (e.g. created during the window) is the only full-populate case:
we create the index and populate the whole program.

Postgres is the source of truth. The Individual/Household ES documents embed related objects, so a
change is any of:

* Individual (base)   -> ``updated_at``
* Household (base)    -> ``updated_at``
* Document            -> ``updated_at`` (embedded in individual.documents and
                         household.head_of_household.documents)
* IndividualIdentity  -> ``modified`` (model_utils TimeStampedModel; embedded in individual.identities)

A soft-delete bumps ``updated_at`` and sets ``is_removed=True``; such records are removed from ES
by ``_id`` (the document, never the index).

Known gaps, out of scope for this incremental pass (need a separate full ``es_shadow_populate``):

* Reference-data rename (Partner / Area / Country / DocumentType): touches documents across many
  programs with no per-program key -- only reported here as a warning, not applied.
* Hard-delete (row physically gone): ``--since`` cannot see it, so its ES document is left orphaned.
  A future ``--reconcile`` id-diff pass would remove such orphans.

The shadow cluster is selected by pointing the pod's ELASTICSEARCH_HOST env at it; the 'default'
connection then writes there.

Examples
--------
Catch up all active programs from the bulk-copy start time (minus a small buffer)::

    python manage.py es_populate_delta --since 2026-07-01T08:55Z --parallel --threads 8

Dry-run -- print each program's delta without writing::

    python manage.py es_populate_delta --since 2026-07-01T08:55Z --dry-run

Narrow to a single program or a whole business area::

    python manage.py es_populate_delta --since 2026-07-01T08:55Z --program my-program-code
    python manage.py es_populate_delta --since 2026-07-01T08:55Z --business-area afghanistan

Report count drift (ES vs DB) without touching anything::

    python manage.py es_populate_delta --reconcile

"""

from datetime import datetime
from typing import Any
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from hope.apps.household.services.index_management import (
    check_program_indexes,
    create_program_indexes,
    populate_program_indexes,
)


class Command(BaseCommand):
    help = (
        "Incrementally catch up per-program ES indexes on a shadow cluster against Postgres: "
        "upsert only changed documents, never delete an index. "
        "Shadow cluster is the one that waits to be plugged into prod and replace the current one."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--using",
            default="default",
            help=(
                "Connection alias from settings.ELASTICSEARCH_DSL (default: 'default'). "
                "Point the pod's ELASTICSEARCH_HOST at the shadow cluster and 'default' writes there."
            ),
        )
        parser.add_argument(
            "--since",
            default=None,
            help=(
                "ISO-8601 timestamp. Sync programs with an Individual/Household/Document/Identity "
                "changed at/after this time. Use the bulk-copy start time minus a small buffer."
            ),
        )
        parser.add_argument(
            "--reconcile",
            action="store_true",
            help="Report ES-vs-DB count drift per in-scope program (read-only, no writes).",
        )
        parser.add_argument(
            "--include-non-active",
            action="store_true",
            help="Include closed/finished programs (default: ACTIVE only).",
        )
        parser.add_argument(
            "--program",
            default=None,
            help="Limit scope to a single program (UUID or code). Handy to sync a small sample first.",
        )
        parser.add_argument(
            "--business-area",
            default=None,
            help="Limit scope to a business area (slug). Combine with --program to narrow further.",
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
            help="Print each program's delta (and full-populate/no-delta status) without writing.",
        )
        parser.add_argument(
            "--verify",
            action="store_true",
            help="After each program, run check_program_indexes() to confirm DB/ES counts match.",
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        using: str = opts["using"]
        if using not in settings.ELASTICSEARCH_DSL:
            raise CommandError(
                f"Connection alias '{using}' is not registered in settings.ELASTICSEARCH_DSL "
                f"(have: {list(settings.ELASTICSEARCH_DSL)}). "
                f"Use --using default and point the pod's ELASTICSEARCH_HOST at the shadow cluster."
            )
        if not opts["since"] and not opts["reconcile"]:
            raise CommandError("Provide --since <timestamp> and/or --reconcile.")

        self._print_server_version(using)

        from hope.models import Program

        scope = Program.objects.all() if opts["include_non_active"] else Program.objects.filter(status=Program.ACTIVE)
        scope = self._apply_scope_filters(scope, opts)
        code_by_id = dict(scope.values_list("id", "code"))
        if (opts["program"] or opts["business_area"]) and not code_by_id:
            self.stdout.write(self.style.WARNING("No programs match --program / --business-area (nothing to do)."))
            return

        if opts["reconcile"]:
            self._report_reconcile(code_by_id, using)

        if not opts["since"]:
            return

        since = self._parse_since(opts["since"])
        self._warn_reference_data(since)
        self.stdout.write(f"Target cluster: '{using}' -> {settings.ELASTICSEARCH_DSL[using]['hosts']}")
        self._sync_programs(code_by_id, since, using, opts)

    def _sync_programs(self, code_by_id: dict, since: datetime, using: str, opts: dict) -> None:
        # Loop every in-scope program and compute its delta *inside* the program (queries scoped to
        # program_id=pid) -- deliberately no single cross-program scan over all Individuals/Households/
        # Documents. A brand-new program (no index yet) lands in the missing-index full-populate branch.
        total = len(code_by_id)
        self.stdout.write(f"Scanning {total} in-scope program(s) for a delta since {since.isoformat()} ...")

        failed: list = []
        synced = 0
        for n, (pid, code) in enumerate(sorted(code_by_id.items(), key=lambda kv: kv[1] or ""), start=1):
            try:
                status, msg = self._process_program(str(pid), since, using, opts)
            except Exception as exc:  # noqa: BLE001  # one bad program must not abort the whole run
                status, msg = "failed", str(exc)
            style = self.style.ERROR if status == "failed" else self.style.SUCCESS
            self.stdout.write(style(f"[{n}/{total}] {code} id={pid}: {status} -- {msg}"))
            if status == "failed":
                failed.append((code, pid, msg))
                continue
            if status != "no delta":
                synced += 1
            if opts["verify"] and not opts["dry_run"]:
                vok, vmsg = check_program_indexes(str(pid))
                self.stdout.write((self.style.SUCCESS if vok else self.style.WARNING)(f"    verify: {vmsg}"))

        if failed:
            self.stdout.write(self.style.ERROR(f"Failed programs ({len(failed)}):"))
            for code, pid, msg in failed:
                self.stdout.write(self.style.ERROR(f"  - {code}  id={pid}  {msg}"))
            raise CommandError(f"Done with {len(failed)} failure(s) on cluster '{using}'.")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Cluster '{using}': {synced} of {total} program(s) had work, rest already in sync."
            )
        )

    def _process_program(self, pid: str, since: datetime, using: str, opts: dict) -> tuple[str, str]:
        """Sync one program: full-populate if the index is missing, else upsert/delete only the delta."""
        from elasticsearch.dsl import connections

        from hope.apps.household.documents import get_household_doc, get_individual_doc

        ind_doc = get_individual_doc(pid)
        hh_doc = get_household_doc(pid)
        es = connections.get_connection(using)
        ind_index = ind_doc._index._name
        hh_index = hh_doc._index._name

        # New program: no index yet -> create + full populate (this is the ONLY full-populate path).
        if not es.indices.exists(index=ind_index) or not es.indices.exists(index=hh_index):
            if opts["dry_run"]:
                return "would-populate (no index)", f"index {ind_index} / {hh_index}"
            ok, msg = create_program_indexes(pid)
            if ok:
                ok, msg = populate_program_indexes(pid, batch_size=opts["chunk_size"])
            return ("populated (new index)", msg) if ok else ("failed", msg)

        delta = self._program_delta(pid, since)
        counts = (
            f"ind +{len(delta['ind_present'])}/-{len(delta['ind_removed'])} "
            f"hh +{len(delta['hh_present'])}/-{len(delta['hh_removed'])}"
        )
        if not any(delta.values()):
            return "no delta", counts
        if opts["dry_run"]:
            return "would-sync delta", counts

        self._apply_delta(pid, delta, ind_doc, hh_doc, opts)
        return "delta synced", counts

    @staticmethod
    def _apply_delta(pid: str, delta: dict, ind_doc: type, hh_doc: type, opts: dict) -> None:
        from hope.apps.utils.elasticsearch_utils import remove_elasticsearch_documents_by_matching_ids
        from hope.models import Household, Individual

        chunk = opts["chunk_size"]
        parallel = opts["parallel"]
        if delta["ind_present"]:
            qs = Individual.all_merge_status_objects.filter(id__in=delta["ind_present"]).iterator(chunk_size=chunk)
            ind_doc().update(qs, action="index", parallel=parallel)
        if delta["hh_present"]:
            qs = Household.objects.filter(id__in=delta["hh_present"]).iterator(chunk_size=chunk)
            hh_doc().update(qs, action="index", parallel=parallel)
        if delta["ind_removed"]:
            remove_elasticsearch_documents_by_matching_ids([str(i) for i in delta["ind_removed"]], ind_doc)
        if delta["hh_removed"]:
            remove_elasticsearch_documents_by_matching_ids([str(i) for i in delta["hh_removed"]], hh_doc)

    @staticmethod
    def _program_delta(pid: str, since: datetime) -> dict:
        """Ids of this program's records to upsert (present) or delete (soft-removed) in ES.

        Mirrors ``get_instances_from_related`` in documents.py (which side-object change forces which
        document to re-index):

        * present individuals = changed directly, or owning a changed Document/Identity, or whose
          household changed (individual doc embeds household.unicef_id / admin1 / admin2)
        * present households = changed directly, or whose head_of_household changed, or whose
          head_of_household owns a changed Document (household doc embeds the head's own fields + docs)
        * removed = soft-deleted (updated_at bumped, is_removed=True); a record both changed and
          removed goes to removed.

        Per-program scoping keeps the unindexed IndividualIdentity.modified join cheap: it starts from
        this program's individuals (indexed program_id) and joins identities by FK, not a full scan.
        """
        from hope.models import Household, Individual

        ind_present = set(
            Individual.all_merge_status_objects.filter(program_id=pid)
            .filter(updated_at__gte=since)
            .values_list("id", flat=True)
        )
        ind_present |= set(
            Individual.all_merge_status_objects.filter(program_id=pid, documents__updated_at__gte=since)
            .values_list("id", flat=True)
            .distinct()
        )
        ind_present |= set(
            Individual.all_merge_status_objects.filter(program_id=pid, identities__modified__gte=since)
            .values_list("id", flat=True)
            .distinct()
        )
        # Individual doc embeds household.unicef_id / admin1 / admin2 -> a household change
        # re-indexes its members (mirrors get_instances_from_related: Household -> individuals.all()).
        ind_present |= set(
            Individual.all_merge_status_objects.filter(program_id=pid, household__updated_at__gte=since)
            .values_list("id", flat=True)
            .distinct()
        )
        ind_removed = set(
            Individual.all_objects.filter(program_id=pid, is_removed=True, updated_at__gte=since).values_list(
                "id", flat=True
            )
        )
        ind_present -= ind_removed

        hh_present = set(
            Household.objects.filter(program_id=pid).filter(updated_at__gte=since).values_list("id", flat=True)
        )
        hh_present |= set(
            Household.objects.filter(program_id=pid, head_of_household__documents__updated_at__gte=since)
            .values_list("id", flat=True)
            .distinct()
        )
        # Household doc embeds head_of_household's own fields (given_name, full_name, phone...) ->
        # a change to the head individual re-indexes the household. This is what es_mutate_stream bumps.
        hh_present |= set(
            Household.objects.filter(program_id=pid, head_of_household__updated_at__gte=since)
            .values_list("id", flat=True)
            .distinct()
        )
        hh_removed = set(
            Household.all_objects.filter(program_id=pid, is_removed=True, updated_at__gte=since).values_list(
                "id", flat=True
            )
        )
        hh_present -= hh_removed
        return {
            "ind_present": ind_present,
            "ind_removed": ind_removed,
            "hh_present": hh_present,
            "hh_removed": hh_removed,
        }

    def _print_server_version(self, using: str) -> None:
        # Confirm which ES server we are about to write to (host + version) before any work.
        from elasticsearch.dsl import connections

        host = settings.ELASTICSEARCH_DSL[using]["hosts"]
        try:
            info = connections.get_connection(using).info()
            version = info["version"]["number"]
            cluster = info.get("cluster_name", "?")
            self.stdout.write(self.style.SUCCESS(f"ES '{using}' -> {host} | cluster={cluster} version={version}"))
        except Exception as exc:  # noqa: BLE001  # surface a clear connection error instead of a later traceback
            raise CommandError(f"Cannot reach ES '{using}' at {host}: {exc}") from exc

    def _report_reconcile(self, code_by_id: dict, using: str) -> None:
        # Read-only drift report. Rebuilding a mismatch would mean deleting the index -- not allowed
        # here; orphan cleanup (hard-deletes) is a separate id-diff pass, not built yet.
        mismatched = []
        for pid, code in code_by_id.items():
            ok, msg = check_program_indexes(str(pid))
            if not ok:
                mismatched.append((code, pid, msg))
        self.stdout.write(f"Reconcile (read-only): {len(mismatched)} of {len(code_by_id)} program(s) drift.")
        for code, pid, msg in mismatched:
            self.stdout.write(self.style.WARNING(f"  - {code}  id={pid}  {msg}"))

    def _warn_reference_data(self, since: datetime) -> None:
        ref_changed = self._reference_data_changed(since)
        if ref_changed:
            self.stdout.write(
                self.style.WARNING(
                    f"Reference data changed since {since.isoformat()} ({', '.join(ref_changed)}); "
                    f"this spans many programs with no per-program key and is NOT applied by the delta -- "
                    f"run a full es_shadow_populate for those."
                )
            )

    @staticmethod
    def _apply_scope_filters(scope: Any, opts: dict) -> Any:
        if opts["business_area"]:
            scope = scope.filter(business_area__slug=opts["business_area"])
        program = opts["program"]
        if program:
            try:
                uuid.UUID(str(program))
                scope = scope.filter(id=program)
            except (ValueError, AttributeError):
                scope = scope.filter(code=program)
        return scope

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
    def _reference_data_changed(since: datetime) -> list[str]:
        """Return names of embedded reference tables (no per-program key) changed at/after `since`.

        A change to any of these can invalidate documents across every program, so it cannot be
        narrowed to record ids. The check is cheap: an indexed ``updated_at`` existence probe.
        Partner (identities.partner.name) has no timestamp field and is undetectable here.
        """
        from hope.models import Area, BusinessArea, Country, DocumentType

        checks = {
            "DocumentType": DocumentType,  # documents.key (type.key)
            "Country": Country,  # documents.country (iso_code3)
            "Area": Area,  # admin1 / admin2 (name)
            "BusinessArea": BusinessArea,  # business_area (slug)
        }
        return [name for name, model in checks.items() if model.objects.filter(updated_at__gte=since).exists()]
