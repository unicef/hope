from django.core.exceptions import ValidationError
from django.core.management import call_command

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.core.base_test_case import APITestCase
from hope.apps.core.models import BusinessArea
from hope.apps.grievance.services.reassign_roles_services import (
    reassign_roles_on_marking_as_duplicate_individual_service,
)
from hope.apps.household.models import (
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Individual,
    IndividualRoleInHousehold,
)
from hope.apps.utils.models import MergeStatusModel


class TestReassignRolesOnUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadbusinessareas")

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program_one = ProgramFactory(name="Test program ONE", business_area=cls.business_area)

        cls.household = HouseholdFactory.build(program=cls.program_one)
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = cls.program_one
        cls.household.registration_data_import.save()

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
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.alternate_collector_individual = IndividualFactory(household=None, program=cls.program_one)
        cls.alternate_collector_individual.household = cls.household
        cls.alternate_collector_individual.save()

        cls.alternate_role = IndividualRoleInHousehold.objects.create(
            household=cls.household,
            individual=cls.alternate_collector_individual,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.no_role_individual = IndividualFactory(household=cls.household, program=cls.program_one)
        cls.user = UserFactory()

    def test_reassign_roles_on_marking_as_duplicate_individual_service(self) -> None:
        duplicated_individuals = Individual.objects.filter(id=self.primary_collector_individual.id)
        role_reassign_data = {
            ROLE_PRIMARY: {
                "role": ROLE_PRIMARY,
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }
        reassign_roles_on_marking_as_duplicate_individual_service(role_reassign_data, self.user, duplicated_individuals)
        assert (
            IndividualRoleInHousehold.objects.filter(
                household=self.household, individual=self.no_role_individual, role=ROLE_PRIMARY
            ).count()
            == 1
        )
        assert (
            IndividualRoleInHousehold.objects.filter(
                household=self.household, individual=self.primary_collector_individual, role=ROLE_PRIMARY
            ).count()
            == 0
        )
        self.household.refresh_from_db()
        assert self.household.head_of_household == self.no_role_individual
        for individual in self.household.individuals.exclude(id=self.no_role_individual.id):
            assert individual.relationship == RELATIONSHIP_UNKNOWN

    def test_reassign_roles_on_marking_as_duplicate_individual_service_wrong_program(self) -> None:
        program_two = ProgramFactory(name="Test program TWO", business_area=self.business_area)
        self.no_role_individual.program = program_two
        self.no_role_individual.save()
        duplicated_individuals = Individual.objects.filter(id=self.primary_collector_individual.id)
        role_reassign_data = {
            ROLE_PRIMARY: {
                "role": ROLE_PRIMARY,
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }
        with self.assertRaises(ValidationError) as error:
            reassign_roles_on_marking_as_duplicate_individual_service(
                role_reassign_data, self.user, duplicated_individuals
            )
        assert str(error.exception.messages[0]) == "Cannot reassign role to individual from different program"

    def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_without_duplicate(self) -> None:
        duplicated_individuals = Individual.objects.none()
        role_reassign_data = {
            ROLE_PRIMARY: {
                "role": ROLE_PRIMARY,
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }

        with self.assertRaises(ValidationError) as error:
            reassign_roles_on_marking_as_duplicate_individual_service(
                role_reassign_data, self.user, duplicated_individuals
            )
        assert (
            str(error.exception.messages[0])
            == f"Individual ({self.primary_collector_individual.unicef_id}) was not marked as duplicated"
        )

    def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_new_individual_is_duplicate(
        self,
    ) -> None:
        duplicated_individuals = Individual.objects.filter(
            id__in=[self.no_role_individual.id, self.primary_collector_individual.id]
        )
        role_reassign_data = {
            ROLE_PRIMARY: {
                "role": ROLE_PRIMARY,
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }

        with self.assertRaises(ValidationError) as error:
            reassign_roles_on_marking_as_duplicate_individual_service(
                role_reassign_data, self.user, duplicated_individuals
            )
        assert (
            str(error.exception.messages[0])
            == f"Individual({self.no_role_individual.unicef_id}) which get role PRIMARY was marked as duplicated"
        )

    def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_from_alternate_to_primary(
        self,
    ) -> None:
        duplicated_individuals = Individual.objects.filter(id__in=[self.primary_collector_individual.id])
        role_reassign_data = {
            ROLE_PRIMARY: {
                "role": ROLE_PRIMARY,
                "new_individual": str(self.alternate_collector_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }

        reassign_roles_on_marking_as_duplicate_individual_service(role_reassign_data, self.user, duplicated_individuals)
        assert (
            IndividualRoleInHousehold.objects.filter(
                household=self.household, individual=self.alternate_collector_individual, role=ROLE_PRIMARY
            ).count()
            == 1
        )
        assert (
            IndividualRoleInHousehold.objects.filter(
                household=self.household, individual=self.alternate_collector_individual
            ).count()
            == 1
        )

    def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_from_primary_to_alternate(
        self,
    ) -> None:
        duplicated_individuals = Individual.objects.filter(id__in=[self.alternate_collector_individual.id])
        role_reassign_data = {
            ROLE_ALTERNATE: {
                "role": ROLE_ALTERNATE,
                "new_individual": str(self.primary_collector_individual.id),
                "household": str(self.household.id),
                "individual": str(self.alternate_collector_individual.id),
            },
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }

        with self.assertRaises(ValidationError) as error:
            reassign_roles_on_marking_as_duplicate_individual_service(
                role_reassign_data, self.user, duplicated_individuals
            )
        assert (
            str(error.exception.messages[0])
            == "Cannot reassign the role. Selected individual has primary collector role."
        )

    def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_wrong_role(
        self,
    ) -> None:
        duplicated_individuals = Individual.objects.filter(id__in=[self.primary_collector_individual.id])
        role_reassign_data = {
            ROLE_PRIMARY: {
                "role": "WRONG_ROLE",
                "new_individual": str(self.alternate_collector_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }
        with self.assertRaises(ValidationError) as error:
            reassign_roles_on_marking_as_duplicate_individual_service(
                role_reassign_data, self.user, duplicated_individuals
            )
        assert str(error.exception.messages[0]) == "Invalid role name"

    def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_from_wrong_person(
        self,
    ) -> None:
        duplicated_individuals = Individual.objects.filter(id__in=[self.alternate_collector_individual.id])
        role_reassign_data = {
            ROLE_PRIMARY: {
                "role": ROLE_PRIMARY,
                "new_individual": str(self.primary_collector_individual.id),
                "household": str(self.household.id),
                "individual": str(self.alternate_collector_individual.id),
            },
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }
        with self.assertRaises(ValidationError) as error:
            reassign_roles_on_marking_as_duplicate_individual_service(
                role_reassign_data, self.user, duplicated_individuals
            )
        assert (
            str(error.exception.messages[0])
            == f"Individual with unicef_id {self.alternate_collector_individual.unicef_id} does not have role PRIMARY in household with unicef_id {self.household.unicef_id}"
        )

    def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_hoh_not_reassigned(
        self,
    ) -> None:
        duplicated_individuals = Individual.objects.filter(id__in=[self.primary_collector_individual.id])
        role_reassign_data = {
            ROLE_PRIMARY: {
                "role": ROLE_PRIMARY,
                "new_individual": str(self.alternate_collector_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }
        with self.assertRaises(ValidationError) as error:
            reassign_roles_on_marking_as_duplicate_individual_service(
                role_reassign_data, self.user, duplicated_individuals
            )
        assert (
            str(error.exception.messages[0]) == ""
            f"Role for head of household in household with unicef_id {self.household.unicef_id} was not reassigned, when individual ({self.primary_collector_individual.unicef_id}) was marked as duplicated"
        )

    def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_primary_not_reassigned(
        self,
    ) -> None:
        duplicated_individuals = Individual.objects.filter(id__in=[self.primary_collector_individual.id])
        role_reassign_data = {
            str(self.primary_collector_individual.id): {
                "role": "HEAD",
                "new_individual": str(self.no_role_individual.id),
                "household": str(self.household.id),
                "individual": str(self.primary_collector_individual.id),
            },
        }
        with self.assertRaises(ValidationError) as error:
            reassign_roles_on_marking_as_duplicate_individual_service(
                role_reassign_data, self.user, duplicated_individuals
            )
        assert (
            str(error.exception.messages[0])
            == f"Primary role in household with unicef_id {self.household.unicef_id} is still assigned to duplicated individual({self.primary_collector_individual.unicef_id})"
        )
