"""Blue-green reindex: build a dark ``_vN+1`` next to each live per-program index, swap the alias.

Prerequisite: every in-scope index name IS an alias (run ``es_bootstrap_aliases`` first - this
command refuses bare/missing indexes rather than half-reimplementing the bootstrap). A program's
individuals+households pair is reindexed as ONE unit:

1. compute ONE next version for the pair - highest ALIAS-TARGET version of the pair + 1, so
   the pair advances in lockstep and a single delta ``--target-suffix`` covers both,
2. create both dark ``_vN+1`` indexes from the CODE mapping (no alias - the app keeps reading
   and writing the old version, completely unaffected); a matching leftover from a previous
   run is RESUMED instead (see Crash/resume below),
3. full-populate the freshly-created dark indexes from Postgres (resumed ones skip this),
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

Crash/resume: the working version is DETERMINISTIC - alias target version + 1 (max over the
pair) - so a re-run lands on the same dark pair a previous run left behind and RESUMES it
instead of rebuilding:

* the leftover's ``mappings._meta.hope_mapping_hash`` stamp (written at creation) must equal
  the hash of the CURRENT code mapping - a wreck from an older deployment is deleted and
  rebuilt under the same number, automatically;
* a resumed index skips the full populate; the catch-up delta runs from the index's own
  ``creation_date``, which covers everything the previous run could have missed changing;
* a HALF-POPULATED wreck (killed mid-populate) cannot be topped up by a delta - the verify
  gate catches it (counts vs Postgres) and the error says to re-run with ``--sweep-wrecks``,
  which deletes dark versions newer than the alias target first for a clean rebuild.

Versions BELOW the alias target (the rollback safety net during a sanity window) are never
touched; those are ``es_drop_old_index_versions``' job, days later.

Fleet-level resume: a program whose ALIAS TARGETS already carry the current code mapping stamp
was completed by this very code, so it is skipped - re-running ``--all`` after a mid-fleet
crash finishes only the remaining programs. ``--force`` rebuilds such programs anyway (next
version as usual); ``--sweep-wrecks`` also bypasses the skip, because analyzer-only changes
are invisible to the stamp and a sweep must never be suppressed by it.

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

from datetime import UTC, datetime
import re
from typing import TYPE_CHECKING, Any
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
    mapping_content_hash,
    versioned_doc,
)
from hope.apps.utils.elasticsearch_utils import populate_index

if TYPE_CHECKING:
    from collections.abc import Callable

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
            default=2000,
            help="Bulk chunk size for the full populate.",
        )
        parser.add_argument(
            "--sweep-wrecks",
            action="store_true",
            help=(
                "Delete dark leftovers newer than the alias target before starting (clean rebuild "
                "instead of the default resume). Use when a resumed pair failed the verify gate, "
                "or after a deploy that changed only analyzers/settings (invisible to the mapping stamp)."
            ),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Reindex even programs whose alias target already carries the current code "
                "mapping stamp. Without it such programs are skipped, so a re-run after a "
                "mid-fleet crash finishes only the remaining programs."
            ),
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
            self._report_plan(es, code_by_id, opts)
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

    def _report_plan(self, es: Elasticsearch, code_by_id: dict, opts: dict) -> None:
        for pid, code in sorted(code_by_id.items(), key=lambda kv: kv[1] or ""):
            docs = self._doc_classes(str(pid))
            names = [d._index._name for d in docs]
            not_aliased = [n for n in names if self._alias_target(es, n) is None]
            if not_aliased:
                self.stdout.write(f"{code}: SKIP - not an alias yet: {not_aliased} (run es_bootstrap_aliases)")
                continue
            current = {n: t for n in names if (t := self._alias_target(es, n)) is not None}
            if (
                not opts["force"]
                and not opts["sweep_wrecks"]
                and all(self._resumable(es, doc, current[doc._index._name]) for doc in docs)
            ):
                self.stdout.write(f"{code}: up-to-date {list(current.values())} - would skip (--force to rebuild)")
                continue
            try:
                suffix = self._pair_suffix(current)
            except CommandError as exc:
                # one hand-mangled alias must not kill the whole plan for --all
                self.stdout.write(self.style.WARNING(f"{code}: SKIP - {exc}"))
                continue
            resume_note = (
                " (will RESUME an existing dark leftover)"
                if any(self._resumable(es, doc, f"{doc._index._name}_{suffix}") for doc in docs)
                else ""
            )
            self.stdout.write(
                f"{code}: REINDEX {list(current.values())} -> _{suffix}, then swap both aliases{resume_note}"
            )

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

    def _sweep_wrecks(self, es: Elasticsearch, name: str, old_target: str) -> None:
        """Delete unaliased versions NEWER than the current alias target, so their number is reused.

        Only wrecks live above the alias target: dark leftovers of crashed runs and versions the
        alias was rolled back FROM. Deleting them here (instead of abandoning them to a later
        sweep) keeps the version counter tight and guarantees the recreated index carries the
        CURRENT code mapping - a wreck may have been created by an older deployment. Versions
        BELOW the target are the rollback safety net of a sanity window and are never touched.
        """
        match = re.match(rf"^{re.escape(name)}_v(\d+)$", old_target)
        if not match:  # alias points at something outside the _vN scheme - nothing provably a wreck
            return
        target_version = int(match.group(1))
        for index, info in es.indices.get(index=f"{name}_v*", ignore_unavailable=True).items():
            version_match = re.match(rf"^{re.escape(name)}_v(\d+)$", index)
            if not version_match or int(version_match.group(1)) <= target_version:
                continue
            if info.get("aliases"):
                continue
            es.indices.delete(index=index)
            self.stdout.write(self.style.WARNING(f"  swept wreck {index} (dark, newer than {old_target})"))

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

        # fleet-level resume: alias targets stamped with the current code mapping were completed
        # by this very code - skip, so a crashed --all run finishes only the remainder. --force
        # rebuilds anyway; --sweep-wrecks bypasses too (analyzer-only changes are invisible to
        # the stamp, a sweep must never be suppressed by it).
        if (
            not opts["force"]
            and not opts["sweep_wrecks"]
            and all(self._resumable(es, doc_class, old[doc_class._index._name]) for doc_class in docs)
        ):
            return f"up-to-date ({list(old.values())} built from current mapping) - skipped, --force to rebuild"

        if opts["sweep_wrecks"]:
            for name, old_target in old.items():
                self._sweep_wrecks(es, name, old_target)
        suffix = self._pair_suffix(old)
        vdocs = [versioned_doc(d, suffix) for d in docs]

        resumed = []
        for doc_class, vdoc in zip(docs, vdocs, strict=True):
            target = vdoc._index._name
            if self._resumable(es, doc_class, target):
                resumed.append(target)
                self.stdout.write(f"  resuming into existing dark {target} (mapping stamp matches)")
                continue
            if es.indices.exists(index=target):
                # a dark leftover created from a DIFFERENT code mapping - resuming would swap an
                # outdated mapping live; rebuild it under the same number
                es.indices.delete(index=target)
                self.stdout.write(self.style.WARNING(f"  rebuilt {target} (mapping changed since it was created)"))
            create_versioned_index(es, doc_class, suffix=suffix, attach_alias=False)
            queryset = vdoc().get_queryset()
            db_count = queryset.count()
            self.stdout.write(f"  populating {target} ({db_count} docs from db)")
            self.stdout.flush()
            populate_index(queryset, vdoc, chunk_size=opts["chunk_size"], progress_cb=self._progress(target, db_count))
            self.stdout.write(f"  populated {target}")

        # the delta anchor covers the oldest target: for a fresh index creation_date == this run's
        # populate start, for a resumed one it reaches back to everything the crashed run may have missed
        anchor = min(self._creation_time(es, f"{name}_{suffix}") for name in names)
        delta_start = timezone.now()
        self._delta(pid, since=anchor, target_suffix=suffix)
        try:
            self._verify_dark(es, pid, vdocs, suffix, anchor=delta_start)
        except CommandError as exc:
            if resumed:
                raise CommandError(
                    f"{exc} (pair was RESUMED from a previous run's leftover, likely killed "
                    f"mid-populate - re-run with --sweep-wrecks for a clean rebuild)"
                ) from exc
            raise

        self._swap(es, old, suffix)

        # two passes: the first covers writes since the pre-swap delta started, the second the
        # (seconds-long) window of the first - both write through the now-live alias
        final_start = timezone.now()
        self._delta(pid, since=delta_start)
        self._delta(pid, since=final_start)
        note = ", resumed dark pair" if resumed else ""
        return f"reindexed {list(old.values())} -> _{suffix}, aliases swapped (old kept for rollback){note}"

    def _progress(self, target: str, db_count: int) -> "Callable[[int], None]":
        def report(n: int) -> None:
            self.stdout.write(f"    {target}: {n}/{db_count}")
            self.stdout.flush()

        return report

    @staticmethod
    def _pair_suffix(old: dict) -> str:
        """Working version = highest alias-target version of the pair + 1.

        Deterministic on purpose: a re-run computes the SAME target as the run it replaces, which
        is what makes resuming a leftover possible (max over physical indexes would skip past it).
        """
        versions = []
        for name, target in old.items():
            match = re.match(rf"^{re.escape(name)}_v(\d+)$", target)
            if not match:
                raise CommandError(f"alias {name} points at {target} - outside the _vN scheme, bootstrap it first")
            versions.append(int(match.group(1)))
        return f"v{max(versions) + 1}"

    @staticmethod
    def _resumable(es: Elasticsearch, doc_class: type, target: str) -> bool:
        """Tell whether a dark leftover was created from the SAME code mapping we have now."""
        if not es.indices.exists(index=target):
            return False
        stored = es.indices.get_mapping(index=target)[target]["mappings"].get("_meta", {}).get("hope_mapping_hash")
        return stored == mapping_content_hash(doc_class._index.to_dict().get("mappings"))

    @staticmethod
    def _creation_time(es: Elasticsearch, index: str) -> datetime:
        ms = int(es.indices.get_settings(index=index)[index]["settings"]["index"]["creation_date"])
        return datetime.fromtimestamp(ms / 1000, tz=UTC)

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
