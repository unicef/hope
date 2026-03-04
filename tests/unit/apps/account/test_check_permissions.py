"""Tests for check_permissions function."""

from typing import Any

from django.contrib.auth.models import AnonymousUser
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions, check_permissions
from hope.models import Area, BusinessArea, Program, Role, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        code="0060",
        name="Afghanistan",
    )


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(status=Program.DRAFT, business_area=business_area)


@pytest.fixture
def role(db: Any) -> Role:
    return RoleFactory(
        name="POPULATION VIEW INDIVIDUALS DETAILS",
        permissions=["POPULATION_VIEW_INDIVIDUALS_DETAILS"],
    )


@pytest.fixture
def area(db: Any) -> Area:
    return AreaFactory(name="POPULATION")


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def role_with_all_permissions(db: Any) -> Role:
    role, created = Role.objects.get_or_create(
        name="Role with all permissions",
        defaults={"permissions": [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS.value]},
    )
    if not created:
        role.permissions = [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS.value]
        role.save()
    return role


def test_user_is_not_authenticated():
    user = AnonymousUser()
    assert not check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS])


def test_business_area_is_invalid(user: User):
    arguments = {"business_area": "invalid"}
    result = check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
    assert not result


def test_user_is_unicef(user: User, business_area: BusinessArea, program: Program, role_with_all_permissions: Role):
    unicef = PartnerFactory(name="UNICEF")
    partner = PartnerFactory(name="UNICEF HQ", parent=unicef)
    user.partner = partner
    user.save()

    arguments = {
        "business_area": business_area.slug,
        "program": program.slug,
    }
    result = check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
    assert result


def test_user_is_not_unicef_and_has_permission_in_different_program(
    user: User,
    business_area: BusinessArea,
    program: Program,
    role: Role,
):
    partner = PartnerFactory(name="Partner")
    user.partner = partner
    user.save()

    RoleAssignmentFactory(
        user=user,
        partner=None,
        business_area=business_area,
        role=role,
        program=ProgramFactory(business_area=business_area),
    )

    arguments = {
        "business_area": business_area.slug,
        "program": program.slug,
    }
    result = check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
    assert not result


def test_user_is_not_unicef_and_partner_has_permission_in_program(
    user: User,
    business_area: BusinessArea,
    program: Program,
    role: Role,
):
    partner = PartnerFactory(name="Partner")
    RoleAssignmentFactory(
        user=None,
        partner=partner,
        business_area=business_area,
        role=role,
        program=program,
    )

    user.partner = partner
    user.save()

    arguments = {
        "business_area": business_area.slug,
        "program": program.slug,
    }
    result = check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
    assert result


def test_user_is_not_unicef_and_user_has_permission_in_program(
    user: User,
    business_area: BusinessArea,
    program: Program,
    role: Role,
):
    partner = PartnerFactory(name="Partner")
    user.partner = partner
    user.save()

    RoleAssignmentFactory(
        user=user,
        partner=None,
        business_area=business_area,
        role=role,
        program=program,
    )

    arguments = {
        "business_area": business_area.slug,
        "program": program.slug,
    }
    result = check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
    assert result


def test_user_is_not_unicef_and_partner_has_permission_in_whole_ba(
    user: User,
    business_area: BusinessArea,
    program: Program,
    role: Role,
):
    partner = PartnerFactory(name="Partner")
    RoleAssignmentFactory(
        user=None,
        partner=partner,
        business_area=business_area,
        role=role,
    )

    user.partner = partner
    user.save()

    arguments = {
        "business_area": business_area.slug,
        "program": program.slug,
    }
    result = check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
    assert result


def test_user_is_not_unicef_and_user_has_permission_in_whole_ba(
    user: User,
    business_area: BusinessArea,
    program: Program,
    role: Role,
):
    partner = PartnerFactory(name="Partner")
    user.partner = partner
    user.save()

    RoleAssignmentFactory(
        user=user,
        partner=None,
        business_area=business_area,
        role=role,
    )

    arguments = {
        "business_area": business_area.slug,
        "program": program.slug,
    }
    result = check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
    assert result
