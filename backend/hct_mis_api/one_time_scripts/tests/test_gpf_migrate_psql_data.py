import logging

from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import (
    HouseholdSelectionFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.one_time_scripts.gpf_migrate_psql_data import migrate_program_psql_db


class TestGPFMigrationToPSQL(TestCase):
    databases = {"default"}

    logging.disable(logging.INFO)
    logging.disable(logging.ERROR)

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.first()

        cls.program_finished = ProgramFactory(status=Program.FINISHED, name="program_finished")
        cls.program_active = ProgramFactory(status=Program.ACTIVE, name="program_active")

        cls.target_population_valid = TargetPopulationFactory(
            status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE, program=cls.program_active
        )
        cls.target_population_invalid_1 = TargetPopulationFactory(
            status=TargetPopulation.STATUS_LOCKED, program=cls.program_active
        )
        cls.target_population_invalid_2 = TargetPopulationFactory(
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST, program=cls.program_finished
        )

        cls.household_1, cls.individuals_1 = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )

        cls.household_2, cls.individuals_2 = create_household(
            household_args={"size": 2, "business_area": cls.business_area}
        )

        cls.household_3, cls.individuals_3 = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )

        cls.household_4, cls.individuals_4 = create_household(
            household_args={"size": 2, "business_area": cls.business_area}
        )

        cls.household_5, cls.individuals_5 = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )

    def test_migrate_program_psql_db(self) -> None:
        HouseholdSelectionFactory(household=self.household_1, target_population=self.target_population_valid)
        HouseholdSelectionFactory(household=self.household_2, target_population=self.target_population_valid)
        HouseholdSelectionFactory(household=self.household_3, target_population=self.target_population_invalid_1)
        HouseholdSelectionFactory(household=self.household_4, target_population=self.target_population_invalid_2)
        HouseholdSelectionFactory(household=self.household_5, target_population=self.target_population_valid)

        migrate_program_psql_db()

        self.household_1.refresh_from_db()
        self.household_2.refresh_from_db()
        self.household_3.refresh_from_db()
        self.household_4.refresh_from_db()
        self.household_5.refresh_from_db()

        self.individuals_1[0].refresh_from_db()
        self.individuals_2[0].refresh_from_db()
        self.individuals_2[1].refresh_from_db()
        self.individuals_3[0].refresh_from_db()
        self.individuals_4[0].refresh_from_db()
        self.individuals_4[1].refresh_from_db()
        self.individuals_5[0].refresh_from_db()

        self.assertEqual(self.household_1.program_id, self.program_active.id)
        self.assertEqual(self.household_2.program_id, self.program_active.id)
        self.assertEqual(self.household_5.program_id, self.program_active.id)

        self.assertEqual(self.individuals_1[0].program_id, self.program_active.id)
        self.assertEqual(self.individuals_2[0].program_id, self.program_active.id)
        self.assertEqual(self.individuals_2[1].program_id, self.program_active.id)
        self.assertEqual(self.individuals_5[0].program_id, self.program_active.id)

        self.assertIsNone(self.household_3.program_id)
        self.assertIsNone(self.household_4.program_id)

        self.assertIsNone(self.individuals_3[0].program_id)
        self.assertIsNone(self.individuals_4[0].program_id)
        self.assertIsNone(self.individuals_4[1].program_id)
