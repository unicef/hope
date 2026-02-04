"""Tests for program update partner access API endpoint."""

from typing import Any, Callable

from django.db.models import Q
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.old_factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from extras.test_utils.old_factories.core import create_afghanistan
from extras.test_utils.old_factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.old_factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.models import AdminAreaLimitedTo, Area, BusinessArea, Country, Partner, Program, RoleAssignment, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return create_afghanistan()


@pytest.fixture
def partner(afghanistan: BusinessArea) -> Partner:
    partner = PartnerFactory(name="Test Partner")
    partner.allowed_business_areas.add(afghanistan)
    return partner


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        partner_access=Program.NONE_PARTNERS_ACCESS,
        name="Test Program for Partner Access",
    )


@pytest.fixture
def partner1_for_assignment(afghanistan: BusinessArea) -> Partner:
    partner = PartnerFactory(name="Test Partner 1")
    partner.allowed_business_areas.add(afghanistan)
    return partner


@pytest.fixture
def partner2_for_assignment(afghanistan: BusinessArea) -> Partner:
    partner = PartnerFactory(name="Test Partner 2")
    partner.allowed_business_areas.add(afghanistan)
    return partner


@pytest.fixture
def unicef_partner() -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=unicef_partner)


@pytest.fixture
def unicef_partner_in_afghanistan(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF Partner for afghanistan", parent=unicef_partner)


@pytest.fixture
def country(afghanistan: BusinessArea) -> Country:
    country = CountryFactory()
    country.business_areas.set([afghanistan])
    return country


@pytest.fixture
def area1(country) -> Area:
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, area_type=admin_type, p_code="AF01", name="Area1")


@pytest.fixture
def area2(country) -> Area:
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, area_type=admin_type, p_code="AF02", name="Area2")


@pytest.fixture
def partners_with_role_assignments(
    partner: Partner, partner1_for_assignment: Partner, partner2_for_assignment: Partner, afghanistan: BusinessArea
) -> Partner:
    # TODO: due to temporary solution in program mutations,
    # Partners need to already have a role in the BA to be able to be granted access to program
    # (created role in program is the same role as the Partner already held in the BA.
    # For each held role, the same role is now applied for the new program.
    # After removing this solution, below lines of setup can be deleted.
    # The Role for RoleAssignment will be passed in input.
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, program=None)
    RoleAssignmentFactory(partner=partner1_for_assignment, business_area=afghanistan, program=None)
    RoleAssignmentFactory(partner=partner2_for_assignment, business_area=afghanistan, program=None)
    return partner


@pytest.fixture
def update_partner_access_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:programs:programs-update-partner-access",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "slug": program.slug,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def base_expected_response(
    partner: Partner,
    unicef_hq: Partner,
    unicef_partner_in_afghanistan: Partner,
    area1: Area,
    area2: Area,
) -> dict:
    return {
        "partners": [
            {
                "id": partner.id,
                "name": partner.name,
                "areas": [
                    {
                        "id": str(area1.id),
                        "level": area1.level,
                    },
                    {
                        "id": str(area2.id),
                        "level": area2.level,
                    },
                ],
                "area_access": "BUSINESS_AREA",
            },
            {
                "id": unicef_hq.id,
                "name": unicef_hq.name,
                "areas": [
                    {
                        "id": str(area1.id),
                        "level": area1.level,
                    },
                    {
                        "id": str(area2.id),
                        "level": area2.level,
                    },
                ],
                "area_access": "BUSINESS_AREA",
            },
            {
                "id": unicef_partner_in_afghanistan.id,
                "name": unicef_partner_in_afghanistan.name,
                "areas": [
                    {
                        "id": str(area1.id),
                        "level": area1.level,
                    },
                    {
                        "id": str(area2.id),
                        "level": area2.level,
                    },
                ],
                "area_access": "BUSINESS_AREA",
            },
        ],
    }


def test_update_partner_access_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    partner: Partner,
    partner1_for_assignment: Partner,
    partner2_for_assignment: Partner,
    partners_with_role_assignments: Partner,
    update_partner_access_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PROGRAMME_UPDATE], afghanistan, whole_business_area_access=True
    )
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0

    payload = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
    response = authenticated_client.post(update_partner_access_url, payload)
    assert response.status_code == status.HTTP_200_OK

    program.refresh_from_db()
    assert program.partner_access == Program.ALL_PARTNERS_ACCESS
    assert response.json() == {"message": "Partner access updated."}
    assert (
        program.role_assignments.count() == 3
    )  # roles created for partner, partner1_for_assignment, partner2_for_assignment
    assert set(program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner1_for_assignment.id,
        partner2_for_assignment.id,
    }


