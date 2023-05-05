import json
import os
import shutil
from typing import Any, Dict, List
from uuid import UUID

from django.conf import settings
from django.core.management import BaseCommand, CommandParser
from django.db.models import Q, QuerySet

from hct_mis_api.apps.core.models import StorageFile
from hct_mis_api.apps.household.models import Document, Household
from hct_mis_api.apps.payment.models import PaymentRecord


def find_paid_households(sf_pk: UUID, business_area_slug: str = "ukraine") -> Dict[str, List[str]]:
    storage_file = StorageFile.objects.get(pk=sf_pk)
    households_loaded_via_sf = Household.objects.filter(
        storage_obj=storage_file, business_area__slug=business_area_slug
    )
    tax_ids_of_inds_loaded_via_sf = Document.objects.filter(
        individual__household__in=households_loaded_via_sf, type__key="tax_id"
    ).values_list("document_number", flat=True)
    hh_ids_not_loaded_via_sf = Household.objects.filter(
        Q(
            individuals__documents__document_number__in=tax_ids_of_inds_loaded_via_sf,
        )
        & ~Q(storage_obj=storage_file)
    ).values_list("id", flat=True)
    payment_records = PaymentRecord.objects.filter(household__id__in=hh_ids_not_loaded_via_sf).distinct("household")
    already_paid_households = payment_records.values_list("household", flat=True)

    def match(household_to_match: Household) -> QuerySet[Household]:
        tax_ids_in_household_to_match = Document.objects.filter(
            individual__household=household_to_match, type__key="tax_id"
        ).values_list("document_number", flat=True)
        return households_loaded_via_sf.filter(
            individuals__documents__document_number__in=tax_ids_in_household_to_match,
        ).values_list("id", flat=True)

    return {str(hh): list(map(str, match(hh))) for hh in already_paid_households}


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("storage_file_pk", type=int)

        parser.add_argument(
            "--business-area-slug",
            type=str,
            default="ukraine",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not options["storage_file_pk"]:
            raise ValueError("storage_file_pk arg is required")

        if not options["business_area_slug"]:
            raise ValueError("business_area_slug arg is required")

        households = find_paid_households(options["storage_file_pk"], options["business_area_slug"])

        generated_dir = os.path.join(settings.PROJECT_ROOT, "..", "generated")
        if os.path.exists(generated_dir):
            shutil.rmtree(generated_dir)
        os.makedirs(generated_dir)
        filepath = os.path.join(generated_dir, "households.json")

        with open(filepath, "w") as file_ptr:
            self.stdout.write(f"Writing households to {filepath}")
            json.dump(households, file_ptr)
