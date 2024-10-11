from contextlib import contextmanager
from typing import Callable, Generator
from unittest import mock
from unittest.mock import patch

from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, connections
from django.forms import model_to_dict
from django.test import TestCase

import pytest
from freezegun import freeze_time
from parameterized import parameterized

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketIndividualDataUpdateDetails,
)
from hct_mis_api.apps.household.fixtures import (
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
)
from hct_mis_api.apps.household.models import (
    BROTHER_SISTER,
    COLLECT_TYPE_FULL,
    COLLECT_TYPE_PARTIAL,
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
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismDataFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism, DeliveryMechanismData
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
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


class TestRdiMergeTask(TestCase):
    fixtures = [
        f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",
        f"{settings.PROJECT_ROOT}/apps/core/fixtures/data.json",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        program = ProgramFactory()
        cls.rdi = RegistrationDataImportFactory(program=program)
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
        household = PendingHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi,
            admin_area=self.area4,
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

        self.set_imported_individuals(household)
        household.head_of_household = PendingIndividual.objects.first()
        household.save()

        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

        households = Household.objects.all()
        individuals = Individual.objects.all()

        household = households.first()

        self.assertEqual(1, households.count())
        self.assertEqual(household.collect_individual_data, COLLECT_TYPE_FULL)
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

        household_data = model_to_dict(
            household,
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
                "admin_area",
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
            "admin_area": self.area4.id,
            "admin1": self.area1.id,
            "admin2": self.area2.id,
            "admin3": self.area3.id,
            "admin4": self.area4.id,
            "zip_code": "00-123",
        }
        self.assertEqual(household_data, expected)

    @freeze_time("2022-01-01")
    @patch(
        "hct_mis_api.apps.grievance.tasks.deduplicate_and_check_sanctions.CheckAgainstSanctionListPreMergeTask.execute"
    )
    def test_merge_rdi_sanction_list_check(self, sanction_execute_mock: mock.MagicMock) -> None:
        household = PendingHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi,
            admin_area=self.area4,
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
        self.business_area.screen_beneficiary = True
        self.business_area.save()
        self.rdi.screen_beneficiary = True
        self.rdi.save()
        self.set_imported_individuals(household)
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)
        sanction_execute_mock.assert_called_once()
        sanction_execute_mock.reset_mock()

    @freeze_time("2022-01-01")
    @patch(
        "hct_mis_api.apps.grievance.tasks.deduplicate_and_check_sanctions.CheckAgainstSanctionListPreMergeTask.execute"
    )
    def test_merge_rdi_sanction_list_check_business_area_false(self, sanction_execute_mock: mock.MagicMock) -> None:
        household = PendingHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi,
            admin_area=self.area4,
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

        # when business_area.screen_beneficiary is False
        self.business_area.screen_beneficiary = False
        self.business_area.save()
        self.rdi.screen_beneficiary = True
        self.rdi.save()
        self.set_imported_individuals(household)
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)
        sanction_execute_mock.assert_not_called()

    @freeze_time("2022-01-01")
    @patch(
        "hct_mis_api.apps.grievance.tasks.deduplicate_and_check_sanctions.CheckAgainstSanctionListPreMergeTask.execute"
    )
    def test_merge_rdi_sanction_list_check_rdi_false(self, sanction_execute_mock: mock.MagicMock) -> None:
        household = PendingHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi,
            admin_area=self.area4,
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

        # when rdi.screen_beneficiary is False
        self.business_area.screen_beneficiary = True
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
        self.rdi.data_source = RegistrationDataImport.PROGRAM_POPULATION
        self.rdi.save()
        imported_household = HouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi,
            unicef_id="HH-9",
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        self.set_imported_individuals(imported_household)
        individual_without_collection = IndividualFactory(
            unicef_id="IND-9",
            business_area=self.rdi.business_area,
            household=None,
        )
        individual_without_collection.individual_collection = None
        individual_without_collection.save()

        individual_collection = IndividualCollectionFactory()
        IndividualFactory(
            unicef_id="IND-8",
            business_area=self.rdi.business_area,
            individual_collection=individual_collection,
            household=None,
        )
        household = None
        household_collection = None
        if household_representation_exists is not None:
            household = HouseholdFactory(
                head_of_household=individual_without_collection,
                business_area=self.rdi.business_area,
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

    @freeze_time("2022-01-01")
    def test_merge_rdi_and_recalculation_for_collect_data_partial(self) -> None:
        household = PendingHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_PARTIAL,
            registration_data_import=self.rdi,
        )
        dct = self.rdi.program.data_collecting_type
        dct.recalculate_composition = True
        dct.save()

        self.set_imported_individuals(household)

        household.head_of_household = PendingIndividual.objects.first()
        household.save()

        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

        households = Household.objects.all()
        individuals = Individual.objects.all()

        self.assertEqual(1, households.count())
        self.assertEqual(households[0].collect_individual_data, COLLECT_TYPE_PARTIAL)
        self.assertEqual(8, individuals.count())

        household_data = model_to_dict(
            households[0],
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
            ),
        )

        expected = {
            "female_age_group_0_5_count": None,
            "female_age_group_6_11_count": None,
            "female_age_group_12_17_count": None,
            "female_age_group_18_59_count": None,
            "female_age_group_60_count": None,
            "male_age_group_0_5_count": None,
            "male_age_group_6_11_count": None,
            "male_age_group_12_17_count": None,
            "male_age_group_18_59_count": None,
            "male_age_group_60_count": None,
            "children_count": None,
            "size": None,
        }
        self.assertEqual(household_data, expected)

    def test_merging_external_collector(self) -> None:
        household = PendingHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi,
            admin_area=self.area4,
            admin4=self.area4,
            zip_code="00-123",
        )
        self.set_imported_individuals(household)
        external_collector = PendingIndividualFactory(
            **{
                "full_name": "External Collector",
                "given_name": "External",
                "family_name": "Collector",
                "relationship": NON_BENEFICIARY,
                "birth_date": "1962-02-02",  # age 39
                "sex": "MALE",
                "registration_data_import": self.rdi,
                "email": "xd@com",
            }
        )
        role = PendingIndividualRoleInHousehold(individual=external_collector, household=household, role=ROLE_ALTERNATE)
        role.save()
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)