def test_update_partner_access_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    partners_with_role_assignments: Partner,
    update_partner_access_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [], afghanistan, whole_business_area_access=True)
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0

    payload = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
    response = authenticated_client.post(update_partner_access_url, payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    program.refresh_from_db()
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS  # Should not change if permission denied


def test_update_partner_access(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    partner: Partner,
    partner1_for_assignment: Partner,
    partner2_for_assignment: Partner,
    partners_with_role_assignments: Partner,
    unicef_hq: Partner,
    unicef_partner_in_afghanistan: Partner,
    area1: Area,
    area2: Area,
    update_partner_access_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0
    # UNICEF HQ and UNICEF Partner for Afghanistan have Role in the whole BA
    assert (
        RoleAssignment.objects.filter(
            Q(partner=unicef_hq) | Q(partner=unicef_partner_in_afghanistan),
            business_area=afghanistan,
            program=None,
        ).count()
        == 2
    )
    assert (
        unicef_hq.role_assignments.filter(program=None, business_area=program.business_area).first().role.name
        == "Role with all permissions"
    )
    assert (
        unicef_partner_in_afghanistan.role_assignments.filter(program=None, business_area=program.business_area)
        .first()
        .role.name
        == "Role for UNICEF Partners"
    )

    # Update partner access NONE_PARTNERS_ACCESS -> ALL_PARTNERS_ACCESS
    payload_1 = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
    response = authenticated_client.post(update_partner_access_url, payload_1)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Partner access updated."}
    program.refresh_from_db()
    assert program.partner_access == Program.ALL_PARTNERS_ACCESS
    assert program.role_assignments.count() == 3
    assert set(program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner1_for_assignment.id,
        partner2_for_assignment.id,
    }

    # Update partner access ALL_PARTNERS_ACCESS -> NONE_PARTNERS_ACCESS
    payload_2 = {"partner_access": Program.NONE_PARTNERS_ACCESS, "partners": []}
    response = authenticated_client.post(update_partner_access_url, payload_2)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Partner access updated."}
    program.refresh_from_db()
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0

    # Update partner access NONE_PARTNERS_ACCESS -> SELECTED_PARTNERS_ACCESS with specific partners
    payload_3 = {
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        "partners": [
            {
                "partner": str(partner.id),
                "areas": [str(area1.id)],
            },
            {
                "partner": str(partner1_for_assignment.id),
                "areas": [],
            },
        ],
    }
    response = authenticated_client.post(update_partner_access_url, payload_3)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Partner access updated."}
    program.refresh_from_db()
    assert program.partner_access == Program.SELECTED_PARTNERS_ACCESS
    assert program.role_assignments.count() == 2
    assert set(program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner1_for_assignment.id,
    }
    assert AdminAreaLimitedTo.objects.filter(program=program).count() == 1
    assert AdminAreaLimitedTo.objects.filter(partner=partner, program=program).count() == 1
    assert AdminAreaLimitedTo.objects.filter(partner=partner1_for_assignment, program=program).count() == 0

    # Update partners for SELECTED_PARTNERS_ACCESS - add partner, change areas
    payload_4 = {
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        "partners": [
            {
                "partner": str(partner.id),
                "areas": [str(area2.id)],
            },
            {
                "partner": str(partner1_for_assignment.id),
                "areas": [str(area2.id)],
            },
            {
                "partner": str(partner2_for_assignment.id),
                "areas": [],
            },
        ],
    }
    response = authenticated_client.post(update_partner_access_url, payload_4)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Partner access updated."}
    program.refresh_from_db()
    assert program.partner_access == Program.SELECTED_PARTNERS_ACCESS
    assert program.role_assignments.count() == 3
    assert set(program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner1_for_assignment.id,
        partner2_for_assignment.id,
    }
    assert AdminAreaLimitedTo.objects.filter(program=program).count() == 2
    assert AdminAreaLimitedTo.objects.filter(partner=partner, program=program).count() == 1
    assert AdminAreaLimitedTo.objects.filter(partner=partner1_for_assignment, program=program).count() == 1
    assert AdminAreaLimitedTo.objects.filter(partner=partner2_for_assignment, program=program).count() == 0

    # Update partners and areas for SELECTED_PARTNERS_ACCESS - remove one of partners, change areas
    payload_5 = {
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        "partners": [
            {
                "partner": str(partner.id),
                "areas": [str(area2.id)],
            },
            {
                "partner": str(partner1_for_assignment.id),
                "areas": [str(area2.id)],
            },
        ],
    }
    response = authenticated_client.post(update_partner_access_url, payload_5)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Partner access updated."}
    program.refresh_from_db()
    assert program.partner_access == Program.SELECTED_PARTNERS_ACCESS
    assert program.role_assignments.count() == 2
    assert set(program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner1_for_assignment.id,
    }
    assert AdminAreaLimitedTo.objects.filter(program=program).count() == 2
    assert AdminAreaLimitedTo.objects.filter(partner=partner, program=program).count() == 1
    assert AdminAreaLimitedTo.objects.filter(partner=partner1_for_assignment, program=program).count() == 1
    assert AdminAreaLimitedTo.objects.filter(partner=partner2_for_assignment, program=program).count() == 0

    # Update partner access SELECTED_PARTNERS_ACCESS -> ALL_PARTNERS_ACCESS
    payload_6 = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
    response = authenticated_client.post(update_partner_access_url, payload_6)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Partner access updated."}
    program.refresh_from_db()
    assert program.partner_access == Program.ALL_PARTNERS_ACCESS
    assert program.role_assignments.count() == 3
    assert set(program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner1_for_assignment.id,
        partner2_for_assignment.id,
    }
    assert AdminAreaLimitedTo.objects.filter(program=program).count() == 0


def test_update_partner_access_invalid_all_partners_access_with_partners_data(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    partner: Partner,
    partner1_for_assignment: Partner,
    partner2_for_assignment: Partner,
    partners_with_role_assignments: Partner,
    unicef_hq: Partner,
    unicef_partner_in_afghanistan: Partner,
    area2: Area,
    update_partner_access_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0

    payload = {
        "partner_access": Program.ALL_PARTNERS_ACCESS,
        "partners": [
            {
                "partner": str(partner1_for_assignment.id),
                "areas": [str(area2.id)],
            },
        ],
    }
    response = authenticated_client.post(update_partner_access_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "partners" in response.json()
    assert response.json()["partners"][0] == "You cannot specify partners for the chosen access type."

    program.refresh_from_db()
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0


def test_update_partner_access_invalid_none_partners_access_with_partners_data(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    partner: Partner,
    partner1_for_assignment: Partner,
    partner2_for_assignment: Partner,
    partners_with_role_assignments: Partner,
    unicef_hq: Partner,
    unicef_partner_in_afghanistan: Partner,
    area2: Area,
    update_partner_access_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0

    payload = {
        "partner_access": Program.NONE_PARTNERS_ACCESS,
        "partners": [
            {
                "partner": str(partner1_for_assignment.id),
                "areas": [str(area2.id)],
            },
        ],
    }
    response = authenticated_client.post(update_partner_access_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "partners" in response.json()
    assert response.json()["partners"][0] == "You cannot specify partners for the chosen access type."

    program.refresh_from_db()
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0


def test_update_partner_access_invalid_selected_partner_access_without_partner(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    partner: Partner,
    partner1_for_assignment: Partner,
    partner2_for_assignment: Partner,
    partners_with_role_assignments: Partner,
    unicef_hq: Partner,
    unicef_partner_in_afghanistan: Partner,
    area2: Area,
    update_partner_access_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0

    # Update partner access NONE_PARTNERS_ACCESS -> SELECTED_PARTNERS_ACCESS without the current partner
    payload = {
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        "partners": [
            {
                "partner": str(partner1_for_assignment.id),
                "areas": [str(area2.id)],
            },
        ],
    }
    response = authenticated_client.post(update_partner_access_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "partners" in response.json()
    assert response.json()["partners"][0] == "Please assign access to your partner before saving the Program."

    program.refresh_from_db()
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0


def test_update_partner_access_all_partners_refresh(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    partner: Partner,
    partner1_for_assignment: Partner,
    partner2_for_assignment: Partner,
    partners_with_role_assignments: Partner,
    unicef_hq: Partner,
    unicef_partner_in_afghanistan: Partner,
    update_partner_access_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0

    # Update partner access NONE_PARTNERS_ACCESS -> ALL_PARTNERS_ACCESS
    payload = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
    response = authenticated_client.post(update_partner_access_url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Partner access updated."}
    program.refresh_from_db()
    assert program.partner_access == Program.ALL_PARTNERS_ACCESS
    assert program.role_assignments.count() == 3

    # new partner allowed in BA
    partner_new = PartnerFactory(name="Test Partner New")
    partner_new.allowed_business_areas.add(afghanistan)

    # TODO: temporary solution to remove below
    RoleAssignmentFactory(partner=partner_new, business_area=afghanistan, program=None)
    # TODO: remove above when the partners access in program actions is implemented properly

    response = authenticated_client.post(update_partner_access_url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Partner access updated."}
    program.refresh_from_db()
    assert program.partner_access == Program.ALL_PARTNERS_ACCESS
    assert program.role_assignments.count() == 4
    assert set(program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner1_for_assignment.id,
        partner2_for_assignment.id,
        partner_new.id,
    }
