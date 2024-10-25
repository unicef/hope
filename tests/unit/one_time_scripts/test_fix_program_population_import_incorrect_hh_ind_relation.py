from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.one_time_scripts.fix_program_population_import_incorrect_hh_ind_relation import (
    fix_program_population_import_incorrect_hh_ind_relation,
)


class TestFixProgramPopulationIncorrectHhIndRelation(TestCase):
    def test_fix_program_population_import_incorrect_hh_ind_relation(self) -> None:
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        copied_from_hh = HouseholdFactory(program=program)
        program2 = ProgramFactory(business_area=business_area)

        rdi = RegistrationDataImportFactory(program=program2, data_source=RegistrationDataImport.PROGRAM_POPULATION)
        rdi2 = RegistrationDataImportFactory(program=program2, data_source=RegistrationDataImport.PROGRAM_POPULATION)
        rdi3 = RegistrationDataImportFactory(program=program2, data_source=RegistrationDataImport.PROGRAM_POPULATION)
        household1, individuals1 = create_household_and_individuals(
            {
                "program": program2,
                "unicef_id": "HH-01",
                "rdi_merge_status": Household.PENDING,
                "registration_data_import": rdi,
                "copied_from": copied_from_hh,
            },
            [
                {"rdi_merge_status": Household.PENDING},
                {"rdi_merge_status": Household.PENDING},
            ],
        )

        household2, individuals2 = create_household_and_individuals(
            {
                "program": program2,
                "unicef_id": "HH-01",
                "rdi_merge_status": Household.PENDING,
                "registration_data_import": rdi2,
                "copied_from": copied_from_hh,
            },
            [{"rdi_merge_status": Household.PENDING}, {"rdi_merge_status": Household.PENDING}],
        )
        ind2_1 = individuals2[0]
        ind2_1.household = household1
        ind2_1.save()

        household3, individuals3 = create_household_and_individuals(
            {
                "program": program2,
                "unicef_id": "HH-01",
                "rdi_merge_status": Household.MERGED,
                "registration_data_import": rdi3,
                "copied_from": copied_from_hh,
            },
            [{"rdi_merge_status": Household.MERGED}, {"rdi_merge_status": Household.MERGED}],
        )
        ind3_1 = individuals3[0]
        ind3_1.household = household1
        ind3_1.save()
        ind3_2 = individuals3[1]
        ind3_2.household = household2
        ind3_2.save()

        # check incorrect data
        self.assertEqual(household1.individuals(manager="all_objects").count(), 4)
        self.assertEqual(household2.individuals(manager="all_objects").count(), 2)
        self.assertEqual(household3.individuals(manager="all_objects").count(), 0)

        self.assertNotEqual(ind2_1.household.registration_data_import, household2.registration_data_import)
        self.assertNotEqual(ind3_1.household.registration_data_import, household3.registration_data_import)
        self.assertNotEqual(ind3_2.household.registration_data_import, household3.registration_data_import)

        fix_program_population_import_incorrect_hh_ind_relation()

        ind2_1.refresh_from_db()
        ind3_1.refresh_from_db()
        ind3_2.refresh_from_db()

        self.assertEqual(household1.individuals(manager="all_objects").count(), 2)

        self.assertEqual(ind2_1.household, household2)
        self.assertEqual(household2.individuals(manager="all_objects").count(), 2)

        self.assertEqual(ind3_1.household, household3)
        self.assertEqual(ind3_2.household, household3)
        self.assertEqual(household3.individuals(manager="all_objects").count(), 2)

        self.assertEqual(ind2_1.household.registration_data_import, household2.registration_data_import)
        self.assertEqual(ind3_1.household.registration_data_import, household3.registration_data_import)
        self.assertEqual(ind3_2.household.registration_data_import, household3.registration_data_import)
