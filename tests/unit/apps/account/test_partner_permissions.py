"""Tests for partner permissions and user access control."""

from typing import Any

import pytest

from extras.test_utils.factories import (
    AdminAreaLimitedToFactory,
    AreaFactory,
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import AdminAreaLimitedTo, Area, BusinessArea, Partner, Program, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def role_create(db: Any) -> Role:
    return RoleFactory(name="Create_program", permissions=["PROGRAMME_CREATE"])


@pytest.fixture
def role_finish(db: Any) -> Role:
    return RoleFactory(name="Finish_program", permissions=["PROGRAMME_FINISH"])


@pytest.fixture
def area_1(db: Any) -> Area:
    return AreaFactory(name="Area 1", p_code="AREA1")


@pytest.fixture
def area_2(db: Any) -> Area:
    return AreaFactory(name="Area 2", p_code="AREA2")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(status=Program.DRAFT, business_area=business_area)


@pytest.fixture
def other_partner(business_area: BusinessArea) -> Partner:
    partner = PartnerFactory(name="Partner")
    partner.allowed_business_areas.add(business_area)
    return partner


@pytest.fixture
def other_user(other_partner: Partner) -> User:
    return UserFactory(partner=other_partner)


@pytest.fixture
def partner_role_assignment(business_area: BusinessArea, program: Program, other_partner: Partner, role_finish: Role):
    return RoleAssignmentFactory(
        business_area=business_area,
        program=program,
        user=None,
        partner=other_partner,
        role=role_finish,
    )


@pytest.fixture
def area_limits(other_partner: Partner, program: Program, area_1: Area):
    return AdminAreaLimitedToFactory(
        partner=other_partner,
        program=program,
        areas=[area_1],
    )


@pytest.fixture
def unicef_partner(db: Any) -> Partner:
    unicef, _ = Partner.objects.get_or_create(name="UNICEF")
    return unicef


@pytest.fixture
def unicef_hq(unicef_partner: Partner, db: Any) -> Partner:
    from django.conf import settings

    unicef_hq, _ = Partner.objects.get_or_create(name=settings.UNICEF_HQ_PARTNER, defaults={"parent": unicef_partner})
    return unicef_hq


@pytest.fixture
def unicef_user(unicef_hq: Partner) -> User:
    return UserFactory(partner=unicef_hq)


@pytest.fixture
def user_role_assignment(business_area: BusinessArea, other_user: User, role_create: Role):
    return RoleAssignmentFactory(
        business_area=business_area,
        user=other_user,
        partner=None,
        role=role_create,
        program=None,
    )


@pytest.fixture
def role_with_all_permissions(db: Any) -> Role:
    role, created = Role.objects.get_or_create(
        name="Role with all permissions",
        defaults={"permissions": ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]},
    )
    if not created:
        role.permissions = ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]
        role.save()
    return role


@pytest.fixture
def unicef_role_assignment(business_area: BusinessArea, unicef_hq: Partner, role_with_all_permissions: Role):
    return RoleAssignmentFactory(
        business_area=business_area,
        user=None,
        partner=unicef_hq,
        role=role_with_all_permissions,
        program=None,
    )


def test_partner_is_unicef(unicef_partner: Partner, other_partner: Partner):
    assert unicef_partner.is_unicef
    assert not other_partner.is_unicef


def test_partner_is_unicef_subpartner(unicef_hq: Partner, other_partner: Partner):
    assert unicef_hq.is_unicef_subpartner
    assert not other_partner.is_unicef_subpartner


def test_get_partner_program_ids_for_business_area(
    partner_role_assignment: RoleAssignment,
    other_user: User,
    unicef_user: User,
    unicef_role_assignment: RoleAssignment,
    business_area: BusinessArea,
    program: Program,
):
    resp_1 = other_user.partner.get_program_ids_for_business_area(business_area_id=business_area.pk)
    assert resp_1 == [str(program.pk)]

    resp_2 = unicef_user.partner.get_program_ids_for_business_area(business_area_id=business_area.pk)
    assert resp_2 == [str(program.pk)]


def test_get_partner_program_ids_for_permission_in_business_area(
    partner_role_assignment: RoleAssignment,
    other_user: User,
    unicef_user: User,
    unicef_role_assignment: RoleAssignment,
    business_area: BusinessArea,
    program: Program,
):
    resp_1 = other_user.partner.get_program_ids_for_permissions_in_business_area(
        business_area_id=business_area.pk,
        permissions=[Permissions.PROGRAMME_CREATE],
    )
    assert resp_1 == []

    resp_2 = other_user.partner.get_program_ids_for_permissions_in_business_area(
        business_area_id=business_area.pk,
        permissions=[
            Permissions.PROGRAMME_CREATE,
            Permissions.PROGRAMME_FINISH,
        ],
    )
    assert resp_2 == [str(program.pk)]

    resp_3 = unicef_user.partner.get_program_ids_for_permissions_in_business_area(
        business_area_id=business_area.pk,
        permissions=[Permissions.PROGRAMME_CREATE],
    )
    assert resp_3 == [str(program.pk)]


