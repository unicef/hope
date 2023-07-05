from django.test import TestCase, override_settings

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    FOSTER_CHILD,
    RELATIONSHIP_OTHER,
    SON_DAUGHTER,
    WIFE_HUSBAND,
)
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.one_time_scripts.assign_foster_child import migrate_foster_child


@override_settings(USE_TZ=False)
class TestMigrationFosterChild(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()

        cls.registration_1 = RegistrationDataImportFactory(created_at="2023-06-03 09:22:14.870000+00:00")
        cls.registration_2 = RegistrationDataImportFactory(created_at="2023-06-05 19:22:14.890000+00:00")
        cls.registration_3 = RegistrationDataImportFactory(created_at="2023-06-11 06:26:15.870000+00:00")
        cls.registration_4 = RegistrationDataImportFactory(created_at="2023-05-31 12:52:11.970000+00:00")
        cls.registration_5 = RegistrationDataImportFactory(created_at="2023-06-10 06:26:16.870000+00:00")
        cls.registration_6 = RegistrationDataImportFactory(created_at="2023-04-10 06:26:16.870000+00:00")

        cls.individual_1 = IndividualFactory(household=None, relationship=SON_DAUGHTER, birth_date="2007-12-12")
        cls.individual_2 = IndividualFactory(household=None, relationship=WIFE_HUSBAND, birth_date="2000-01-01")
        cls.individual_3 = IndividualFactory(household=None, relationship=RELATIONSHIP_OTHER, birth_date="2010-11-11")
        cls.individual_4 = IndividualFactory(household=None, relationship=RELATIONSHIP_OTHER, birth_date="1991-05-05")
        cls.individual_5 = IndividualFactory(household=None, relationship=RELATIONSHIP_OTHER, birth_date="2012-12-24")
        cls.individual_6 = IndividualFactory(household=None, relationship=RELATIONSHIP_OTHER, birth_date="2015-10-26")

        cls.household_1 = HouseholdFactory(
            registration_data_import=cls.registration_1, head_of_household=cls.individual_1
        )
        cls.household_2 = HouseholdFactory(
            registration_data_import=cls.registration_2, head_of_household=cls.individual_2
        )
        cls.household_3 = HouseholdFactory(
            registration_data_import=cls.registration_3, head_of_household=cls.individual_3
        )
        cls.household_4 = HouseholdFactory(
            registration_data_import=cls.registration_4, head_of_household=cls.individual_4
        )
        cls.household_5 = HouseholdFactory(
            registration_data_import=cls.registration_5, head_of_household=cls.individual_5
        )
        cls.household_6 = HouseholdFactory(
            registration_data_import=cls.registration_6, head_of_household=cls.individual_6
        )

        cls.individual_1.household = cls.household_1
        cls.individual_2.household = cls.household_2
        cls.individual_3.household = cls.household_3
        cls.individual_4.household = cls.household_4
        cls.individual_5.household = cls.household_5
        cls.individual_6.household = cls.household_6

        cls.individual_1.save()
        cls.individual_2.save()
        cls.individual_3.save()
        cls.individual_4.save()
        cls.individual_5.save()
        cls.individual_6.save()

    def test_foster_child_migration(self) -> None:
        migrate_foster_child()

        self.individual_1.refresh_from_db()
        self.individual_2.refresh_from_db()
        self.individual_3.refresh_from_db()
        self.individual_4.refresh_from_db()
        self.individual_5.refresh_from_db()
        self.individual_6.refresh_from_db()

        self.assertEqual(self.individual_1.relationship, SON_DAUGHTER)
        self.assertEqual(self.individual_2.relationship, WIFE_HUSBAND)
        self.assertEqual(self.individual_3.relationship, FOSTER_CHILD)
        self.assertEqual(self.individual_4.relationship, RELATIONSHIP_OTHER)
        self.assertEqual(self.individual_5.relationship, FOSTER_CHILD)
        self.assertEqual(self.individual_6.relationship, RELATIONSHIP_OTHER)
