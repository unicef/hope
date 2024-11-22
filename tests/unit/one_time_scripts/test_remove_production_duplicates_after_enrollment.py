from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.fixtures import PaymentFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.one_time_scripts.remove_production_duplicates_after_enrollment import (
    remove_production_duplicates_after_enrollment,
)


class TestRemoveProductionDuplicatesAfterEnrollment(TestCase):
    def test_remove_production_duplicates_after_enrollment(self) -> None:
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        program2 = ProgramFactory(business_area=business_area)
        hh_unicef_id = "HH-20-0000.0001"
        household_special_case1, individuals_special_case1 = create_household_and_individuals(
            household_data={
                "id": "8b9bf768-4837-49aa-a598-5ad3c5822ca8",
                "unicef_id": hh_unicef_id,
                "business_area": program.business_area,
                "program": program,
            },
            individuals_data=[{}],
        )
        household_special_case2, individuals_special_case2 = create_household_and_individuals(
            household_data={
                "id": "33a7bdf0-650d-49b4-b333-c49a7eb05356",
                "unicef_id": hh_unicef_id,
                "business_area": program.business_area,
                "program": program,
            },
            individuals_data=[{}],
        )
        household1, individuals1 = create_household_and_individuals(
            household_data={
                "unicef_id": hh_unicef_id,
                "business_area": program.business_area,
                "program": program,
            },
            individuals_data=[{}, {}],
        )
        household2, individuals2 = create_household_and_individuals(
            household_data={
                "unicef_id": hh_unicef_id,
                "business_area": program.business_area,
                "program": program,
            },
            individuals_data=[{}, {}],
        )
        household3, individuals3 = create_household_and_individuals(
            household_data={
                "unicef_id": hh_unicef_id,
                "business_area": program.business_area,
                "program": program,
            },
            individuals_data=[{}],
        )
        PaymentFactory(household=household3)

        household4, individuals4 = create_household_and_individuals(
            household_data={
                "unicef_id": hh_unicef_id,
                "business_area": program.business_area,
                "program": program,
            },
            individuals_data=[{}],
        )
        household_from_another_program, individuals_from_another_program = create_household_and_individuals(
            household_data={
                "unicef_id": hh_unicef_id,
                "business_area": program2.business_area,
                "program": program2,
            },
            individuals_data=[{}],
        )

        remove_production_duplicates_after_enrollment()

        self.assertIsNotNone(Household.all_objects.filter(id=household1.id).first())
        self.assertIsNotNone(Individual.all_objects.filter(id=individuals1[0].id).first())
        self.assertIsNotNone(Individual.all_objects.filter(id=individuals1[1].id).first())

        self.assertIsNone(Household.all_objects.filter(id=household2.id).first())
        self.assertIsNone(Individual.all_objects.filter(id=individuals2[0].id).first())
        self.assertIsNone(Individual.all_objects.filter(id=individuals2[1].id).first())

        self.assertIsNotNone(Individual.all_objects.filter(id=individuals3[0].id).first())
        self.assertIsNotNone(Household.all_objects.filter(id=household3.id).first())

        self.assertIsNone(Household.all_objects.filter(id=household4.id).first())
        self.assertIsNone(Individual.all_objects.filter(id=individuals4[0].id).first())

        self.assertIsNotNone(Household.all_objects.filter(id=household_from_another_program.id).first())
        self.assertIsNotNone(Individual.all_objects.filter(id=individuals_from_another_program[0].id).first())

        self.assertIsNone(Household.all_objects.filter(id=household_special_case1.id).first())
        self.assertIsNone(Individual.all_objects.filter(id=individuals_special_case1[0].id).first())

        self.assertIsNone(Household.all_objects.filter(id=household_special_case2.id).first())
        self.assertIsNone(Individual.all_objects.filter(id=individuals_special_case2[0].id).first())
