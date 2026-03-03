from typing import Any
from unittest.mock import MagicMock

import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.grievance.services.reassign_roles_services import (
    _validate_role_reassignment,
    reassign_roles_on_marking_as_duplicate_individual_service,
)
from hope.apps.household.const import RELATIONSHIP_UNKNOWN, ROLE_ALTERNATE, ROLE_PRIMARY
from hope.models import Individual, IndividualRoleInHousehold

pytestmark = pytest.mark.django_db


@pytest.fixture
def base_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    program_one = ProgramFactory(name="Test program ONE", business_area=business_area)
    household = HouseholdFactory(
        program=program_one,
        business_area=business_area,
        create_role=False,
    )

    primary_collector_individual = household.head_of_household
    primary_role = IndividualRoleInHouseholdFactory(
        household=household,
        individual=primary_collector_individual,
        role=ROLE_PRIMARY,
    )

    alternate_collector_individual = IndividualFactory(
        household=household,
        program=program_one,
        business_area=business_area,
        registration_data_import=household.registration_data_import,
    )
    alternate_role = IndividualRoleInHouseholdFactory(
        household=household,
        individual=alternate_collector_individual,
        role=ROLE_ALTERNATE,
    )

    no_role_individual = IndividualFactory(
        household=household,
        program=program_one,
        business_area=business_area,
        registration_data_import=household.registration_data_import,
    )
    user = UserFactory()

    return {
        "business_area": business_area,
        "program_one": program_one,
        "household": household,
        "primary_collector_individual": primary_collector_individual,
        "primary_role": primary_role,
        "alternate_collector_individual": alternate_collector_individual,
        "alternate_role": alternate_role,
        "no_role_individual": no_role_individual,
        "user": user,
    }


@pytest.fixture
def program_two(base_context: dict[str, Any]):
    return ProgramFactory(name="Test program TWO", business_area=base_context["business_area"])


