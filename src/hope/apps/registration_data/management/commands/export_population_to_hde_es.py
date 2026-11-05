"""One-off export of the merged population of business areas' active programs into HDE's biographic Elasticsearch."""

from argparse import ArgumentParser
from collections.abc import Iterable, Iterator
import os
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db.models import QuerySet
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from hope.models import BusinessArea, Individual, Program

# HDE reserves this set id for documents HOPE writes itself; its set ids are UUIDs, so they never collide.
MIGRATED_DATASET_ID = "0"
APPROVED_STATUS = "approved"
DEFAULT_CHUNK_SIZE = 2000
REQUEST_TIMEOUT = 60

# Mirrors HDE `schemas.PAYLOAD_FIELDS`: the only fields HDE scores on.
TEXT_FIELDS = ("given_name", "family_name", "full_name", "middle_name", "sex", "relationship")
PHONE_FIELDS = ("phone_no", "phone_no_alternative")
# Mirrors HDE `index.KEY_FIELDS`. HDE filters on them as keyword and refuses an index that maps them otherwise, and
# documents written there would be lost with it when HDE recreates it.
KEY_FIELDS = ("dataset_id", "status")


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
        "Export the merged population of the given business areas' active programs to HDE's biographic Elasticsearch "
        "as approved documents. Reads the HDE Elasticsearch URL from $HDE_ELASTICSEARCH_HOST."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--business-area", dest="business_areas", nargs="+", required=True, help="Business area slugs."
        )
        parser.add_argument("--program", help="Export only the active program with this code.")
        parser.add_argument(
            "--index-prefix",
            default=os.environ.get("HDE_ELASTICSEARCH_PREFIX", ""),
            help="HDE's ELASTICSEARCH_PREFIX. Defaults to $HDE_ELASTICSEARCH_PREFIX.",
        )
        parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help="Documents per bulk request.")
        parser.add_argument("--dry-run", action="store_true", help="Check the indexes and count, write nothing.")

    def handle(self, *args: Any, **options: Any) -> None:
        es_host = self._es_host()
        slugs = options["business_areas"]
        programs = self._programs(self._business_areas(slugs), slugs, options["program"])

        populations = [(program, self._population(program)) for program in programs]
        populations = [(program, queryset) for program, queryset in populations if queryset.exists()]
        if not populations:
            self.stdout.write(f"Nothing to export: no active program in {', '.join(slugs)} has a population.")
            return

        client = Elasticsearch(hosts=[es_host], request_timeout=REQUEST_TIMEOUT)
        index_names = {program.id: hde_index_name(options["index_prefix"], program) for program, _ in populations}
        self._check_indexes(client, index_names.values())

        for program, queryset in populations:
            name = index_names[program.id]
            if options["dry_run"]:
                self.stdout.write(f"{program.code}: {queryset.count()} individuals would be written to {name}")
                continue
            actions = self._actions(name, program, queryset, options["chunk_size"])
            written, _ = bulk(client, actions, chunk_size=options["chunk_size"])
            client.indices.refresh(index=name)
            self.stdout.write(self.style.SUCCESS(f"{program.code}: {written} individuals written to {name}"))

    def _es_host(self) -> str:
        es_host = os.environ.get("HDE_ELASTICSEARCH_HOST")
        if not es_host:
            raise CommandError("HDE Elasticsearch host missing: set HDE_ELASTICSEARCH_HOST.")
        return es_host

    def _business_areas(self, slugs: list[str]) -> list[BusinessArea]:
        business_areas = list(BusinessArea.objects.filter(slug__in=slugs))
        if unknown := sorted(set(slugs) - {business_area.slug for business_area in business_areas}):
            raise CommandError(f"Unknown business area slugs: {', '.join(unknown)}")
        return business_areas

    def _programs(self, business_areas: list[BusinessArea], slugs: list[str], code: str | None) -> QuerySet[Program]:
        programs = Program.objects.filter(business_area__in=business_areas, status=Program.ACTIVE)
        if code:
            programs = programs.filter(code=code)
            if not programs.exists():
                raise CommandError(f"No active program with code {code} in {', '.join(slugs)}.")
        return programs.select_related("business_area").order_by("business_area__slug", "code")

    def _check_indexes(self, client: Elasticsearch, index_names: Iterable[str]) -> None:
        # Runs over every index before the first write, so a run over several business areas is all or nothing.
        index_names = list(index_names)
        if missing := [name for name in index_names if not client.indices.exists(index=name)]:
            raise CommandError(f"HDE has not created these indexes yet, nothing was written: {', '.join(missing)}")
        if outdated := self._mapping_problems(client, index_names):
            raise CommandError(
                f"HDE has to recreate these indexes, they do not map {', '.join(KEY_FIELDS)} as keyword. "
                f"Nothing was written: {'; '.join(outdated)}"
            )

    def _mapping_problems(self, client: Elasticsearch, index_names: Iterable[str]) -> list[str]:
        problems = []
        for name in index_names:
            response = client.indices.get_mapping(index=name)
            properties = next(iter(response.values()))["mappings"].get("properties", {})
            for field in KEY_FIELDS:
                field_type = properties.get(field, {}).get("type")
                if field_type != "keyword":
                    problems.append(f"{name} maps {field} as {field_type or 'nothing'}")
        return problems

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
