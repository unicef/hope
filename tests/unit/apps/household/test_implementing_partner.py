from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Household, Program
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def other_program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def household_list_client(
    api_client: Callable, afghanistan: BusinessArea, program: Program, create_user_role_with_permissions: Callable
) -> Any:
    user = UserFactory(partner=PartnerFactory(name="TestPartner"))
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=afghanistan,
        program=program,
    )
    return api_client(user)


@pytest.fixture
def individual_list_client(
    api_client: Callable, afghanistan: BusinessArea, program: Program, create_user_role_with_permissions: Callable
) -> Any:
    user = UserFactory(partner=PartnerFactory(name="TestPartner"))
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=afghanistan,
        program=program,
    )
    return api_client(user)


@pytest.fixture
def no_permission_client(api_client: Callable) -> Any:
    return api_client(UserFactory(partner=PartnerFactory(name="TestPartner")))


@pytest.fixture
def household_list_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:households:households-list",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code},
    )


@pytest.fixture
def individual_list_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:households:individuals-list",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code},
    )


@pytest.fixture
def household_partners_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:households:households-implementing-partners",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code},
    )


@pytest.fixture
def plan_household(afghanistan: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(program=program, business_area=afghanistan, org_name_enumerator="Plan International")


@pytest.fixture
def second_plan_household(afghanistan: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(program=program, business_area=afghanistan, org_name_enumerator="Plan International")


@pytest.fixture
def care_household(afghanistan: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(program=program, business_area=afghanistan, org_name_enumerator="CARE")


@pytest.fixture
def blank_partner_household(afghanistan: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(program=program, business_area=afghanistan, org_name_enumerator="")


@pytest.fixture
def pending_household(afghanistan: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(
        program=program,
        business_area=afghanistan,
        org_name_enumerator="World Vision",
        rdi_merge_status=MergeStatusModel.PENDING,
    )


@pytest.fixture
def other_program_household(afghanistan: BusinessArea, other_program: Program) -> Household:
    return HouseholdFactory(program=other_program, business_area=afghanistan, org_name_enumerator="Save the Children")


def test_household_list_filtered_by_implementing_partner_returns_only_that_partner(
    household_list_client: Any,
    household_list_url: str,
    plan_household: Household,
    care_household: Household,
) -> None:
    response = household_list_client.get(household_list_url, {"org_name_enumerator": "Plan International"})

    assert response.status_code == status.HTTP_200_OK
    assert [row["id"] for row in response.json()["results"]] == [str(plan_household.id)]


def test_individual_list_filtered_by_implementing_partner_returns_only_that_partner(
    individual_list_client: Any,
    individual_list_url: str,
    plan_household: Household,
    care_household: Household,
) -> None:
    response = individual_list_client.get(individual_list_url, {"org_name_enumerator": "CARE"})

    assert response.status_code == status.HTTP_200_OK
    assert [row["id"] for row in response.json()["results"]] == [str(care_household.head_of_household.id)]


def test_household_implementing_partners_returns_distinct_sorted_merged_names_of_the_program(
    household_list_client: Any,
    household_partners_url: str,
    plan_household: Household,
    second_plan_household: Household,
    care_household: Household,
    blank_partner_household: Household,
    pending_household: Household,
    other_program_household: Household,
) -> None:
    response = household_list_client.get(household_partners_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"name": "CARE", "value": "CARE"},
        {"name": "Plan International", "value": "Plan International"},
    ]


def test_household_implementing_partners_with_individuals_list_permission_returns_names(
    individual_list_client: Any,
    household_partners_url: str,
    plan_household: Household,
    care_household: Household,
) -> None:
    response = individual_list_client.get(household_partners_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"name": "CARE", "value": "CARE"},
        {"name": "Plan International", "value": "Plan International"},
    ]


def test_household_implementing_partners_without_permission_is_forbidden(
    no_permission_client: Any, household_partners_url: str
) -> None:
    response = no_permission_client.get(household_partners_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
