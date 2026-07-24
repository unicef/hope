"""Bootstrap per-program ES indexes from bare physical names to ``alias -> <name>_v1`` (clone-first).

Today the app addresses each per-program index by its bare physical name
(``individuals_<ba>_<code>``). Blue-green reindexing needs that name to be an ALIAS so a future
mapping change can build ``_v2`` next to ``_v1`` and swap atomically. ES has no rename, but
``_clone`` hard-links segments (seconds, no data copied), so per index the sequence is:

1. write-block the source index (reads keep working; blocked writes are in Postgres),
2. ``_clone`` source -> ``<name>_v1`` (target replicas=0 - a replica would be a network copy),
3. wait until the clone's primary is active, sanity-check doc counts (source is frozen -> exact),
4. ONE atomic ``_aliases`` call: ``remove_index`` source + ``add`` alias ``<name>`` -> ``_v1``
   (an alias cannot coexist with an index of the same name, hence delete+add in one breath),
5. unblock the clone and restore its replica count (rebuilds in the background).

The app never notices: the name resolves to the old physical until the atomic call, to the clone
after it. The state in ES drives everything, so the command is resumable and idempotent:

* name is already an alias      -> skip (bootstrapped earlier),
* name missing (fresh program)  -> create ``_v1`` with the alias attached at creation,
* ``_v1`` exists but the name is still a physical index (crash between clone and takeover)
                                -> re-block source, skip the clone, redo the takeover.

After the loop one ``es_populate_delta --since <run start - buffer>`` pass sweeps the writes that
failed during the per-index freeze windows (they live in Postgres; the delta writes through the
now-live alias, so it needs no adaptation).

Examples
--------
Preview, then bootstrap everything::

    python manage.py es_bootstrap_aliases --all --dry-run
    python manage.py es_bootstrap_aliases --all

One small program first (canary), or one business area::

    python manage.py es_bootstrap_aliases --program <uuid-or-code>
    python manage.py es_bootstrap_aliases --business-area afghanistan

Read-only state report::

    python manage.py es_bootstrap_aliases --all --status

"""

from typing import Any
import uuid

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from elasticsearch import BadRequestError, Elasticsearch
from elasticsearch.dsl import connections

from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.services.index_management import create_versioned_index

DELTA_SINCE_BUFFER_MINUTES = 5


