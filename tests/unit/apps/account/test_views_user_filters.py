"""Tests for user filtering API views."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FeedbackFactory,
    GrievanceTicketFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    SurveyFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import INACTIVE, BusinessArea, Message, Partner, Program, Role, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(code="0060", name="Afghanistan", slug="afghanistan", active=True)


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner, first_name="Alice")


@pytest.fixture
def role_with_user_management_permissions(db: Any) -> Role:
    return RoleFactory(
        name="Role For User",
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST.value],
    )


@pytest.fixture
def program1(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def program2(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def role1(db: Any) -> Role:
    return RoleFactory(name="TestRole1", permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value])


@pytest.fixture
def role2(db: Any) -> Role:
    return RoleFactory(name="TestRole2", permissions=[Permissions.PROGRAMME_REMOVE.value])


@pytest.fixture
def user1(partner: Partner, afghanistan: BusinessArea, role1: Role) -> User:
    user = UserFactory(partner=partner, first_name="Bob")
    RoleAssignmentFactory(user=user, business_area=afghanistan, role=role1)
    return user


@pytest.fixture
def user2(partner: Partner, afghanistan: BusinessArea, program1: Program, role2: Role) -> User:
    user = UserFactory(partner=partner, first_name="Carol")
    RoleAssignmentFactory(user=user, business_area=afghanistan, program=program1, role=role2)
    return user


@pytest.fixture
def partner_with_role_1(afghanistan: BusinessArea, role1: Role) -> Partner:
    partner = PartnerFactory(name="TestPartner1")
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, role=role1)
    return partner


@pytest.fixture
def user3(partner_with_role_1: Partner) -> User:
    return UserFactory(partner=partner_with_role_1, first_name="Dave")


@pytest.fixture
def partner_with_role_2(afghanistan: BusinessArea, program1: Program, role2: Role) -> Partner:
    partner = PartnerFactory(name="TestPartner2")
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, program=program1, role=role2)
    return partner


@pytest.fixture
def user4(partner_with_role_2: Partner) -> User:
    return UserFactory(partner=partner_with_role_2, first_name="Eve")


@pytest.fixture
def user_in_different_program(partner: Partner, afghanistan: BusinessArea, program2: Program, role1: Role) -> User:
    user = UserFactory(partner=partner, first_name="Frank")
    RoleAssignmentFactory(user=user, business_area=afghanistan, program=program2, role=role1)
    return user


@pytest.fixture
def user_in_different_ba(partner: Partner, role2: Role) -> User:
    user = UserFactory(partner=partner, first_name="George")
    RoleAssignmentFactory(user=user, business_area=BusinessAreaFactory(slug="ukraine"), role=role2)
    return user


@pytest.fixture
def all_users(
    user_with_management_permissions: User,
    user1: User,
    user2: User,
    user3: User,
    user4: User,
    user_in_different_program: User,
    user_in_different_ba: User,
) -> dict:
    return {
        "user_with_management_permissions": user_with_management_permissions,
        "user1": user1,
        "user2": user2,
        "user3": user3,
        "user4": user4,
        "user_in_different_program": user_in_different_program,
        "user_in_different_ba": user_in_different_ba,
    }


@pytest.fixture
def user_with_management_permissions(
    user: User, afghanistan: BusinessArea, role_with_user_management_permissions: Role
) -> User:
    RoleAssignmentFactory(
        user=user, business_area=afghanistan, program=None, role=role_with_user_management_permissions
    )
    return user


@pytest.fixture
def list_url(afghanistan: BusinessArea) -> str:
    return reverse("api:accounts:users-list", kwargs={"business_area_slug": afghanistan.slug})


@pytest.fixture
def authenticated_client(api_client: Callable, user_with_management_permissions: User) -> Any:
    return api_client(user_with_management_permissions)


def test_filter_by_program_returns_users_with_access_to_program(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    program1: Program,
    program2: Program,
    list_url: str,
    all_users: dict,
) -> None:
    user_with_management_permissions = all_users["user_with_management_permissions"]
    user1 = all_users["user1"]
    user2 = all_users["user2"]
    user3 = all_users["user3"]
    user4 = all_users["user4"]
    user_in_different_program = all_users["user_in_different_program"]

    response = authenticated_client.get(list_url, {"program": program1.slug})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 5
    users_ids = [result["id"] for result in response_results]
    assert str(user_with_management_permissions.id) in users_ids
    assert str(user1.id) in users_ids
    assert str(user2.id) in users_ids
    assert str(user3.id) in users_ids
    assert str(user4.id) in users_ids

    response_2 = authenticated_client.get(list_url, {"program": program2.slug})
    assert response_2.status_code == status.HTTP_200_OK
    response_results_2 = response_2.data["results"]
    assert len(response_results_2) == 4
    users_ids_2 = [result["id"] for result in response_results_2]
    assert str(user_with_management_permissions.id) in users_ids_2
    assert str(user1.id) in users_ids_2
    assert str(user3.id) in users_ids_2
    assert str(user_in_different_program.id) in users_ids_2


def test_filter_by_status(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    list_url: str,
    all_users: dict,
) -> None:
    user2 = all_users["user2"]
    user_in_different_program = all_users["user_in_different_program"]
    user2.status = INACTIVE
    user2.save()
    user_in_different_program.status = INACTIVE
    user_in_different_program.save()

    response = authenticated_client.get(list_url, {"status": "INACTIVE"})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 2
    users_ids = [result["id"] for result in response_results]
    assert str(user2.id) in users_ids
    assert str(user_in_different_program.id) in users_ids


def test_filter_by_partner(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    partner_with_role_1: Partner,
    list_url: str,
    all_users: dict,
) -> None:
    response = authenticated_client.get(list_url, {"partner": partner_with_role_1.id})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1
    assert response_results[0]["id"] == str(all_users["user3"].id)


def test_filter_by_role_returns_users_with_role(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    role1: Role,
    list_url: str,
    all_users: dict,
) -> None:
    response = authenticated_client.get(list_url, {"roles": str(role1.id)})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 3
    users_ids = [result["id"] for result in response_results]
    assert str(all_users["user1"].id) in users_ids
    assert str(all_users["user3"].id) in users_ids
    assert str(all_users["user_in_different_program"].id) in users_ids


def test_filter_by_is_ticket_creator(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    list_url: str,
    all_users: dict,
) -> None:
    user2 = all_users["user2"]
    GrievanceTicketFactory(created_by=user2, business_area=afghanistan)

    response = authenticated_client.get(list_url, {"is_ticket_creator": True})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1
    assert response_results[0]["id"] == str(user2.id)


def test_filter_by_is_survey_creator_false(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    list_url: str,
    all_users: dict,
) -> None:
    user_with_management_permissions = all_users["user_with_management_permissions"]
    user1 = all_users["user1"]
    user2 = all_users["user2"]
    user3 = all_users["user3"]
    user4 = all_users["user4"]
    user_in_different_program = all_users["user_in_different_program"]

    SurveyFactory(created_by=user2)

    response = authenticated_client.get(list_url, {"is_survey_creator": False})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 5
    users_ids = [result["id"] for result in response_results]
    assert str(user_with_management_permissions.id) in users_ids
    assert str(user1.id) in users_ids
    assert str(user3.id) in users_ids
    assert str(user4.id) in users_ids
    assert str(user_in_different_program.id) in users_ids


def test_filter_by_is_message_creator(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    list_url: str,
    all_users: dict,
) -> None:
    user1 = all_users["user1"]
    Message.objects.create(created_by=user1, title="Test Message", business_area=afghanistan)

    response = authenticated_client.get(list_url, {"is_message_creator": True})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1
    assert response_results[0]["id"] == str(user1.id)


def test_filter_by_is_feedback_creator(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    list_url: str,
    all_users: dict,
) -> None:
    user_in_different_program = all_users["user_in_different_program"]

    FeedbackFactory(created_by=user_in_different_program)

    response = authenticated_client.get(list_url, {"is_feedback_creator": True})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1
    assert response_results[0]["id"] == str(user_in_different_program.id)


def test_search_by_name(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    list_url: str,
    all_users: dict,
) -> None:
    response = authenticated_client.get(list_url, {"search": "Bob"})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1
    assert response_results[0]["id"] == str(all_users["user1"].id)


def test_search_by_email(
    afghanistan: BusinessArea,
    authenticated_client: Any,
    list_url: str,
    all_users: dict,
) -> None:
    user_in_different_program = all_users["user_in_different_program"]

    user_in_different_program.email = "newemail@unicef.com"
    user_in_different_program.save()

    response = authenticated_client.get(list_url, {"search": "new"})
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1
    assert response_results[0]["id"] == str(user_in_different_program.id)
