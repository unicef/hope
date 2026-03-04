"""Tests for partner for grievance choices API views."""

from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Household, Individual, Partner, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        slug="afghanistan",
        active=True,
    )


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(name="Test Program", status=Program.DRAFT, business_area=afghanistan)


@pytest.fixture
def program_for_household(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        name="Test Program for Household",
        status=Program.DRAFT,
        business_area=afghanistan,
    )


@pytest.fixture
def household(afghanistan: BusinessArea, program_for_household: Program) -> Household:
    return HouseholdFactory(
        business_area=afghanistan,
        program=program_for_household,
    )


@pytest.fixture
def individual(household: Household) -> Individual:
    return IndividualFactory(
        business_area=household.business_area,
        program=household.program,
        household=household,
    )


@pytest.fixture
def unicef_structure(db: Any) -> dict:
    partner_unicef = PartnerFactory(name="UNICEF")
    unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner_unicef)
    unicef_partner_for_afghanistan = PartnerFactory(name="UNICEF Partner for afghanistan", parent=partner_unicef)
    return {
        "unicef_hq": unicef_hq,
        "unicef_partner_for_afghanistan": unicef_partner_for_afghanistan,
    }


@pytest.fixture
def unicef_user(unicef_structure: dict) -> User:
    return UserFactory(partner=unicef_structure["unicef_hq"], username="unicef_user")


@pytest.fixture
def partner_with_access_to_test_program(
    afghanistan: BusinessArea, program: Program, create_partner_role_with_permissions: Any
) -> Partner:
    """Partner with access to Test Program.

    Should be returned if Program is passed or if neither program nor
    household/individual is passed (because it has access to ANY program in this BA).
    """
    partner = PartnerFactory(name="Partner with access to Test Program")
    create_partner_role_with_permissions(partner, [], afghanistan, program)
    return partner


@pytest.fixture
def partner_with_access_to_test_program_for_hh(
    afghanistan: BusinessArea, program_for_household: Program, create_partner_role_with_permissions: Any
) -> Partner:
    """Partner with access to Test Program for Household.

    Should be returned if Program is not passed and household/individual is passed
    or if neither program nor household/individual is passed
    (because it has access to ANY program in this BA).
    """
    partner = PartnerFactory(name="Partner with access to Test Program for Household")
    create_partner_role_with_permissions(partner, [], afghanistan, program_for_household)
    return partner


@pytest.fixture
def partner_with_access_to_all_programs(
    afghanistan: BusinessArea, create_partner_role_with_permissions: Any
) -> Partner:
    """Partner with access to all programs.

    Should be returned if neither program nor household/individual is passed
    or if any program is passed or if household/individual is passed
    (because it has access to all programs in this BA).
    """
    partner = PartnerFactory(name="Partner with access to All Programs")
    create_partner_role_with_permissions(partner, [], afghanistan, whole_business_area_access=True)
    return partner


@pytest.fixture
def partner_without_program_access(db: Any) -> Partner:
    """Partner without access to any program in this BA.

    Should not be returned in any case.
    """
    return PartnerFactory(name="Partner Without Program Access")


@pytest.fixture
def partner_for_grievance_choices_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:accounts:users-partner-for-grievance-choices",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.fixture
def authenticated_client(api_client: Any, unicef_user: User) -> Any:
    return api_client(unicef_user)


def test_get_partner_for_grievance_choices_for_program(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    unicef_user: User,
    program: Program,
    partner_for_grievance_choices_url: str,
    partner_with_access_to_test_program: Partner,
    partner_with_access_to_all_programs: Partner,
    unicef_structure: dict,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=unicef_user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(
        partner_for_grievance_choices_url,
        {"program": program.slug},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        {
            "name": partner_with_access_to_all_programs.name,
            "value": partner_with_access_to_all_programs.id,
        },
        {
            "name": partner_with_access_to_test_program.name,
            "value": partner_with_access_to_test_program.id,
        },
        {"name": unicef_structure["unicef_hq"].name, "value": unicef_structure["unicef_hq"].id},
        {
            "name": unicef_structure["unicef_partner_for_afghanistan"].name,
            "value": unicef_structure["unicef_partner_for_afghanistan"].id,
        },
    ]


def test_get_partner_for_grievance_choices_for_household(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    unicef_user: User,
    household: Household,
    partner_for_grievance_choices_url: str,
    partner_with_access_to_test_program_for_hh: Partner,
    partner_with_access_to_all_programs: Partner,
    unicef_structure: dict,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=unicef_user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(
        partner_for_grievance_choices_url,
        {"household": household.pk},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        {
            "name": partner_with_access_to_all_programs.name,
            "value": partner_with_access_to_all_programs.id,
        },
        {
            "name": partner_with_access_to_test_program_for_hh.name,
            "value": partner_with_access_to_test_program_for_hh.id,
        },
        {"name": unicef_structure["unicef_hq"].name, "value": unicef_structure["unicef_hq"].id},
        {
            "name": unicef_structure["unicef_partner_for_afghanistan"].name,
            "value": unicef_structure["unicef_partner_for_afghanistan"].id,
        },
    ]


def test_get_partner_for_grievance_choices_for_individual(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    unicef_user: User,
    individual: Individual,
    partner_for_grievance_choices_url: str,
    partner_with_access_to_test_program_for_hh: Partner,
    partner_with_access_to_all_programs: Partner,
    unicef_structure: dict,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=unicef_user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(
        partner_for_grievance_choices_url,
        {"individual": individual.pk},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        {
            "name": partner_with_access_to_all_programs.name,
            "value": partner_with_access_to_all_programs.id,
        },
        {
            "name": partner_with_access_to_test_program_for_hh.name,
            "value": partner_with_access_to_test_program_for_hh.id,
        },
        {"name": unicef_structure["unicef_hq"].name, "value": unicef_structure["unicef_hq"].id},
        {
            "name": unicef_structure["unicef_partner_for_afghanistan"].name,
            "value": unicef_structure["unicef_partner_for_afghanistan"].id,
        },
    ]


def test_get_partner_for_grievance_choices_without_params(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    unicef_user: User,
    partner_for_grievance_choices_url: str,
    partner_with_access_to_test_program: Partner,
    partner_with_access_to_test_program_for_hh: Partner,
    partner_with_access_to_all_programs: Partner,
    unicef_structure: dict,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=unicef_user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(partner_for_grievance_choices_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        {
            "name": partner_with_access_to_all_programs.name,
            "value": partner_with_access_to_all_programs.id,
        },
        {
            "name": partner_with_access_to_test_program.name,
            "value": partner_with_access_to_test_program.id,
        },
        {
            "name": partner_with_access_to_test_program_for_hh.name,
            "value": partner_with_access_to_test_program_for_hh.id,
        },
        {"name": unicef_structure["unicef_hq"].name, "value": unicef_structure["unicef_hq"].id},
        {
            "name": unicef_structure["unicef_partner_for_afghanistan"].name,
            "value": unicef_structure["unicef_partner_for_afghanistan"].id,
        },
    ]
