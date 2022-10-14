from datetime import date

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_FULL,
    COLLECT_TYPE_NONE,
    COLLECT_TYPE_PARTIAL,
    HEAD,
    MALE,
)
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class TestOptionalRecalculationOfIndividuals(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.business_area = BusinessAreaFactory(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            slug="afghanistan",
            has_data_sharing_agreement=True,
        )
        cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)

    def create_hh(self, collect_individual_data):
        household, _ = create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "business_area": self.business_area,
                "collect_individual_data": collect_individual_data,
            },
            individuals_data=[
                {
                    "registration_data_import": self.registration_data_import,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": date.today(),
                },
            ],
        )
        return household

    def test_recalculating_data_when_flag_is_full(self):
        household = self.create_hh(COLLECT_TYPE_FULL)
        self.assertEqual(household.collect_individual_data, COLLECT_TYPE_FULL)
        household.female_age_group_0_5_count = 123
        household.save()
        recalculate_data(household)
        self.assertEqual(household.female_age_group_0_5_count, 0)

    def test_recalculating_data_when_flag_is_partial(self):
        household = self.create_hh(COLLECT_TYPE_PARTIAL)
        self.assertEqual(household.collect_individual_data, COLLECT_TYPE_PARTIAL)
        household.female_age_group_0_5_count = 123
        household.save()
        recalculate_data(household)
        self.assertEqual(household.female_age_group_0_5_count, None)

    def test_recalculating_data_when_flag_is_none(self):
        household = self.create_hh(COLLECT_TYPE_NONE)
        self.assertEqual(household.collect_individual_data, COLLECT_TYPE_NONE)
        household.female_age_group_0_5_count = 123
        household.save()
        recalculate_data(household)
        self.assertEqual(household.female_age_group_0_5_count, 123)
