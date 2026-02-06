"""Tests for program activate API endpoint."""

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
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="Test Partner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.DRAFT,
        name="Test Program For Activate",
    )


@pytest.fixture
def activate_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:programs:programs-activate",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "slug": program.slug,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_activate_program_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    activate_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_ACTIVATE],
        afghanistan,
        whole_business_area_access=True,
    )
    assert program.status == Program.DRAFT

    response = authenticated_client.post(activate_url)
    assert response.status_code == status.HTTP_200_OK
    program.refresh_from_db()
    assert program.status == Program.ACTIVE
    assert response.json() == {"message": "Program Activated."}


@pytest.mark.parametrize(
    "permissions",
    [
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        [],
    ],
)
def test_activate_program_without_permission(
    permissions: list,
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    activate_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, whole_business_area_access=True)
    assert program.status == Program.DRAFT

    response = authenticated_client.post(activate_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    program.refresh_from_db()
    assert program.status == Program.DRAFT


def test_activate_program_already_active(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    activate_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_ACTIVATE],
        afghanistan,
        whole_business_area_access=True,
    )
    program.status = Program.ACTIVE
    program.save()

    response = authenticated_client.post(activate_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Program is already active." in response.json()

    program.refresh_from_db()
    assert program.status == Program.ACTIVE


def test_activate_program_status_finished(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    activate_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_ACTIVATE],
        afghanistan,
        whole_business_area_access=True,
    )
    program.status = Program.FINISHED
    program.save()

    response = authenticated_client.post(activate_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Program Activated."}

    program.refresh_from_db()
    assert program.status == Program.ACTIVE
