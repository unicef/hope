"""Tests for PDU online edit users available endpoint."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, Program, User

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
def partner_empty() -> Partner:
    return PartnerFactory(name="EmptyPartner")


@pytest.fixture
def user_can_save_data(
    partner_empty: Partner,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory(
        partner=partner_empty,
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@test.com",
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        program,
    )
    return user


@pytest.fixture
def user_can_approve(
    partner_empty: Partner,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory(
        partner=partner_empty,
        first_name="Bob",
        last_name="Smith",
        email="bob.smith@example.org",
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program,
    )
    return user


@pytest.fixture
def user_can_merge(
    partner_empty: Partner,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory(
        partner=partner_empty,
        first_name="Charlie",
        last_name="Brown",
        email="charlie.brown@company.com",
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )
    return user


@pytest.fixture
def user_can_all(
    partner_empty: Partner,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory(
        partner=partner_empty,
        first_name="David",
        last_name="Wilson",
        email="d.wilson@hope.org",
    )
    create_user_role_with_permissions(
        user,
        [
            Permissions.PDU_ONLINE_SAVE_DATA,
            Permissions.PDU_ONLINE_APPROVE,
            Permissions.PDU_ONLINE_MERGE,
        ],
        afghanistan,
        program,
    )
    return user


@pytest.fixture
def user_partner_can_all(
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    partner_with_permissions = PartnerFactory(name="Partner with PDU Permissions")
    user = UserFactory(
        partner=partner_with_permissions,
        first_name="Eve",
        last_name="Davis",
        email="eve.davis@partner.org",
    )
    create_user_role_with_permissions(
        user,
        [
            Permissions.PDU_ONLINE_SAVE_DATA,
            Permissions.PDU_ONLINE_APPROVE,
            Permissions.PDU_ONLINE_MERGE,
        ],
        afghanistan,
        program,
    )
    return user


@pytest.fixture
def user_can_approve_in_whole_ba(
    partner_empty: Partner,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory(
        partner=partner_empty,
        first_name="Grace",
        last_name="Chen",
        email="grace.chen@global.org",
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        None,  # Permission in whole business area
        whole_business_area_access=True,
    )
    return user


@pytest.fixture
def user_no_pdu_permissions(
    partner_empty: Partner,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory(
        partner=partner_empty,
        first_name="Frank",
        last_name="Miller",
        email="frank.miller@test.com",
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        program,
    )
    return user


@pytest.fixture
def url_users_available(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-users-available",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_200_OK),
        ([Permissions.PROGRAMME_UPDATE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_users_available_permissions(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available)
    assert response.status_code == expected_status


def test_users_available_list(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    response = authenticated_client.get(url_users_available)
    assert response.status_code == status.HTTP_200_OK

    results = response.json()

    assert len(results) == 6

    user_ids = {user_data["id"] for user_data in results}
    assert str(user_can_save_data.id) in user_ids
    assert str(user_can_approve.id) in user_ids
    assert str(user_can_merge.id) in user_ids
    assert str(user_can_all.id) in user_ids
    assert str(user_partner_can_all.id) in user_ids
    assert str(user_can_approve_in_whole_ba.id) in user_ids

    assert results[0] == {
        "id": str(user_can_save_data.id),
        "first_name": user_can_save_data.first_name,
        "last_name": user_can_save_data.last_name,
        "username": user_can_save_data.username,
        "email": user_can_save_data.email,
        "pdu_permissions": [Permissions.PDU_ONLINE_SAVE_DATA.value],
    }
    assert results[1] == {
        "id": str(user_can_approve.id),
        "first_name": user_can_approve.first_name,
        "last_name": user_can_approve.last_name,
        "username": user_can_approve.username,
        "email": user_can_approve.email,
        "pdu_permissions": [Permissions.PDU_ONLINE_APPROVE.value],
    }
    assert results[2] == {
        "id": str(user_can_merge.id),
        "first_name": user_can_merge.first_name,
        "last_name": user_can_merge.last_name,
        "username": user_can_merge.username,
        "email": user_can_merge.email,
        "pdu_permissions": [Permissions.PDU_ONLINE_MERGE.value],
    }
    assert results[3] == {
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
    }
    assert results[4] == {
        "id": str(user_partner_can_all.id),
        "first_name": user_partner_can_all.first_name,
        "last_name": user_partner_can_all.last_name,
        "username": user_partner_can_all.username,
        "email": user_partner_can_all.email,
        "pdu_permissions": [
            Permissions.PDU_ONLINE_APPROVE.value,
            Permissions.PDU_ONLINE_MERGE.value,
            Permissions.PDU_ONLINE_SAVE_DATA.value,
        ],
    }
    assert results[5] == {
        "id": str(user_can_approve_in_whole_ba.id),
        "first_name": user_can_approve_in_whole_ba.first_name,
        "last_name": user_can_approve_in_whole_ba.last_name,
        "username": user_can_approve_in_whole_ba.username,
        "email": user_can_approve_in_whole_ba.email,
        "pdu_permissions": [
            Permissions.PDU_ONLINE_APPROVE.value,
        ],
    }


def test_users_available_filter_by_save_data_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    response = authenticated_client.get(url_users_available, {"permission": Permissions.PDU_ONLINE_SAVE_DATA.value})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 3
    user_ids = {user_data["id"] for user_data in results}
    assert str(user_can_save_data.id) in user_ids
    assert str(user_can_all.id) in user_ids
    assert str(user_partner_can_all.id) in user_ids


def test_users_available_filter_by_approve_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    response = authenticated_client.get(url_users_available, {"permission": Permissions.PDU_ONLINE_APPROVE.value})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 4
    user_ids = {user_data["id"] for user_data in results}
    assert str(user_can_approve.id) in user_ids
    assert str(user_can_all.id) in user_ids
    assert str(user_partner_can_all.id) in user_ids
    assert str(user_can_approve_in_whole_ba.id) in user_ids


def test_users_available_filter_by_merge_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    response = authenticated_client.get(url_users_available, {"permission": Permissions.PDU_ONLINE_MERGE.value})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 3
    user_ids = {user_data["id"] for user_data in results}
    assert str(user_can_merge.id) in user_ids
    assert str(user_can_all.id) in user_ids
    assert str(user_partner_can_all.id) in user_ids


def test_users_available_filter_by_invalid_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )

    response = authenticated_client.get(url_users_available, {"permission": Permissions.PROGRAMME_UPDATE.value})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid permission" in response.json()[0]


def test_users_available_search_by_first_name(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": "Alice"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 1
    assert results[0]["id"] == str(user_can_save_data.id)
    assert results[0]["first_name"] == "Alice"


def test_users_available_search_by_last_name(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": "Brown"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 1
    assert results[0]["id"] == str(user_can_merge.id)
    assert results[0]["last_name"] == "Brown"


def test_users_available_search_by_email(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": "bob.smith@example.org"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 1
    assert results[0]["id"] == str(user_can_approve.id)
    assert results[0]["email"] == "bob.smith@example.org"


def test_users_available_search_by_full_name(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": "David Wilson"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 1
    assert results[0]["id"] == str(user_can_all.id)
    assert results[0]["first_name"] == "David"
    assert results[0]["last_name"] == "Wilson"


def test_users_available_search_by_full_name_reversed(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": "Davis Eve"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 1
    assert results[0]["id"] == str(user_partner_can_all.id)
    assert results[0]["first_name"] == "Eve"
    assert results[0]["last_name"] == "Davis"


def test_users_available_search_partial_match(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": "Char"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 1
    assert results[0]["id"] == str(user_can_merge.id)
    assert results[0]["first_name"] == "Charlie"


def test_users_available_search_case_insensitive(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": "ALICE JOHNSON"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 1
    assert results[0]["id"] == str(user_can_save_data.id)


def test_users_available_search_no_results(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": "NonExistentUser"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    assert len(results) == 0


def test_users_available_search_empty_string(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(url_users_available, {"search": ""})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    # Should return all users (same as no search)
    assert len(results) == 6


def test_users_available_search_with_permission_filter(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_users_available: str,
    user_can_save_data: User,
    user_can_approve: User,
    user_can_merge: User,
    user_can_all: User,
    user_partner_can_all: User,
    user_can_approve_in_whole_ba: User,
    user_no_pdu_permissions: User,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program,
    )
    response = authenticated_client.get(
        url_users_available, {"search": "David", "permission": Permissions.PDU_ONLINE_SAVE_DATA.value}
    )
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    # Should return David who has save data permission
    assert len(results) == 1
    assert results[0]["id"] == str(user_can_all.id)
    assert results[0]["first_name"] == "David"
