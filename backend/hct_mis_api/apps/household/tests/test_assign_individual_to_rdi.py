from django.core.management import call_command
from django.db.models import Count
from django.test import TransactionTestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class TestMigrationIndAssignToRDI(TransactionTestCase):
    def test_assign_individual_to_rdi_migration(self) -> None:
        call_command("migrate", "household", "0184_migration", verbosity=0)

        ba_afghanistan = create_afghanistan()
        program_1 = ProgramFactory(name="program_1", business_area=ba_afghanistan, biometric_deduplication_enabled=True)
        program_2 = ProgramFactory(name="program_2", business_area=ba_afghanistan, biometric_deduplication_enabled=True)
        create_household_and_individuals(
            household_data={
                "business_area": ba_afghanistan,
                "program": program_1,
            },
            individuals_data=[
                {
                    "business_area": ba_afghanistan,
                    "program": program_1,
                },
            ],
        )
        create_household_and_individuals(
            household_data={
                "business_area": ba_afghanistan,
                "program": program_2,
            },
            individuals_data=[
                {
                    "business_area": ba_afghanistan,
                    "program": program_2,
                },
            ],
        )
        # set registration_data_import to null
        Household.objects.all().update(registration_data_import=None)
        Individual.objects.all().update(registration_data_import=None)
        # add more individuals assigned to RDI
        program_3 = ProgramFactory(name="Program 333", business_area=ba_afghanistan)
        create_household_and_individuals(
            household_data={
                "business_area": ba_afghanistan,
                "program": program_3,
            },
            individuals_data=[
                {
                    "business_area": ba_afghanistan,
                    "program": program_3,
                },
                {
                    "business_area": ba_afghanistan,
                    "program": program_3,
                },
            ],
        )
        # check before migrate data
        self.assertEqual(RegistrationDataImport.objects.count(), 3)
        self.assertEqual(Program.objects.count(), 3)
        self.assertEqual(Individual.objects.count(), 4)
        self.assertEqual(Household.objects.count(), 3)
        self.assertEqual(Individual.objects.filter(program=program_1).count(), 1)
        self.assertEqual(Individual.objects.filter(program=program_2).count(), 1)
        self.assertEqual(Individual.objects.filter(registration_data_import__isnull=True).count(), 2)
        self.assertEqual(Household.objects.filter(registration_data_import__isnull=True).count(), 2)

        # call_command("migrate", "household", "0185_migration", verbosity=0)
        for program in Program.objects.all():
            # create RDI only if exists any individual without RDI
            individual_qs = Individual.objects.filter(program=program, registration_data_import__isnull=True)
            aggregated_data = individual_qs.aggregate(
                individual_count=Count("id"), household_count=Count("household", distinct=True)
            )
            if aggregated_data["individual_count"] > 0:
                rdi = RegistrationDataImport.objects.create(
                    name=f"RDI for Individuals [data migration for Programme: {program.name}]",
                    status="MERGED",
                    imported_by=None,
                    data_source="XLS",
                    number_of_individuals=aggregated_data["individual_count"],
                    number_of_households=aggregated_data["household_count"],
                    business_area=program.business_area,
                    program_id=program.id,
                    import_data=None,
                    deduplication_engine_status="PENDING" if program.biometric_deduplication_enabled else None,
                )

                individual_qs.update(registration_data_import_id=rdi.id)

        # 3 old RDIs and + 2 new created
        self.assertEqual(RegistrationDataImport.objects.count(), 5)
        self.assertEqual(Individual.objects.filter(registration_data_import__isnull=False).count(), 4)
        self.assertEqual(Household.objects.filter(registration_data_import__isnull=True).count(), 2)

        rdi_1 = RegistrationDataImport.objects.get(
            name=f"RDI for Individuals [data migration for Programme: {program_1.name}]"
        )
        self.assertEqual(rdi_1.status, "MERGED")
        self.assertEqual(rdi_1.deduplication_engine_status, "PENDING")
        self.assertEqual(rdi_1.number_of_individuals, 1)
        self.assertEqual(rdi_1.number_of_households, 1)

        rdi_2 = RegistrationDataImport.objects.get(
            name=f"RDI for Individuals [data migration for Programme: {program_2.name}]"
        )
        self.assertEqual(rdi_2.status, "MERGED")
        self.assertEqual(rdi_2.deduplication_engine_status, "PENDING")
        self.assertEqual(rdi_2.number_of_individuals, 1)
        self.assertEqual(rdi_2.number_of_households, 1)
