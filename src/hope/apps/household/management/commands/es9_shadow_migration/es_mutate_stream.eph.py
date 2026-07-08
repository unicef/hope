"""eph-1 ONLY test tool — generates a change stream to prove the delta shrinks. Not for prod.

Each pass picks a random ACTIVE program and touches N rows within it (indexed program_id,
no full-table sort — the dev's order_by("?") is unusably slow on eph-1's ~12M rows).
Appends every change to a JSONL log. CLI unchanged from the PR command.
"""

import json
import random
import time
from typing import IO, Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from hope.models import Household, Individual, Program


class Command(BaseCommand):
    help = "Continuously mutate households/individuals to feed es_populate_delta (dev/test tool)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--sleep", type=float, default=3.0, help="Seconds between passes.")
        parser.add_argument("--batch", type=int, default=5, help="Records touched per model per pass.")
        parser.add_argument("--passes", type=int, default=0, help="Number of passes (0 = forever).")
        parser.add_argument(
            "--delete-every", type=int, default=10, help="Soft-delete 1 individual every N passes (0 = off)."
        )
        parser.add_argument("--log", default="mutate_log.jsonl", help="JSONL log path (appended, never clobbered).")

    def handle(self, *args: Any, **opts: Any) -> None:
        n_progs = Program.objects.filter(status=Program.ACTIVE).count()
        self.stdout.write(f"start: {n_progs} active programs -> log={opts['log']} (Ctrl+C stops)")
        if n_progs == 0:
            self.stdout.write(self.style.WARNING("no active programs to mutate -- seed some data first."))
            return

        fh = open(opts["log"], "a", encoding="utf-8")  # noqa: SIM115  # kept open across the loop
        i = 0
        try:
            while opts["passes"] == 0 or i < opts["passes"]:
                i += 1
                try:
                    pid = self._random_active_program_id()
                    ni = self._touch_individuals(pid, opts["batch"], fh)
                    nh = self._touch_households(pid, opts["batch"], fh)
                    extra = ""
                    if opts["delete_every"] and i % opts["delete_every"] == 0:
                        uid = self._soft_delete_one(pid, fh)
                        extra = f", soft-deleted {uid}" if uid else ""
                    stamp = timezone.now().isoformat(timespec="seconds")
                    self.stdout.write(f"[{stamp}] pass {i} prog={pid}: touched {ni} ind / {nh} hh{extra}")
                except Exception as e:  # noqa: BLE001  # pragma: no cover  # keep loop alive on transient error
                    self.stdout.write(self.style.ERROR(f"pass {i}: error, continuing -- {e}"))
                time.sleep(opts["sleep"])
        except KeyboardInterrupt:  # pragma: no cover
            self.stdout.write(f"\nstopped at pass {i}. log: {opts['log']}")
        finally:
            fh.close()

    @staticmethod
    def _random_active_program_id() -> str:
        # Program table is small (hundreds of rows), so order_by("?") here is cheap.
        return str(Program.objects.filter(status=Program.ACTIVE).order_by("?").values_list("id", flat=True).first())

    @staticmethod
    def _write(fh: IO[str], record: dict) -> None:
        fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        fh.flush()  # crash-safe: every mutation is on disk before the next one

    @staticmethod
    def _record(  # noqa: PLR0913
        action: str, model: str, ind: Individual | None, hh: Household | None, field: str, old: Any, new: Any
    ) -> dict:
        return {
            "ts": timezone.now().isoformat(timespec="seconds"),
            "action": action,
            "model": model,
            "object_id": str(ind.id if model == "Individual" else hh.id),
            "individual_id": str(ind.id) if ind else None,
            "household_id": str(hh.id) if hh else None,
            "individual_unicef_id": ind.unicef_id if ind else None,
            "household_unicef_id": hh.unicef_id if hh else None,
            "field": field,
            "old": old,
            "new": new,
            "program_id": str(ind.program_id if ind else (hh.program_id if hh else None)),
        }

    @classmethod
    def _touch_individuals(cls, program_id: str, n: int, fh: IO[str]) -> int:
        # program_id is indexed. NO order_by: an ORDER BY id would ignore that index and
        # walk the PK filtering by program_id (IO-bound over 12M rows). Unordered LIMIT n
        # uses the program_id index directly -> a handful of rows, milliseconds.
        inds = list(
            Individual.all_merge_status_objects.select_related("household").filter(program_id=program_id)[:n]
        )
        for ind in inds:
            old = ind.given_name
            ind.given_name = f"{(old or 'Name').split('#')[0]}#{random.randint(1000, 9999)}"  # noqa: S311
            # must list updated_at: Django does NOT auto-add auto_now fields to update_fields,
            # and the delta keys entirely off updated_at.
            ind.save(update_fields=["given_name", "updated_at"])
            cls._write(fh, cls._record("update", "Individual", ind, ind.household, "given_name", old, ind.given_name))
        return len(inds)

    @classmethod
    def _touch_households(cls, program_id: str, n: int, fh: IO[str]) -> int:
        hhs = list(Household.objects.filter(program_id=program_id)[:n])
        for hh in hhs:
            old = hh.size
            hh.size = (old or 0) + 1
            hh.save(update_fields=["size", "updated_at"])  # list updated_at (see _touch_individuals)
            cls._write(fh, cls._record("update", "Household", None, hh, "size", old, hh.size))  # ind side N/A
        return len(hhs)

    @classmethod
    def _soft_delete_one(cls, program_id: str, fh: IO[str]) -> str | None:
        ind = next(
            iter(Individual.all_merge_status_objects.select_related("household").filter(program_id=program_id)[:1]),
            None,
        )
        if ind is None:  # pragma: no cover
            return None
        hh = ind.household
        ind.delete()  # SoftDeletableMergeStatusModel -> soft=True by default
        cls._write(fh, cls._record("soft_delete", "Individual", ind, hh, "is_removed", False, True))
        return ind.unicef_id
