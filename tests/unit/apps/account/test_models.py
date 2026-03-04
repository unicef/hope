"""Tests for account models - RoleAssignment, Partner, AdminAreaLimitedTo."""

from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
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
from hope.models import Area, BusinessArea, Partner, Program, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_1(db: Any) -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def business_area_2(db: Any) -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def role(db: Any) -> Role:
    return RoleFactory(
        name="Test Role",
        permissions=["PROGRAMME_CREATE", "PROGRAMME_FINISH"],
    )


@pytest.fixture
def role_2(db: Any) -> Role:
    return RoleFactory(
        name="Test Role 2",
        permissions=["PROGRAMME_UPDATE"],
    )


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory(first_name="Test", last_name="User")


@pytest.fixture
def partner(business_area_1: BusinessArea) -> Partner:
    partner = PartnerFactory(name="Partner")
    partner.allowed_business_areas.add(business_area_1)
    return partner


@pytest.fixture
def program_1(business_area_1: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=business_area_1,
        name="Program 1",
        status=Program.ACTIVE,
    )


@pytest.fixture
def program_2(business_area_1: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=business_area_1,
        name="Program 2",
        status=Program.ACTIVE,
    )


@pytest.fixture
def user_role_assignment(user: User, role: Role, business_area_1: BusinessArea) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=user,
        partner=None,
        role=role,
        business_area=business_area_1,
    )


@pytest.fixture
def area_1(db: Any) -> Area:
    return AreaFactory(name="Area 1", p_code="AREA1")


def test_role_assignment_requires_user_or_partner(role_2, business_area_1):
    with pytest.raises(ValidationError) as exc_info:
        RoleAssignment.objects.create(
            user=None,
            partner=None,
            role=role_2,
            business_area=business_area_1,
        )
    assert "Either user or partner must be set, but not both." in str(exc_info.value)


def test_role_assignment_cannot_have_both_user_and_partner(user, partner, role_2, business_area_1, program_1):
    with pytest.raises(ValidationError) as exc_info:
        RoleAssignment.objects.create(
            user=user,
            role=role_2,
            business_area=business_area_1,
            partner=partner,
            program=program_1,
        )

    assert "Either user or partner must be set, but not both." in str(exc_info.value)


def test_role_assignment_respects_is_available_for_partner_flag_true(partner, role_2, business_area_1):
    role_assignment = RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role_2,
        business_area=business_area_1,
    )

    assert role_assignment.id is not None


def test_role_assignment_respects_is_available_for_partner_flag_false(partner, role_2, business_area_1):
    role_2.is_available_for_partner = False
    role_2.save()

    with pytest.raises(ValidationError) as exc_info:
        RoleAssignment.objects.create(
            user=None,
            partner=partner,
            role=role_2,
            business_area=business_area_1,
        )

    assert "Partner can only be assigned roles that are available for partners." in str(exc_info.value)


def test_role_assignment_user_ignores_is_available_for_partner_flag(user, role_2, business_area_1):
    role_2.is_available_for_partner = False
    role_2.save()

    role_assignment = RoleAssignmentFactory(
        user=user,
        partner=None,
        role=role_2,
        business_area=business_area_1,
    )

    assert role_assignment.id is not None


def test_role_assignment_unicef_subpartner_ignores_is_available_for_partner_flag(role_2, business_area_1):
    role_2.is_available_for_partner = False
    role_2.save()

    unicef = PartnerFactory(name="UNICEF")
    unicef_hq = PartnerFactory(name="UNICEF HQ", parent=unicef)
    unicef_hq.allowed_business_areas.add(business_area_1)

    role_assignment = RoleAssignmentFactory(
        user=None,
        partner=unicef_hq,
        role=role_2,
        business_area=business_area_1,
    )

    assert role_assignment.id is not None


def test_role_assignment_partner_in_allowed_business_area(partner, role, business_area_1):
    role_assignment = RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role,
        business_area=business_area_1,
    )

    assert role_assignment.id is not None


def test_role_assignment_partner_not_in_allowed_business_area(partner, role, business_area_2):
    with pytest.raises(ValidationError) as exc_info:
        RoleAssignment.objects.create(
            user=None,
            partner=partner,
            role=role,
            business_area=business_area_2,
        )

    assert f"{business_area_2} is not within the allowed business areas for {partner}." in str(exc_info.value)


def test_role_assignment_user_not_restricted_by_business_area(user, role, business_area_2):
    role_assignment = RoleAssignmentFactory(
        user=user,
        partner=None,
        role=role,
        business_area=business_area_2,
    )

    assert role_assignment.id is not None


