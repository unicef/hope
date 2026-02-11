"""Tests for PDU online edit send back functionality."""

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
def pdu_edit_ready_authorized(afghanistan: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Ready Edit Authorized",
        status=PDUOnlineEdit.Status.READY,
        authorized_users=[user],
    )


@pytest.fixture
def pdu_edit_ready_not_authorized(afghanistan: BusinessArea, program: Program) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Ready Edit Not Authorized",
        status=PDUOnlineEdit.Status.READY,
    )


@pytest.fixture
def pdu_edit_new(afghanistan: BusinessArea, program: Program, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="New Edit",
        status=PDUOnlineEdit.Status.NEW,
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


def get_send_back_url(afghanistan: BusinessArea, program: Program, pdu_edit_id: int) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-send-back",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
            "pk": pdu_edit_id,
        },
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_200_OK),
        ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_403_FORBIDDEN),
    ],
)
def test_send_back_permissions(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        program,
    )

    url = get_send_back_url(afghanistan, program, pdu_edit_ready_authorized.id)
    data = {"comment": "Please fix the data"}
    response = authenticated_client.post(url, data=data)
    assert response.status_code == expected_status


def test_send_back_success(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    url = get_send_back_url(afghanistan, program, pdu_edit_ready_authorized.id)
    comment_text = "Please review the vaccination data for accuracy"
    data = {"comment": comment_text}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "PDU Online Edit sent back successfully."}

    # Verify edit status changed
    pdu_edit_ready_authorized.refresh_from_db()
    assert pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.NEW

    # Verify comment was created
    assert PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_ready_authorized).exists()
    comment = PDUOnlineEditSentBackComment.objects.get(pdu_online_edit=pdu_edit_ready_authorized)
    assert comment.comment == comment_text
    assert comment.created_by == user
    assert comment.created_at is not None


def test_send_back_not_authorized_user(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready_not_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    # Attempt to send back an edit the user is not authorized for
    url = get_send_back_url(afghanistan, program, pdu_edit_ready_not_authorized.id)
    data = {"comment": "Please fix"}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    response_json = response.json()
    assert "You are not an authorized user for this PDU online edit." in response_json["detail"]

    # Verify no changes were made
    pdu_edit_ready_not_authorized.refresh_from_db()
    assert pdu_edit_ready_not_authorized.status == PDUOnlineEdit.Status.READY
    assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_ready_not_authorized).exists()


def test_send_back_invalid_status_new(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_new: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    url = get_send_back_url(afghanistan, program, pdu_edit_new.id)
    data = {"comment": "Cannot send back NEW status"}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "PDU Online Edit is not in the 'Ready' status and cannot be sent back." in response_json[0]

    # Verify no changes were made
    pdu_edit_new.refresh_from_db()
    assert pdu_edit_new.status == PDUOnlineEdit.Status.NEW
    assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_new).exists()


def test_send_back_invalid_status_approved(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    url = get_send_back_url(afghanistan, program, pdu_edit_approved.id)
    data = {"comment": "Cannot send back APPROVED status"}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "PDU Online Edit is not in the 'Ready' status and cannot be sent back." in response_json[0]

    # Verify no changes were made
    pdu_edit_approved.refresh_from_db()
    assert pdu_edit_approved.status == PDUOnlineEdit.Status.APPROVED
    assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_approved).exists()


def test_send_back_empty_comment(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    url = get_send_back_url(afghanistan, program, pdu_edit_ready_authorized.id)
    data = {"comment": ""}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "comment" in response_json
    assert "This field may not be blank." in response_json["comment"]

    # Verify no changes were made
    pdu_edit_ready_authorized.refresh_from_db()
    assert pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.READY
    assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_ready_authorized).exists()


def test_send_back_missing_comment(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    url = get_send_back_url(afghanistan, program, pdu_edit_ready_authorized.id)
    data = {}  # No comment field
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "comment" in response_json
    assert "This field is required." in response_json["comment"]

    # Verify no changes were made
    pdu_edit_ready_authorized.refresh_from_db()
    assert pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.READY
    assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_ready_authorized).exists()


def test_send_back_null_comment(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    url = get_send_back_url(afghanistan, program, pdu_edit_ready_authorized.id)
    data = {"comment": None}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "comment" in response_json
    assert "This field may not be null." in response_json["comment"]

    # Verify no changes were made
    pdu_edit_ready_authorized.refresh_from_db()
    assert pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.READY
    assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=pdu_edit_ready_authorized).exists()


def test_send_back_comment_with_leading_trailing_whitespace(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    url = get_send_back_url(afghanistan, program, pdu_edit_ready_authorized.id)
    comment_with_whitespace = "   Valid comment with whitespace   "
    expected_trimmed_comment = "Valid comment with whitespace"
    data = {"comment": comment_with_whitespace}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "PDU Online Edit sent back successfully."}

    pdu_edit_ready_authorized.refresh_from_db()
    assert pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.NEW

    # Verify comment was created with trimmed content
    comment = PDUOnlineEditSentBackComment.objects.get(pdu_online_edit=pdu_edit_ready_authorized)
    assert comment.comment == expected_trimmed_comment
    assert comment.created_by == user


def test_send_back_preserves_other_fields(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_ready_authorized: PDUOnlineEdit,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )

    # Store original values
    original_name = pdu_edit_ready_authorized.name
    original_created_by = pdu_edit_ready_authorized.created_by
    original_created_at = pdu_edit_ready_authorized.created_at
    original_number_of_records = pdu_edit_ready_authorized.number_of_records
    original_authorized_users = list(pdu_edit_ready_authorized.authorized_users.all())

    url = get_send_back_url(afghanistan, program, pdu_edit_ready_authorized.id)
    data = {"comment": "Data needs revision"}
    response = authenticated_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK

    pdu_edit_ready_authorized.refresh_from_db()

    # Verify only status changed
    assert pdu_edit_ready_authorized.name == original_name
    assert pdu_edit_ready_authorized.created_by == original_created_by
    assert pdu_edit_ready_authorized.created_at == original_created_at
    assert pdu_edit_ready_authorized.number_of_records == original_number_of_records
    assert list(pdu_edit_ready_authorized.authorized_users.all()) == original_authorized_users

    # Verify status changed
    assert pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.NEW

    # Verify comment was created
    comment = PDUOnlineEditSentBackComment.objects.get(pdu_online_edit=pdu_edit_ready_authorized)
    assert comment.comment == "Data needs revision"
    assert comment.created_by == user
