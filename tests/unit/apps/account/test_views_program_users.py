"""Tests for program users API views."""

import datetime
import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
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
from hope.models import Program, Role

pytestmark = pytest.mark.django_db


def get_role_data(role: Role) -> dict:
    return {
        "name": role.name,
        "subsystem": role.subsystem,
        "is_visible_on_ui": role.is_visible_on_ui,
        "is_available_for_partner": role.is_available_for_partner,
    }


@pytest.fixture
def afghanistan(db: Any):
    return BusinessAreaFactory(code="0060", name="Afghanistan", slug="afghanistan", active=True)


@pytest.fixture
def program(afghanistan):
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def partner(db: Any):
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner, first_name="Alice")


@pytest.fixture
def role1(db: Any):
    return RoleFactory(
        name="TestRole1",
        permissions=[
            Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value,
            Permissions.PROGRAMME_FINISH.value,
        ],
    )


@pytest.fixture
def role2(db: Any):
    return RoleFactory(
        name="TestRole2",
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS.value],
    )


@pytest.fixture
def role3(db: Any):
    return RoleFactory(name="TestRole3", permissions=[Permissions.TARGETING_VIEW_LIST.value])


@pytest.fixture
def role_p1(db: Any):
    return RoleFactory(
        name="TestRoleP1",
        permissions=[Permissions.PM_CREATE.value, Permissions.PM_VIEW_LIST.value],
    )


@pytest.fixture
def role_p2(db: Any):
    return RoleFactory(
        name="TestRoleP2",
        permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE.value],
    )


@pytest.fixture
def role_with_user_management_permissions(db: Any):
    return RoleFactory(
        name="Role For User",
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST.value],
    )


@pytest.fixture
def partner_with_role_1(afghanistan, role_p1):
    partner = PartnerFactory(name="TestPartner1")
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, role=role_p1)
    return partner


@pytest.fixture
def partner_with_role_2(afghanistan, program, role_p2):
    partner = PartnerFactory(name="TestPartner2")
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, program=program, role=role_p2)
    return partner


@pytest.fixture
def user1(partner, afghanistan, role1):
    user = UserFactory(
        partner=partner,
        first_name="Bob",
        last_login=timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
    )
    RoleAssignmentFactory(user=user, business_area=afghanistan, role=role1)
    return user


@pytest.fixture
def user2(partner, afghanistan, program, role2):
    user = UserFactory(partner=partner, first_name="Carol")
    RoleAssignmentFactory(user=user, business_area=afghanistan, program=program, role=role2)
    return user


@pytest.fixture
def user3(partner_with_role_1):
    return UserFactory(partner=partner_with_role_1, first_name="Dave")


@pytest.fixture
def user4(partner_with_role_2):
    return UserFactory(partner=partner_with_role_2, first_name="Eve")


@pytest.fixture
def user5(partner_with_role_2, afghanistan, program, role3):
    user = UserFactory(partner=partner_with_role_2, first_name="Frank")
    RoleAssignmentFactory(user=user, business_area=afghanistan, program=program, role=role3)
    return user


@pytest.fixture
def user_without_role(partner):
    return UserFactory(partner=partner, first_name="Gina")


@pytest.fixture
def list_url(afghanistan):
    return reverse("api:accounts:users-list", kwargs={"business_area_slug": afghanistan.slug})


@pytest.fixture
def authenticated_client(api_client: Callable, user):
    return api_client(user)


def test_program_users_returns_users_with_roles_in_program(
    authenticated_client,
    user,
    afghanistan,
    program,
    partner,
    list_url: str,
    role1,
    role2,
    role3,
    role_p1,
    role_p2,
    role_with_user_management_permissions,
    user1,
    user2,
    user3,
    user4,
    user5,
    user_without_role,
):
    RoleAssignmentFactory(
        user=user,
        business_area=afghanistan,
        program=None,
        role=role_with_user_management_permissions,
    )

    response = authenticated_client.get(list_url, {"program": program.slug, "serializer": "program_users"})
    assert response.status_code == status.HTTP_200_OK

    response_results = response.data["results"]
    assert len(response_results) == 6

    for i, expected_user in enumerate([user, user1, user2, user3, user4, user5]):
        user_result = response_results[i]
        assert user_result["id"] == str(expected_user.id)
        assert user_result["username"] == expected_user.username
        assert user_result["email"] == expected_user.email
        assert user_result["first_name"] == expected_user.first_name
        assert user_result["last_name"] == expected_user.last_name
        assert user_result["is_superuser"] == expected_user.is_superuser
        assert user_result["partner"] == {
            "id": expected_user.partner.id,
            "name": expected_user.partner.name,
        }
        assert user_result["status"] == expected_user.status
        assert user_result["last_login"] == (
            f"{expected_user.last_login:%Y-%m-%dT%H:%M:%SZ}" if expected_user.last_login else None
        )

    # user
    assert response_results[0]["partner_roles"] == []
    assert response_results[0]["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role_with_user_management_permissions),
        }
    ]

    # user1
    assert response_results[1]["partner_roles"] == []
    assert response_results[1]["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role1),
        },
    ]

    # user2
    assert response_results[2]["partner_roles"] == []
    assert response_results[2]["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": program.name,
            "role": get_role_data(role2),
        },
    ]

    # user3
    assert response_results[3]["partner_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": None,
            "role": get_role_data(role_p1),
        },
    ]
    assert response_results[3]["user_roles"] == []

    # user4
    assert response_results[4]["partner_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": program.name,
            "role": get_role_data(role_p2),
        },
    ]
    assert response_results[4]["user_roles"] == []

    # user5
    assert response_results[5]["partner_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": program.name,
            "role": get_role_data(role_p2),
        }
    ]
    assert response_results[5]["user_roles"] == [
        {
            "business_area": afghanistan.slug,
            "program": program.name,
            "role": get_role_data(role3),
        },
    ]


def test_program_users_caching(
    authenticated_client: Any,
    user: Any,
    create_user_role_with_permissions: Any,
    afghanistan: Any,
    program: Any,
    list_url: str,
    user1: Any,
    user2: Any,
    user3: Any,
    user5: Any,
    partner_with_role_2: Any,
    user4: Any,
    user_without_role: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url, {"program": program.slug, "serializer": "program_users"})
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 6
        assert len(ctx.captured_queries) == 21

    # no change - use cache
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url, {"program": program.slug, "serializer": "program_users"})
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second_call = response.headers["etag"]
        assert etag == etag_second_call
        assert len(ctx.captured_queries) == 10

    user2.first_name = "Zoe"
    user2.save()
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url, {"program": program.slug, "serializer": "program_users"})
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_third_call = response.headers["etag"]
        assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
        assert etag_third_call not in [etag, etag_second_call]
        # 6 queries are saved because of cached permissions calculations
        assert len(ctx.captured_queries) == 15

    user3.delete()
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url, {"program": program.slug, "serializer": "program_users"})
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fourth_call = response.headers["etag"]
        assert len(response.json()["results"]) == 5
        assert etag_fourth_call not in [etag, etag_second_call, etag_third_call]
        assert len(ctx.captured_queries) == 15

    # no change - use cache
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url, {"program": program.slug, "serializer": "program_users"})
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fifth_call = response.headers["etag"]
        assert etag_fifth_call == etag_fourth_call
        assert len(ctx.captured_queries) == 10
