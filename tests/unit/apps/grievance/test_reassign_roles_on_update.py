from typing import Any

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
from hope.apps.grievance.services.reassign_roles_services import reassign_roles_on_update_service
from hope.apps.household.const import HEAD, ROLE_ALTERNATE, ROLE_PRIMARY
from hope.models import IndividualRoleInHousehold

pytestmark = pytest.mark.django_db


@pytest.fixture
def base_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    program = ProgramFactory(name="Test program ONE", business_area=business_area)
    user = UserFactory()

    household = HouseholdFactory(
        program=program,
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
        program=program,
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
        program=program,
        business_area=business_area,
        registration_data_import=household.registration_data_import,
    )

    return {
        "business_area": business_area,
        "program": program,
        "user": user,
        "household": household,
        "primary_collector_individual": primary_collector_individual,
        "primary_role": primary_role,
        "alternate_collector_individual": alternate_collector_individual,
        "alternate_role": alternate_role,
        "no_role_individual": no_role_individual,
    }


def test_reassign_role_to_another_individual(base_context: dict[str, Any]) -> None:
    household = base_context["household"]
    program = base_context["program"]
    business_area = base_context["business_area"]
    individual = IndividualFactory(
        household=household,
        program=program,
        business_area=business_area,
        registration_data_import=household.registration_data_import,
    )

    role_reassign_data = {
        "HEAD": {
            "role": "HEAD",
            "household": str(household.id),
            "individual": str(individual.id),
        },
        str(base_context["primary_role"].id): {
            "role": "PRIMARY",
            "household": str(household.id),
            "individual": str(individual.id),
        },
    }

    reassign_roles_on_update_service(
        base_context["primary_collector_individual"],
        role_reassign_data,
        base_context["user"],
        program,
    )

    individual.refresh_from_db()
    household.refresh_from_db()
    assert household.head_of_household == individual
    assert individual.relationship == HEAD
    role = IndividualRoleInHousehold.objects.get(household=household, individual=individual).role
    assert role == ROLE_PRIMARY


def test_reassign_alternate_role_to_primary_collector(base_context: dict[str, Any]) -> None:
    household = base_context["household"]
    role_reassign_data = {
        str(base_context["alternate_role"].id): {
            "role": "ALTERNATE",
            "household": str(household.id),
            "individual": str(base_context["primary_collector_individual"].id),
        },
    }

    with pytest.raises(ValidationError, match="Cannot reassign the role"):
        reassign_roles_on_update_service(
            base_context["alternate_collector_individual"],
            role_reassign_data,
            base_context["user"],
            base_context["program"],
        )


def test_reassign_alternate_role(base_context: dict[str, Any]) -> None:
    household = base_context["household"]
    program = base_context["program"]
    business_area = base_context["business_area"]
    individual = IndividualFactory(
        household=household,
        program=program,
        business_area=business_area,
        registration_data_import=household.registration_data_import,
    )

    role_reassign_data = {
        str(base_context["alternate_role"].id): {
            "role": "ALTERNATE",
            "household": str(household.id),
            "individual": str(individual.id),
        },
    }

    reassign_roles_on_update_service(
        base_context["alternate_collector_individual"],
        role_reassign_data,
        base_context["user"],
        program,
    )
    role = IndividualRoleInHousehold.objects.get(household=household, individual=individual).role
    assert role == ROLE_ALTERNATE


def test_reassign_primary_role_to_current_alternate_collector(base_context: dict[str, Any]) -> None:
    household = base_context["household"]
    role_reassign_data = {
        str(base_context["primary_role"].id): {
            "role": "PRIMARY",
            "household": household.id,
            "individual": base_context["alternate_collector_individual"].id,
        },
    }

    reassign_roles_on_update_service(
        base_context["primary_collector_individual"],
        role_reassign_data,
        base_context["user"],
        base_context["program"],
    )

    role = IndividualRoleInHousehold.objects.get(
        household=household,
        individual=base_context["alternate_collector_individual"],
    ).role
    assert role == ROLE_PRIMARY

    previous_role = IndividualRoleInHousehold.objects.filter(household=household, role=ROLE_ALTERNATE).first()
    assert previous_role is None


def test_reassign_alternate_role_to_individual_with_primary_role_in_another_household(
    base_context: dict[str, Any],
) -> None:
    program = base_context["program"]
    business_area = base_context["business_area"]
    household = base_context["household"]
    external_household = HouseholdFactory(
        program=program,
        business_area=business_area,
        create_role=False,
    )
    IndividualRoleInHouseholdFactory(
        household=external_household,
        individual=base_context["no_role_individual"],
        role=ROLE_PRIMARY,
    )

    role_reassign_data = {
        str(base_context["alternate_role"].id): {
            "role": "ALTERNATE",
            "household": str(household.id),
            "individual": str(base_context["no_role_individual"].id),
        },
    }

    reassign_roles_on_update_service(
        base_context["alternate_collector_individual"],
        role_reassign_data,
        base_context["user"],
        program,
    )

    role = IndividualRoleInHousehold.objects.get(
        household=household,
        individual=base_context["no_role_individual"],
    ).role
    assert role == ROLE_ALTERNATE

    external_role = IndividualRoleInHousehold.objects.get(
        household=external_household,
        individual=base_context["no_role_individual"],
    ).role
    assert external_role == ROLE_PRIMARY
