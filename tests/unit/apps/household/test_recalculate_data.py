import datetime
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.celery_tasks import recalculate_population_fields_task
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    AUNT_UNCLE,
    BROTHER_SISTER,
    COUSIN,
    FEMALE,
    GRANDDAUGHTER_GRANDSON,
    HEAD,
    MALE,
    NON_BENEFICIARY,
    Household,
)
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class TestRecalculateData(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.program = ProgramFactory()
        data_collecting_type = cls.program.data_collecting_type
        data_collecting_type.recalculate_composition = True
        data_collecting_type.save()
        business_area = BusinessArea.objects.first()
        registration_data_import = RegistrationDataImportFactory(business_area=business_area)

        cls.household_data = {
            "business_area": business_area,
            "program": cls.program,
            "registration_data_import": registration_data_import,
            "female_age_group_0_5_count": 2,
            "female_age_group_6_11_count": 1,
            "female_age_group_12_17_count": 0,
            "female_age_group_18_59_count": 2,
            "female_age_group_60_count": 0,
            "male_age_group_0_5_count": 0,
            "male_age_group_6_11_count": 0,
            "male_age_group_12_17_count": 0,
            "male_age_group_18_59_count": 1,
            "male_age_group_60_count": 0,
            "female_age_group_0_5_disabled_count": 2,
            "female_age_group_6_11_disabled_count": 1,
            "female_age_group_12_17_disabled_count": 0,
            "female_age_group_18_59_disabled_count": 2,
            "female_age_group_60_disabled_count": 0,
            "male_age_group_0_5_disabled_count": 0,
            "male_age_group_6_11_disabled_count": 0,
            "male_age_group_12_17_disabled_count": 0,
            "male_age_group_18_59_disabled_count": 1,
            "male_age_group_60_disabled_count": 0,
            "size": 6,
            "pregnant_count": 2,
            "fchild_hoh": True,
            "child_hoh": False,
        }

        individuals_data = [
            {
                "registration_data_import": registration_data_import,
                # "age": 39,
                "relationship": COUSIN,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("1981-08-08", "%Y-%m-%d").date(),
                "pregnant": True,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2020-10-29", "%Y-%m-%d")),
                "physical_disability": "LOT_DIFFICULTY",
                "program": cls.program,
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 27,
                "relationship": GRANDDAUGHTER_GRANDSON,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("1993-09-01", "%Y-%m-%d").date(),
                "pregnant": True,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-07-03", "%Y-%m-%d")),
                "selfcare_disability": "CANNOT_DO",
                "program": cls.program,
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 0,
                "relationship": HEAD,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("2021-06-29", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
                "memory_disability": "LOT_DIFFICULTY",
                "program": cls.program,
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 5,
                "relationship": BROTHER_SISTER,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("2015-07-29", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
                "seeing_disability": "LOT_DIFFICULTY",
                "hearing_disability": "LOT_DIFFICULTY",
                "physical_disability": "LOT_DIFFICULTY",
                "memory_disability": "LOT_DIFFICULTY",
                "selfcare_disability": "LOT_DIFFICULTY",
                "comms_disability": "LOT_DIFFICULTY",
                "program": cls.program,
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 11,
                "relationship": AUNT_UNCLE,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("2009-07-29", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
                "hearing_disability": "CANNOT_DO",
                "program": cls.program,
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 5,
                "relationship": NON_BENEFICIARY,
                "sex": MALE,
                "birth_date": datetime.datetime.strptime("2015-07-29", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
                "hearing_disability": "CANNOT_DO",
                "program": cls.program,
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 59,
                "relationship": COUSIN,
                "sex": MALE,
                "birth_date": datetime.datetime.strptime("1961-07-29", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2020-10-29", "%Y-%m-%d")),
                "memory_disability": "LOT_DIFFICULTY",
                "comms_disability": "LOT_DIFFICULTY",
                "program": cls.program,
            },
        ]

        cls.household, cls.individuals = create_household_and_individuals(cls.household_data, individuals_data)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_0_5_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_0_5_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_6_11_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_6_11_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_12_17_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_12_17_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_18_59_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_18_59_count, 2)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_60_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_60_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_0_5_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_0_5_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_6_11_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_6_11_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_12_17_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_12_17_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_18_59_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_18_59_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_60_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_60_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_0_5_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_0_5_disabled_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_6_11_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_6_11_disabled_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_12_17_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_12_17_disabled_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_18_59_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_18_59_disabled_count, 2)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_60_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_60_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_0_5_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_0_5_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_6_11_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_6_11_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_12_17_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_12_17_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_18_59_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_18_59_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_60_disabled_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_60_disabled_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_size(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.size, 6)

    @freeze_time("2021-07-30")
    def test_recalculate_pregnant_count(self) -> None:
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.pregnant_count, 2)

    @patch("hct_mis_api.apps.household.celery_tasks.recalculate_population_fields_task.delay")
    @freeze_time("2021-07-30")
    def test_interval_recalculate_population_fields_task(
        self, recalculate_population_fields_task_mock: MagicMock
    ) -> None:
        from hct_mis_api.apps.household.celery_tasks import (
            interval_recalculate_population_fields_task,
        )

        interval_recalculate_population_fields_task.delay()
        recalculate_population_fields_task_mock.assert_called_once_with(household_ids=[self.household.pk])

    def test_recalculation_for_last_registration_date(self) -> None:
        registration_data_import = RegistrationDataImportFactory(business_area=BusinessArea.objects.first())
        individuals_data = [
            {
                "registration_data_import": registration_data_import,
                # "age": 42,
                "relationship": COUSIN,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("1981-01-01", "%Y-%m-%d").date(),
                "pregnant": True,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2020-10-29", "%Y-%m-%d")),
                "physical_disability": "LOT_DIFFICULTY",
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 30,
                "relationship": GRANDDAUGHTER_GRANDSON,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("1993-01-01", "%Y-%m-%d").date(),
                "pregnant": True,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-07-03", "%Y-%m-%d")),
                "selfcare_disability": "CANNOT_DO",
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 1,
                "relationship": HEAD,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("2022-01-01", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
                "memory_disability": "LOT_DIFFICULTY",
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 23,
                "relationship": BROTHER_SISTER,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
                "seeing_disability": "LOT_DIFFICULTY",
                "hearing_disability": "LOT_DIFFICULTY",
                "physical_disability": "LOT_DIFFICULTY",
                "memory_disability": "LOT_DIFFICULTY",
                "selfcare_disability": "LOT_DIFFICULTY",
                "comms_disability": "LOT_DIFFICULTY",
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 14,
                "relationship": AUNT_UNCLE,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("2009-01-01", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-01-01", "%Y-%m-%d")),
                "hearing_disability": "CANNOT_DO",
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 3,
                "relationship": NON_BENEFICIARY,
                "sex": MALE,
                "birth_date": datetime.datetime.strptime("2020-01-01", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
                "hearing_disability": "CANNOT_DO",
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 68,
                "relationship": COUSIN,
                "sex": MALE,
                "birth_date": datetime.datetime.strptime("1955-01-01", "%Y-%m-%d").date(),
                "pregnant": False,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2020-10-29", "%Y-%m-%d")),
                "memory_disability": "LOT_DIFFICULTY",
                "comms_disability": "LOT_DIFFICULTY",
            },
        ]

        household, individuals = create_household_and_individuals(self.household_data, individuals_data)
        household.last_registration_date = timezone.make_aware(datetime.datetime.strptime("2023-01-02", "%Y-%m-%d"))
        household.save()

        household, _ = recalculate_data(household=household, save=True)

        self.assertEqual(household.size, 6)
        self.assertEqual(household.female_age_group_0_5_count, 1)
        self.assertEqual(household.male_age_group_0_5_count, 0)  # NON_BENEFICIARY
        self.assertEqual(household.female_age_group_12_17_count, 1)
        self.assertEqual(household.female_age_group_18_59_count, 3)
        self.assertEqual(household.male_age_group_60_count, 1)
        self.assertEqual(household.pregnant_count, 2)
        self.assertEqual(household.female_age_group_0_5_disabled_count, 1)
        self.assertEqual(household.female_age_group_12_17_disabled_count, 1)
        self.assertEqual(household.female_age_group_18_59_disabled_count, 3)
        self.assertEqual(household.children_count, 2)
        self.assertEqual(household.female_children_count, 2)
        self.assertEqual(household.children_disabled_count, 2)
        self.assertEqual(household.female_children_disabled_count, 2)

    @freeze_time("2021-07-30")
    def test_recalculate_population_fields_task(self) -> None:
        recalculate_population_fields_task(household_ids=[self.household.pk])
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.size, 6)
