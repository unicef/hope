"""Tests for incompatible roles validation."""

from typing import Any

from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from hope.models import IncompatibleRoles, Role, RoleAssignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def role_1(db: Any) -> Role:
    return RoleFactory(name="Role_1")


@pytest.fixture
def role_2(db: Any) -> Role:
    return RoleFactory(name="Role_2")


def test_unique_pair_allowed(role_1: Role, role_2: Role):
    test_role = IncompatibleRoles(role_one=role_1, role_two=role_2)
    test_role.full_clean()
    test_role.save()
    assert IncompatibleRoles.objects.filter(role_one=role_1, role_two=role_2).exists()


def test_roles_must_be_different(role_1: Role):
    incomp_role = IncompatibleRoles(role_one=role_1, role_two=role_1)
    with pytest.raises(ValidationError) as exc_info:
        incomp_role.full_clean()

    assert "Choose two different roles." in str(exc_info.value)


def test_only_unique_combinations_allowed(role_1: Role, role_2: Role):
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    test_role = IncompatibleRoles(role_one=role_2, role_two=role_1)
    with pytest.raises(ValidationError) as exc_info:
        test_role.full_clean()

    assert "This combination of roles already exists as incompatible pair." in str(exc_info.value)


def test_any_users_already_with_the_roles(role_1: Role, role_2: Role):
    business_area = BusinessAreaFactory(
        slug="afghanistan",
        code="0060",
        name="Afghanistan",
    )
    user = UserFactory()

    RoleAssignment.objects.create(
        role=role_1,
        business_area=business_area,
        user=user,
        partner=None,
    )
    RoleAssignment.objects.create(
        role=role_2,
        business_area=business_area,
        user=user,
        partner=None,
    )

    test_role = IncompatibleRoles(role_one=role_1, role_two=role_2)

    with pytest.raises(ValidationError) as exc_info:
        test_role.full_clean()

    error_message = str(exc_info.value)
    assert f"Users: [{user.email}] have these roles assigned to them in the same business area." in error_message
    assert "Please fix them before creating this incompatible roles pair." in error_message
