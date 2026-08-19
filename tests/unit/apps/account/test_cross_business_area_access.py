"""Cross business area scoping of the partner choices lookup (GHSA-2xf8-jjc2-9pmv).

The business area comes from the url path, the beneficiary that names the program comes as a
global id in the query.
"""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Household, Individual, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def attacker_business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def attacker(attacker_business_area: BusinessArea, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.USER_MANAGEMENT_VIEW_LIST],
        attacker_business_area,
        whole_business_area_access=True,
    )
    return user


@pytest.fixture
def authenticated_client(api_client: Callable, attacker: User) -> Any:
    return api_client(attacker)


@pytest.fixture
def victim_program() -> Program:
    return ProgramFactory(business_area=BusinessAreaFactory(name="Ukraine", slug="ukraine"))


@pytest.fixture
def victim_household(victim_program: Program) -> Household:
    return HouseholdFactory(business_area=victim_program.business_area, program=victim_program, create_role=False)


@pytest.fixture
def victim_individual(victim_household: Household) -> Individual:
    return IndividualFactory(
        business_area=victim_household.business_area,
        program=victim_household.program,
        household=victim_household,
    )


@pytest.fixture
def url(attacker_business_area: BusinessArea) -> str:
    return reverse(
        "api:accounts:users-partner-for-grievance-choices",
        kwargs={"business_area_slug": attacker_business_area.slug},
    )


def test_partner_choices_for_household_of_other_business_area_is_denied(
    authenticated_client: Any, url: str, victim_household: Household
) -> None:
    response = authenticated_client.get(url, {"household": str(victim_household.id)})

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_partner_choices_for_individual_of_other_business_area_is_denied(
    authenticated_client: Any, url: str, victim_individual: Individual
) -> None:
    response = authenticated_client.get(url, {"individual": str(victim_individual.id)})

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
