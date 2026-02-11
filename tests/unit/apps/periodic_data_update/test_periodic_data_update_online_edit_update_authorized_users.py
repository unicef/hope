"""Tests for PDU online edit update authorized users functionality."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    PDUOnlineEditFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, PDUOnlineEdit, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def creator(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def other_user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authorized_user1(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authorized_user2(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authorized_user3(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, creator: User) -> Any:
    return api_client(creator)


@pytest.fixture
def pdu_edit_new(
    afghanistan: BusinessArea,
    program: Program,
    creator: User,
    authorized_user1: User,
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="New Edit",
        status=PDUOnlineEdit.Status.NEW,
        created_by=creator,
        authorized_users=[authorized_user1],
    )


@pytest.fixture
def pdu_edit_ready(
    afghanistan: BusinessArea,
    program: Program,
    creator: User,
    authorized_user1: User,
    authorized_user2: User,
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Ready Edit",
        status=PDUOnlineEdit.Status.READY,
        created_by=creator,
        authorized_users=[authorized_user1, authorized_user2],
    )


@pytest.fixture
def pdu_edit_approved(
    afghanistan: BusinessArea,
    program: Program,
    creator: User,
    authorized_user1: User,
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Approved Edit",
        status=PDUOnlineEdit.Status.APPROVED,
        created_by=creator,
        authorized_users=[authorized_user1],
    )


@pytest.fixture
def pdu_edit_other_creator(
    afghanistan: BusinessArea,
    program: Program,
    other_user: User,
    authorized_user1: User,
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Other Creator Edit",
        status=PDUOnlineEdit.Status.NEW,
        created_by=other_user,
        authorized_users=[authorized_user1],
    )


def get_update_authorized_users_url(afghanistan: BusinessArea, program: Program, pdu_edit_id: int) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-update-authorized-users",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
            "pk": pdu_edit_id,
        },
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_200_OK),
        ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_authorized_users_permissions(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    authorized_user1: User,
    authorized_user2: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        permissions,
        afghanistan,
        program,
    )

    url = get_update_authorized_users_url(afghanistan, program, pdu_edit_new.id)
    data = {"authorized_users": [authorized_user1.id, authorized_user2.id]}
    response = authenticated_client.post(url, data=data)
    assert response.status_code == expected_status


def test_update_authorized_users_success_add_users(
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    authorized_user1: User,
    authorized_user2: User,
    authorized_user3: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    # Verify initial state - only authorized_user1
    initial_authorized_users = list(pdu_edit_new.authorized_users.all())
    assert len(initial_authorized_users) == 1
    assert authorized_user1 in initial_authorized_users

    url = get_update_authorized_users_url(afghanistan, program, pdu_edit_new.id)
    data = {"authorized_users": [authorized_user1.id, authorized_user2.id, authorized_user3.id]}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "Authorized users updated successfully."}

    # Verify users were added
    pdu_edit_new.refresh_from_db()
    updated_authorized_users = list(pdu_edit_new.authorized_users.all())
    assert len(updated_authorized_users) == 3
    assert authorized_user1 in updated_authorized_users
    assert authorized_user2 in updated_authorized_users
    assert authorized_user3 in updated_authorized_users


def test_update_authorized_users_success_remove_users(
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready: PDUOnlineEdit,
    authorized_user1: User,
    authorized_user2: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    # Verify initial state - has authorized_user1 and authorized_user2
    initial_authorized_users = list(pdu_edit_ready.authorized_users.all())
    assert len(initial_authorized_users) == 2
    assert authorized_user1 in initial_authorized_users
    assert authorized_user2 in initial_authorized_users

    url = get_update_authorized_users_url(afghanistan, program, pdu_edit_ready.id)
    data = {"authorized_users": [authorized_user1.id]}  # Remove authorized_user2
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "Authorized users updated successfully."}

    # Verify user was removed
    pdu_edit_ready.refresh_from_db()
    updated_authorized_users = list(pdu_edit_ready.authorized_users.all())
    assert len(updated_authorized_users) == 1
    assert authorized_user1 in updated_authorized_users
    assert authorized_user2 not in updated_authorized_users


def test_update_authorized_users_success_replace_all_users(
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    authorized_user1: User,
    authorized_user2: User,
    authorized_user3: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    # Verify initial state
    initial_authorized_users = list(pdu_edit_new.authorized_users.all())
    assert len(initial_authorized_users) == 1
    assert authorized_user1 in initial_authorized_users

    url = get_update_authorized_users_url(afghanistan, program, pdu_edit_new.id)
    data = {"authorized_users": [authorized_user2.id, authorized_user3.id]}  # Replace with different users
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK

    # Verify users were completely replaced
    pdu_edit_new.refresh_from_db()
    updated_authorized_users = list(pdu_edit_new.authorized_users.all())
    assert len(updated_authorized_users) == 2
    assert authorized_user1 not in updated_authorized_users
    assert authorized_user2 in updated_authorized_users
    assert authorized_user3 in updated_authorized_users


def test_update_authorized_users_success_clear_all_users(
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    # Verify initial state
    initial_authorized_users = list(pdu_edit_new.authorized_users.all())
    assert len(initial_authorized_users) == 1

    url = get_update_authorized_users_url(afghanistan, program, pdu_edit_new.id)
    data = {"authorized_users": []}  # Clear all users
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK

    # Verify all users were removed
    pdu_edit_new.refresh_from_db()
    updated_authorized_users = list(pdu_edit_new.authorized_users.all())
    assert len(updated_authorized_users) == 0


def test_update_authorized_users_not_creator(
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    pdu_edit_other_creator: PDUOnlineEdit,
    authorized_user1: User,
    authorized_user2: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    url = get_update_authorized_users_url(afghanistan, program, pdu_edit_other_creator.id)
    data = {"authorized_users": [authorized_user2.id]}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "Only the creator of the PDU Online Edit can update authorized users." in response_json[0]

    # Verify no changes were made
    pdu_edit_other_creator.refresh_from_db()
    original_authorized_users = list(pdu_edit_other_creator.authorized_users.all())
    assert len(original_authorized_users) == 1
    assert authorized_user1 in original_authorized_users


def test_update_authorized_users_works_in_all_statuses(
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    pdu_edit_ready: PDUOnlineEdit,
    pdu_edit_approved: PDUOnlineEdit,
    authorized_user3: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    test_cases = [
        (pdu_edit_new, PDUOnlineEdit.Status.NEW),
        (pdu_edit_ready, PDUOnlineEdit.Status.READY),
        (pdu_edit_approved, PDUOnlineEdit.Status.APPROVED),
    ]

    for pdu_edit, expected_status in test_cases:
        url = get_update_authorized_users_url(afghanistan, program, pdu_edit.id)
        data = {"authorized_users": [authorized_user3.id]}
        response = authenticated_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK, f"Failed for status {expected_status}"

        # Verify changes were made
        pdu_edit.refresh_from_db()
        updated_authorized_users = list(pdu_edit.authorized_users.all())
        assert len(updated_authorized_users) == 1
        assert authorized_user3 in updated_authorized_users

        # Verify status remained unchanged
        assert pdu_edit.status == expected_status


def test_update_authorized_users_invalid_user_id(
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    authorized_user1: User,
    authorized_user3: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    url = get_update_authorized_users_url(afghanistan, program, pdu_edit_new.id)
    data = {"authorized_users": [authorized_user3.id, 99999]}  # Mix of valid and invalid
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "authorized_users" in response_json

    # Verify no changes were made
    pdu_edit_new.refresh_from_db()
    original_authorized_users = list(pdu_edit_new.authorized_users.all())
    assert len(original_authorized_users) == 1
    assert authorized_user1 in original_authorized_users


def test_update_authorized_users_missing_field(
    authenticated_client: Any,
    creator: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    authorized_user1: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        creator,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    url = get_update_authorized_users_url(afghanistan, program, pdu_edit_new.id)
    data = {}  # Missing authorized_users field
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "authorized_users" in response_json
    assert "This field is required." in response_json["authorized_users"]

    # Verify no changes were made
    pdu_edit_new.refresh_from_db()
    original_authorized_users = list(pdu_edit_new.authorized_users.all())
    assert len(original_authorized_users) == 1
    assert authorized_user1 in original_authorized_users
