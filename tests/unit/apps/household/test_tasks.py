import pytest
from django.test import TestCase
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    DocumentFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.household.celery_tasks import enroll_households_to_program_task
from hope.apps.household.models import ROLE_PRIMARY, Household
from hope.apps.program.models import Program


@pytest.mark.elasticsearch
class TestEnrollHouseholdsToProgramTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        user = UserFactory()
        cls.str_user_id = str(user.pk)
        cls.program_source = ProgramFactory(
            status=Program.ACTIVE,
            name="Program source",
            business_area=cls.business_area,
        )
        cls.program_target = ProgramFactory(
            status=Program.ACTIVE,
            name="Program target",
            business_area=cls.business_area,
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
        (
            cls.household2_repr_in_target_program,
            individuals2_repr,
        ) = create_household_and_individuals(
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
        assert self.program_target.households.count() == 1
        assert self.program_target.individuals.count() == 1
        assert self.program_source.households.count() == 2
        assert self.program_source.individuals.count() == 2

        assert self.household1.household_collection is None

        assert Household.objects.filter(unicef_id=self.household1.unicef_id).count() == 1
        assert Household.objects.filter(unicef_id=self.household2.unicef_id).count() == 2

        enroll_households_to_program_task(
            households_ids=[self.household1.id, self.household2.id],
            program_for_enroll_id=str(self.program_target.id),
            user_id=self.str_user_id,
        )
        self.household1.refresh_from_db()
        self.household2.refresh_from_db()

        assert self.program_target.households.count() == 2
        assert self.program_target.individuals.count() == 2
        assert self.program_source.households.count() == 2
        assert self.program_source.individuals.count() == 2

        assert self.household1.household_collection is not None

        assert Household.objects.filter(unicef_id=self.household1.unicef_id).count() == 2
        assert Household.objects.filter(unicef_id=self.household2.unicef_id).count() == 2
        enrolled_household = Household.objects.filter(
            program=self.program_target, unicef_id=self.household1.unicef_id
        ).first()
        assert (
            enrolled_household.individuals_and_roles.filter(role=ROLE_PRIMARY).first().individual.unicef_id
            == self.individual.unicef_id
        )
        assert enrolled_household.individuals.first().documents.count() == 1
        assert enrolled_household.individuals.first().identities.count() == 1
