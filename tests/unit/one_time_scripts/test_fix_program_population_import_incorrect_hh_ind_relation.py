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
        program3 = ProgramFactory(business_area=business_area)

        rdi = RegistrationDataImportFactory(program=program2, data_source=RegistrationDataImport.PROGRAM_POPULATION)
        rdi2 = RegistrationDataImportFactory(program=program2, data_source=RegistrationDataImport.PROGRAM_POPULATION)
        household1, individuals1 = create_household_and_individuals(
            {
                "program": program2,
                "unicef_id": "HH-01",
                "rdi_merge_status": Household.PENDING,
                "registration_data_import": rdi,
                "copied_from": copied_from_hh,
            },
            [{"rdi_merge_status": Household.PENDING}, {"rdi_merge_status": Household.MERGED}],
        )
        for ind in individuals1:
            ind.registration_data_import = rdi2
            ind.save()
        household2, individuals2 = create_household_and_individuals(
            {
                "program": program2,
                "unicef_id": "HH-01",
                "rdi_merge_status": Household.PENDING,
                "registration_data_import": rdi2,
                "copied_from": copied_from_hh,
            },
            [{"rdi_merge_status": Household.PENDING}, {"rdi_merge_status": Household.MERGED}],
        )
        fix_program_population_import_incorrect_hh_ind_relation()
        ind1 = individuals1[0]
        ind2 = individuals1[1]
        ind1.refresh_from_db()
        ind2.refresh_from_db()
        self.assertEqual(ind1.household, household2)
        self.assertEqual(ind2.household, household2)
        self.assertEqual(household1.individuals(manager="all_objects").count(), 0)
        self.assertEqual(household2.individuals(manager="all_objects").count(), 4)
        household2_individuals = [x for x in household2.individuals(manager="all_objects").values_list("id", flat=True)]
        # hhs not to be fixed

        # different program
        household, individuals = create_household_and_individuals(
            {
                "program": program3,
                "unicef_id": "HH-01",
                "rdi_merge_status": Household.PENDING,
                "registration_data_import": rdi,
                "copied_from": copied_from_hh,
            },
            [{}, {}],
        )
        for ind in individuals:
            ind.registration_data_import = rdi2
            ind.save()

        # different unicef_id
        household, individuals = create_household_and_individuals(
            {
                "program": program2,
                "unicef_id": "HH-100",
                "rdi_merge_status": Household.PENDING,
                "registration_data_import": rdi,
                "copied_from": copied_from_hh,
            },
            [{}, {}],
        )
        for ind in individuals:
            ind.registration_data_import = rdi2
            ind.save()

        # hhs and inds have the same rdi
        create_household_and_individuals(
            {
                "program": program2,
                "unicef_id": "HH-01",
                "rdi_merge_status": Household.PENDING,
                "registration_data_import": rdi,
                "copied_from": copied_from_hh,
            },
            [{}, {}],
        )

        fix_program_population_import_incorrect_hh_ind_relation()
        self.assertEqual(household2.individuals(manager="all_objects").count(), 4)
        self.assertEqual(
            household2_individuals,
            [x for x in household2.individuals(manager="all_objects").values_list("id", flat=True)],
        )
