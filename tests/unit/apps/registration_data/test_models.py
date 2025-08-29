import datetime

from django.core.management import call_command
from django.test import TestCase
from freezegun import freeze_time

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import (
    RegistrationDataImportDatahubFactory,
    RegistrationDataImportFactory,
)
from hope.models.household import Household
from hope.models.individual import Individual
from hope.models.individual_identity import IndividualIdentity
from hope.models.program import Program
from hope.models.registration_data_import import RegistrationDataImport


class TestRegistrationDataModels(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init_geo_fixtures")
        create_afghanistan()
        cls.program = ProgramFactory(status=Program.ACTIVE)
        partner = PartnerFactory()

        # RegistrationDataImport
        cls.registration_data_import = RegistrationDataImportFactory(
            status=RegistrationDataImport.IN_REVIEW, program=cls.program
        )
        cls.imported_individual_1 = IndividualFactory(
            registration_data_import_id=cls.registration_data_import.id,
            rdi_merge_status=Individual.PENDING,
        )
        cls.imported_individual_2 = IndividualFactory(
            registration_data_import_id=cls.registration_data_import.id,
            rdi_merge_status=Individual.PENDING,
        )

        # ImportedHousehold
        cls.imported_household = HouseholdFactory(
            head_of_household=IndividualFactory(),
            registration_data_import=cls.registration_data_import,
            rdi_merge_status=Household.PENDING,
            size=99,
        )

        # ImportedIndividual
        cls.imported_individual_3 = IndividualFactory(
            full_name="Jane Doe",
            birth_date=datetime.datetime(1991, 3, 4),
            registration_data_import=cls.registration_data_import,
            rdi_merge_status=Individual.PENDING,
            household=cls.imported_household,
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
        assert self.registration_data_import.can_be_merged()

    def test_imported_household_str(self) -> None:
        assert str(self.imported_household) == self.imported_household.unicef_id

    @freeze_time("2024-05-27")
    def test_imported_individual_age(self) -> None:
        assert self.imported_individual_3.age == 33

    def test_imported_individual_str(self) -> None:
        assert str(self.imported_individual_3) == self.imported_individual_3.unicef_id

    def test_imported_document_type_str(self) -> None:
        assert str(self.imported_document_type) == self.imported_document_type.label

    def test_imported_individual_identity_str(self) -> None:
        assert (
            str(self.imported_individual_identity)
            == f"UNICEF HQ [Sub-Partner of UNICEF] {self.imported_individual_3.unicef_id} 123456789"
        )

    def test_bulk_update_household_size(self) -> None:
        self.imported_household.refresh_from_db(fields=["size"])
        assert self.imported_household.size == 99

        self.registration_data_import.bulk_update_household_size()
        self.imported_household.refresh_from_db(fields=["size"])
        assert self.imported_household.size == 99

        # upd DCT recalculate_composition
        self.program.data_collecting_type.recalculate_composition = True
        self.program.data_collecting_type.save()

        self.registration_data_import.bulk_update_household_size()
        self.imported_household.refresh_from_db(fields=["size"])
        assert self.imported_household.size == 1


class TestRegistrationDataImportDatahub(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.name = "RDI datahub name"
        cls.business_area_slug = "RDI business_area slug"
        cls.rdi_datahub = RegistrationDataImportDatahubFactory(
            name=cls.name,
            business_area_slug=cls.business_area_slug,
        )
        cls.program = ProgramFactory(status=Program.ACTIVE)
        cls.rdi = RegistrationDataImportFactory(
            program=cls.program,
        )

    def test_str(self) -> None:
        assert str(self.rdi_datahub) == self.rdi_datahub.name

    def test_business_area(self) -> None:
        assert self.rdi_datahub.business_area == self.business_area_slug
