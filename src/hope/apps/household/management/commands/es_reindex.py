"""Blue-green reindex: build a dark ``_vN+1`` next to each live per-program index, swap the alias.

Prerequisite: every in-scope index name IS an alias (run ``es_bootstrap_aliases`` first - this
command refuses bare/missing indexes rather than half-reimplementing the bootstrap). A program's
individuals+households pair is reindexed as ONE unit:

1. compute ONE next version for the pair - ``max`` over both indexes' existing ``_vN`` numbers
   + 1, so the pair advances in lockstep and a single delta ``--target-suffix`` covers both,
2. create both dark ``_vN+1`` indexes from the CODE mapping (no alias - the app keeps reading
   and writing the old version, completely unaffected),
3. full-populate both dark indexes from Postgres,
4. one ``es_populate_delta --target-suffix`` pass for rows changed during the populate,
5. verify: refresh + doc count, dark index vs Postgres, per index. On a mismatch (live writes
   race the check) ONE extra delta pass runs and the count is re-checked; still off -> abort
   BEFORE the swap, alias untouched,
6. ONE atomic ``_aliases`` call moves BOTH aliases old -> new (``must_exist`` removes + adds,
   4 actions) - a program is never half-swapped - then a postcondition read-back,
7. two post-swap delta passes through the now-live alias close the remaining race window
   (each pass re-reads fresh Postgres state; last write wins).

The old ``_vN`` stays in place unaliased = instant rollback target (flip the alias back by hand,
see the runbook) until ``es_drop_old_index_versions`` removes it after the 24-72h sanity window.

Crash/resume: state never needs reconstructing - a dark leftover from a killed run is simply
abandoned (the next run picks a higher version; ``es_drop_old_index_versions`` sweeps unaliased
leftovers) and an already-swapped program shows its new version in ``--status``. Re-running the
command is always safe; it reindexes every in-scope program again (there is deliberately no
"mapping unchanged, skip" detection - the operator decides when a reindex is due).

Examples
--------
Preview, then reindex everything::

    django-admin es_reindex --all --dry-run
    django-admin es_reindex --all

One program first (canary), or one business area::

    django-admin es_reindex --program <uuid-or-code>
    django-admin es_reindex --business-area afghanistan

Read-only state report::

    django-admin es_reindex --all --status

"""

from typing import Any
import uuid

from constance import config
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from elasticsearch import BadRequestError, Elasticsearch
from elasticsearch.dsl import connections

from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.services.index_management import (
    create_versioned_index,
    existing_version_numbers,
    next_version_suffix,
    versioned_doc,
)
from hope.apps.utils.elasticsearch_utils import populate_index

DELTA_SINCE_BUFFER_MINUTES = 5


