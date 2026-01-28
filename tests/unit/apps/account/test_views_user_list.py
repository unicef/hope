"""Tests for user list API views."""

import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
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
from hope.apps.account.permissions import ALL_GRIEVANCES_CREATE_MODIFY, Permissions
from hope.models import Partner, Program, Role, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> Any:
    return BusinessAreaFactory(code="0060", name="Afghanistan", slug="afghanistan", active=True)


@pytest.fixture
def ukraine(db: Any) -> Any:
    return BusinessAreaFactory(code="4410", name="Ukraine", slug="ukraine", active=True)


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner, first_name="Alice")


@pytest.fixture
def program(afghanistan: Any) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def role(db: Any) -> Role:
    return RoleFactory(name="TestRole", permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value])


@pytest.fixture
def partner_with_role_1(afghanistan: Any, role: Role) -> Partner:
    partner = PartnerFactory(name="TestPartner1")
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, role=role)
    return partner


@pytest.fixture
def partner_with_role_2(afghanistan: Any, program: Program, role: Role) -> Partner:
    partner = PartnerFactory(name="TestPartner2")
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, program=program, role=role)
    return partner


@pytest.fixture
def user1(partner: Partner, afghanistan: Any, role: Role) -> User:
    user = UserFactory(partner=partner, first_name="Bob")
    RoleAssignmentFactory(user=user, business_area=afghanistan, role=role)
    return user


@pytest.fixture
def user2(partner: Partner, afghanistan: Any, program: Program, role: Role) -> User:
    user = UserFactory(partner=partner, first_name="Carol")
    RoleAssignmentFactory(user=user, business_area=afghanistan, program=program, role=role)
    return user


@pytest.fixture
def user3(partner_with_role_1: Partner) -> User:
    return UserFactory(partner=partner_with_role_1, first_name="Dave")


@pytest.fixture
def user4(partner_with_role_2: Partner) -> User:
    return UserFactory(partner=partner_with_role_2, first_name="Eve")


@pytest.fixture
def user_in_different_ba(partner: Partner, ukraine: Any, role: Role) -> User:
    user = UserFactory(partner=partner, first_name="Frank")
    RoleAssignmentFactory(user=user, business_area=ukraine, role=role)
    return user


@pytest.fixture
def list_url(afghanistan: Any) -> str:
    return reverse("api:accounts:users-list", kwargs={"business_area_slug": afghanistan.slug})


@pytest.fixture
def count_url(afghanistan: Any) -> str:
    return reverse("api:accounts:users-count", kwargs={"business_area_slug": afghanistan.slug})


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.USER_MANAGEMENT_VIEW_LIST], status.HTTP_200_OK),
        (ALL_GRIEVANCES_CREATE_MODIFY, status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
        ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_403_FORBIDDEN),
    ],
)
def test_user_list_permissions(
    authenticated_client: Any,
    user: User,
    afghanistan: Any,
    list_url: str,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=permissions,
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(list_url)
    assert response.status_code == expected_status


def test_user_list_returns_all_users_in_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: Any,
    list_url: str,
    count_url: str,
    user1: User,
    user2: User,
    user3: User,
    user4: User,
    user_in_different_ba: User,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    response_results = response.json()["results"]
    assert len(response_results) == 5

    response_count = authenticated_client.get(count_url)
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 5

    for i, expected_user in enumerate([user, user1, user2, user3, user4]):
        user_result = response_results[i]
        assert user_result["id"] == str(expected_user.id)
        assert user_result["first_name"] == expected_user.first_name
        assert user_result["last_name"] == expected_user.last_name
        assert user_result["email"] == expected_user.email
        assert user_result["username"] == expected_user.username


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.USER_MANAGEMENT_VIEW_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_user_count_permissions(
    authenticated_client: Any,
    user: User,
    afghanistan: Any,
    program: Program,
    count_url: str,
    user1: User,
    user2: User,
    user3: User,
    user4: User,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=permissions,
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(count_url)
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert response.json()["count"] == 5


def test_user_list_caching(
    authenticated_client: Any,
    user: User,
    afghanistan: Any,
    program: Program,
    list_url: str,
    user1: User,
    user2: User,
    user3: User,
    user4: User,
    user_in_different_ba: User,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 5
        assert len(ctx.captured_queries) == 12

    # no change - use cache
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second_call = response.headers["etag"]
        assert etag == etag_second_call
        assert len(ctx.captured_queries) == 6

    user2.first_name = "Zoe"
    user2.save()
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_third_call = response.headers["etag"]
        assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
        assert etag_third_call not in [etag, etag_second_call]
        # 4 queries are saved because of cached permissions calculations
        assert len(ctx.captured_queries) == 8

    user3.delete()
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fourth_call = response.headers["etag"]
        assert len(response.json()["results"]) == 4
        assert etag_fourth_call not in [etag, etag_second_call, etag_third_call, etag_third_call]
        assert len(ctx.captured_queries) == 8

    # no change - use cache
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fifth_call = response.headers["etag"]
        assert etag_fifth_call == etag_fourth_call
        assert len(ctx.captured_queries) == 6
