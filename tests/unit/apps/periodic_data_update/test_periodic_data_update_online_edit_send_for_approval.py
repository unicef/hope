"""Tests for PDU online edit send for approval functionality."""

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
from hope.models import BusinessArea, Partner, PDUOnlineEdit, PDUOnlineEditSentBackComment, Program, User

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
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def pdu_edit_new_authorized(afghanistan: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="New Edit Authorized",
        status=PDUOnlineEdit.Status.NEW,
        authorized_users=[user],
    )


@pytest.fixture
def pdu_edit_new_not_authorized(afghanistan: BusinessArea, program: Program) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="New Edit Not Authorized",
        status=PDUOnlineEdit.Status.NEW,
    )


@pytest.fixture
def pdu_edit_ready(afghanistan: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Ready Edit",
        status=PDUOnlineEdit.Status.READY,
        authorized_users=[user],
    )


@pytest.fixture
def pdu_edit_approved(afghanistan: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Approved Edit",
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
    )


def get_send_for_approval_url(afghanistan: BusinessArea, program: Program, pdu_edit_id: int) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-send-for-approval",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
            "pk": pdu_edit_id,
        },
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_200_OK),
        ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_send_for_approval_permissions(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        program,
    )

    url = get_send_for_approval_url(afghanistan, program, pdu_edit_new_authorized.id)
    response = authenticated_client.post(url)
    assert response.status_code == expected_status


def test_send_for_approval_success(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        program,
    )

    url = get_send_for_approval_url(afghanistan, program, pdu_edit_new_authorized.id)
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "PDU Online Edit sent for approval."}

    # Verify edit status changed from NEW to READY
    pdu_edit_new_authorized.refresh_from_db()
    assert pdu_edit_new_authorized.status == PDUOnlineEdit.Status.READY


def test_send_for_approval_not_authorized_user(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new_not_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        program,
    )

    url = get_send_for_approval_url(afghanistan, program, pdu_edit_new_not_authorized.id)
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    response_json = response.json()
    assert "You are not an authorized user for this PDU online edit." in response_json["detail"]

    # Verify no changes were made
    pdu_edit_new_not_authorized.refresh_from_db()
    assert pdu_edit_new_not_authorized.status == PDUOnlineEdit.Status.NEW


def test_send_for_approval_invalid_status_ready(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        program,
    )

    url = get_send_for_approval_url(afghanistan, program, pdu_edit_ready.id)
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "Only new edits can be sent for approval." in response_json[0]

    # Verify no changes were made
    pdu_edit_ready.refresh_from_db()
    assert pdu_edit_ready.status == PDUOnlineEdit.Status.READY


def test_send_for_approval_invalid_status_approved(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        program,
    )

    url = get_send_for_approval_url(afghanistan, program, pdu_edit_approved.id)
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "Only new edits can be sent for approval." in response_json[0]

    # Verify no changes were made
    pdu_edit_approved.refresh_from_db()
    assert pdu_edit_approved.status == PDUOnlineEdit.Status.APPROVED


def test_send_for_approval_clears_sent_back_comment(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        program,
    )

    # Create a sent back comment for the PDU edit
    comment = PDUOnlineEditSentBackComment.objects.create(
        comment="Please fix the data validation issues",
        created_by=user,
        pdu_online_edit=pdu_edit_new_authorized,
    )

    # Verify comment exists before sending for approval
    assert PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_new_authorized).exists()

    url = get_send_for_approval_url(afghanistan, program, pdu_edit_new_authorized.id)
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "PDU Online Edit sent for approval."}

    # Verify edit status changed
    pdu_edit_new_authorized.refresh_from_db()
    assert pdu_edit_new_authorized.status == PDUOnlineEdit.Status.READY

    # Verify sent back comment was cleared
    assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_new_authorized).exists()
    assert not PDUOnlineEditSentBackComment.objects.filter(id=comment.id).exists()


def test_send_for_approval_preserves_other_fields(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        program,
    )

    # Store original values
    original_name = pdu_edit_new_authorized.name
    original_created_by = pdu_edit_new_authorized.created_by
    original_created_at = pdu_edit_new_authorized.created_at
    original_number_of_records = pdu_edit_new_authorized.number_of_records
    original_authorized_users = list(pdu_edit_new_authorized.authorized_users.all())

    url = get_send_for_approval_url(afghanistan, program, pdu_edit_new_authorized.id)
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_200_OK

    pdu_edit_new_authorized.refresh_from_db()

    # Verify other fields remain unchanged
    assert pdu_edit_new_authorized.name == original_name
    assert pdu_edit_new_authorized.created_by == original_created_by
    assert pdu_edit_new_authorized.created_at == original_created_at
    assert pdu_edit_new_authorized.number_of_records == original_number_of_records
    assert list(pdu_edit_new_authorized.authorized_users.all()) == original_authorized_users

    # Verify only status changed
    assert pdu_edit_new_authorized.status == PDUOnlineEdit.Status.READY

    # Verify approval fields are still empty
    assert pdu_edit_new_authorized.approved_by is None
    assert pdu_edit_new_authorized.approved_at is None
