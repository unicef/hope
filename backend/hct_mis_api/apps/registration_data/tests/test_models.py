import datetime

from django.conf import settings
from django.test import TestCase

from freezegun import freeze_time

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import Record
from hct_mis_api.apps.registration_datahub.fixtures import (
    ImportedDocumentTypeFactory,
    ImportedHouseholdFactory,
    ImportedIndividualFactory,
    ImportedIndividualIdentityFactory,
    RecordFactory,
    RegistrationDataImportDatahubFactory,
)


class TestRegistrationDataModels(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.program = ProgramFactory(status=Program.ACTIVE)

        # RegistrationDataImport
        cls.registration_data_import = RegistrationDataImportFactory(
            status=RegistrationDataImport.IN_REVIEW, program=cls.program
        )
        cls.rdi = RegistrationDataImportDatahubFactory(hct_id=cls.registration_data_import.id)
        cls.registration_data_import.datahub_id = cls.rdi.id
        cls.registration_data_import.save()
        cls.imported_individual_1 = ImportedIndividualFactory(registration_data_import_id=cls.rdi.id)
        cls.imported_individual_2 = ImportedIndividualFactory(registration_data_import_id=cls.rdi.id)

        # RegistrationDataImportDatahub
        cls.registration_data_import_datahub = RegistrationDataImportDatahubFactory(name="some_name")

        # ImportedHousehold
        cls.imported_household = ImportedHouseholdFactory(
            head_of_household=ImportedIndividualFactory(), registration_data_import=cls.rdi
        )

        # ImportedIndividual
        cls.imported_individual_3 = ImportedIndividualFactory(
            full_name="Jane Doe", birth_date=datetime.datetime(1991, 3, 4), registration_data_import=cls.rdi
        )

        # ImportedDocumentType
        cls.imported_document_type = ImportedDocumentTypeFactory(label="some_label")

        # ImportedIndividualIdentity
        cls.imported_individual_identity = ImportedIndividualIdentityFactory(
            individual=cls.imported_individual_3, document_number="123456789"
        )

        # Record
        cls.record = RecordFactory(
            status=Record.STATUS_TO_IMPORT,
            files=None,
            storage=None,
            fields={},
            registration=1,
            source_id=1,
            timestamp="2023-12-12",
        )

    def test_rdi_all_imported_individuals(self) -> None:
        self.assertTrue(self.imported_individual_1 in self.registration_data_import.all_imported_individuals)
        self.assertTrue(self.imported_individual_2 in self.registration_data_import.all_imported_individuals)

    def test_rdi_can_be_merged(self) -> None:
        self.assertTrue(self.registration_data_import.can_be_merged())

    def test_rdi_datahub_str(self) -> None:
        self.assertEqual(str(self.registration_data_import_datahub), self.registration_data_import_datahub.name)

    def test_imported_household_str(self) -> None:
        self.assertEqual(str(self.imported_household), f"Household ID: {self.imported_household.id}")

    @freeze_time("2024-05-27")
    def test_imported_individual_age(self) -> None:
        self.assertEqual(self.imported_individual_3.age, 33)

    def test_imported_individual_str(self) -> None:
        self.assertEqual(str(self.imported_individual_3), self.imported_individual_3.full_name)

    def test_imported_document_type_str(self) -> None:
        self.assertEqual(str(self.imported_document_type), self.imported_document_type.label)

    def test_record_mark_as_invalid(self) -> None:
        self.record.mark_as_invalid(msg="some_invalid_reason")
        self.assertEqual(self.record.status, Record.STATUS_ERROR)
        self.assertEqual(self.record.error_message, "some_invalid_reason")

    def test_record_mark_as_imported(self) -> None:
        self.record.mark_as_imported()
        self.assertEqual(self.record.status, Record.STATUS_IMPORTED)

    def test_record_get_data(self) -> None:
        self.assertEqual(self.record.get_data(), {})

    def test_imported_individual_identity_str(self) -> None:
        self.assertEqual(str(self.imported_individual_identity), "UNICEF Jane Doe 123456789")
