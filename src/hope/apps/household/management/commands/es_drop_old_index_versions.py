"""Delete unaliased ``<index>_vN`` leftovers once the post-swap sanity window is over.

After ``es_reindex`` swaps an alias to ``_vN+1``, the old ``_vN`` is deliberately kept as an
instant rollback target. Days later this command sweeps it - together with any dark leftovers
from crashed reindex runs. Safety by construction:

* only indexes matching a program's ``<name>_vN`` pattern are considered,
* the alias's CURRENT target is never touched,
* anything that still has ANY alias attached is skipped (nothing pointed-at gets deleted),
* a name that is not an alias at all (pre-bootstrap program) is skipped with a warning,
* it prints only, unless ``--confirm`` is given.

Examples
--------
List what would go, then actually drop::

    django-admin es_drop_old_index_versions --all
    django-admin es_drop_old_index_versions --all --confirm

"""

from typing import Any
import uuid

from django.core.management.base import BaseCommand, CommandError
from elasticsearch import Elasticsearch
from elasticsearch.dsl import connections

from hope.apps.household.documents import get_household_doc, get_individual_doc


class Command(BaseCommand):
    help = (
        "Delete unaliased _vN leftovers (old versions after a reindex sanity window, dark wrecks "
        "of crashed runs). Prints only unless --confirm is given; never touches an aliased index."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--program", default=None, help="Limit to a single program (UUID or code).")
        parser.add_argument("--business-area", default=None, help="Limit to a business area (slug).")
        parser.add_argument("--all", action="store_true", help="Every active program.")
        parser.add_argument("--confirm", action="store_true", help="Actually delete (default: list only).")

    def handle(self, *args: Any, **opts: Any) -> None:
        if sum([bool(opts["program"]), bool(opts["business_area"]), opts["all"]]) != 1:
            raise CommandError("Provide exactly one scope: --program, --business-area or --all.")

        es: Elasticsearch = connections.get_connection()
        code_by_id = self._scope(opts)
        if not code_by_id:
            self.stdout.write(self.style.WARNING("No active programs in scope - nothing to do."))
            return

        dropped = 0
        for pid, code in sorted(code_by_id.items(), key=lambda kv: kv[1] or ""):
            for doc_class in (get_individual_doc(str(pid)), get_household_doc(str(pid))):
                dropped += self._sweep_index(es, code, doc_class._index._name, confirm=opts["confirm"])

        verb = "Dropped" if opts["confirm"] else "Would drop"
        tail = "" if opts["confirm"] else " (re-run with --confirm to delete)"
        self.stdout.write(self.style.SUCCESS(f"{verb} {dropped} index(es).{tail}"))

    def _sweep_index(self, es: Elasticsearch, code: str, name: str, confirm: bool) -> int:
        if not es.indices.exists_alias(name=name):
            self.stdout.write(self.style.WARNING(f"{code}  {name}: not an alias - skipped (pre-bootstrap?)"))
            return 0
        current = set(es.indices.get_alias(name=name))
        candidates = es.indices.get(index=f"{name}_v*", ignore_unavailable=True)
        dropped = 0
        for candidate in sorted(candidates):
            if candidate in current:
                continue
            if candidates[candidate].get("aliases"):
                self.stdout.write(self.style.WARNING(f"{code}  {candidate}: has aliases attached - skipped"))
                continue
            if confirm:
                es.indices.delete(index=candidate)
            self.stdout.write(f"{code}  {candidate}: {'DROPPED' if confirm else 'would drop'}")
            dropped += 1
        return dropped

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
