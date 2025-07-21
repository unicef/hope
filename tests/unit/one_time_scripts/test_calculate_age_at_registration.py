from django.test.testcases import TestCase

from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import IndividualFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.one_time_scripts.calculate_age_at_registration import (
    calculate_age_at_registration_field,
)


class TestCalculatingAgeAtRegistrationMigration(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()

        cls.registration_1 = RegistrationDataImportFactory(created_at="2019-01-12 16:15:31.864423+00:00")
        cls.registration_2 = RegistrationDataImportFactory(created_at="2021-04-12 17:25:32.112983+00:00")

        cls.individual_1 = IndividualFactory(
            household=None, birth_date="2007-12-12", registration_data_import=cls.registration_1
        )
        cls.individual_2 = IndividualFactory(
            household=None, birth_date="2000-01-01", registration_data_import=cls.registration_1
        )
        cls.individual_3 = IndividualFactory(
            household=None, birth_date="2010-11-11", registration_data_import=cls.registration_1
        )
        cls.individual_4 = IndividualFactory(
            household=None, birth_date="1991-05-05", registration_data_import=cls.registration_2
        )
        cls.individual_5 = IndividualFactory(
            household=None, birth_date="2012-12-24", registration_data_import=cls.registration_2
        )
        cls.individual_6 = IndividualFactory(
            household=None, birth_date="1988-10-26", registration_data_import=cls.registration_2
        )

    def test_calculating_age_at_registration(self) -> None:
        calculate_age_at_registration_field()

        self.individual_1.refresh_from_db()
        self.individual_2.refresh_from_db()
        self.individual_3.refresh_from_db()
        self.individual_4.refresh_from_db()
        self.individual_5.refresh_from_db()
        self.individual_6.refresh_from_db()

        self.assertEqual(self.individual_1.age_at_registration, 11)
        self.assertEqual(self.individual_2.age_at_registration, 19)
        self.assertEqual(self.individual_3.age_at_registration, 8)
        self.assertEqual(self.individual_4.age_at_registration, 29)
        self.assertEqual(self.individual_5.age_at_registration, 8)
        self.assertEqual(self.individual_6.age_at_registration, 32)
