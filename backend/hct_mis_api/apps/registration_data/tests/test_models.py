import datetime

from django.conf import settings
from django.test import TestCase

from freezegun import freeze_time

from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import (
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
)
from hct_mis_api.apps.household.models import Household, Individual, IndividualIdentity
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class TestRegistrationDataModels(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.program = ProgramFactory(status=Program.ACTIVE)
        partner = PartnerFactory()

        # RegistrationDataImport
        cls.registration_data_import = RegistrationDataImportFactory(
            status=RegistrationDataImport.IN_REVIEW, program=cls.program
        )
        cls.imported_individual_1 = IndividualFactory(
            registration_data_import_id=cls.registration_data_import.id, rdi_merge_status=Individual.PENDING
        )
        cls.imported_individual_2 = IndividualFactory(
            registration_data_import_id=cls.registration_data_import.id, rdi_merge_status=Individual.PENDING
        )

        # ImportedHousehold
        cls.imported_household = HouseholdFactory(
            head_of_household=IndividualFactory(),
            registration_data_import=cls.registration_data_import,
            rdi_merge_status=Household.PENDING,
        )

        # ImportedIndividual
        cls.imported_individual_3 = IndividualFactory(
            full_name="Jane Doe",
            birth_date=datetime.datetime(1991, 3, 4),
            registration_data_import=cls.registration_data_import,
            rdi_merge_status=Individual.PENDING,
        )

        # ImportedDocumentType
        cls.imported_document_type = DocumentTypeFactory(label="some_label")

        # ImportedIndividualIdentity
        cls.imported_individual_identity = IndividualIdentityFactory(
            individual=cls.imported_individual_3,
            number="123456789",
            rdi_merge_status=IndividualIdentity.PENDING,
            partner=partner,
        )

    def test_rdi_can_be_merged(self) -> None:
        self.assertTrue(self.registration_data_import.can_be_merged())

    def test_imported_household_str(self) -> None:
        self.assertEqual(str(self.imported_household), self.imported_household.unicef_id)

    @freeze_time("2024-05-27")
    def test_imported_individual_age(self) -> None:
        self.assertEqual(self.imported_individual_3.age, 33)

    def test_imported_individual_str(self) -> None:
        self.assertEqual(str(self.imported_individual_3), self.imported_individual_3.unicef_id)

    def test_imported_document_type_str(self) -> None:
        self.assertEqual(str(self.imported_document_type), self.imported_document_type.label)

    def test_imported_individual_identity_str(self) -> None:
        self.assertEqual(
            str(self.imported_individual_identity), f"UNICEF {self.imported_individual_3.unicef_id} 123456789"
        )
