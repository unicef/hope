"""Continuously mutate households/individuals to produce a realistic change stream.

A dev/test companion to ``es_populate_delta``: run it while the delta command catches up a shadow
cluster and each pass bumps ``updated_at`` on a random sample, so re-running ``--since <start>``
should report a shrinking number of programs as the delta converges.

Every mutation is appended to a JSONL log (one JSON object per line) with the exact ids and the
before/after value, so ES output can be asserted against it afterwards::

    {"ts": "...", "action": "update", "model": "Individual", "object_id": "<uuid>",
     "individual_id": "<uuid>", "household_id": "<uuid|null>",
     "individual_unicef_id": "IND-...", "household_unicef_id": "HH-...|null",
     "field": "given_name", "old": "Anna", "new": "Anna#4821"}

For Household mutations the individual side is left null (a household change has no single
individual). Read the log back with::

    [json.loads(line) for line in open("mutate_log.jsonl")]

Examples
--------
    python manage.py es_mutate_stream                          # forever, 3s between passes
    python manage.py es_mutate_stream --sleep 5 --batch 3 --passes 20
    python manage.py es_mutate_stream --delete-every 0         # no soft-deletes
    python manage.py es_mutate_stream --log /tmp/run1.jsonl

"""

import json
import random
import time
from typing import IO, Any
import uuid

from django.core.management.base import BaseCommand
from django.db.models import QuerySet
from django.utils import timezone

from hope.models import Household, Individual


class Command(BaseCommand):
    help = "Continuously mutate households/individuals to feed es_populate_delta (dev/test tool)."

    # residence_status is embedded in HouseholdDocument, so its change is verifiable in ES (unlike size).
    RESIDENCE_STATUSES = ("IDP", "IDP_RETURNEE", "REFUGEE", "OTHERS_OF_CONCERN", "HOST", "NON_HOST", "RETURNEE")

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--sleep", type=float, default=3.0, help="Seconds between passes.")
        parser.add_argument("--batch", type=int, default=5, help="Records touched per model per pass.")
        parser.add_argument("--passes", type=int, default=0, help="Number of passes (0 = forever).")
        parser.add_argument(
            "--delete-every", type=int, default=10, help="Soft-delete 1 individual every N passes (0 = off)."
        )
        parser.add_argument("--log", default="mutate_log.jsonl", help="JSONL log path (appended, never clobbered).")

    def handle(self, *args: Any, **opts: Any) -> None:
        ind_total = Individual.all_merge_status_objects.count()
        hh_total = Household.objects.count()
        self.stdout.write(f"start: individuals={ind_total} households={hh_total} -> log={opts['log']} (Ctrl+C stops)")
        if ind_total == 0 and hh_total == 0:
            self.stdout.write(self.style.WARNING("nothing to mutate (empty DB) -- seed some data first."))
            return

        fh = open(opts["log"], "a", encoding="utf-8")  # noqa: SIM115  # kept open across the loop
        i = 0
        try:
            while opts["passes"] == 0 or i < opts["passes"]:
                i += 1
                try:
                    ni = self._touch_individuals(opts["batch"], fh)
                    nh = self._touch_households(opts["batch"], fh)
                    extra = ""
                    if opts["delete_every"] and i % opts["delete_every"] == 0:
                        uid = self._soft_delete_one(fh)
                        extra = f", soft-deleted {uid}" if uid else ""
                    stamp = timezone.now().isoformat(timespec="seconds")
                    self.stdout.write(f"[{stamp}] pass {i}: touched {ni} ind / {nh} hh{extra}")
                except Exception as e:  # noqa: BLE001  # pragma: no cover  # keep loop alive on transient error
                    self.stdout.write(self.style.ERROR(f"pass {i}: error, continuing -- {e}"))
                time.sleep(opts["sleep"])
        except KeyboardInterrupt:  # pragma: no cover
            self.stdout.write(f"\nstopped at pass {i}. log: {opts['log']}")
        finally:
            fh.close()

    @staticmethod
    def _random_window(qs: QuerySet, n: int) -> list:
        # order_by("?") is ORDER BY RANDOM() -> full-table sort (deadly on 12M rows).
        # UUID pk is indexed: seek from a random uuid, wrap around if it lands near the end.
        pivot = uuid.uuid4()
        rows = list(qs.filter(pk__gte=pivot).order_by("pk")[:n])
        if len(rows) < n:
            rows += list(qs.filter(pk__lt=pivot).order_by("pk")[: n - len(rows)])
        return rows

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
        }

    @classmethod
    def _touch_individuals(cls, n: int, fh: IO[str]) -> int:
        inds = cls._random_window(Individual.all_merge_status_objects.select_related("household"), n)
        for ind in inds:
            old = ind.given_name
            ind.given_name = f"{(old or 'Name').split('#')[0]}#{random.randint(1000, 9999)}"  # noqa: S311
            # updated_at must be listed: Django does NOT auto-add auto_now fields to
            # update_fields, and es_populate_delta --since keys off updated_at.
            ind.save(update_fields=["given_name", "updated_at"])
            cls._write(fh, cls._record("update", "Individual", ind, ind.household, "given_name", old, ind.given_name))
        return len(inds)

    @classmethod
    def _touch_households(cls, n: int, fh: IO[str]) -> int:
        hhs = cls._random_window(Household.objects.all(), n)
        for hh in hhs:
            old = hh.residence_status
            new = random.choice([s for s in cls.RESIDENCE_STATUSES if s != old])  # noqa: S311  # embedded in ES doc
            hh.residence_status = new
            hh.save(update_fields=["residence_status", "updated_at"])  # list updated_at (see _touch_individuals)
            cls._write(fh, cls._record("update", "Household", None, hh, "residence_status", old, new))  # ind side N/A
        return len(hhs)

    @classmethod
    def _soft_delete_one(cls, fh: IO[str]) -> str | None:
        rows = cls._random_window(Individual.all_merge_status_objects.select_related("household"), 1)
        if not rows:  # pragma: no cover
            return None
        ind = rows[0]
        hh = ind.household
        ind.delete()  # SoftDeletableMergeStatusModel -> soft=True by default
        cls._write(fh, cls._record("soft_delete", "Individual", ind, hh, "is_removed", False, True))
        return ind.unicef_id