def test_role_assignment_unique_user_role_ba_program_with_program(user, business_area_1, program_1):
    role = RoleFactory(name="Test Role Duplicate")

    RoleAssignmentFactory(
        user=user,
        partner=None,
        role=role,
        business_area=business_area_1,
        program=program_1,
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        RoleAssignment.objects.create(
            user=user,
            partner=None,
            role=role,
            business_area=business_area_1,
            program=program_1,
        )


def test_role_assignment_unique_user_role_ba_program_without_program(user, business_area_1):
    role = RoleFactory(name="Test Role Duplicate")

    RoleAssignmentFactory(
        user=user,
        partner=None,
        role=role,
        business_area=business_area_1,
        program=None,
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        RoleAssignment.objects.create(
            user=user,
            partner=None,
            role=role,
            business_area=business_area_1,
            program=None,
        )


def test_role_assignment_unique_partner_role_ba_program_with_program(partner, business_area_1, program_1):
    role = RoleFactory(name="Test Role Duplicate")

    RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role,
        business_area=business_area_1,
        program=program_1,
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        RoleAssignment.objects.create(
            user=None,
            partner=partner,
            role=role,
            business_area=business_area_1,
            program=program_1,
        )


def test_role_assignment_unique_partner_role_ba_program_without_program(partner, business_area_1):
    role = RoleFactory(name="Test Role Duplicate")

    RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role,
        business_area=business_area_1,
        program=None,
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        RoleAssignment.objects.create(
            user=None,
            partner=partner,
            role=role,
            business_area=business_area_1,
            program=None,
        )


def test_role_assignment_allowed_for_child_partner(business_area_1, role):
    parent_partner = PartnerFactory(name="Parent Partner")
    child_partner = PartnerFactory(name="Child Partner", parent=parent_partner)
    child_partner.allowed_business_areas.add(business_area_1)

    role_assignment = RoleAssignmentFactory(
        user=None,
        partner=child_partner,
        role=role,
        business_area=business_area_1,
    )

    assert role_assignment.id is not None


def test_role_assignment_not_allowed_for_parent_partner(business_area_1, role):
    parent_partner = PartnerFactory(name="Parent Partner")
    PartnerFactory(name="Child Partner", parent=parent_partner)
    parent_partner.allowed_business_areas.add(business_area_1)

    with pytest.raises(ValidationError) as exc_info:
        RoleAssignment.objects.create(
            user=None,
            partner=parent_partner,
            role=role,
            business_area=business_area_1,
        )

    assert f"{parent_partner} is a parent partner and cannot have role assignments." in str(exc_info.value)


def test_partner_with_role_assignment_cannot_become_parent(business_area_1, role):
    partner = PartnerFactory(name="Partner With Role")
    partner.allowed_business_areas.add(business_area_1)

    RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role,
        business_area=business_area_1,
    )

    with pytest.raises(ValidationError) as exc_info:
        PartnerFactory(name="Child Partner", parent=partner)

    assert f"{partner} cannot become a parent as it has RoleAssignments." in str(exc_info.value)


def test_user_cannot_be_assigned_to_parent_partner():
    parent_partner = PartnerFactory(name="Parent Partner")
    child_partner = PartnerFactory(name="Child Partner", parent=parent_partner)

    user = UserFactory(partner=child_partner)
    user.partner = parent_partner

    with pytest.raises(ValidationError) as exc_info:
        user.save()

    assert f"{parent_partner} is a parent partner and cannot have users." in str(exc_info.value)


def test_partner_with_users_cannot_become_parent():
    partner_with_user = PartnerFactory(name="Partner With User")
    UserFactory(partner=partner_with_user)

    child_partner = PartnerFactory(name="Child Partner")
    child_partner.parent = partner_with_user

    with pytest.raises(ValidationError) as exc_info:
        child_partner.save()

    assert f"{partner_with_user} cannot become a parent as it has users." in str(exc_info.value)


def test_area_limits_allowed_for_selected_partners_access(partner, area_1, business_area_1):
    program = ProgramFactory(
        business_area=business_area_1,
        partner_access=Program.SELECTED_PARTNERS_ACCESS,
    )

    admin_area_limit = AdminAreaLimitedToFactory(
        partner=partner,
        program=program,
        areas=[area_1],
    )

    assert admin_area_limit.id is not None


def test_area_limits_not_allowed_for_all_partners_access(partner, area_1, business_area_1):
    program = ProgramFactory(
        business_area=business_area_1,
        partner_access=Program.ALL_PARTNERS_ACCESS,
    )

    with pytest.raises(ValidationError) as exc_info:
        AdminAreaLimitedToFactory(
            partner=partner,
            program=program,
            areas=[area_1],
        )

    assert f"Area limits cannot be set for programs with {program.partner_access} access." in str(exc_info.value)


def test_area_limits_not_allowed_for_none_partners_access(partner, area_1, business_area_1):
    program = ProgramFactory(
        business_area=business_area_1,
        partner_access=Program.NONE_PARTNERS_ACCESS,
    )

    with pytest.raises(ValidationError) as exc_info:
        AdminAreaLimitedToFactory(
            partner=partner,
            program=program,
            areas=[area_1],
        )

    assert f"Area limits cannot be set for programs with {program.partner_access} access." in str(exc_info.value)
