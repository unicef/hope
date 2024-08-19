from django.core.management import call_command
from django.test.testcases import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Individual, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class TestIndividualRDIMigration(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        call_command("migrate", "household", "0184_migration", verbosity=0)

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
        # TODO: add maybe program 3 and Ind there with RDI inside
        Household.objects.all().update(registration_data_import=None)
        Individual.objects.all().update(registration_data_import=None)
        RegistrationDataImport.objects.all().delete()

    def test_assign_individual_to_rdi_migration(self) -> None:
        self.assertEqual(RegistrationDataImport.objects.count(), 0)
        self.assertEqual(Individual.objects.count(), 2)
        self.assertEqual(Household.objects.count(), 2)
        self.assertEqual(Individual.objects.filter(program=self.program_1).count(), 1)
        self.assertEqual(Individual.objects.filter(registration_data_import__isnull=True).count(), 2)
        self.assertEqual(Household.objects.filter(registration_data_import__isnull=True).count(), 2)

        call_command("migrate", "household", "0185_migration", verbosity=0)

        self.assertEqual(RegistrationDataImport.objects.count(), 2)
        self.assertEqual(Individual.objects.filter(registration_data_import__isnull=False).count(), 2)
        self.assertEqual(Household.objects.filter(registration_data_import__isnull=True).count(), 2)
        rdi = RegistrationDataImport.objects.first()
        self.assertEqual(rdi.name, f"RDI for Individuals [data migration for Programme: {rdi.program.name}]")
        self.assertEqual(rdi.status, "MERGED")
        self.assertEqual(rdi.number_of_individuals, 1)
        self.assertEqual(rdi.number_of_households, 1)

        rdi_2 = RegistrationDataImport.objects.last()
        self.assertEqual(rdi_2.name, f"RDI for Individuals [data migration for Programme: {rdi_2.program.name}]")
        self.assertEqual(rdi_2.status, "MERGED")
        self.assertEqual(rdi_2.number_of_individuals, 1)
        self.assertEqual(rdi_2.number_of_households, 1)
