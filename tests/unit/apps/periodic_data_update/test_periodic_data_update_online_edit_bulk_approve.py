"""Tests for periodic data update online edit bulk approve."""

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
from hope.models import BusinessArea, PDUOnlineEdit, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def partner(db: Any) -> Any:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Any) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def pdu_edit_ready_1(business_area: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=business_area,
        program=program,
        name="Ready Edit 1",
        status=PDUOnlineEdit.Status.READY,
        authorized_users=[user],
    )


@pytest.fixture
def pdu_edit_ready_2(business_area: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=business_area,
        program=program,
        name="Ready Edit 2",
        status=PDUOnlineEdit.Status.READY,
        authorized_users=[user],
    )


@pytest.fixture
def pdu_edit_ready_not_authorized(business_area: BusinessArea, program: Program) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=business_area,
        program=program,
        name="Ready Edit Not Authorized",
        status=PDUOnlineEdit.Status.READY,
    )


@pytest.fixture
def pdu_edit_new(business_area: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=business_area,
        program=program,
        name="New Edit",
        status=PDUOnlineEdit.Status.NEW,
        authorized_users=[user],
    )


@pytest.fixture
def pdu_edit_approved(business_area: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=business_area,
        program=program,
        name="Already Approved Edit",
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
    )


@pytest.fixture
def url_bulk_approve(business_area: BusinessArea, program: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-bulk-approve",
        kwargs={"business_area_slug": business_area.slug, "program_slug": program.slug},
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_200_OK),
        ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_403_FORBIDDEN),
    ],
)
def test_bulk_approve_permissions(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit_ready_1: PDUOnlineEdit,
    pdu_edit_ready_2: PDUOnlineEdit,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=permissions,
        business_area=business_area,
        program=program,
    )

    data = {"ids": [pdu_edit_ready_1.id, pdu_edit_ready_2.id]}
    response = authenticated_client.post(url_bulk_approve, data=data)
    assert response.status_code == expected_status


def test_bulk_approve_check_authorized_user_single_edit(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit_ready_not_authorized: PDUOnlineEdit,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    # Attempt to approve an edit the user is not authorized for
    data = {"ids": [pdu_edit_ready_not_authorized.id]}
    response = authenticated_client.post(url_bulk_approve, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    response_json = response.json()
    assert (
        f"You are not an authorized user for PDU Online Edit: {pdu_edit_ready_not_authorized.id}"
        in response_json["detail"]
    )

    # Verify the edit was not approved
    pdu_edit_ready_not_authorized.refresh_from_db()
    assert pdu_edit_ready_not_authorized.status == PDUOnlineEdit.Status.READY


def test_bulk_approve_check_authorized_user_mixed(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit_ready_not_authorized: PDUOnlineEdit,
    pdu_edit_ready_1: PDUOnlineEdit,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    # Attempt to approve an edit the user is not authorized for all edits in the list
    data = {"ids": [pdu_edit_ready_not_authorized.id, pdu_edit_ready_1.id]}
    response = authenticated_client.post(url_bulk_approve, data=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response_json = response.json()
    assert (
        f"You are not an authorized user for PDU Online Edit: {pdu_edit_ready_not_authorized.id}"
        in response_json["detail"]
    )

    # Verify no edits were approved
    pdu_edit_ready_not_authorized.refresh_from_db()
    pdu_edit_ready_1.refresh_from_db()
    assert pdu_edit_ready_not_authorized.status == PDUOnlineEdit.Status.READY
    assert pdu_edit_ready_1.status == PDUOnlineEdit.Status.READY


def test_bulk_approve_success(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit_ready_1: PDUOnlineEdit,
    pdu_edit_ready_2: PDUOnlineEdit,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    data = {"ids": [pdu_edit_ready_1.id, pdu_edit_ready_2.id]}
    response = authenticated_client.post(url_bulk_approve, data=data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "2 PDU Online Edits approved successfully."}

    # Verify edits were approved
    pdu_edit_ready_1.refresh_from_db()
    pdu_edit_ready_2.refresh_from_db()

    assert pdu_edit_ready_1.status == PDUOnlineEdit.Status.APPROVED
    assert pdu_edit_ready_1.approved_by == user
    assert pdu_edit_ready_1.approved_at is not None

    assert pdu_edit_ready_2.status == PDUOnlineEdit.Status.APPROVED
    assert pdu_edit_ready_2.approved_by == user
    assert pdu_edit_ready_2.approved_at is not None


def test_bulk_approve_single_edit(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit_ready_1: PDUOnlineEdit,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    data = {"ids": [pdu_edit_ready_1.id]}
    response = authenticated_client.post(url_bulk_approve, data=data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "1 PDU Online Edits approved successfully."}

    pdu_edit_ready_1.refresh_from_db()
    assert pdu_edit_ready_1.status == PDUOnlineEdit.Status.APPROVED


def test_bulk_approve_invalid_status(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit_ready_1: PDUOnlineEdit,
    pdu_edit_new: PDUOnlineEdit,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    # Try to approve edits that are not in READY status
    data = {"ids": [pdu_edit_ready_1.id, pdu_edit_new.id]}
    response = authenticated_client.post(url_bulk_approve, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "PDU Online Edit is not in the 'Ready' status and cannot be approved." in response_json[0]

    # Verify no edits were approved
    pdu_edit_ready_1.refresh_from_db()
    pdu_edit_new.refresh_from_db()
    assert pdu_edit_ready_1.status == PDUOnlineEdit.Status.READY
    assert pdu_edit_new.status == PDUOnlineEdit.Status.NEW


def test_bulk_approve_mixed_statuses(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit_ready_1: PDUOnlineEdit,
    pdu_edit_new: PDUOnlineEdit,
    pdu_edit_approved: PDUOnlineEdit,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    # Try to approve mix of READY, NEW, and APPROVED edits
    data = {"ids": [pdu_edit_ready_1.id, pdu_edit_new.id, pdu_edit_approved.id]}
    response = authenticated_client.post(url_bulk_approve, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "PDU Online Edit is not in the 'Ready' status and cannot be approved." in response_json[0]


def test_bulk_approve_empty_ids(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    data = {"ids": []}
    response = authenticated_client.post(url_bulk_approve, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "This list may not be empty." in response_json["ids"][0]


def test_bulk_approve_non_existent_ids(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    non_existent_id = 99999
    data = {"ids": [non_existent_id]}
    response = authenticated_client.post(url_bulk_approve, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "One or more PDU online edits not found." in response_json[0]


def test_bulk_approve_preserves_other_fields(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit_ready_1: PDUOnlineEdit,
    url_bulk_approve: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    # Store original values
    original_name = pdu_edit_ready_1.name
    original_created_by = pdu_edit_ready_1.created_by
    original_created_at = pdu_edit_ready_1.created_at
    original_number_of_records = pdu_edit_ready_1.number_of_records

    data = {"ids": [pdu_edit_ready_1.id]}
    response = authenticated_client.post(url_bulk_approve, data=data)

    assert response.status_code == status.HTTP_200_OK

    pdu_edit_ready_1.refresh_from_db()

    # Verify only approval-related fields changed
    assert pdu_edit_ready_1.name == original_name
    assert pdu_edit_ready_1.created_by == original_created_by
    assert pdu_edit_ready_1.created_at == original_created_at
    assert pdu_edit_ready_1.number_of_records == original_number_of_records

    # Verify approval fields were updated
    assert pdu_edit_ready_1.status == PDUOnlineEdit.Status.APPROVED
    assert pdu_edit_ready_1.approved_by == user
    assert pdu_edit_ready_1.approved_at is not None
