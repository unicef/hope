import random
import time

from django.core.management import BaseCommand, call_command
from django.db import transaction
from django_countries.data import COUNTRIES

from account.fixtures import UserFactory
from core.fixtures import AdminAreaFactory, AdminAreaTypeFactory
from core.models import BusinessArea, AdminArea
from household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    EntitlementCardFactory,
)
from django.utils.translation import ugettext_lazy as _
from household.models import RELATIONSHIP_CHOICE, DocumentType
from payment.fixtures import PaymentRecordFactory
from program.fixtures import CashPlanFactory, ProgramFactory
from registration_data.fixtures import RegistrationDataImportFactory
from registration_data.models import RegistrationDataImport
from registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    ImportedIndividualFactory,
    ImportedHouseholdFactory,
)
from targeting.fixtures import (
    TargetPopulationFactory,
    TargetingCriteriaRuleFactory,
    TargetingCriteriaRuleFilterFactory,
    TargetingCriteriaFactory,
)


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
        for alpha2, name in COUNTRIES:
            for type, label in identification_type_choice:
                document_types.append(
                    DocumentType(country=alpha2, type=type, label=label)
                )
        DocumentType.objects.bulk_create(document_types)
