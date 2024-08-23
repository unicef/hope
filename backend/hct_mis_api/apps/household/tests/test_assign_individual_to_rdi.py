from django.core.management import call_command
from django.test.testcases import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class TestIndividualRDIMigration(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("migrate", "household", "0184_migration", verbosity=0)

        cls.ba_afghanistan = create_afghanistan()
        cls.program_1 = ProgramFactory(name="program_1", business_area=cls.ba_afghanistan)
        cls.program_2 = ProgramFactory(name="program_2", business_area=cls.ba_afghanistan)
        create_household_and_individuals(
            household_data={
                "business_area": cls.ba_afghanistan,
                "program": cls.program_1,
            },
            individuals_data=[
                {
                    "business_area": cls.ba_afghanistan,
                    "program": cls.program_1,
                },
            ],
        )
        create_household_and_individuals(
            household_data={
                "business_area": cls.ba_afghanistan,
                "program": cls.program_2,
            },
            individuals_data=[
                {
                    "business_area": cls.ba_afghanistan,
                    "program": cls.program_2,
                },
            ],
        )
        Household.objects.all().update(registration_data_import=None)
        Individual.objects.all().update(registration_data_import=None)

    def test_assign_individual_to_rdi_migration(self) -> None:
        # add individual assigned to RDI
        program_3 = ProgramFactory(name="Program 333", business_area=self.ba_afghanistan)
        create_household_and_individuals(
            household_data={
                "business_area": self.ba_afghanistan,
                "program": program_3,
            },
            individuals_data=[
                {
                    "business_area": self.ba_afghanistan,
                    "program": program_3,
                },
                {
                    "business_area": self.ba_afghanistan,
                    "program": program_3,
                },
            ],
        )
        self.assertEqual(RegistrationDataImport.objects.count(), 3)
        self.assertEqual(Program.objects.count(), 3)
        self.assertEqual(Individual.objects.count(), 4)
        self.assertEqual(Household.objects.count(), 3)
        self.assertEqual(Individual.objects.filter(program=self.program_1).count(), 1)
        self.assertEqual(Individual.objects.filter(program=self.program_2).count(), 1)
        self.assertEqual(Individual.objects.filter(registration_data_import__isnull=True).count(), 2)
        self.assertEqual(Household.objects.filter(registration_data_import__isnull=True).count(), 2)

        call_command("migrate", "household", "0185_migration", verbosity=0)

        # 3 old rdi and + 2 new created
        self.assertEqual(RegistrationDataImport.objects.count(), 5)
        # check new RDIs
        self.assertEqual(
            RegistrationDataImport.objects.filter(
                name__startwith="RDI for Individuals [data migration for Programme"
            ).count(),
            5,
        )
        self.assertEqual(Individual.objects.filter(registration_data_import__isnull=False).count(), 4)
        self.assertEqual(Household.objects.filter(registration_data_import__isnull=True).count(), 3)

        rdi_1 = RegistrationDataImport.objects.get(
            name=f"RDI for Individuals [data migration for Programme: {self.program_1.name}]"
        )
        self.assertEqual(rdi_1.status, "MERGED")
        self.assertEqual(rdi_1.number_of_individuals, 1)
        self.assertEqual(rdi_1.number_of_households, 1)

        rdi_2 = RegistrationDataImport.objects.get(
            name=f"RDI for Individuals [data migration for Programme: {self.program_2.name}]"
        )
        self.assertEqual(rdi_2.status, "MERGED")
        self.assertEqual(rdi_2.number_of_individuals, 1)
        self.assertEqual(rdi_2.number_of_households, 1)
