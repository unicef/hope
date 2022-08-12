from graphql import GraphQLError

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.mutations_extras.utils import (
    reassign_roles_on_disable_individual,
)
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestReassignRolesOnDisableIndividual(APITestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        program_one = ProgramFactory(name="Test program ONE", business_area=business_area)

        cls.household = HouseholdFactory.build(id="b5cb9bb2-a4f3-49f0-a9c8-a2f260026054")
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.save()
        cls.household.programs.add(program_one)

        cls.primary_collector_individual = IndividualFactory(household=None)
        cls.household.head_of_household = cls.primary_collector_individual
        cls.household.save()
        cls.primary_collector_individual.household = cls.household
        cls.primary_collector_individual.save()

        cls.household.refresh_from_db()
        cls.primary_collector_individual.refresh_from_db()

        cls.primary_role = IndividualRoleInHousehold.objects.create(
            household=cls.household,
            individual=cls.primary_collector_individual,
            role=ROLE_PRIMARY,
        )

        cls.alternate_collector_individual = IndividualFactory(household=None)
        cls.alternate_collector_individual.household = cls.household
        cls.alternate_collector_individual.save()

        cls.alternate_role = IndividualRoleInHousehold.objects.create(
            household=cls.household,
            individual=cls.alternate_collector_individual,
            role=ROLE_ALTERNATE,
        )

    def test_reassign_role_to_another_individual(self):
        individual = IndividualFactory(household=None)

        individual.household = self.household
        individual.save()

        role_reassign_data = {
            "HEAD": {
                "role": "HEAD",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(individual.id, "IndividualNode"),
            },
            str(self.primary_role.id): {
                "role": "PRIMARY",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(individual.id, "IndividualNode"),
            },
        }

        reassign_roles_on_disable_individual(self.primary_collector_individual, role_reassign_data)

        individual.refresh_from_db()
        self.household.refresh_from_db()

        self.assertEqual(self.household.head_of_household, individual)
        self.assertEqual(individual.relationship, HEAD)
        role = IndividualRoleInHousehold.objects.get(household=self.household, individual=individual).role
        self.assertEqual(role, ROLE_PRIMARY)

    def test_reassign_alternate_role_to_primary_collector(self):
        role_reassign_data = {
            str(self.alternate_role.id): {
                "role": "ALTERNATE",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(self.primary_collector_individual.id, "IndividualNode"),
            },
        }

        with self.assertRaises(GraphQLError) as context:
            reassign_roles_on_disable_individual(self.alternate_collector_individual, role_reassign_data)

        self.assertTrue("Cannot reassign the role" in str(context.exception))

    def test_reassign_alternate_role(self):
        individual = IndividualFactory(household=None)
        individual.household = self.household
        individual.save()

        role_reassign_data = {
            str(self.alternate_role.id): {
                "role": "ALTERNATE",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(individual.id, "IndividualNode"),
            },
        }

        reassign_roles_on_disable_individual(self.alternate_collector_individual, role_reassign_data)

        role = IndividualRoleInHousehold.objects.get(household=self.household, individual=individual).role
        self.assertEqual(role, ROLE_ALTERNATE)
