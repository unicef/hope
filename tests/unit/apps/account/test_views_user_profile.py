"""Tests for user profile API views."""

from typing import Any

import pytest
from rest_framework import status

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
        "subsystem": role.subsystem,
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
def user_profile_setup(api_client: Any) -> dict:
    afghanistan = BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        slug="afghanistan",
    )
    ukraine = BusinessAreaFactory(
        code="1230",
        name="Ukraine",
        slug="ukraine",
    )

    partner = PartnerFactory(name="TestPartner")
    partner.allowed_business_areas.add(afghanistan, ukraine)

    user = UserFactory(partner=partner)

    program1 = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
    )
    program2 = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
    )
    program3 = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
    )
    program_u = ProgramFactory(
        business_area=ukraine,
        status=Program.ACTIVE,
    )

    role1 = RoleFactory(
        name="Role with ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW",
        permissions=[Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
    )
    role2 = RoleFactory(
        name="Role with ACTIVITY_LOG_VIEW",
        permissions=[Permissions.ACTIVITY_LOG_VIEW.value],
    )
    role3 = RoleFactory(
        name="Role with PM_VIEW_LIST",
        permissions=[Permissions.PM_VIEW_LIST.value],
    )
    role4 = RoleFactory(
        name="Role with ACTIVITY_LOG_CREATE",
        permissions=[Permissions.ACTIVITY_LOG_CREATE.value],
    )

    role_p1 = RoleFactory(
        name="Partner Role with ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW",
        permissions=[Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
        is_available_for_partner=True,
    )
    role_p2 = RoleFactory(
        name="Partner Role with ACTIVITY_LOG_VIEW",
        permissions=[Permissions.ACTIVITY_LOG_VIEW.value],
        is_available_for_partner=True,
    )
    role_p3 = RoleFactory(
        name="Partner Role with PM_VIEW_LIST",
        permissions=[Permissions.PM_VIEW_LIST.value],
        is_available_for_partner=True,
    )

    # User role assignments (assigned to user)
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
        business_area=ukraine,
    )

    # Partner role assignments (assigned to partner)
    RoleAssignmentFactory(
        partner=partner,
        role=role_p1,
        business_area=afghanistan,
    )
    RoleAssignmentFactory(
        partner=partner,
        role=role_p2,
        business_area=afghanistan,
        program=program3,
    )
    RoleAssignmentFactory(
        partner=partner,
        role=role_p3,
        business_area=ukraine,
    )

    return {
        "api_client": api_client(user),
        "user_profile_url": "api:accounts:users-profile",
        "user": user,
        "partner": partner,
        "afghanistan": afghanistan,
        "ukraine": ukraine,
        "program1": program1,
        "program2": program2,
        "program3": program3,
        "program_u": program_u,
        "role1": role1,
        "role2": role2,
        "role3": role3,
        "role4": role4,
        "role_p1": role_p1,
        "role_p2": role_p2,
        "role_p3": role_p3,
    }


def test_user_profile_in_scope_business_area(user_profile_setup: dict):
    api_client = user_profile_setup["api_client"]
    user_profile_url = user_profile_setup["user_profile_url"]
    user = user_profile_setup["user"]
    partner = user_profile_setup["partner"]
    afghanistan = user_profile_setup["afghanistan"]
    ukraine = user_profile_setup["ukraine"]
    program1 = user_profile_setup["program1"]
    program2 = user_profile_setup["program2"]
    program3 = user_profile_setup["program3"]
    program_u = user_profile_setup["program_u"]
    role1 = user_profile_setup["role1"]
    role2 = user_profile_setup["role2"]
    role3 = user_profile_setup["role3"]
    role4 = user_profile_setup["role4"]
    role_p1 = user_profile_setup["role_p1"]
    role_p2 = user_profile_setup["role_p2"]
    role_p3 = user_profile_setup["role_p3"]

    response = api_client.get(user_profile_url)
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
            "permissions_in_role": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
        },
        {
            "business_area": afghanistan.slug,
            "program": program3.slug,
            "role": get_role_data(role_p2),
            "permissions_in_role": [Permissions.ACTIVITY_LOG_VIEW.value],
        },
        {
            "business_area": ukraine.slug,
            "program": None,
            "role": get_role_data(role_p3),
            "permissions_in_role": [Permissions.PM_VIEW_LIST.value],
        },
    ]

    assert profile_data["custom_fields"] is not None
    assert profile_data["allowed_business_areas"] == [
        get_business_area_data(afghanistan),
        get_business_area_data(ukraine),
    ]

    # Business area (Afghanistan) filter
    response = api_client.get(user_profile_url, {"business_area": afghanistan.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data

    assert profile_data["roles_details"] == [
        {
            "business_area": get_business_area_data(afghanistan),
            "program": None,
            "role": get_role_data(role1),
            "permissions_in_role": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
            "expiry_date": None,
        },
        {
            "business_area": get_business_area_data(afghanistan),
            "program": get_program_data(program1),
            "role": get_role_data(role2),
            "permissions_in_role": [Permissions.ACTIVITY_LOG_VIEW.value],
            "expiry_date": None,
        },
        {
            "business_area": get_business_area_data(afghanistan),
            "program": get_program_data(program2),
            "role": get_role_data(role3),
            "permissions_in_role": [Permissions.PM_VIEW_LIST.value],
            "expiry_date": None,
        },
    ]

    assert profile_data["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role1),
            "permissions_in_role": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
        },
        {
            "business_area": afghanistan.slug,
            "program": program1.slug,
            "role": get_role_data(role2),
            "permissions_in_role": [Permissions.ACTIVITY_LOG_VIEW.value],
        },
        {
            "business_area": afghanistan.slug,
            "program": program2.slug,
            "role": get_role_data(role3),
            "permissions_in_role": [Permissions.PM_VIEW_LIST.value],
        },
    ]
    assert set(profile_data["available_permissions"]) == {
        Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value,
        Permissions.ACTIVITY_LOG_VIEW.value,
        Permissions.PM_VIEW_LIST.value,
    }

    # Ukraine filter
    response = api_client.get(user_profile_url, {"business_area": ukraine.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data
    assert profile_data["user_roles"] == [
        {
            "business_area": ukraine.slug,
            "program": None,
            "role": get_role_data(role4),
            "permissions_in_role": [Permissions.ACTIVITY_LOG_CREATE.value],
        },
    ]


def test_user_profile_in_scope_program(user_profile_setup: dict):
    api_client = user_profile_setup["api_client"]
    user_profile_url = user_profile_setup["user_profile_url"]
    user = user_profile_setup["user"]
    partner = user_profile_setup["partner"]
    afghanistan = user_profile_setup["afghanistan"]
    ukraine = user_profile_setup["ukraine"]
    program1 = user_profile_setup["program1"]
    program2 = user_profile_setup["program2"]
    program3 = user_profile_setup["program3"]
    program_u = user_profile_setup["program_u"]
    role1 = user_profile_setup["role1"]
    role2 = user_profile_setup["role2"]
    role3 = user_profile_setup["role3"]
    role4 = user_profile_setup["role4"]
    role_p1 = user_profile_setup["role_p1"]
    role_p2 = user_profile_setup["role_p2"]
    role_p3 = user_profile_setup["role_p3"]

    # Program filter
    response = api_client.get(user_profile_url, {"program": program1.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data

    assert profile_data["roles_details"] == [
        {
            "business_area": get_business_area_data(afghanistan),
            "program": None,
            "role": get_role_data(role1),
            "permissions_in_role": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
            "expiry_date": None,
        },
        {
            "business_area": get_business_area_data(afghanistan),
            "program": get_program_data(program1),
            "role": get_role_data(role2),
            "permissions_in_role": [Permissions.ACTIVITY_LOG_VIEW.value],
            "expiry_date": None,
        },
    ]

    assert profile_data["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role1),
            "permissions_in_role": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
        },
        {
            "business_area": afghanistan.slug,
            "program": program1.slug,
            "role": get_role_data(role2),
            "permissions_in_role": [Permissions.ACTIVITY_LOG_VIEW.value],
        },
    ]
    assert set(profile_data["available_permissions"]) == {
        Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value,
        Permissions.ACTIVITY_LOG_VIEW.value,
    }

    # Program2 filter
    response = api_client.get(user_profile_url, {"program": program2.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data
    assert profile_data["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role1),
            "permissions_in_role": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
        },
        {
            "business_area": afghanistan.slug,
            "program": program2.slug,
            "role": get_role_data(role3),
            "permissions_in_role": [Permissions.PM_VIEW_LIST.value],
        },
    ]

    # Program3 filter
    response = api_client.get(user_profile_url, {"program": program3.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data
    assert profile_data["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role1),
            "permissions_in_role": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW.value],
        },
    ]


@pytest.mark.parametrize(
    ("role_permissions", "filter_available"),
    [
        ([Permissions.CROSS_AREA_FILTER.value], True),
        ([], False),
    ],
)
def test_cross_area_filter_available_in_scope_business_area(
    api_client: Any, role_permissions: list, filter_available: bool
):
    afghanistan = BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        slug="afghanistan",
    )
    partner = PartnerFactory(name="TestPartner")
    partner.allowed_business_areas.add(afghanistan)

    user = UserFactory(partner=partner)
    role1 = RoleFactory(
        name="Role with CROSS_AREA_FILTER",
        permissions=role_permissions,
    )

    RoleAssignmentFactory(
        user=user,
        role=role1,
        business_area=afghanistan,
    )

    api_client = api_client(user)
    user_profile_url = "api:accounts:users-profile"

    response = api_client.get(user_profile_url, {"business_area": afghanistan.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data
    assert profile_data["cross_area_filter_available"] == filter_available


@pytest.mark.parametrize(
    ("role_permissions", "filter_available"),
    [
        ([Permissions.CROSS_AREA_FILTER.value], True),
        ([], False),
    ],
)
def test_cross_area_filter_available_in_scope_program(
    api_client: Any, role_permissions: list, filter_available: bool
):
    afghanistan = BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        slug="afghanistan",
    )
    partner = PartnerFactory(name="TestPartner")
    partner.allowed_business_areas.add(afghanistan)

    user = UserFactory(partner=partner)
    program1 = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
    )
    role1 = RoleFactory(
        name="Role with CROSS_AREA_FILTER",
        permissions=role_permissions,
    )

    RoleAssignmentFactory(
        user=user,
        role=role1,
        business_area=afghanistan,
        program=program1,
    )

    api_client = api_client(user)
    user_profile_url = "api:accounts:users-profile"

    response = api_client.get(user_profile_url, {"program": program1.slug})
    assert response.status_code == status.HTTP_200_OK
    profile_data = response.data
    assert profile_data["cross_area_filter_available"] == filter_available

