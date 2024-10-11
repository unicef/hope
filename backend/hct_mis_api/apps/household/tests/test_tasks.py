from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.celery_tasks import enroll_households_to_program_task
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestEnrollHouseholdsToProgramTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.program_source = ProgramFactory(
            status=Program.ACTIVE, name="Program source", business_area=cls.business_area
        )
        cls.program_target = ProgramFactory(
            status=Program.ACTIVE, name="Program target", business_area=cls.business_area
        )

        cls.household1, individuals1 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program": cls.program_source,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program": cls.program_source,
                },
            ],
        )
        cls.individual = individuals1[0]
        cls.individual_role_in_household1 = IndividualRoleInHouseholdFactory(
            individual=cls.individual,
            household=cls.household1,
            role=ROLE_PRIMARY,
        )
        cls.document1 = DocumentFactory(individual=cls.individual, program=cls.individual.program)
        cls.individual_identity1 = IndividualIdentityFactory(individual=cls.individual)
        cls.bank_account_info1 = BankAccountInfoFactory(individual=cls.individual)
        cls.individual.individual_collection = None
        cls.individual.save()
        cls.household1.household_collection = None
        cls.household1.save()

        # already existing hh in the target program
        cls.household2, individuals2 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program": cls.program_source,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program": cls.program_source,
                },
            ],
        )
        cls.household2_repr_in_target_program, individuals2_repr = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program": cls.program_target,
                "unicef_id": cls.household2.unicef_id,
                "household_collection": cls.household2.household_collection,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program": cls.program_target,
                    "unicef_id": cls.household2.individuals.first().unicef_id,
                    "individual_collection": cls.household2.individuals.first().individual_collection,
                },
            ],
        )
        cls.individual2_repr_in_target_program = individuals2_repr[0]

    def test_enroll_households_to_program_task(self) -> None:
        self.assertEqual(self.program_target.household_set.count(), 1)
        self.assertEqual(self.program_target.individuals.count(), 1)
        self.assertEqual(self.program_source.household_set.count(), 2)
        self.assertEqual(self.program_source.individuals.count(), 2)

        self.assertIsNone(self.household1.household_collection)

        self.assertEqual(Household.objects.filter(unicef_id=self.household1.unicef_id).count(), 1)
        self.assertEqual(Household.objects.filter(unicef_id=self.household2.unicef_id).count(), 2)

        enroll_households_to_program_task(
            households_ids=[self.household1.id, self.household2.id], program_for_enroll_id=str(self.program_target.id)
        )
        self.household1.refresh_from_db()
        self.household2.refresh_from_db()

        self.assertEqual(self.program_target.household_set.count(), 2)
        self.assertEqual(self.program_target.individuals.count(), 2)
        self.assertEqual(self.program_source.household_set.count(), 2)
        self.assertEqual(self.program_source.individuals.count(), 2)

        self.assertIsNotNone(self.household1.household_collection)

        self.assertEqual(Household.objects.filter(unicef_id=self.household1.unicef_id).count(), 2)
        self.assertEqual(Household.objects.filter(unicef_id=self.household2.unicef_id).count(), 2)
        enrolled_household = Household.objects.filter(
            program=self.program_target, unicef_id=self.household1.unicef_id
        ).first()
        self.assertEqual(
            enrolled_household.individuals_and_roles.filter(role=ROLE_PRIMARY).first().individual.unicef_id,
            self.individual.unicef_id,
        )
        self.assertEqual(enrolled_household.individuals.first().documents.count(), 1)
        self.assertEqual(enrolled_household.individuals.first().identities.count(), 1)
        self.assertEqual(enrolled_household.individuals.first().bank_account_info.count(), 1)
