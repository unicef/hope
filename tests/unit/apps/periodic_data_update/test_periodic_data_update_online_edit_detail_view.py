"""Tests for PDU online edit detail view."""

from datetime import datetime
from typing import Any, Callable

from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    PDUOnlineEditFactory,
    PDUOnlineEditSentBackCommentFactory,
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
def partner_empty(db: Any) -> Any:
    return PartnerFactory(name="EmptyPartner")


@pytest.fixture
def user_can_approve(
    partner_empty: Any,
    business_area: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory(partner=partner_empty, first_name="Bob")
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        business_area,
        program,
    )
    return user


@pytest.fixture
def user_can_all(
    partner_empty: Any,
    business_area: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory(partner=partner_empty, first_name="David")
    create_user_role_with_permissions(
        user,
        [
            Permissions.PDU_ONLINE_SAVE_DATA,
            Permissions.PDU_ONLINE_APPROVE,
            Permissions.PDU_ONLINE_MERGE,
        ],
        business_area,
        program,
    )
    return user


@pytest.fixture
def user_partner_can_merge(
    business_area: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    partner_can_merge = PartnerFactory(name="Partner with PDU Permission")
    user = UserFactory(partner=partner_can_merge, first_name="Eve")
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        business_area,
        program,
    )
    return user


@pytest.fixture
def pdu_edit(
    program: Program,
    business_area: BusinessArea,
    user: User,
    user_can_approve: User,
    user_can_all: User,
    user_partner_can_merge: User,
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        program=program,
        business_area=business_area,
        authorized_users=[user_partner_can_merge, user_can_all, user_can_approve],
        status=PDUOnlineEdit.Status.APPROVED,
        name="Test PDU Edit",
        number_of_records=100,
        created_by=user,
        approved_by=user_can_approve,
        approved_at=timezone.make_aware(datetime(year=2024, month=8, day=20)),
    )


@pytest.fixture
def sent_back_comment(pdu_edit: PDUOnlineEdit, user_can_approve: User) -> Any:
    return PDUOnlineEditSentBackCommentFactory(
        pdu_online_edit=pdu_edit,
        comment="This is a sent back comment.",
        created_by=user_can_approve,
    )


@pytest.fixture
def url_detail(business_area: BusinessArea, program: Program, pdu_edit: PDUOnlineEdit) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program.slug,
            "pk": pdu_edit.pk,
        },
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_VIEW_LIST_AND_DETAILS], status.HTTP_200_OK),
        ([Permissions.PROGRAMME_UPDATE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pdu_online_edit_detail_permissions(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit: PDUOnlineEdit,
    user_can_approve: User,
    user_can_all: User,
    user_partner_can_merge: User,
    sent_back_comment: Any,
    url_detail: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        business_area,
        program,
    )
    response = authenticated_client.get(url_detail)
    assert response.status_code == expected_status


def test_pdu_online_edit_detail(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit: PDUOnlineEdit,
    user_can_approve: User,
    user_can_all: User,
    user_partner_can_merge: User,
    sent_back_comment: Any,
    url_detail: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area,
        program,
    )
    response = authenticated_client.get(url_detail)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["id"] == pdu_edit.id
    assert result["name"] == pdu_edit.name
    assert result["number_of_records"] == pdu_edit.number_of_records
    assert result["created_by"] == pdu_edit.created_by.get_full_name()
    assert result["created_at"] == f"{pdu_edit.created_at:%Y-%m-%dT%H:%M:%SZ}"
    assert result["status"] == pdu_edit.status
    assert result["status_display"] == pdu_edit.get_status_display()
    assert result["is_authorized"] is False
    assert result["is_creator"] is True
    assert result["approved_by"] == pdu_edit.approved_by.get_full_name()
    assert result["approved_at"] == f"{pdu_edit.approved_at:%Y-%m-%dT%H:%M:%SZ}"
    assert result["sent_back_comment"] == {
        "comment": pdu_edit.sent_back_comment.comment,
        "created_by": pdu_edit.sent_back_comment.created_by.get_full_name(),
        "created_at": f"{pdu_edit.sent_back_comment.created_at:%Y-%m-%dT%H:%M:%SZ}",
    }
    assert result["edit_data"] == pdu_edit.edit_data
    assert result["authorized_users"] == [
        {
            "id": str(user_can_approve.id),
            "first_name": user_can_approve.first_name,
            "last_name": user_can_approve.last_name,
            "username": user_can_approve.username,
            "email": user_can_approve.email,
            "pdu_permissions": [Permissions.PDU_ONLINE_APPROVE.value],
        },
        {
            "id": str(user_can_all.id),
            "first_name": user_can_all.first_name,
            "last_name": user_can_all.last_name,
            "username": user_can_all.username,
            "email": user_can_all.email,
            "pdu_permissions": [
                Permissions.PDU_ONLINE_APPROVE.value,
                Permissions.PDU_ONLINE_MERGE.value,
                Permissions.PDU_ONLINE_SAVE_DATA.value,
            ],
        },
        {
            "id": str(user_partner_can_merge.id),
            "first_name": user_partner_can_merge.first_name,
            "last_name": user_partner_can_merge.last_name,
            "username": user_partner_can_merge.username,
            "email": user_partner_can_merge.email,
            "pdu_permissions": [Permissions.PDU_ONLINE_MERGE.value],
        },
    ]
