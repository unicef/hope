"""Tests for user profile API views."""

import datetime
from typing import Any

from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, Program, Role, User

pytestmark = pytest.mark.django_db


def get_role_data(role: Role) -> dict:
    return {
        "name": role.name,
        "is_visible_on_ui": role.is_visible_on_ui,
        "is_available_for_partner": role.is_available_for_partner,
    }


def get_business_area_data(business_area: BusinessArea) -> dict:
    return {
        "id": str(business_area.id),
        "name": business_area.name,
        "slug": business_area.slug,
        "is_accountability_applicable": False,
    }


def get_partner_data(partner: Partner) -> dict:
    return {
        "id": partner.id,
        "name": partner.name,
    }


def get_program_data(program: Program) -> dict:
    return {
        "id": str(program.id),
        "name": program.name,
        "slug": program.slug,
    }


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        slug="afghanistan",
        active=True,
    )


@pytest.fixture
def ukraine(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        code="1230",
        name="Ukraine",
        slug="ukraine",
        active=True,
    )


@pytest.fixture
def partner(afghanistan: BusinessArea, ukraine: BusinessArea) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(
        partner=partner,
        last_login=timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
    )


@pytest.fixture
def program1(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
    )


@pytest.fixture
def program2(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
    )


@pytest.fixture
def program3(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
    )


@pytest.fixture
def program_u(ukraine: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=ukraine,
        status=Program.ACTIVE,
    )


@pytest.fixture
def role1(db: Any) -> Role:
    return RoleFactory(
        name="TestRole1",
        permissions=[
            Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value,
            Permissions.PROGRAMME_FINISH.value,
        ],
    )


@pytest.fixture
def role2(db: Any) -> Role:
    return RoleFactory(
        name="TestRole2",
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS.value],
    )


@pytest.fixture
def role3(db: Any) -> Role:
    return RoleFactory(
        name="TestRole3",
        permissions=[Permissions.TARGETING_VIEW_LIST.value],
    )


@pytest.fixture
def role4(db: Any) -> Role:
    return RoleFactory(
        name="TestRole4",
        permissions=[Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE.value],
    )


@pytest.fixture
def role_p1(db: Any) -> Role:
    return RoleFactory(
        name="TestRoleP1",
        permissions=[Permissions.PM_CREATE.value, Permissions.PM_VIEW_LIST.value],
    )


@pytest.fixture
def role_p2(db: Any) -> Role:
    return RoleFactory(
        name="TestRoleP2",
        permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE.value],
    )


@pytest.fixture
def role_p3(db: Any) -> Role:
    return RoleFactory(
        name="TestRoleP3",
        permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST.value],
    )


@pytest.fixture
def user_role_assignments(
    user: User,
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    program1: Program,
    program2: Program,
    program3: Program,
    program_u: Program,
    role1: Role,
    role2: Role,
    role3: Role,
    role4: Role,
) -> None:
    RoleAssignmentFactory(
        user=user,
        role=role1,
        business_area=afghanistan,
    )
    RoleAssignmentFactory(
        user=user,
        role=role2,
        business_area=afghanistan,
        program=program1,
    )
    RoleAssignmentFactory(
        user=user,
        role=role3,
        business_area=afghanistan,
        program=program2,
    )
    RoleAssignmentFactory(
        user=user,
        role=role4,
        business_area=afghanistan,
        program=program3,
    )
    RoleAssignmentFactory(
        user=user,
        role=role1,
        business_area=ukraine,
        program=program_u,
    )


@pytest.fixture
def partner_role_assignments(
    partner: Partner,
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    program1: Program,
    program2: Program,
    role_p1: Role,
    role_p2: Role,
    role_p3: Role,
) -> None:
    RoleAssignmentFactory(
        partner=partner,
        role=role_p1,
        business_area=afghanistan,
    )
    RoleAssignmentFactory(
        partner=partner,
        role=role_p2,
        business_area=afghanistan,
        program=program1,
    )
    RoleAssignmentFactory(
        partner=partner,
        role=role_p3,
        business_area=afghanistan,
        program=program2,
    )
    RoleAssignmentFactory(
        partner=partner,
        role=role_p1,
        business_area=ukraine,
    )


@pytest.fixture
def user_profile_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:accounts:users-profile",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.fixture
def authenticated_client(api_client: Any, user: User):
    return api_client(user)


