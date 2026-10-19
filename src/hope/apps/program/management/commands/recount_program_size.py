"""Recount household_count and individual_count on every programme."""

import time

from django.core.management.base import BaseCommand

from hope.apps.program.signals import increase_program_version_cache
from hope.models import Program


class Command(BaseCommand):
    help = "Recount household_count and individual_count on every programme. Safe to re-run."

    def handle(self, *args: str, **options: str) -> None:
        programs = list(
            Program.objects.select_related("business_area")
            .only("pk", "name", "household_count", "individual_count", "business_area__slug")
            .order_by("pk")
        )
        total = len(programs)
        updated = 0
        for number, program in enumerate(programs, start=1):
            started = time.monotonic()
            before = (program.household_count, program.individual_count)
            program.adjust_program_size()
            after = (program.household_count, program.individual_count)
            if after != before:
                Program.objects.filter(pk=program.pk).update(
                    household_count=program.household_count, individual_count=program.individual_count
                )
                increase_program_version_cache(Program, instance=program)
                updated += 1
            self.stdout.write(
                f"[{number}/{total}] {program.name}: {before} -> {after} in {time.monotonic() - started:.1f}s"
            )
        self.stdout.write(self.style.SUCCESS(f"Checked {total} programmes, updated {updated}"))
