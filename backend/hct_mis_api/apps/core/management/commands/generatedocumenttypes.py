from django.core.management import BaseCommand
from django.db import transaction
from django_countries.data import COUNTRIES

from household.models import DocumentType, IDENTIFICATION_TYPE_CHOICE
from registration_datahub.models import ImportedDocumentType as RDHDocumentType


class Command(BaseCommand):
    help = "Generate document types for all countries"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING("Generate document types for all countries")
        )
        self._generate_document_types_for_all_countries()

    def _generate_document_types_for_all_countries(self):
        identification_type_choice = tuple(
            (doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE
            if doc_type != "OTHER"
        )
        document_types = []
        rdh_document_types = []
        for alpha2 in COUNTRIES:
            for doc_type, label in identification_type_choice:
                document_types.append(
                    DocumentType(country=alpha2, label=label, type=doc_type)
                )
                rdh_document_types.append(
                    RDHDocumentType(country=alpha2, label=label, type=doc_type)
                )
        DocumentType.objects.bulk_create(document_types)
        RDHDocumentType.objects.bulk_create(rdh_document_types)