def test_user_profile_in_scope_business_area(
    authenticated_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    program1: Program,
    program2: Program,
    program3: Program,
    program_u: Program,
    role1: Role,
    role2: Role,
    role3: Role,
    role4: Role,
    role_p1: Role,
    role_p2: Role,
    role_p3: Role,
    user_role_assignments: None,
    partner_role_assignments: None,
    user_profile_url: str,
):
    response = authenticated_client.get(user_profile_url)
    assert response.status_code == status.HTTP_200_OK

    profile_data = response.data
    assert profile_data["id"] == str(user.id)
    assert profile_data["username"] == user.username
    assert profile_data["email"] == user.email
    assert profile_data["first_name"] == user.first_name
    assert profile_data["last_name"] == user.last_name
    assert profile_data["is_superuser"] == user.is_superuser
    assert profile_data["partner"] == {
        "id": partner.id,
        "name": partner.name,
    }
    assert profile_data["partner_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role_p1),
        },
        {
            "business_area": afghanistan.slug,
            "program": program1.name,
            "role": get_role_data(role_p2),
        },
        {
            "business_area": afghanistan.slug,
            "program": program2.name,
            "role": get_role_data(role_p3),
        },
        {
            "business_area": ukraine.slug,
            "program": None,
            "role": get_role_data(role_p1),
        },
    ]

    assert profile_data["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role1),
        },
        {
            "business_area": afghanistan.slug,
            "program": program1.name,
            "role": get_role_data(role2),
        },
        {
            "business_area": afghanistan.slug,
            "program": program2.name,
            "role": get_role_data(role3),
        },
        {
            "business_area": afghanistan.slug,
            "program": program3.name,
            "role": get_role_data(role4),
        },
        {
            "business_area": ukraine.slug,
            "program": program_u.name,
            "role": get_role_data(role1),
        },
    ]
    assert profile_data["business_areas"] == [
        {
            **get_business_area_data(afghanistan),
            "permissions": {
                str(perm)
                for perm in [
                    *role1.permissions,
                    *role2.permissions,
                    *role3.permissions,
                    *role4.permissions,
                    *role_p1.permissions,
                    *role_p2.permissions,
                    *role_p3.permissions,
                ]
            },
        },
        {
            **get_business_area_data(ukraine),
            "permissions": {
                str(perm)
                for perm in [
                    *role1.permissions,
                    *role_p1.permissions,
                ]
            },
        },
    ]

    assert profile_data["permissions_in_scope"] == {
        str(perm)
        for perm in [
            *role1.permissions,
            *role2.permissions,
            *role3.permissions,
            *role4.permissions,
            *role_p1.permissions,
            *role_p2.permissions,
            *role_p3.permissions,
        ]
    }
    assert profile_data["cross_area_filter_available"] is False

    assert profile_data["status"] == user.status
    assert profile_data["last_login"] == f"{user.last_login:%Y-%m-%dT%H:%M:%SZ}"


def test_user_profile_in_scope_program(
    authenticated_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    program1: Program,
    program2: Program,
    program3: Program,
    program_u: Program,
    role1: Role,
    role2: Role,
    role3: Role,
    role4: Role,
    role_p1: Role,
    role_p2: Role,
    role_p3: Role,
    user_role_assignments: None,
    partner_role_assignments: None,
    user_profile_url: str,
):
    response = authenticated_client.get(user_profile_url, {"program": program1.slug})
    assert response.status_code == status.HTTP_200_OK

    profile_data = response.data
    assert profile_data["id"] == str(user.id)
    assert profile_data["username"] == user.username
    assert profile_data["email"] == user.email
    assert profile_data["first_name"] == user.first_name
    assert profile_data["last_name"] == user.last_name
    assert profile_data["is_superuser"] == user.is_superuser
    assert profile_data["partner"] == {
        "id": partner.id,
        "name": partner.name,
    }

    assert profile_data["partner_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role_p1),
        },
        {
            "business_area": afghanistan.slug,
            "program": program1.name,
            "role": get_role_data(role_p2),
        },
        {
            "business_area": afghanistan.slug,
            "program": program2.name,
            "role": get_role_data(role_p3),
        },
        {
            "business_area": ukraine.slug,
            "program": None,
            "role": get_role_data(role_p1),
        },
    ]

    assert profile_data["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role1),
        },
        {
            "business_area": afghanistan.slug,
            "program": program1.name,
            "role": get_role_data(role2),
        },
        {
            "business_area": afghanistan.slug,
            "program": program2.name,
            "role": get_role_data(role3),
        },
        {
            "business_area": afghanistan.slug,
            "program": program3.name,
            "role": get_role_data(role4),
        },
        {
            "business_area": ukraine.slug,
            "program": program_u.name,
            "role": get_role_data(role1),
        },
    ]
    assert profile_data["business_areas"] == [
        {
            **get_business_area_data(afghanistan),
            "permissions": {
                str(perm)
                for perm in [
                    *role1.permissions,
                    *role2.permissions,
                    *role3.permissions,
                    *role4.permissions,
                    *role_p1.permissions,
                    *role_p2.permissions,
                    *role_p3.permissions,
                ]
            },
        },
        {
            **get_business_area_data(ukraine),
            "permissions": {
                str(perm)
                for perm in [
                    *role1.permissions,
                    *role_p1.permissions,
                ]
            },
        },
    ]

    # change here - only permissions within the program
    assert profile_data["permissions_in_scope"] == {
        str(perm)
        for perm in [
            *role1.permissions,
            *role2.permissions,
            *role_p1.permissions,
            *role_p2.permissions,
        ]
    }
    assert profile_data["cross_area_filter_available"] is False


@pytest.mark.parametrize(
    ("permissions", "filter_available"),
    [
        ([Permissions.GRIEVANCES_CROSS_AREA_FILTER], True),
        ([], False),
    ],
)
def test_cross_area_filter_available_in_scope_business_area(
    afghanistan: BusinessArea,
    user: User,
    user_profile_url: str,
    api_client: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    filter_available: bool,
):
    authenticated_client = api_client(user)
    create_user_role_with_permissions(
        user=user,
        permissions=permissions,
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(user_profile_url, {"business_area": afghanistan.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data
    assert profile_data["cross_area_filter_available"] == filter_available


@pytest.mark.parametrize(
    ("permissions", "filter_available"),
    [
        ([Permissions.GRIEVANCES_CROSS_AREA_FILTER], True),
        ([], False),
    ],
)
def test_cross_area_filter_available_in_scope_program(
    afghanistan: BusinessArea,
    user: User,
    program1: Program,
    user_profile_url: str,
    api_client: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    filter_available: bool,
):
    authenticated_client = api_client(user)
    create_user_role_with_permissions(
        user=user,
        permissions=permissions,
        business_area=afghanistan,
        program=program1,
    )

    response = authenticated_client.get(user_profile_url, {"program": program1.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data
    assert profile_data["cross_area_filter_available"] == filter_available