def test_get_user_program_ids_for_permission_in_business_area(
    user_role_assignment: RoleAssignment,
    partner_role_assignment: RoleAssignment,
    other_user: User,
    unicef_user: User,
    unicef_role_assignment: RoleAssignment,
    business_area: BusinessArea,
    program: Program,
):
    program_other = ProgramFactory(status=Program.DRAFT, business_area=business_area)

    resp_1 = other_user.get_program_ids_for_permissions_in_business_area(
        business_area_id=business_area.pk,
        permissions=[Permissions.PROGRAMME_CREATE],
    )
    assert str(program.pk) in resp_1
    assert str(program_other.pk) in resp_1

    resp_2 = other_user.get_program_ids_for_permissions_in_business_area(
        business_area_id=business_area.pk,
        permissions=[Permissions.PROGRAMME_CREATE, Permissions.PROGRAMME_FINISH],
    )
    assert str(program.pk) in resp_2
    assert str(program_other.pk) in resp_2

    resp_3 = unicef_user.get_program_ids_for_permissions_in_business_area(
        business_area_id=business_area.pk,
        permissions=[Permissions.PROGRAMME_CREATE],
    )
    assert str(program.pk) in resp_3
    assert str(program_other.pk) in resp_3


def test_get_partner_area_limits_per_program(
    area_limits: AdminAreaLimitedTo,
    other_user: User,
    program: Program,
    area_1: Area,
):
    other_partner_areas = other_user.partner.get_area_limits_for_program(program.pk)
    assert list(other_partner_areas) == list(Area.objects.filter(id=area_1.pk))


def test_has_area_access(
    area_limits: AdminAreaLimitedTo,
    other_user: User,
    unicef_user: User,
    unicef_role_assignment: RoleAssignment,
    program: Program,
    area_1: Area,
    area_2: Area,
):
    assert other_user.partner.has_area_access(area_1.pk, program.pk)
    assert not other_user.partner.has_area_access(area_2.pk, program.pk)

    assert unicef_user.partner.has_area_access(area_1.pk, program.pk)
    assert unicef_user.partner.has_area_access(area_2.pk, program.pk)


def test_partner_permissions_in_business_area(
    user_role_assignment: RoleAssignment,
    partner_role_assignment: RoleAssignment,
    other_user: User,
    business_area: BusinessArea,
    program: Program,
):
    # 2 permissions in BA
    permissions_in_ba = User.permissions_in_business_area(other_user, business_area_slug=business_area.slug)
    for perm in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
        assert perm in permissions_in_ba

    permissions_in_program = User.permissions_in_business_area(
        other_user,
        business_area_slug=business_area.slug,
        program_id=program.pk,
    )
    for perm in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
        assert perm in permissions_in_program

    another_program = ProgramFactory(status=Program.DRAFT, business_area=business_area)
    permissions_in_another_program = User.permissions_in_business_area(
        other_user,
        business_area_slug=business_area.slug,
        program_id=another_program.pk,
    )
    assert "PROGRAMME_CREATE" in permissions_in_another_program


def test_unicef_permissions_in_business_area(
    unicef_role_assignment: RoleAssignment,
    unicef_user: User,
    business_area: BusinessArea,
    program: Program,
):
    permissions_unicef_in_ba = User.permissions_in_business_area(unicef_user, business_area_slug=business_area.slug)
    for perm in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
        assert perm in permissions_unicef_in_ba

    assert unicef_user.partner.role_assignments.count() == 1
    assert unicef_user.partner.role_assignments.first().role == Role.objects.get(name="Role with all permissions")

    permissions_unicef_in_program = User.permissions_in_business_area(
        unicef_user,
        business_area_slug=business_area.slug,
        program_id=program.pk,
    )
    for perm in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
        assert perm in permissions_unicef_in_program


def test_user_has_permission_unicef_user(
    unicef_role_assignment: RoleAssignment,
    unicef_user: User,
    business_area: BusinessArea,
):
    assert User.has_perm(unicef_user, "PROGRAMME_CREATE", business_area)

    assert not User.has_perm(unicef_user, "Role_Not_Added", business_area)


def test_user_has_permission(
    user_role_assignment: RoleAssignment,
    partner_role_assignment: RoleAssignment,
    other_user: User,
    business_area: BusinessArea,
):
    # check partner roles
    assert User.has_perm(other_user, "PROGRAMME_FINISH", business_area)
    # check user roles
    assert User.has_perm(other_user, "PROGRAMME_CREATE", business_area)


def test_user_has_permission_for_program(
    user_role_assignment: RoleAssignment,
    partner_role_assignment: RoleAssignment,
    other_user: User,
    program: Program,
):
    assert User.has_perm(other_user, "PROGRAMME_CREATE", program)  # role on user is for program=None

    assert User.has_perm(other_user, "PROGRAMME_FINISH", program)  # role on partner is for program=self.program


def test_user_has_permission_for_another_program(
    user_role_assignment: RoleAssignment,
    partner_role_assignment: RoleAssignment,
    other_user: User,
    business_area: BusinessArea,
):
    another_program = ProgramFactory(status=Program.DRAFT, business_area=business_area)

    assert User.has_perm(other_user, "PROGRAMME_CREATE", another_program)  # role on user is for program=None

    assert not User.has_perm(other_user, "PROGRAMME_FINISH", another_program)  # role is only for self.program


def test_partner_has_permission_unicef_for_program(
    unicef_role_assignment: RoleAssignment,
    unicef_user: User,
    program: Program,
):
    assert User.has_perm(unicef_user, "PROGRAMME_FINISH", program)
    assert User.has_perm(unicef_user, "PROGRAMME_CREATE", program)
