import datetime
from django.utils import timezone

from django.core.management import call_command
from django.test import TestCase

from freezegun import freeze_time

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    AUNT_UNCLE,
    BROTHER_SISTER,
    COUSIN,
    FEMALE,
    GRANDDAUGHER_GRANDSON,
    HEAD,
    MALE,
    NON_BENEFICIARY,
    Household,
    Individual,
)
from hct_mis_api.apps.household.services.household_recalculate_data import recalculate_data
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class TestRecalculateData(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()

        business_area = BusinessArea.objects.first()
        registration_data_import = RegistrationDataImportFactory(business_area=business_area)

        household_data = {
            "business_area": business_area,
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
            "collect_individual_data": "1",
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
            },
            {
                "registration_data_import": registration_data_import,
                # "age": 27,
                "relationship": GRANDDAUGHER_GRANDSON,
                "sex": FEMALE,
                "birth_date": datetime.datetime.strptime("1993-09-01", "%Y-%m-%d").date(),
                "pregnant": True,
                "first_registration_date": timezone.make_aware(datetime.datetime.strptime("2021-07-03", "%Y-%m-%d")),
                "selfcare_disability": "CANNOT_DO",
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
            },
        ]

        cls.household, cls.individuals = create_household_and_individuals(household_data, individuals_data)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_0_5_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_0_5_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_6_11_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_6_11_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_12_17_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_12_17_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_18_59_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_18_59_count, 2)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_60_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_60_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_0_5_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_0_5_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_6_11_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_6_11_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_12_17_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_12_17_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_18_59_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_18_59_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_60_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_60_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_0_5_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_0_5_disabled_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_6_11_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_6_11_disabled_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_12_17_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_12_17_disabled_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_18_59_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_18_59_disabled_count, 2)

    @freeze_time("2021-07-30")
    def test_recalculate_female_age_group_60_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.female_age_group_60_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_0_5_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_0_5_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_6_11_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_6_11_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_12_17_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_12_17_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_18_59_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_18_59_disabled_count, 0)

    @freeze_time("2021-07-30")
    def test_recalculate_male_age_group_60_disabled_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.male_age_group_60_disabled_count, 1)

    @freeze_time("2021-07-30")
    def test_recalculate_size(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.size, 6)

    @freeze_time("2021-07-30")
    def test_recalculate_pregnant_count(self):
        recalculate_data(self.household)
        household = Household.objects.get(pk=self.household.pk)
        self.assertEqual(household.pregnant_count, 2)
