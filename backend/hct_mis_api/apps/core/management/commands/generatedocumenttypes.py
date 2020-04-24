from django.core.management import BaseCommand
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django_countries.data import COUNTRIES

from household.models import DocumentType
from registration_datahub.models import DocumentType as RDHDocumentType


class Command(BaseCommand):
    help = "Generate document types for all countries"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING("Generate document types for all countries")
        )
        self._generate_document_types_for_all_countries()

    def _generate_document_types_for_all_countries(self):
        identification_type_choice = (
            ("BIRTH_CERTIFICATE", _("Birth Certificate")),
            ("DRIVING_LICENSE", _("Driving License")),
            ("NATIONAL_ID", _("National ID")),
            ("NATIONAL_PASSPORT", _("National Passport")),
        )
        document_types = []
        rdh_document_types = []
        for alpha2 in COUNTRIES:
            for type, label in identification_type_choice:
                document_types.append(
                    DocumentType(country=alpha2, type=type, label=label)
                )
                rdh_document_types.append(
                    RDHDocumentType(country=alpha2, type=type, label=label)
                )
        DocumentType.objects.bulk_create(document_types)
        RDHDocumentType.objects.bulk_create(rdh_document_types)