def test_reassign_roles_on_marking_as_duplicate_individual_service(base_context: dict[str, Any]) -> None:
    duplicated_individuals = Individual.objects.filter(id=base_context["primary_collector_individual"].id)
    role_reassign_data = {
        ROLE_PRIMARY: {
            "role": ROLE_PRIMARY,
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }
    reassign_roles_on_marking_as_duplicate_individual_service(
        role_reassign_data,
        base_context["user"],
        duplicated_individuals,
    )
    assert (
        IndividualRoleInHousehold.objects.filter(
            household=base_context["household"],
            individual=base_context["no_role_individual"],
            role=ROLE_PRIMARY,
        ).count()
        == 1
    )
    assert (
        IndividualRoleInHousehold.objects.filter(
            household=base_context["household"],
            individual=base_context["primary_collector_individual"],
            role=ROLE_PRIMARY,
        ).count()
        == 0
    )
    base_context["household"].refresh_from_db()
    assert base_context["household"].head_of_household == base_context["no_role_individual"]

    base_context["primary_collector_individual"].refresh_from_db()
    assert base_context["primary_collector_individual"].relationship == RELATIONSHIP_UNKNOWN

    base_context["alternate_collector_individual"].refresh_from_db()
    assert base_context["alternate_collector_individual"].relationship == RELATIONSHIP_UNKNOWN


def test_reassign_roles_on_marking_as_duplicate_individual_service_wrong_program(
    base_context: dict[str, Any],
    program_two,
) -> None:
    base_context["no_role_individual"].program = program_two
    base_context["no_role_individual"].save(update_fields=["program"])
    duplicated_individuals = Individual.objects.filter(id=base_context["primary_collector_individual"].id)
    role_reassign_data = {
        ROLE_PRIMARY: {
            "role": ROLE_PRIMARY,
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }
    with pytest.raises(ValidationError) as error:
        reassign_roles_on_marking_as_duplicate_individual_service(
            role_reassign_data,
            base_context["user"],
            duplicated_individuals,
        )
    assert str(error.value.detail[0]) == "Cannot reassign role to individual from different program"


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_without_duplicate(
    base_context: dict[str, Any],
) -> None:
    duplicated_individuals = Individual.objects.none()
    role_reassign_data = {
        ROLE_PRIMARY: {
            "role": ROLE_PRIMARY,
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }

    with pytest.raises(ValidationError) as error:
        reassign_roles_on_marking_as_duplicate_individual_service(
            role_reassign_data,
            base_context["user"],
            duplicated_individuals,
        )
    assert (
        str(error.value.detail[0])
        == f"Individual ({base_context['primary_collector_individual'].unicef_id}) was not marked as duplicated"
    )


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_new_individual_is_duplicate(
    base_context: dict[str, Any],
) -> None:
    duplicated_individuals = Individual.objects.filter(
        id__in=[
            base_context["no_role_individual"].id,
            base_context["primary_collector_individual"].id,
        ]
    )
    role_reassign_data = {
        ROLE_PRIMARY: {
            "role": ROLE_PRIMARY,
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }

    with pytest.raises(ValidationError) as error:
        reassign_roles_on_marking_as_duplicate_individual_service(
            role_reassign_data,
            base_context["user"],
            duplicated_individuals,
        )
    assert (
        str(error.value.detail[0])
        == f"Individual({base_context['no_role_individual'].unicef_id}) which get role PRIMARY was marked as duplicated"
    )


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_from_alternate_to_primary(
    base_context: dict[str, Any],
) -> None:
    duplicated_individuals = Individual.objects.filter(id__in=[base_context["primary_collector_individual"].id])
    role_reassign_data = {
        ROLE_PRIMARY: {
            "role": ROLE_PRIMARY,
            "new_individual": str(base_context["alternate_collector_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }

    reassign_roles_on_marking_as_duplicate_individual_service(
        role_reassign_data,
        base_context["user"],
        duplicated_individuals,
    )
    assert (
        IndividualRoleInHousehold.objects.filter(
            household=base_context["household"],
            individual=base_context["alternate_collector_individual"],
            role=ROLE_PRIMARY,
        ).count()
        == 1
    )
    assert (
        IndividualRoleInHousehold.objects.filter(
            household=base_context["household"],
            individual=base_context["alternate_collector_individual"],
        ).count()
        == 1
    )


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_from_primary_to_alternate(
    base_context: dict[str, Any],
) -> None:
    duplicated_individuals = Individual.objects.filter(id__in=[base_context["alternate_collector_individual"].id])
    role_reassign_data = {
        ROLE_ALTERNATE: {
            "role": ROLE_ALTERNATE,
            "new_individual": str(base_context["primary_collector_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["alternate_collector_individual"].id),
        },
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }

    with pytest.raises(ValidationError) as error:
        reassign_roles_on_marking_as_duplicate_individual_service(
            role_reassign_data,
            base_context["user"],
            duplicated_individuals,
        )
    assert str(error.value.detail[0]) == "Cannot reassign the role. Selected individual has primary collector role."


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_wrong_role(
    base_context: dict[str, Any],
) -> None:
    duplicated_individuals = Individual.objects.filter(id__in=[base_context["primary_collector_individual"].id])
    role_reassign_data = {
        ROLE_PRIMARY: {
            "role": "WRONG_ROLE",
            "new_individual": str(base_context["alternate_collector_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }
    with pytest.raises(ValidationError) as error:
        reassign_roles_on_marking_as_duplicate_individual_service(
            role_reassign_data,
            base_context["user"],
            duplicated_individuals,
        )
    assert str(error.value.detail[0]) == "Invalid role name"


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_from_wrong_person(
    base_context: dict[str, Any],
) -> None:
    duplicated_individuals = Individual.objects.filter(id__in=[base_context["alternate_collector_individual"].id])
    role_reassign_data = {
        ROLE_PRIMARY: {
            "role": ROLE_PRIMARY,
            "new_individual": str(base_context["primary_collector_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["alternate_collector_individual"].id),
        },
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }
    with pytest.raises(ValidationError) as error:
        reassign_roles_on_marking_as_duplicate_individual_service(
            role_reassign_data,
            base_context["user"],
            duplicated_individuals,
        )
    assert (
        str(error.value.detail[0])
        == f"Individual with unicef_id {base_context['alternate_collector_individual'].unicef_id} does not have role "
        f"PRIMARY in household with unicef_id {base_context['household'].unicef_id}"
    )


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_hoh_not_reassigned(
    base_context: dict[str, Any],
) -> None:
    duplicated_individuals = Individual.objects.filter(id__in=[base_context["primary_collector_individual"].id])
    role_reassign_data = {
        ROLE_PRIMARY: {
            "role": ROLE_PRIMARY,
            "new_individual": str(base_context["alternate_collector_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }
    with pytest.raises(ValidationError) as error:
        reassign_roles_on_marking_as_duplicate_individual_service(
            role_reassign_data,
            base_context["user"],
            duplicated_individuals,
        )
    assert (
        str(error.value.detail[0]) == f"Role for head of household in household with unicef_id "
        f"{base_context['household'].unicef_id} was not reassigned, when individual "
        f"({base_context['primary_collector_individual'].unicef_id}) was marked as "
        f"duplicated"
    )


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_primary_not_reassigned(
    base_context: dict[str, Any],
) -> None:
    duplicated_individuals = Individual.objects.filter(id__in=[base_context["primary_collector_individual"].id])
    role_reassign_data = {
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }
    with pytest.raises(ValidationError) as error:
        reassign_roles_on_marking_as_duplicate_individual_service(
            role_reassign_data,
            base_context["user"],
            duplicated_individuals,
        )
    assert (
        str(error.value.detail[0])
        == f"Primary role in household with unicef_id {base_context['household'].unicef_id} is still assigned to "
        f"duplicated individual({base_context['primary_collector_individual'].unicef_id})"
    )


def test_reassign_roles_on_marking_as_duplicate_individual_service_reassign_primary_hh_withdrawn(
    base_context: dict[str, Any],
) -> None:
    base_context["household"].withdrawn = True
    base_context["household"].save(update_fields=["withdrawn"])
    duplicated_individuals = Individual.objects.filter(id__in=[base_context["primary_collector_individual"].id])
    role_reassign_data = {
        str(base_context["primary_collector_individual"].id): {
            "role": "HEAD",
            "new_individual": str(base_context["no_role_individual"].id),
            "household": str(base_context["household"].id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }
    reassign_roles_on_marking_as_duplicate_individual_service(
        role_reassign_data,
        base_context["user"],
        duplicated_individuals,
    )
    assert (
        IndividualRoleInHousehold.objects.filter(individual=base_context["primary_collector_individual"]).count() == 1
    )


# ============================================================================
# _validate_role_reassignment unit tests (mock-based, no DB needed)
# ============================================================================


def test_validate_role_reassignment_raises_when_programs_differ():
    new_individual = MagicMock()
    new_individual.program = MagicMock()
    individual_which_loses_role = MagicMock()
    individual_which_loses_role.program = MagicMock()

    with pytest.raises(ValidationError, match="Cannot reassign role to individual from different program"):
        _validate_role_reassignment([], ROLE_PRIMARY, new_individual, individual_which_loses_role)


def test_validate_role_reassignment_raises_when_loser_not_in_duplicated_ids():
    program = MagicMock()
    new_individual = MagicMock()
    new_individual.program = program
    new_individual.id = "new-id"
    individual_which_loses_role = MagicMock()
    individual_which_loses_role.program = program
    individual_which_loses_role.id = "loser-id"
    individual_which_loses_role.unicef_id = "IND-001"

    with pytest.raises(ValidationError, match="was not marked as duplicated"):
        _validate_role_reassignment(["other-id"], ROLE_PRIMARY, new_individual, individual_which_loses_role)


def test_validate_role_reassignment_raises_when_new_individual_in_duplicated_ids():
    program = MagicMock()
    new_individual = MagicMock()
    new_individual.program = program
    new_individual.id = "new-id"
    new_individual.unicef_id = "IND-002"
    individual_which_loses_role = MagicMock()
    individual_which_loses_role.program = program
    individual_which_loses_role.id = "loser-id"
    individual_which_loses_role.unicef_id = "IND-001"

    with pytest.raises(ValidationError, match="was marked as duplicated"):
        _validate_role_reassignment(["loser-id", "new-id"], ROLE_PRIMARY, new_individual, individual_which_loses_role)


def test_validate_role_reassignment_passes_when_all_conditions_met():
    program = MagicMock()
    new_individual = MagicMock()
    new_individual.program = program
    new_individual.id = "new-id"
    individual_which_loses_role = MagicMock()
    individual_which_loses_role.program = program
    individual_which_loses_role.id = "loser-id"

    # Should not raise
    _validate_role_reassignment(["loser-id"], ROLE_PRIMARY, new_individual, individual_which_loses_role)
