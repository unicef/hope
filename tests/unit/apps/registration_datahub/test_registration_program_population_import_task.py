from typing import Any, Optional
from unittest.mock import patch

from django.test import TestCase
import pytest

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, CountryFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.models.household import (
    HEAD,
    MALE,
    ROLE_PRIMARY,
    Household,
)
from hope.models.individual_role_in_household import IndividualRoleInHousehold
from hope.models.individual_identity import IndividualIdentity
from hope.models.individual import Individual
from hope.models.document import Document
from hope.models.registration_data_import import RegistrationDataImport
from hope.apps.registration_datahub.celery_tasks import (
    registration_program_population_import_task,
)
from hope.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestRegistrationProgramPopulationImportTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.afghanistan = create_afghanistan()
        country = CountryFactory()
        cls.program_from = ProgramFactory(business_area=cls.afghanistan)
        cls.program_to = ProgramFactory(business_area=cls.afghanistan)
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.afghanistan,
            program=cls.program_to,
        )
        cls.rdi_other = RegistrationDataImportFactory(
            business_area=cls.afghanistan,
            program=cls.program_from,
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.rdi_other,
                "program": cls.program_from,
                "admin1": AreaFactory(),
                "admin2": AreaFactory(),
                "admin3": AreaFactory(),
                "admin4": AreaFactory(),
                "detail_id": "1234567890",
                "flex_fields": {"enumerator_id": "123", "some": "thing"},
            },
            individuals_data=[
                {
                    "registration_data_import": cls.rdi_other,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-07",
                },
                {},
            ],
        )
        cls.ind_role_in_hh = IndividualRoleInHouseholdFactory(
            household=cls.household,
            individual=cls.individuals[1],
            role=ROLE_PRIMARY,
        )
        document_type = DocumentTypeFactory(key="birth_certificate")
        DocumentTypeFactory(
            key=document_type.key,
        )
        cls.document = DocumentFactory(
            individual=cls.individuals[0],
            program=cls.program_from,
            type=document_type,
            country=country,
        )
        cls.identity = IndividualIdentityFactory(
            individual=cls.individuals[0],
            country=country,
            partner=PartnerFactory(),
        )

        rebuild_search_index()

    def _run_task(self, rdi_id: Optional[str] = None) -> None:
        registration_program_population_import_task(
            rdi_id or str(self.registration_data_import.id),
            str(self.afghanistan.id),
            str(self.program_from.id),
            str(self.program_to.id),
        )

    def _imported_objects_count_before(self) -> None:
        assert Household.pending_objects.filter().count() == 0
        assert Individual.pending_objects.count() == 0
        assert IndividualIdentity.pending_objects.count() == 0
        assert Document.pending_objects.count() == 0
        assert IndividualRoleInHousehold.pending_objects.count() == 0

    def _imported_objects_count_after(self, multiplier: int = 1) -> None:
        assert Household.pending_objects.count() == 1 * multiplier
        assert Individual.pending_objects.count() == 2 * multiplier
        assert IndividualIdentity.pending_objects.count() == 1 * multiplier
        assert Document.pending_objects.count() == 1 * multiplier
        assert IndividualRoleInHousehold.pending_objects.count() == 1 * multiplier

    def test_registration_program_population_import_task_wrong_status(self) -> None:
        rdi_status = self.registration_data_import.status
        self._run_task()
        self.registration_data_import.refresh_from_db()
        assert rdi_status == self.registration_data_import.status

    def test_registration_program_population_import_task(self) -> None:
        self.registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
        self.registration_data_import.save()

        self._imported_objects_count_before()

        self._run_task()

        self.registration_data_import.refresh_from_db()
        assert self.registration_data_import.status == RegistrationDataImport.IN_REVIEW

        self._imported_objects_count_after()

        registration_data_import2 = RegistrationDataImportFactory(
            name="Other",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            business_area=self.afghanistan,
            program=self.program_to,
        )

        registration_program_population_import_task(
            str(registration_data_import2.id),
            str(self.afghanistan.id),
            str(self.program_from.id),
            str(self.program_to.id),
        )
        self._imported_objects_count_after(1)

    def test_registration_program_population_import_task_error(self) -> None:
        rdi_id = self.registration_data_import.id
        self.registration_data_import.delete()
        with pytest.raises(RegistrationDataImport.DoesNotExist):
            self._run_task(str(rdi_id))

    def test_registration_program_population_import_ba_postpone_deduplication(
        self,
    ) -> None:
        self.afghanistan.postpone_deduplication = True
        self.afghanistan.save()
        self.registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
        self.registration_data_import.save()

        self._run_task()

        self.registration_data_import.refresh_from_db()
        assert self.registration_data_import.status == RegistrationDataImport.IN_REVIEW

    @patch("hope.apps.registration_datahub.celery_tasks.locked_cache")
    def test_registration_program_population_import_locked_cache(self, mocked_locked_cache: Any) -> None:
        mocked_locked_cache.return_value.__enter__.return_value = False
        self.registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
        self.registration_data_import.save()

        self._run_task()

        self.registration_data_import.refresh_from_db()
        assert self.registration_data_import.status == RegistrationDataImport.IMPORT_SCHEDULED
