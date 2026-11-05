"""One-off export of the merged population of a business area's active programs into HDE's biographic Elasticsearch."""

from argparse import ArgumentParser
from collections.abc import Iterator
import os
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db.models import QuerySet
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from hope.models import BusinessArea, Individual, Program

MIGRATED_DATASET_ID = 0
APPROVED_STATUS = "approved"
DEFAULT_CHUNK_SIZE = 2000
REQUEST_TIMEOUT = 60

# Mirrors HDE `schemas.PAYLOAD_FIELDS`: the only fields HDE scores on.
TEXT_FIELDS = ("given_name", "family_name", "full_name", "middle_name", "sex", "relationship")
PHONE_FIELDS = ("phone_no", "phone_no_alternative")


def hde_index_name(prefix: str, program: Program) -> str:
    return f"{prefix}biographic_{program.business_area.slug.lower()}_{program.code.lower()}"


def hde_reference_pk(individual: Individual) -> str:
    # TODO(346504): the identity of migrated individuals is not decided yet. Biographic findings are
    # resolved by country_workspace_id, so an individual exported under its HOPE id is not found.
    return individual.country_workspace_id or str(individual.id)


def to_hde_document(individual: Individual, program: Program) -> dict[str, Any]:
    document: dict[str, Any] = {
        "reference_pk": hde_reference_pk(individual),
        "dataset_id": MIGRATED_DATASET_ID,
        "business_area": program.business_area.slug.lower(),
        "program_code": program.code.lower(),
        "status": APPROVED_STATUS,
        "birth_date": individual.birth_date.isoformat(),
    }
    for field in TEXT_FIELDS:
        document[field] = getattr(individual, field)
    for field in PHONE_FIELDS:
        # The same `__str__` HOPE's own index uses; phones score as exact keyword matches.
        document[field] = str(getattr(individual, field))
    return document


class Command(BaseCommand):
    help = (
        "Export the merged population of a business area's active programs to HDE's biographic Elasticsearch "
        "as approved documents. Reads the HDE Elasticsearch URL from $HDE_ELASTICSEARCH_HOST."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--business-area", required=True, help="Business area slug.")
        parser.add_argument("--program", help="Export only the active program with this code.")
        parser.add_argument(
            "--index-prefix",
            default=os.environ.get("HDE_ELASTICSEARCH_PREFIX", ""),
            help="HDE's ELASTICSEARCH_PREFIX. Defaults to $HDE_ELASTICSEARCH_PREFIX.",
        )
        parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help="Documents per bulk request.")
        parser.add_argument("--dry-run", action="store_true", help="Check the indexes and count, write nothing.")

    def handle(self, *args: Any, **options: Any) -> None:
        es_host = os.environ.get("HDE_ELASTICSEARCH_HOST")
        if not es_host:
            raise CommandError("HDE Elasticsearch host missing: set HDE_ELASTICSEARCH_HOST.")
        business_area = BusinessArea.objects.filter(slug=options["business_area"]).first()
        if business_area is None:
            raise CommandError(f"Unknown business area slug: {options['business_area']}")

        programs = Program.objects.filter(business_area=business_area, status=Program.ACTIVE).select_related(
            "business_area"
        )
        if options["program"]:
            programs = programs.filter(code=options["program"])
            if not programs.exists():
                raise CommandError(f"No active program with code {options['program']} in {business_area.slug}.")

        populations = [(program, self._population(program)) for program in programs.order_by("code")]
        populations = [(program, queryset) for program, queryset in populations if queryset.exists()]
        if not populations:
            self.stdout.write(f"Nothing to export: no active program in {business_area.slug} has a population.")
            return

        client = Elasticsearch(hosts=[es_host], request_timeout=REQUEST_TIMEOUT)
        names = {program.id: hde_index_name(options["index_prefix"], program) for program, _ in populations}
        if missing := [name for name in names.values() if not client.indices.exists(index=name)]:
            raise CommandError(f"HDE has not created these indexes yet, nothing was written: {', '.join(missing)}")

        for program, queryset in populations:
            name = names[program.id]
            if options["dry_run"]:
                self.stdout.write(f"{program.code}: {queryset.count()} individuals would be written to {name}")
                continue
            actions = self._actions(name, program, queryset, options["chunk_size"])
            written, _ = bulk(client, actions, chunk_size=options["chunk_size"])
            client.indices.refresh(index=name)
            self.stdout.write(self.style.SUCCESS(f"{program.code}: {written} individuals written to {name}"))

    def _population(self, program: Program) -> QuerySet[Individual]:
        return (
            Individual.available_objects.filter(program=program, withdrawn=False)
            .only("id", "country_workspace_id", "birth_date", *TEXT_FIELDS, *PHONE_FIELDS)
            .order_by("id")
        )

    def _actions(
        self, name: str, program: Program, queryset: QuerySet[Individual], chunk_size: int
    ) -> Iterator[dict[str, Any]]:
        for individual in queryset.iterator(chunk_size=chunk_size):
            document = to_hde_document(individual, program)
            yield {
                "_index": name,
                "_id": f"{MIGRATED_DATASET_ID}:{document['reference_pk']}",
                "_source": document,
            }
