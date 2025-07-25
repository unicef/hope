from contextlib import contextmanager
from typing import Callable, Dict, Generator
from unittest import mock
from unittest.mock import patch

from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections
from django.forms import model_to_dict
from django.test import TestCase

import pytest
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import (
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from extras.test_utils.factories.sanction_list import SanctionListFactory
from freezegun import freeze_time
from parameterized import parameterized

from hct_mis_api.apps.household.models import (
    BROTHER_SISTER,
    COUSIN,
    HEAD,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    Household,
    Individual,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from hct_mis_api.apps.registration_data.models import (
    KoboImportedSubmission,
    RegistrationDataImport,
)
from hct_mis_api.apps.registration_datahub.tasks.rdi_merge import RdiMergeTask
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@contextmanager
def capture_on_commit_callbacks(
    *, using: str = DEFAULT_DB_ALIAS, execute: bool = False
) -> Generator[list[Callable[[], None]], None, None]:
    callbacks: list[Callable[[], None]] = []
    start_count = len(connections[using].run_on_commit)
    try:
        yield callbacks
    finally:
        while True:
            callback_count = len(connections[using].run_on_commit)
            for _, callback in connections[using].run_on_commit[start_count:]:
                callbacks.append(callback)
                if execute:
                    callback()

            if callback_count == len(connections[using].run_on_commit):
                break
            start_count = callback_count


@pytest.mark.elasticsearch
class TestRdiMergeTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
        call_command("init-core-fixtures")
        cls.business_area = create_afghanistan()
        program = ProgramFactory()
        cls.rdi = RegistrationDataImportFactory(program=program, business_area=cls.business_area)
        cls.rdi.business_area.postpone_deduplication = True
        cls.rdi.business_area.save()

        area_type_level_1 = AreaTypeFactory(
            name="State1",
            area_level=1,
        )
        area_type_level_2 = AreaTypeFactory(
            name="State2",
            area_level=2,
        )
        area_type_level_3 = AreaTypeFactory(
            name="State3",
            area_level=3,
        )
        area_type_level_4 = AreaTypeFactory(
            name="State4",
            area_level=4,
        )
        cls.area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")
        cls.area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code="area2", parent=cls.area1)
        cls.area3 = AreaFactory(name="City Test3", area_type=area_type_level_3, p_code="area3", parent=cls.area2)
        cls.area4 = AreaFactory(name="City Test4", area_type=area_type_level_4, p_code="area4", parent=cls.area3)

        rebuild_search_index()

    @classmethod
    def set_imported_individuals(cls, household: PendingHousehold) -> None:
        individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "relationship": HEAD,
                "birth_date": "1962-02-02",  # age 39
                "sex": "MALE",
                "registration_data_import": cls.rdi,
                "household": household,
                "email": "fake_email_1@com",
                "wallet_name": "Wallet Name 1",
                "blockchain_name": "Blockchain Name 1",
                "wallet_address": "Wallet Address 1",
                "unicef_id": "IND-9",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "relationship": COUSIN,
                "birth_date": "2017-02-15",  # age 4
                "sex": "MALE",
                "registration_data_import": cls.rdi,
                "household": household,
                "email": "fake_email_2@com",
                "unicef_id": "IND-8",
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "relationship": COUSIN,
                "birth_date": "2011-12-21",  # age 10
                "sex": "MALE",
                "registration_data_import": cls.rdi,
                "household": household,
                "email": "fake_email_3@com",
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "relationship": BROTHER_SISTER,
                "birth_date": "2006-03-23",  # age 15
                "sex": "MALE",
                "registration_data_import": cls.rdi,
                "household": household,
                "email": "fake_email_4@com",
            },
            {
                "full_name": "Baz Bush",
                "given_name": "Baz",
                "family_name": "Bush",
                "relationship": BROTHER_SISTER,
                "birth_date": "2005-02-21",  # age 16
                "sex": "MALE",
                "registration_data_import": cls.rdi,
                "household": household,
                "email": "fake_email_5@com",
            },
            {
                "full_name": "Liz Female",
                "given_name": "Liz",
                "family_name": "Female",
                "relationship": BROTHER_SISTER,
                "birth_date": "2005-10-10",  # age 16
                "sex": "FEMALE",
                "registration_data_import": cls.rdi,
                "phone_no": "+41 (0) 78 927 2696",
                "phone_no_alternative": "+41 (0) 78 927 2696",
                "phone_no_valid": None,
                "phone_no_alternative_valid": None,
                "household": household,
                "email": "fake_email_6@com",
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "relationship": BROTHER_SISTER,
                "birth_date": "1996-11-29",  # age 25
                "sex": "FEMALE",
                "registration_data_import": cls.rdi,
                "phone_no": "wrong-phone",
                "phone_no_alternative": "definitely-wrong-phone",
                "phone_no_valid": None,
                "phone_no_alternative_valid": None,
                "household": household,
                "email": "fake_email_7@com",
            },
            {
                "full_name": "Bob Jackson",
                "given_name": "Bob",
                "family_name": "Jackson",
                "relationship": BROTHER_SISTER,
                "birth_date": "1956-03-03",  # age 65
                "sex": "MALE",
                "registration_data_import": cls.rdi,
                "household": household,
                "email": "",
            },
        ]

        cls.individuals = [PendingIndividualFactory(**individual) for individual in individuals_to_create]

    @freeze_time("2022-01-01")
    def test_merge_rdi_and_recalculation(self) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=self.rdi,
            admin4=self.area4,
            admin3=self.area3,
            admin2=self.area2,
            admin1=self.area1,
            zip_code="00-123",
            detail_id="123456123",
            kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
            kobo_submission_time="2022-02-22T12:22:22",
            flex_fields={"enumerator_id": 1234567890},
            program=self.rdi.program,
        )
        dct = self.rdi.program.data_collecting_type
        dct.recalculate_composition = True
        dct.save()

        self.set_imported_individuals(hh)
        hh.head_of_household = PendingIndividual.objects.first()
        hh.save()

        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

        households = Household.objects.all()
        individuals = Individual.objects.all()

        household = households.first()

        self.assertEqual(1, households.count())
        self.assertEqual(8, individuals.count())
        self.assertEqual(household.flex_fields.get("enumerator_id"), 1234567890)
        self.assertEqual(household.detail_id, "123456123")

        # check KoboImportedSubmission
        kobo_import_submission_qs = KoboImportedSubmission.objects.all()
        kobo_import_submission = kobo_import_submission_qs.first()
        self.assertEqual(kobo_import_submission_qs.count(), 1)
        self.assertEqual(str(kobo_import_submission.kobo_submission_uuid), "c09130af-6c9c-4dba-8c7f-1b2ff1970d19")
        self.assertEqual(kobo_import_submission.kobo_asset_id, "123456123")
        self.assertEqual(str(kobo_import_submission.kobo_submission_time), "2022-02-22 12:22:22+00:00")
        # self.assertEqual(kobo_import_submission.imported_household, None)

        individual_with_valid_phone_data = Individual.objects.filter(given_name="Liz").first()
        individual_with_invalid_phone_data = Individual.objects.filter(given_name="Jenna").first()

        self.assertEqual(individual_with_valid_phone_data.phone_no_valid, True)
        self.assertEqual(individual_with_valid_phone_data.phone_no_alternative_valid, True)

        self.assertEqual(individual_with_invalid_phone_data.phone_no_valid, False)
        self.assertEqual(individual_with_invalid_phone_data.phone_no_alternative_valid, False)

        self.assertEqual(Individual.objects.filter(full_name="Baz Bush").first().email, "fake_email_5@com")
        self.assertEqual(Individual.objects.filter(full_name="Benjamin Butler").first().email, "fake_email_1@com")
        self.assertEqual(Individual.objects.filter(full_name="Bob Jackson").first().email, "")
        self.assertEqual(Individual.objects.filter(full_name="Benjamin Butler").first().wallet_name, "Wallet Name 1")
        self.assertEqual(
            Individual.objects.filter(full_name="Benjamin Butler").first().blockchain_name, "Blockchain Name 1"
        )
        self.assertEqual(
            Individual.objects.filter(full_name="Benjamin Butler").first().wallet_address, "Wallet Address 1"
        )

        household_data: Dict = model_to_dict(
            household,  # type: ignore
            (
                "female_age_group_0_5_count",
                "female_age_group_6_11_count",
                "female_age_group_12_17_count",
                "female_age_group_18_59_count",
                "female_age_group_60_count",
                "male_age_group_0_5_count",
                "male_age_group_6_11_count",
                "male_age_group_12_17_count",
                "male_age_group_18_59_count",
                "male_age_group_60_count",
                "children_count",
                "size",
                "admin1",
                "admin2",
                "admin3",
                "admin4",
                "zip_code",
            ),
        )

        expected = {
            "female_age_group_0_5_count": 0,
            "female_age_group_6_11_count": 0,
            "female_age_group_12_17_count": 1,
            "female_age_group_18_59_count": 1,
            "female_age_group_60_count": 0,
            "male_age_group_0_5_count": 1,
            "male_age_group_6_11_count": 1,
            "male_age_group_12_17_count": 2,
            "male_age_group_18_59_count": 1,
            "male_age_group_60_count": 1,
            "children_count": 5,
            "size": 8,
            "admin1": self.area1.id,
            "admin2": self.area2.id,
            "admin3": self.area3.id,
            "admin4": self.area4.id,
            "zip_code": "00-123",
        }
        self.assertEqual(household_data, expected)

    @freeze_time("2022-01-01")
    @patch("hct_mis_api.apps.registration_datahub.tasks.rdi_merge.check_against_sanction_list_pre_merge")
    def test_merge_rdi_sanction_list_check(self, sanction_execute_mock: mock.MagicMock) -> None:
        household = PendingHouseholdFactory(
            registration_data_import=self.rdi,
            admin4=self.area4,
            admin3=self.area3,
            admin2=self.area2,
            admin1=self.area1,
            zip_code="00-123",
            detail_id="123456123",
            kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
            kobo_submission_time="2022-02-22T12:22:22",
            flex_fields={"enumerator_id": 1234567890},
        )
        sanction_list = SanctionListFactory()
        dct = self.rdi.program.data_collecting_type
        dct.recalculate_composition = True
        dct.save()
        self.business_area.save()
        self.rdi.screen_beneficiary = True
        self.rdi.save()
        program = self.rdi.program
        program.sanction_lists.add(sanction_list)
        program.refresh_from_db()
        self.set_imported_individuals(household)
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)
        sanction_execute_mock.assert_called_once()
        sanction_execute_mock.reset_mock()

    @freeze_time("2022-01-01")
    @patch("hct_mis_api.apps.registration_datahub.tasks.rdi_merge.check_against_sanction_list_pre_merge")
    def test_merge_rdi_sanction_list_check_business_area_false(self, sanction_execute_mock: mock.MagicMock) -> None:
        household = PendingHouseholdFactory(
            registration_data_import=self.rdi,
            admin4=self.area4,
            admin3=self.area3,
            admin2=self.area2,
            admin1=self.area1,
            zip_code="00-123",
            detail_id="123456123",
            kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
            kobo_submission_time="2022-02-22T12:22:22",
            flex_fields={"enumerator_id": 1234567890},
        )
        dct = self.rdi.program.data_collecting_type
        dct.recalculate_composition = True
        dct.save()

        self.business_area.save()
        self.rdi.screen_beneficiary = True
        self.rdi.save()
        self.set_imported_individuals(household)
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)
        sanction_execute_mock.assert_not_called()

    @freeze_time("2022-01-01")
    @patch("hct_mis_api.apps.registration_datahub.tasks.rdi_merge.check_against_sanction_list_pre_merge")
    def test_merge_rdi_sanction_list_check_rdi_false(self, sanction_execute_mock: mock.MagicMock) -> None:
        household = PendingHouseholdFactory(
            registration_data_import=self.rdi,
            admin4=self.area4,
            admin3=self.area3,
            admin2=self.area2,
            admin1=self.area1,
            zip_code="00-123",
            detail_id="123456123",
            kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
            kobo_submission_time="2022-02-22T12:22:22",
            flex_fields={"enumerator_id": 1234567890},
        )
        self.business_area.save()
        self.rdi.screen_beneficiary = False
        self.rdi.save()
        self.set_imported_individuals(household)
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)
        sanction_execute_mock.assert_not_called()

    @parameterized.expand(
        [
            True,
            False,
            None,
        ]
    )
    def test_merge_rdi_create_collections(self, household_representation_exists: bool) -> None:
        """
        household_representation_exists:
        if True, another household representation exists, and it has collection,
        if False, another household representation exists, but it does not have collection,
        if None, household representation does not exist in another program
        """
        program_2 = ProgramFactory(business_area=self.rdi.business_area)
        self.rdi.data_source = RegistrationDataImport.PROGRAM_POPULATION
        self.rdi.save()
        imported_household = HouseholdFactory(
            registration_data_import=self.rdi,
            unicef_id="HH-9",
            rdi_merge_status=MergeStatusModel.PENDING,
            program=self.rdi.program,
        )
        self.set_imported_individuals(imported_household)
        individual_without_collection = IndividualFactory(
            unicef_id="IND-9",
            business_area=self.rdi.business_area,
            program=program_2,
            household=None,
        )
        individual_without_collection.individual_collection = None
        individual_without_collection.save()

        individual_collection = IndividualCollectionFactory()
        IndividualFactory(
            unicef_id="IND-8",
            business_area=self.rdi.business_area,
            program=program_2,
            individual_collection=individual_collection,
            household=None,
        )
        household = None
        household_collection = None
        if household_representation_exists is not None:
            household = HouseholdFactory(
                head_of_household=individual_without_collection,
                business_area=self.rdi.business_area,
                program=program_2,
                unicef_id="HH-9",
            )
            household.household_collection = None
            household.save()
            if household_representation_exists:
                household_collection = HouseholdCollectionFactory()
                household.household_collection = household_collection
                household.save()

        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

        individual_without_collection.refresh_from_db()
        self.assertIsNotNone(individual_without_collection.individual_collection)
        self.assertEqual(
            individual_without_collection.individual_collection.individuals.count(),
            2,
        )
        self.assertEqual(
            individual_collection.individuals.count(),
            2,
        )
        if household_representation_exists is not None:
            if household_representation_exists:
                household_collection.refresh_from_db()
                self.assertEqual(household_collection.households.count(), 2)
            else:
                household.refresh_from_db()
                self.assertIsNotNone(household.household_collection)
                self.assertEqual(household.household_collection.households.count(), 2)

    def test_merging_external_collector(self) -> None:
        household = PendingHouseholdFactory(
            registration_data_import=self.rdi,
            admin4=self.area4,
            zip_code="00-123",
        )
        self.set_imported_individuals(household)
        external_collector = PendingIndividualFactory(
            full_name="External Collector",
            given_name="External",
            family_name="Collector",
            relationship=NON_BENEFICIARY,
            birth_date="1962-02-02",
            sex="OTHER",
            registration_data_import=self.rdi,
            email="xd@com",
        )
        role = PendingIndividualRoleInHousehold(individual=external_collector, household=household, role=ROLE_ALTERNATE)
        role.save()
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

    @patch.dict(
        "os.environ",
        {"DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key", "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com"},
    )
    @mock.patch(
        "hct_mis_api.apps.registration_datahub.services.biometric_deduplication.BiometricDeduplicationService.create_grievance_tickets_for_duplicates"
    )
    @mock.patch(
        "hct_mis_api.apps.registration_datahub.services.biometric_deduplication.BiometricDeduplicationService.update_rdis_deduplication_statistics"
    )
    def test_merge_biometric_deduplication_enabled(
        self,
        update_rdis_deduplication_statistics_mock: mock.Mock,
        create_grievance_tickets_for_duplicates_mock: mock.Mock,
    ) -> None:
        program = self.rdi.program
        program.biometric_deduplication_enabled = True
        program.save()
        household = PendingHouseholdFactory(
            registration_data_import=self.rdi,
            admin4=self.area4,
            zip_code="00-123",
        )
        self.set_imported_individuals(household)
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)
        create_grievance_tickets_for_duplicates_mock.assert_called_once_with(self.rdi)
        update_rdis_deduplication_statistics_mock.assert_called_once_with(program, exclude_rdi=self.rdi)

    def test_merge_empty_rdi(self) -> None:
        rdi = self.rdi
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(rdi.pk)
        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.MERGED)