class Command(BaseCommand):
    help = (
        "Blue-green reindex of per-program ES indexes: build a dark _vN+1 pair from the code "
        "mapping, catch up, atomically swap both aliases. The old version stays for rollback "
        "until es_drop_old_index_versions."
    )

    # Same ES-index-as-mutex trick as es_bootstrap_aliases (create is atomic, fails if exists).
    LOCK_INDEX = f"{settings.ELASTICSEARCH_INDEX_PREFIX}es-reindex-lock"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--program", default=None, help="Reindex a single program (UUID or code).")
        parser.add_argument("--business-area", default=None, help="Reindex every active program in this BA (slug).")
        parser.add_argument("--all", action="store_true", help="Reindex every active program.")
        parser.add_argument("--status", action="store_true", help="Read-only per-index state report, then exit.")
        parser.add_argument("--dry-run", action="store_true", help="Print the per-program plan without touching ES.")
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=getattr(settings, "ELASTICSEARCH_POPULATE_CHUNK_SIZE", 2000),
            help="Bulk chunk size for the full populate.",
        )
        parser.add_argument(
            "--force-unlock",
            action="store_true",
            help="Remove a stale lock left by a crashed run, then continue.",
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        if sum([bool(opts["program"]), bool(opts["business_area"]), opts["all"]]) != 1:
            raise CommandError("Provide exactly one scope: --program, --business-area or --all.")
        if not config.IS_ELASTICSEARCH_ENABLED:
            raise CommandError("IS_ELASTICSEARCH_ENABLED is off - populate would silently no-op. Aborting.")

        es: Elasticsearch = connections.get_connection()
        code_by_id = self._scope(opts)
        if not code_by_id:
            self.stdout.write(self.style.WARNING("No active programs in scope - nothing to do."))
            return
        if opts["program"] and len(code_by_id) > 1:
            raise CommandError(
                f"--program '{opts['program']}' matches {len(code_by_id)} programs "
                f"(a program code is only unique per business area). "
                f"Use the program UUID or add --business-area."
            )

        if opts["status"]:
            self._report_status(es, code_by_id)
            return
        if opts["dry_run"]:
            self._report_plan(es, code_by_id)
            return

        self._acquire_lock(es, force=opts["force_unlock"])
        try:
            failed = self._reindex_programs(es, code_by_id, opts)
        finally:
            self._release_lock(es)

        if failed:
            raise CommandError(f"{len(failed)} program(s) failed: {[f'{c}: {m}' for c, _, m in failed]}")

    @staticmethod
    def _scope(opts: dict) -> dict:
        from hope.models import Program

        qs = Program.objects.filter(status=Program.ACTIVE)
        if opts["business_area"]:
            qs = qs.filter(business_area__slug=opts["business_area"])
        if opts["program"]:
            try:
                uuid.UUID(str(opts["program"]))
                qs = qs.filter(id=opts["program"])
            except (ValueError, AttributeError):
                qs = qs.filter(code=opts["program"])
        return dict(qs.values_list("id", "code"))

    def _doc_classes(self, pid: str) -> list:
        return [get_individual_doc(pid), get_household_doc(pid)]

    @staticmethod
    def _alias_target(es: Elasticsearch, name: str) -> str | None:
        if not es.indices.exists_alias(name=name):
            return None
        return next(iter(es.indices.get_alias(name=name)))

    def _report_status(self, es: Elasticsearch, code_by_id: dict) -> None:
        for pid, code in sorted(code_by_id.items(), key=lambda kv: kv[1] or ""):
            for doc_class in self._doc_classes(str(pid)):
                name = doc_class._index._name
                target = self._alias_target(es, name)
                versions = sorted(existing_version_numbers(es, name))
                if target is None:
                    detail = "NOT AN ALIAS (run es_bootstrap_aliases)"
                    es_count = "-"
                else:
                    detail = f"ALIAS -> {target}"
                    es_count = es.count(index=name)["count"]
                db_count = doc_class().get_queryset().count()
                self.stdout.write(f"{code}  {name}: {detail}  versions={versions}  es={es_count} db={db_count}")

    def _report_plan(self, es: Elasticsearch, code_by_id: dict) -> None:
        for pid, code in sorted(code_by_id.items(), key=lambda kv: kv[1] or ""):
            docs = self._doc_classes(str(pid))
            names = [d._index._name for d in docs]
            not_aliased = [n for n in names if self._alias_target(es, n) is None]
            if not_aliased:
                self.stdout.write(f"{code}: SKIP - not an alias yet: {not_aliased} (run es_bootstrap_aliases)")
                continue
            suffix = next_version_suffix(es, docs)
            current = {n: self._alias_target(es, n) for n in names}
            self.stdout.write(f"{code}: REINDEX {list(current.values())} -> _{suffix}, then swap both aliases")

    def _acquire_lock(self, es: Elasticsearch, force: bool) -> None:
        if force:
            es.options(ignore_status=[404]).indices.delete(index=self.LOCK_INDEX)
        try:
            es.indices.create(index=self.LOCK_INDEX)
        except BadRequestError as exc:
            raise CommandError(
                f"Another reindex run holds the lock ({self.LOCK_INDEX}). If it crashed, re-run with --force-unlock."
            ) from exc

    def _release_lock(self, es: Elasticsearch) -> None:
        es.options(ignore_status=[404]).indices.delete(index=self.LOCK_INDEX)

    def _reindex_programs(self, es: Elasticsearch, code_by_id: dict, opts: dict) -> list:
        total = len(code_by_id)
        failed: list = []
        for n, (pid, code) in enumerate(sorted(code_by_id.items(), key=lambda kv: kv[1] or ""), start=1):
            try:
                outcome = self._reindex_program(es, str(pid), opts)
            except Exception as exc:  # noqa: BLE001  # one bad program must not abort the fleet
                outcome = f"FAILED - {exc}"
                failed.append((code, pid, str(exc)))
            style = self.style.ERROR if outcome.startswith("FAILED") else self.style.SUCCESS
            self.stdout.write(style(f"[{n}/{total}] {code}: {outcome}"))
        return failed

    def _reindex_program(self, es: Elasticsearch, pid: str, opts: dict) -> str:
        docs = self._doc_classes(pid)
        names = [d._index._name for d in docs]
        old = {}
        for name in names:
            target = self._alias_target(es, name)
            if target is None:
                raise CommandError(f"{name} is not an alias - run es_bootstrap_aliases first")
            old[name] = target

        suffix = next_version_suffix(es, docs)
        vdocs = [versioned_doc(d, suffix) for d in docs]

        populate_start = timezone.now()
        for doc_class in docs:
            create_versioned_index(es, doc_class, suffix=suffix, attach_alias=False)
        for vdoc in vdocs:
            populate_index(vdoc().get_queryset(), vdoc, chunk_size=opts["chunk_size"])

        delta_start = timezone.now()
        self._delta(pid, since=populate_start, target_suffix=suffix)
        self._verify_dark(es, pid, vdocs, suffix, anchor=delta_start)

        self._swap(es, old, suffix)

        # two passes: the first covers writes since the pre-swap delta started, the second the
        # (seconds-long) window of the first - both write through the now-live alias
        final_start = timezone.now()
        self._delta(pid, since=delta_start)
        self._delta(pid, since=final_start)
        return f"reindexed {list(old.values())} -> _{suffix}, aliases swapped (old kept for rollback)"

    def _verify_dark(self, es: Elasticsearch, pid: str, vdocs: list, suffix: str, anchor: Any) -> None:
        """Gate before the swap: each dark index must match Postgres exactly.

        The new index is built FROM Postgres, so unlike the bootstrap (which preserves whatever
        drift prod ES has) an exact DB comparison is the correct check here. Live writes can race
        the first check - one extra delta pass absorbs them before we call it a failure.
        """
        if self._count_mismatches(es, vdocs) == []:
            return
        self._delta(pid, since=anchor, target_suffix=suffix)
        mismatches = self._count_mismatches(es, vdocs)
        if mismatches:
            raise CommandError(f"verify failed, aborting before swap (alias untouched): {'; '.join(mismatches)}")

    @staticmethod
    def _count_mismatches(es: Elasticsearch, vdocs: list) -> list[str]:
        mismatches = []
        for vdoc in vdocs:
            target = vdoc._index._name
            es.indices.refresh(index=target)
            db_count = vdoc().get_queryset().count()
            es_count = es.count(index=target)["count"]
            if db_count != es_count:
                mismatches.append(f"{target}: es={es_count} db={db_count}")
        return mismatches

    @staticmethod
    def _swap(es: Elasticsearch, old: dict, suffix: str) -> None:
        # ONE atomic call for the whole pair: must_exist makes a lost race (someone moved the
        # alias meanwhile) an error instead of a silent double-add
        actions: list = []
        for name, old_target in old.items():
            actions.append({"remove": {"index": old_target, "alias": name, "must_exist": True}})
            actions.append({"add": {"index": f"{name}_{suffix}", "alias": name}})
        es.indices.update_aliases(actions=actions)
        for name in old:
            aliased = set(es.indices.get_alias(name=name))
            if aliased != {f"{name}_{suffix}"}:
                raise CommandError(
                    f"postcondition failed: alias {name} points at {aliased}, expected {{{name}_{suffix}}}"
                )

    @staticmethod
    def _delta(pid: str, since: Any, target_suffix: str | None = None) -> None:
        kwargs = {
            "since": (since - timezone.timedelta(minutes=DELTA_SINCE_BUFFER_MINUTES)).isoformat(),
            "program": pid,
        }
        if target_suffix:
            kwargs["target_suffix"] = target_suffix
        call_command("es_populate_delta", **kwargs)
