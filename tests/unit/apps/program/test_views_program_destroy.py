"""Tests for program destroy API endpoint."""

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
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.DRAFT)


@pytest.fixture
def destroy_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:programs:programs-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "slug": program.slug,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_program_destroy_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    destroy_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [], afghanistan, program)

    response = authenticated_client.delete(destroy_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Program.objects.filter(id=program.id).exists()


def test_program_destroy_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    destroy_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PROGRAMME_REMOVE], afghanistan, program)

    response = authenticated_client.delete(destroy_url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Program.objects.filter(id=program.id).exists()


def test_program_destroy_active(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    destroy_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PROGRAMME_REMOVE], afghanistan, program)
    program.status = Program.ACTIVE
    program.save()
    response = authenticated_client.delete(destroy_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == ["Only Draft Program can be deleted."]

    assert Program.objects.filter(id=program.id).exists()
