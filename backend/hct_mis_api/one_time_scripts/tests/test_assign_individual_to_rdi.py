from django.test.testcases import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.one_time_scripts.assign_individual_to_rdi import (
    assign_individual_to_rdi,
)


class TestProgramCycleDataMigration(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        ba_afghanistan = create_afghanistan()
        cls.program_1 = ProgramFactory(name="program_1", business_area=ba_afghanistan)
        cls.program_2 = ProgramFactory(name="program_2", business_area=ba_afghanistan)
        create_household_and_individuals(
            household_data={
                "business_area": ba_afghanistan,
                "program": cls.program_1,
            },
            individuals_data=[
                {
                    "business_area": ba_afghanistan,
                    "program": cls.program_1,
                },
            ],
        )
        create_household_and_individuals(
            household_data={
                "business_area": ba_afghanistan,
                "program": cls.program_2,
            },
            individuals_data=[
                {
                    "business_area": ba_afghanistan,
                    "program": cls.program_2,
                },
            ],
        )

    def test_assign_individual_to_rdi_migration(self) -> None:
        self.assertEqual(RegistrationDataImport.objects.count(), 0)
        self.assertEqual(Individual.objects.filter(program=self.program_1).count(), 1)
        self.assertEqual(Individual.objects.filter(registration_data_import__isnull=True).count(), 2)

        # run script
        assign_individual_to_rdi()

        self.assertEqual(RegistrationDataImport.objects.count(), 2)
        self.assertEqual(Individual.objects.filter(registration_data_import__isnull=False).count(), 2)
        rdi = RegistrationDataImport.objects.fitst()
        self.assertEqual(rdi.name, "RDI for Individuals [data migration]")
        self.assertEqual(rdi.status, "MERGED")
        self.assertEqual(rdi.number_of_individuals, 2)
        self.assertEqual(rdi.number_of_households, 2)
