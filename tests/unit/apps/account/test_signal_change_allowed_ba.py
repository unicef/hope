"""Tests for signal that changes allowed business areas for partners."""

from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
)
from hope.models import AdminAreaLimitedTo, BusinessArea, Partner, Program, Role, RoleAssignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_afg(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        code="0060",
        name="Afghanistan",
    )


@pytest.fixture
def business_area_ukr(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="ukraine",
        code="4410",
        name="Ukraine",
    )


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="Partner")


@pytest.fixture
def role(db: Any) -> Role:
    return RoleFactory(name="Role for Partner")


@pytest.fixture
def role_assignment1(partner: Partner, role: Role, business_area_afg: BusinessArea) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role,
        business_area=business_area_afg,
    )


@pytest.fixture
def program_afg(business_area_afg: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.DRAFT,
        business_area=business_area_afg,
        partner_access=Program.ALL_PARTNERS_ACCESS,
    )


@pytest.fixture
def program_ukr(business_area_ukr: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.DRAFT,
        business_area=business_area_ukr,
        partner_access=Program.SELECTED_PARTNERS_ACCESS,
    )


@pytest.fixture
def program_ukr_2(business_area_ukr: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.DRAFT,
        business_area=business_area_ukr,
        partner_access=Program.SELECTED_PARTNERS_ACCESS,
    )


@pytest.fixture
def role_assignment2(
    partner: Partner, role: Role, business_area_ukr: BusinessArea, program_ukr_2: Program
) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role,
        business_area=business_area_ukr,
        program=program_ukr_2,
    )


def test_signal_change_allowed_business_areas(
    partner: Partner,
    role: Role,
    business_area_afg: BusinessArea,
    business_area_ukr: BusinessArea,
    role_assignment1: RoleAssignment,
    program_afg: Program,
    program_ukr: Program,
    program_ukr_2: Program,
    role_assignment2: RoleAssignment,
):
    # ALL_PARTNERS_ACCESS - Partner that has access to AFG (signal on program)
    assert program_afg.role_assignments.count() == 1
    assert program_afg.role_assignments.first().partner == partner

    # UNICEF HQ, UNICEF for afg, partner
    assert RoleAssignment.objects.filter(business_area=business_area_afg, program=None).count() == 3

    # SELECTED_PARTNERS_ACCESS - no auto-assignment
    assert program_ukr.role_assignments.count() == 0

    # UNICEF HQ, UNICEF for ukr
    assert RoleAssignment.objects.filter(business_area=business_area_ukr, program=None).count() == 2

    # SELECTED_PARTNERS_ACCESS - manually assigned
    assert program_ukr_2.role_assignments.count() == 1
    assert program_ukr_2.role_assignments.first().partner == partner

    # Partner has 3 role assignments total
    assert partner.role_assignments.count() == 3
    assert partner.role_assignments.filter(program=program_afg).first() is not None
    assert partner.role_assignments.filter(program=None, business_area=business_area_afg).first() is not None
    assert partner.role_assignments.filter(program=program_ukr_2).first() is not None

    # No area limits initially
    assert AdminAreaLimitedTo.objects.filter(partner=partner).count() == 0

    # Remove AFG from allowed business areas
    partner.allowed_business_areas.remove(business_area_afg)

    # Removing from allowed BA removes roles in this BA
    assert partner.role_assignments.filter(program=program_afg).first() is None
    assert partner.role_assignments.filter(program=None, business_area=business_area_afg).first() is None
    assert partner.role_assignments.filter(program=program_ukr_2).first() is not None
