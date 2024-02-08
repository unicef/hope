from django.core.exceptions import ValidationError
from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.services.reassign_roles_services import (
    reassign_roles_on_update_service,
)
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestReassignRolesOnUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("loadbusinessareas")

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program_one = ProgramFactory(name="Test program ONE", business_area=cls.business_area)

        cls.household = HouseholdFactory.build(id="b5cb9bb2-a4f3-49f0-a9c8-a2f260026054", program=cls.program_one)
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = cls.program_one
        cls.household.registration_data_import.save()
        cls.household.programs.add(cls.program_one)

        cls.primary_collector_individual = IndividualFactory(household=None, program=cls.program_one)
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

        cls.alternate_collector_individual = IndividualFactory(household=None, program=cls.program_one)
        cls.alternate_collector_individual.household = cls.household
        cls.alternate_collector_individual.save()

        cls.alternate_role = IndividualRoleInHousehold.objects.create(
            household=cls.household,
            individual=cls.alternate_collector_individual,
            role=ROLE_ALTERNATE,
        )

        cls.no_role_individual = IndividualFactory(household=None, program=cls.program_one)
        cls.no_role_individual.household = cls.household
        cls.no_role_individual.save()

    def test_reassign_role_to_another_individual(self) -> None:
        individual = IndividualFactory(household=self.household, program=self.program_one)

        role_reassign_data = {
            "HEAD": {
                "role": "HEAD",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(individual.id, "IndividualNode"),
            },
            self.primary_role.id: {
                "role": "PRIMARY",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(individual.id, "IndividualNode"),
            },
        }

        reassign_roles_on_update_service(
            self.primary_collector_individual, role_reassign_data, UserFactory(), self.program_one
        )

        individual.refresh_from_db()
        self.household.refresh_from_db()

        self.assertEqual(self.household.head_of_household, individual)
        self.assertEqual(individual.relationship, HEAD)
        role = IndividualRoleInHousehold.objects.get(household=self.household, individual=individual).role
        self.assertEqual(role, ROLE_PRIMARY)

    def test_reassign_alternate_role_to_primary_collector(self) -> None:
        role_reassign_data = {
            self.alternate_role.id: {
                "role": "ALTERNATE",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(self.primary_collector_individual.id, "IndividualNode"),
            },
        }

        with self.assertRaises(ValidationError) as context:
            reassign_roles_on_update_service(
                self.alternate_collector_individual, role_reassign_data, UserFactory(), self.program_one
            )

        self.assertTrue("Cannot reassign the role" in str(context.exception))

    def test_reassign_alternate_role(self) -> None:
        individual = IndividualFactory(household=self.household, program=self.program_one)

        role_reassign_data = {
            self.alternate_role.id: {
                "role": "ALTERNATE",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(individual.id, "IndividualNode"),
            },
        }

        reassign_roles_on_update_service(
            self.alternate_collector_individual, role_reassign_data, UserFactory(), self.program_one
        )
        role = IndividualRoleInHousehold.objects.get(household=self.household, individual=individual).role
        self.assertEqual(role, ROLE_ALTERNATE)

    def test_reassign_primary_role_to_current_alternate_collector(self) -> None:
        role_reassign_data = {
            self.primary_role.id: {
                "role": "PRIMARY",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(self.alternate_collector_individual.id, "IndividualNode"),
            },
        }

        reassign_roles_on_update_service(
            self.primary_collector_individual, role_reassign_data, UserFactory(), self.program_one
        )

        role = IndividualRoleInHousehold.objects.get(
            household=self.household, individual=self.alternate_collector_individual
        ).role
        self.assertEqual(role, ROLE_PRIMARY)

        previous_role = IndividualRoleInHousehold.objects.filter(household=self.household, role=ROLE_ALTERNATE).first()
        self.assertIsNone(previous_role)

    def test_reassign_alternate_role_to_individual_with_primary_role_in_another_household(self) -> None:
        household = HouseholdFactory.build(business_area=self.business_area, program=self.program_one)
        household.household_collection.save()
        household.registration_data_import.imported_by.save()
        household.registration_data_import.program = household.program
        household.registration_data_import.save()
        hoh = IndividualFactory(household=household, program=self.program_one)
        household.head_of_household = hoh
        household.save()

        IndividualRoleInHousehold.objects.create(
            household=household,
            individual=self.no_role_individual,
            role=ROLE_PRIMARY,
        )

        role_reassign_data = {
            self.alternate_role.id: {
                "role": "ALTERNATE",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(self.no_role_individual.id, "IndividualNode"),
            },
        }

        reassign_roles_on_update_service(
            self.alternate_collector_individual, role_reassign_data, UserFactory(), self.program_one
        )

        role = IndividualRoleInHousehold.objects.get(household=self.household, individual=self.no_role_individual).role
        self.assertEqual(role, ROLE_ALTERNATE)

        external_role = IndividualRoleInHousehold.objects.get(
            household=household, individual=self.no_role_individual
        ).role
        self.assertEqual(external_role, ROLE_PRIMARY)  # still with primary role in another household
