from django.db import models
from django.db.models import Count
from django.db.models.functions import Extract

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Individual, Household, REFUGEE, DISABILITY_CHOICES, DISABLED, NOT_DISABLED


class Age(models.Func):
    function = "AGE"


def get_households_at_least_3():
    individuals = (
        Individual.objects.annotate(new_age=Extract(Age("first_registration_date", "birth_date"), "year"))
        .filter(new_age__lt=18, withdrawn=False)
        .values("household_id")
        .annotate(count_household=Count("id"))
        .filter(count_household__gte=3)
        .distinct()
    )
    return Household.objects.filter(id__in=individuals.values("household_id"), payment_records__isnull=True).distinct()


def get_households_disabled():
    individuals = (
        Individual.objects.annotate(new_age=Extract(Age("first_registration_date", "birth_date"), "year"))
        .filter(new_age__lt=18, disability=DISABLED, withdrawn=False)
        .distinct()
    )
    return Household.objects.filter(id__in=individuals.values("household_id"), payment_records__isnull=True).distinct()


class TestOptionalRecalculationOfIndividuals(APITestCase):
    def test_get_households_3(self):
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        create_household_and_individuals(
            {"business_area": business_area},
            individuals_data=[
                {"birth_date": "2004-11-07", "first_registration_date": "2022-05-07"},
                {"birth_date": "2004-11-08", "first_registration_date": "2022-05-07"},
                {"birth_date": "2004-11-18", "first_registration_date": "2022-05-07"},
            ],
        )
        households = get_households_at_least_3()
        self.assertEqual(households.count(), 1)

    def test_get_zero_households_3(self):
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        create_household_and_individuals(
            {"business_area": business_area},
            individuals_data=[
                {"birth_date": "2004-05-06", "first_registration_date": "2022-05-07"},
                {"birth_date": "2004-11-08", "first_registration_date": "2022-05-07"},
                {"birth_date": "2004-11-18", "first_registration_date": "2022-05-07"},
            ],
        )
        households = get_households_at_least_3()
        self.assertEqual(households.count(), 0)

    def test_get_households_disability(self):
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        create_household_and_individuals(
            {"business_area": business_area},
            individuals_data=[
                {"birth_date": "2004-11-07", "first_registration_date": "2022-05-07", "disability": NOT_DISABLED},
                {"birth_date": "2004-11-08", "first_registration_date": "2022-05-07", "disability": DISABLED},
                {"birth_date": "2004-11-18", "first_registration_date": "2022-05-07", "disability": NOT_DISABLED},
            ],
        )
        create_household_and_individuals(
            {"business_area": business_area},
            individuals_data=[
                {"birth_date": "2004-11-07", "first_registration_date": "2022-05-07", "disability": NOT_DISABLED},
                {"birth_date": "2004-11-08", "first_registration_date": "2022-05-07", "disability": NOT_DISABLED},
                {"birth_date": "2004-11-18", "first_registration_date": "2022-05-07", "disability": NOT_DISABLED},
            ],
        )
        households = get_households_disabled()
        self.assertEqual(households.count(), 1)