class TestRdiMergeTaskDeliveryMechanismData(TestCase):
    fixtures = [
        f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",
        f"{settings.PROJECT_ROOT}/apps/core/fixtures/data.json",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.program = ProgramFactory()
        cls.rdi = RegistrationDataImportFactory(program=cls.program)
        generate_delivery_mechanisms()

    def test_create_grievance_tickets_for_delivery_mechanisms_errors(self) -> None:
        program = ProgramFactory()
        ind = IndividualFactory(household=None, program=program)
        ind2 = IndividualFactory(household=None, program=program)
        ind3 = IndividualFactory(household=None, program=program)
        hh = HouseholdFactory(head_of_household=ind)
        ind.household = hh
        ind.save()
        ind2.household = hh
        ind2.save()
        ind3.household = hh
        ind3.full_name = ind.full_name
        ind3.save()

        dm_atm_card = DeliveryMechanism.objects.get(code="atm_card")

        # valid data
        dmd = DeliveryMechanismDataFactory(
            individual=ind,
            delivery_mechanism=dm_atm_card,
            data={
                "card_number__atm_card": "123",
                "card_expiry_date__atm_card": "2022-01-01",
                "name_of_cardholder__atm_card": "Marek",
            },
        )
        # invalid data, ticket should be created
        dmd2 = DeliveryMechanismDataFactory(
            individual=ind2,
            delivery_mechanism=dm_atm_card,
            data={
                "card_number__atm_card": "123",
                "card_expiry_date__atm_card": None,
                "name_of_cardholder__atm_card": "Marek",
            },
        )
        # not unique data, ticket should be created
        dmd3 = DeliveryMechanismDataFactory(
            individual=ind3,
            delivery_mechanism=dm_atm_card,
            data={
                "card_number__atm_card": "123",
                "card_expiry_date__atm_card": "2022-01-01",
                "name_of_cardholder__atm_card": "Marek",
            },
        )

        self.assertEqual(0, self.rdi.grievanceticket_set.count())
        RdiMergeTask()._create_grievance_tickets_for_delivery_mechanisms_errors(
            DeliveryMechanismData.objects.all(), self.rdi
        )
        self.assertEqual(2, self.rdi.grievanceticket_set.count())
        self.assertEqual(2, TicketIndividualDataUpdateDetails.objects.count())

        data_not_valid_ticket = TicketIndividualDataUpdateDetails.objects.get(
            individual=ind2,
        )

        self.assertEqual(
            data_not_valid_ticket.individual_data,
            {
                "delivery_mechanism_data_to_edit": [
                    {
                        "approve_status": False,
                        "data_fields": [{"name": "card_expiry_date__atm_card", "previous_value": None, "value": None}],
                        "id": str(dmd2.id),
                        "label": "ATM Card",
                    }
                ]
            },
        )
        self.assertEqual(data_not_valid_ticket.ticket.comments, f"This is a system generated ticket for RDI {self.rdi}")
        self.assertEqual(
            data_not_valid_ticket.ticket.description,
            f"Missing required fields ['card_expiry_date__atm_card'] values for delivery mechanism {dmd2.delivery_mechanism}",
        )
        self.assertEqual(
            data_not_valid_ticket.ticket.issue_type, GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE
        )
        self.assertEqual(data_not_valid_ticket.ticket.category, GrievanceTicket.CATEGORY_DATA_CHANGE)
        self.assertEqual(data_not_valid_ticket.ticket.registration_data_import, self.rdi)

        data_not_unique_ticket = TicketIndividualDataUpdateDetails.objects.get(
            individual=ind3,
        )
        self.assertEqual(
            data_not_unique_ticket.individual_data,
            {
                "delivery_mechanism_data_to_edit": [
                    {
                        "approve_status": False,
                        "data_fields": [
                            {"name": "card_number__atm_card", "previous_value": "123", "value": None},
                            {"name": "card_expiry_date__atm_card", "previous_value": "2022-01-01", "value": None},
                            {"name": "name_of_cardholder__atm_card", "previous_value": "Marek", "value": None},
                        ],
                        "id": str(dmd3.id),
                        "label": "ATM Card",
                    }
                ],
            },
        )
        self.assertEqual(
            data_not_unique_ticket.ticket.comments, f"This is a system generated ticket for RDI {self.rdi}"
        )
        self.assertEqual(
            data_not_unique_ticket.ticket.description,
            f"Fields not unique ['card_number__atm_card', 'card_expiry_date__atm_card', 'name_of_cardholder__atm_card'] across program"
            f" for delivery mechanism {dmd3.delivery_mechanism}, possible duplicate of {dmd}",
        )
        self.assertEqual(
            data_not_unique_ticket.ticket.issue_type, GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE
        )
        self.assertEqual(data_not_unique_ticket.ticket.category, GrievanceTicket.CATEGORY_DATA_CHANGE)
        self.assertEqual(data_not_unique_ticket.ticket.registration_data_import, self.rdi)