class Command(BaseCommand):
    help = (
        "One-time blue-green bootstrap: turn every per-program bare index name into an alias "
        "pointing at a <name>_v1 clone. Clone-first: no data is copied or rebuilt; the only cost "
        "is a seconds-long write freeze per index."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--program", default=None, help="Bootstrap a single program (UUID or code).")
        parser.add_argument("--business-area", default=None, help="Bootstrap every active program in this BA (slug).")
        parser.add_argument("--all", action="store_true", help="Bootstrap every active program.")
        parser.add_argument("--status", action="store_true", help="Read-only per-index state report, then exit.")
        parser.add_argument("--dry-run", action="store_true", help="Print the per-index plan without touching ES.")
        parser.add_argument("--skip-delta", action="store_true", help="Skip the final es_populate_delta pass.")
        parser.add_argument(
            "--force-unlock",
            action="store_true",
            help="Remove a stale lock left by a crashed run, then continue.",
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        if sum([bool(opts["program"]), bool(opts["business_area"]), opts["all"]]) != 1:
            raise CommandError("Provide exactly one scope: --program, --business-area or --all.")

        es: Elasticsearch = connections.get_connection()
        code_by_id = self._scope(opts)
        if not code_by_id:
            self.stdout.write(self.style.WARNING("No active programs in scope - nothing to do."))
            return

        if opts["status"]:
            self._report_status(es, code_by_id)
            return

        health = es.cluster.health()
        if health.get("status") != "green":
            raise CommandError(f"Cluster health is {health.get('status')} - _clone needs GREEN. Aborting.")

        if opts["dry_run"]:
            self._report_plan(es, code_by_id)
            return

        run_start = timezone.now()
        self._acquire_lock(es, force=opts["force_unlock"])
        try:
            self._bootstrap_programs(es, code_by_id)
        finally:
            self._release_lock(es)

        if not opts["skip_delta"]:
            since = run_start - timezone.timedelta(minutes=DELTA_SINCE_BUFFER_MINUTES)
            self.stdout.write(f"Sweeping freeze-window writes: es_populate_delta --since {since.isoformat()}")
            call_command(
                "es_populate_delta",
                since=since.isoformat(),
                program=opts["program"],
                business_area=opts["business_area"],
            )

    # ── scope ────────────────────────────────────────────────────────────────

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

    # ── state inspection ─────────────────────────────────────────────────────

    @staticmethod
    def _index_state(es: Elasticsearch, name: str) -> str:
        if es.indices.exists_alias(name=name):
            return "alias"
        if es.indices.exists(index=name):
            return "bare"
        return "missing"

    def _report_status(self, es: Elasticsearch, code_by_id: dict) -> None:
        for pid, code in sorted(code_by_id.items(), key=lambda kv: kv[1] or ""):
            for doc_class in self._doc_classes(str(pid)):
                name = doc_class._index._name
                state = self._index_state(es, name)
                if state == "alias":
                    target = next(iter(es.indices.get_alias(name=name)))
                    detail = f"ALIAS -> {target}"
                elif state == "bare":
                    detail = "BARE physical (pre-bootstrap)"
                else:
                    detail = "MISSING"
                db_count = doc_class().get_queryset().count()
                es_count = es.count(index=name)["count"] if state != "missing" else "-"
                self.stdout.write(f"{code}  {name}: {detail}  es={es_count} db={db_count}")

    def _report_plan(self, es: Elasticsearch, code_by_id: dict) -> None:
        plans = {
            "alias": "skip (already bootstrapped)",
            "bare": "BOOTSTRAP (clone-first)",
            "missing": "create _v1 + alias",
        }
        for pid, code in sorted(code_by_id.items(), key=lambda kv: kv[1] or ""):
            for doc_class in self._doc_classes(str(pid)):
                name = doc_class._index._name
                self.stdout.write(f"{code}  {name}: {plans[self._index_state(es, name)]}")

    # ── lock ─────────────────────────────────────────────────────────────────
    # ponytail: an ES index doubles as a cluster-wide mutex (create is atomic, fails if it
    # exists) - good enough for a manually-run one-time command; no extra infra.

    LOCK_INDEX = f"{settings.ELASTICSEARCH_INDEX_PREFIX}es-bootstrap-lock"

    def _acquire_lock(self, es: Elasticsearch, force: bool) -> None:
        if force:
            es.options(ignore_status=[404]).indices.delete(index=self.LOCK_INDEX)
        try:
            es.indices.create(index=self.LOCK_INDEX)
        except BadRequestError as exc:
            raise CommandError(
                f"Another bootstrap run holds the lock ({self.LOCK_INDEX}). If it crashed, re-run with --force-unlock."
            ) from exc

    def _release_lock(self, es: Elasticsearch) -> None:
        es.options(ignore_status=[404]).indices.delete(index=self.LOCK_INDEX)

    # ── the actual bootstrap ─────────────────────────────────────────────────

    def _bootstrap_programs(self, es: Elasticsearch, code_by_id: dict) -> None:
        total = len(code_by_id)
        failed: list = []
        for n, (pid, code) in enumerate(sorted(code_by_id.items(), key=lambda kv: kv[1] or ""), start=1):
            for doc_class in self._doc_classes(str(pid)):
                name = doc_class._index._name
                try:
                    outcome = self._bootstrap_index(es, doc_class)
                except Exception as exc:  # noqa: BLE001  # one bad index must not abort the fleet
                    outcome = f"FAILED - {exc}"
                    failed.append((code, name, str(exc)))
                style = self.style.ERROR if outcome.startswith("FAILED") else self.style.SUCCESS
                self.stdout.write(style(f"[{n}/{total}] {code}  {name}: {outcome}"))
        if failed:
            raise CommandError(f"{len(failed)} index(es) failed: {[f'{c}/{i}' for c, i, _ in failed]}")

    def _bootstrap_index(self, es: Elasticsearch, doc_class: type) -> str:
        name = doc_class._index._name
        state = self._index_state(es, name)
        if state == "alias":
            return "skip (already alias)"
        if state == "missing":
            create_versioned_index(es, doc_class)
            return "created _v1 + alias"

        target = f"{name}_v1"
        replicas = self._original_replicas(es, name)
        es.indices.put_settings(index=name, settings={"index.blocks.write": True})
        if not es.indices.exists(index=target):
            es.indices.clone(index=name, target=target, settings={"index.number_of_replicas": 0})
        es.cluster.health(index=target, wait_for_status="yellow", timeout="120s")

        es.indices.refresh(index=target)
        src_count = es.count(index=name)["count"]
        tgt_count = es.count(index=target)["count"]
        if src_count != tgt_count:
            # abort BEFORE the point of no return and unfreeze writes on the still-live source
            es.indices.put_settings(index=name, settings={"index.blocks.write": None})
            raise CommandError(f"count mismatch on {name}: source={src_count} clone={tgt_count}")

        es.indices.update_aliases(
            actions=[
                {"remove_index": {"index": name}},
                {"add": {"index": target, "alias": name}},
            ]
        )
        aliased = set(es.indices.get_alias(name=name))
        if aliased != {target}:
            raise CommandError(f"postcondition failed: alias {name} points at {aliased}, expected {{{target}}}")
        es.indices.put_settings(
            index=target,
            settings={"index.blocks.write": None, "index.number_of_replicas": replicas},
        )
        return f"bootstrapped -> {target}"

    @staticmethod
    def _original_replicas(es: Elasticsearch, name: str) -> str:
        index_settings = es.indices.get_settings(index=name)
        return index_settings[name]["settings"]["index"].get("number_of_replicas", "0")
