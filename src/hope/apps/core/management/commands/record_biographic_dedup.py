"""record_biographic_dedup — record what legacy HOPE biographic dedup does for given XLSX file with seeded population.

    ./manage.py record_biographic_dedup <program_id> <population.xlsx> <rdi.xlsx> <output.json>

INPUT:

- ``population.xlsx`` — seeds the program population
- ``rdi.xlsx`` — the RDI under test

OUTPUT — a JSON file with:

- ``findings`` — Hope deduplication engine-shaped findings.
- ``tickets`` — Needs Adjudication tickets HOPE created for the RDI under test.

Every individual in the JSON (``reference_pk``, ``golden_records_individual``,
``possible_duplicate(s)``) is referenced by ``<population|rdi>:<xlsx row>`` instead of
its UUID, because UUIDs change on every import. The row comes from ``Individual.detail_id``.
Example for a population XLSX with Maria Gonzalez in row 3 and an RDI XLSX with Maria Gonzalez in row 3:

    {
      "findings": [
        {
          "first": {"reference_pk": "rdi:3"},
          "second": {"reference_pk": "population:3"},
          "score": 12.0,
          "status_code": 200
        }
      ],
      "tickets": [
        {
          "issue_type": 24,
          "is_multiple_duplicates_version": true,
          "golden_records_individual": "rdi:3",
          "possible_duplicate": "rdi:3",
          "possible_duplicates": ["population:3"],
          "score_min": 12.0,
          "score_max": 12.0
        }
      ]
    }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.core.files import File
from django.core.management import BaseCommand

from hope.apps.grievance.models import TicketNeedsAdjudicationDetails
from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
from hope.apps.registration_data.tasks.rdi_xlsx_people_create import RdiXlsxPeopleCreateTask
from hope.models import ImportData, Individual, Program, RegistrationDataImport

if TYPE_CHECKING:
    from argparse import ArgumentParser


class Command(BaseCommand):
    help = "Record HOPE biographic dedup findings and tickets for a population XLSX + RDI XLSX pair."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("program_id")
        parser.add_argument("population_xlsx")
        parser.add_argument("rdi_xlsx")
        parser.add_argument("output")

    def handle(self, *args: Any, **options: Any) -> None:
        program = Program.objects.select_related("business_area").get(id=options["program_id"])
        population_seed_rdi = self._import_and_merge(program, Path(options["population_xlsx"]), "population")
        rdi = self._import_and_merge(program, Path(options["rdi_xlsx"]), "rdi")

        keys = self._stable_keys_by_individual_id(population_seed_rdi, rdi)
        recording = {"findings": self._findings(rdi, keys), "tickets": self._tickets(rdi, keys)}
        Path(options["output"]).write_text(json.dumps(recording, indent=2))

    def _stable_keys_by_individual_id(
        self, population_seed_rdi: RegistrationDataImport, rdi: RegistrationDataImport
    ) -> dict[str, str]:
        keys = {}
        for label, imported_rdi in (("population", population_seed_rdi), ("rdi", rdi)):
            for individual in Individual.objects.filter(registration_data_import=imported_rdi):
                keys[str(individual.id)] = f"{label}:{individual.detail_id}"
        return keys

    def _import_and_merge(self, program: Program, path: Path, label: str) -> RegistrationDataImport:
        business_area = program.business_area
        with path.open("rb") as f:
            import_data = ImportData.objects.create(
                status=ImportData.STATUS_FINISHED,
                business_area_slug=business_area.slug,
                file=File(f, name=path.name),
            )
        rdi = RegistrationDataImport.objects.create(
            name=f"record-biographic-dedup-{label}-{import_data.id}",
            status=RegistrationDataImport.IMPORTING,
            data_source=RegistrationDataImport.XLS,
            business_area=business_area,
            program=program,
            import_data=import_data,
            number_of_individuals=0,
            number_of_households=0,
        )
        RdiXlsxPeopleCreateTask().execute(str(rdi.id), str(import_data.id), str(business_area.id), str(program.id))
        RdiMergeTask().execute(str(rdi.id))
        return rdi

    def _findings(self, rdi: RegistrationDataImport, keys: dict[str, str]) -> list[dict]:
        # Batch pairs are reported on both sides, so collect into a dict keyed by the (ordered) pair.
        scores: dict[tuple[str, ...], float] = {}
        for individual in Individual.objects.filter(registration_data_import=rdi):
            duplicates = individual.deduplication_golden_record_results.get(
                "duplicates", []
            ) + individual.deduplication_batch_results.get("duplicates", [])
            for duplicate in duplicates:
                pair = (keys[str(individual.id)], keys[str(duplicate["hit_id"])])
                scores[tuple(sorted(pair, key=lambda key: (not key.startswith("rdi:"), key)))] = duplicate["score"]
        return [
            {
                "first": {"reference_pk": first},
                "second": {"reference_pk": second},
                "score": score,
                "status_code": 200,
            }
            for (first, second), score in sorted(scores.items())
        ]

    def _tickets(self, rdi: RegistrationDataImport, keys: dict[str, str]) -> list[dict]:
        details = (
            TicketNeedsAdjudicationDetails.objects.filter(ticket__registration_data_import=rdi)
            .select_related("ticket")
            .prefetch_related("possible_duplicates")
        )
        return sorted(
            (
                {
                    "issue_type": detail.ticket.issue_type,
                    "is_multiple_duplicates_version": detail.is_multiple_duplicates_version,
                    "golden_records_individual": keys[str(detail.golden_records_individual_id)],
                    "possible_duplicate": keys.get(str(detail.possible_duplicate_id)),
                    "possible_duplicates": sorted(keys[str(ind.id)] for ind in detail.possible_duplicates.all()),
                    "score_min": detail.score_min,
                    "score_max": detail.score_max,
                }
                for detail in details
            ),
            key=lambda ticket: ticket["golden_records_individual"],
        )
