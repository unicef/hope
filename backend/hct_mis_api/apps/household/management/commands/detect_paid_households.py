import json
import os
import shutil
from collections import defaultdict
from dataclasses import dataclass

from django.core.management import BaseCommand
from django.db.models import Q
from django.conf import settings

from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.core.models import StorageFile


def find_paid_households(sf_pk, business_area_slug="ukraine"):
    storage_file = StorageFile.objects.get(pk=sf_pk)
    households_loaded_via_sf = Household.objects.filter(
        storage_obj=storage_file, business_area__slug=business_area_slug
    )
    tax_ids_of_inds_loaded_via_sf = Document.objects.filter(
        individual__household__in=households_loaded_via_sf, type__type="TAX_ID"
    ).values_list("document_number", flat=True)
    print(f"tax_ids_of_inds_loaded_via_sf")
    hh_ids_not_loaded_via_sf = Household.objects.filter(
        Q(
            individuals__documents__document_number__in=tax_ids_of_inds_loaded_via_sf,
        )
        & ~Q(storage_obj=storage_file)
    ).values_list("id", flat=True)
    print(f"hh_ids_not_loaded_via_sf")
    payment_records = PaymentRecord.objects.filter(household__id__in=hh_ids_not_loaded_via_sf).distinct("household")
    already_paid_households = payment_records.values_list("household", flat=True)
    mapping = {}
    count = already_paid_households.count()
    print(f"already_paid_households",count)
    already_paid_pairs = Document.objects.filter(
        individual__household__in=already_paid_households, type__type="TAX_ID"
    ).values("document_number", "individual__household__unicef_id")
    print(f"already_paid_pairs")
    loaded_via_sf_pairs = Document.objects.filter(
        individual__household__in=households_loaded_via_sf, type__type="TAX_ID"
    ).values("document_number", "individual__household__unicef_id")
    already_paid_documents_dict = {pair["document_number"]: pair["individual__household__unicef_id"] for pair in already_paid_pairs}
    loaded_via_sf_documents_dict =defaultdict(list)
    print(f"already_paid_documents_dict")
    for pair in loaded_via_sf_pairs:
        loaded_via_sf_documents_dict[pair["document_number"]].append(str(pair["individual__household__unicef_id"]))
    already_paid_documents_set = set(already_paid_documents_dict.keys())
    loaded_via_sf_documents_set = set(loaded_via_sf_documents_dict.keys())
    print(f"loaded_via_sf_documents_set")
    intersect_docs = already_paid_documents_set.intersection(loaded_via_sf_documents_set)
    print(f"intersect_docs")

    for doc in intersect_docs:
        if len(loaded_via_sf_documents_dict[doc]) > 1:
            print(f"doc {doc} has more than one household {loaded_via_sf_documents_dict[doc]}")
        mapping[str(already_paid_documents_dict[doc])] = (loaded_via_sf_documents_dict[doc],doc)
    return mapping


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("storage_file_pk", type=int)

        parser.add_argument(
            "--business-area-slug",
            type=str,
            default="ukraine",
        )

    def handle(self, *args, **options):
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
            json_list = []
            for key, value in households.items():
                json_list.append({
                    'original_household': key,
                    'households_from_file': value[0],
                    'tax_id': value[1]
                })
            json.dump(json_list, file_ptr)
