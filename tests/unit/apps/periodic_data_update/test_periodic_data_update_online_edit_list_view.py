"""Tests for PDU online edit list view."""

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
def other_program(business_area: BusinessArea) -> Program:
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
def user_other(partner: Any) -> User:
    return UserFactory(partner=partner, first_name="Charlie")


@pytest.fixture
def pdu_edit1(program: Program, business_area: BusinessArea, user_other: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        program=program,
        business_area=business_area,
        authorized_users=[user_other],
        status=PDUOnlineEdit.Status.NEW,
    )


@pytest.fixture
def pdu_edit2(program: Program, business_area: BusinessArea, user: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        program=program,
        business_area=business_area,
        authorized_users=[user],
        status=PDUOnlineEdit.Status.READY,
    )  # Request user is authorized


@pytest.fixture
def pdu_edit_other_program(other_program: Program, business_area: BusinessArea) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(program=other_program, business_area=business_area)


@pytest.fixture
def url_list(business_area: BusinessArea, program: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-list",
        kwargs={"business_area_slug": business_area.slug, "program_slug": program.slug},
    )


@pytest.fixture
def url_count(business_area: BusinessArea, program: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-count",
        kwargs={"business_area_slug": business_area.slug, "program_slug": program.slug},
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_VIEW_LIST_AND_DETAILS], status.HTTP_200_OK),
        ([Permissions.PROGRAMME_UPDATE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pdu_online_edit_list_permissions(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit1: PDUOnlineEdit,
    pdu_edit2: PDUOnlineEdit,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=permissions,
        business_area=business_area,
        program=program,
    )
    response = authenticated_client.get(url_list)
    assert response.status_code == expected_status


def test_pdu_online_edit_list(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit1: PDUOnlineEdit,
    pdu_edit2: PDUOnlineEdit,
    pdu_edit_other_program: PDUOnlineEdit,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area=business_area,
        program=program,
    )
    response = authenticated_client.get(url_list)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 2
    result_ids = {item["id"] for item in results}
    assert pdu_edit1.id in result_ids
    assert pdu_edit2.id in result_ids
    assert pdu_edit_other_program.id not in result_ids

    assert results == sorted(
        [
            {
                "id": pdu_edit1.id,
                "name": pdu_edit1.name,
                "number_of_records": pdu_edit1.number_of_records,
                "created_by": pdu_edit1.created_by.get_full_name(),
                "created_at": f"{pdu_edit1.created_at:%Y-%m-%dT%H:%M:%SZ}",
                "status": pdu_edit1.combined_status,
                "status_display": pdu_edit1.combined_status_display,
                "is_authorized": False,
            },
            {
                "id": pdu_edit2.id,
                "name": pdu_edit2.name,
                "number_of_records": pdu_edit2.number_of_records,
                "created_by": pdu_edit2.created_by.get_full_name(),
                "created_at": f"{pdu_edit2.created_at:%Y-%m-%dT%H:%M:%SZ}",
                "status": pdu_edit2.combined_status,
                "status_display": pdu_edit2.combined_status_display,
                "is_authorized": True,
            },
        ],
        key=lambda x: x["id"],
    )


@pytest.mark.parametrize(
    ("status_filter", "expected_count"),
    [
        (PDUOnlineEdit.Status.NEW, 2),  # pdu_edit1 and one created in the test
        (PDUOnlineEdit.Status.READY, 2),  # pdu_edit2 and one created in the test
        (PDUOnlineEdit.Status.APPROVED, 1),
        (PDUOnlineEdit.Status.MERGED, 1),
    ],
)
def test_pdu_online_edit_list_filter_by_status(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit1: PDUOnlineEdit,
    pdu_edit2: PDUOnlineEdit,
    url_list: str,
    status_filter: str,
    expected_count: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area=business_area,
        program=program,
    )
    PDUOnlineEditFactory(program=program, business_area=business_area, status=PDUOnlineEdit.Status.NEW)
    PDUOnlineEditFactory(program=program, business_area=business_area, status=PDUOnlineEdit.Status.READY)
    PDUOnlineEditFactory(program=program, business_area=business_area, status=PDUOnlineEdit.Status.APPROVED)
    PDUOnlineEditFactory(program=program, business_area=business_area, status=PDUOnlineEdit.Status.MERGED)

    response = authenticated_client.get(f"{url_list}?status={status_filter}")
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == expected_count
    assert all(item["status"] == status_filter for item in results)


def test_pdu_online_edit_list_filter_by_status_multiple_statuses(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit1: PDUOnlineEdit,
    pdu_edit2: PDUOnlineEdit,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area=business_area,
        program=program,
    )
    PDUOnlineEditFactory(program=program, business_area=business_area, status=PDUOnlineEdit.Status.APPROVED)

    response = authenticated_client.get(
        f"{url_list}?status={PDUOnlineEdit.Status.NEW}&status={PDUOnlineEdit.Status.APPROVED}"
    )
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 2
    statuses = {item["status"] for item in results}
    assert {PDUOnlineEdit.Status.NEW, PDUOnlineEdit.Status.APPROVED} == statuses


def test_pdu_online_edit_list_filter_by_status_invalid_status(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area=business_area,
        program=program,
    )
    response = authenticated_client.get(f"{url_list}?status=invalid_status")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_VIEW_LIST_AND_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pdu_online_edit_count(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    pdu_edit1: PDUOnlineEdit,
    pdu_edit2: PDUOnlineEdit,
    url_count: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=permissions,
        business_area=business_area,
        program=program,
    )
    response = authenticated_client.get(url_count)
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json()["count"] == 2
