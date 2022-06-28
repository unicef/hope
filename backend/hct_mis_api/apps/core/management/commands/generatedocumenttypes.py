from django.core.management import BaseCommand
from django.db import transaction

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_CHOICE,
    Agency,
    DocumentType,
)
from hct_mis_api.apps.registration_datahub.models import ImportedAgency
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocumentType as RDHDocumentType,
)


class Command(BaseCommand):
    help = "Generate document types for all countries"

    @transaction.atomic
    def handle(self, *args, **options):
        # self.stdout.write(self.style.WARNING("Generate document types for all countries"))
        self._generate_document_types_for_all_countries()

    def _generate_document_types_for_all_countries(self):
        identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
        document_types = []
        rdh_document_types = []
        agencies = []
        rdh_agencies = []
        for country in Country.objects.all():
            for doc_type, label in identification_type_choice:
                document_types.append(DocumentType(country=country, label=label, type=doc_type))
                rdh_document_types.append(RDHDocumentType(country=country.iso_code2, label=label, type=doc_type))
            agencies_types = {
                "UNHCR",
                "WFP",
            }
            for agency in agencies_types:
                agencies.append(Agency(type=agency, label=agency, country=country.iso_code2))
                rdh_agencies.append(ImportedAgency(type=agency, label=agency, country=country.iso_code2))

        DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)
        RDHDocumentType.objects.bulk_create(rdh_document_types, ignore_conflicts=True)
        Agency.objects.bulk_create(agencies, ignore_conflicts=True)
        ImportedAgency.objects.bulk_create(rdh_agencies, ignore_conflicts=True)
