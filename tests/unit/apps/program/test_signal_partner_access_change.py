from typing import Any

import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    PartnerFactory,
    ProgramFactory,
    RoleFactory,
)
from hope.models import (
    AdminAreaLimitedTo,
    Area,
    AreaType,
    BusinessArea,
    Country,
    Partner,
    Program,
    Role,
    RoleAssignment,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def unicef_partner(db: Any) -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def role(db: Any) -> Role:
    return RoleFactory(name="Role for Partner")


@pytest.fixture
def partner_with_role_in_afg_1(business_area: BusinessArea, role: Role) -> Partner:
    partner = PartnerFactory(name="Partner with role in Afg 1")
    partner.allowed_business_areas.set([business_area])
    # TODO: Due to temporary solution on program mutation, partner has to hold a role in business area.
    # After temporary solution is removed, partners will just need to be allowed in business area.
    RoleAssignment.objects.create(
        partner=partner,
        role=role,
        business_area=business_area,
        program=None,
    )
    return partner


@pytest.fixture
def partner_with_role_in_afg_2(business_area: BusinessArea, role: Role) -> Partner:
    partner = PartnerFactory(name="Partner with role in Afg 2")
    partner.allowed_business_areas.set([business_area])
    # TODO: Due to temporary solution on program mutation, partner has to hold a role in business area.
    # After temporary solution is removed, partners will just need to be allowed in business area.
    RoleAssignment.objects.create(
        partner=partner,
        role=role,
        business_area=business_area,
        program=None,
    )
    return partner


@pytest.fixture
def partner_not_allowed_in_ba(db: Any) -> Partner:
    return PartnerFactory(name="Partner without role in Afg")


@pytest.fixture
def country_afg(business_area: BusinessArea) -> Country:
    country = CountryFactory(name="Afghanistan")
    country.business_areas.set([business_area])
    return country


@pytest.fixture
def area_type_afg(country_afg: Country) -> AreaType:
    return AreaTypeFactory(name="Area Type in Afg", country=country_afg)


@pytest.fixture
def country_other(db: Any) -> Country:
    return CountryFactory(
        name="Other Country",
        short_name="Oth",
        iso_code2="O",
        iso_code3="OTH",
        iso_num="111",
    )


@pytest.fixture
def area_type_other(country_other: Country) -> AreaType:
    return AreaTypeFactory(name="Area Type Other", country=country_other)


@pytest.fixture
def area_in_afg_1(area_type_afg: AreaType) -> Area:
    return AreaFactory(name="Area in AFG 1", area_type=area_type_afg, p_code="AREA-IN-AFG1")


@pytest.fixture
def area_in_afg_2(area_type_afg: AreaType) -> Area:
    return AreaFactory(name="Area in AFG 2", area_type=area_type_afg, p_code="AREA-IN-AFG2")


@pytest.fixture
def area_not_in_afg(area_type_other: AreaType) -> Area:
    return AreaFactory(
        name="Area not in AFG",
        area_type=area_type_other,
        p_code="AREA-NOT-IN-AFG",
    )


@pytest.fixture
def program(
    business_area: BusinessArea,
    unicef_partner: Partner,
    partner_with_role_in_afg_1: Partner,
    partner_with_role_in_afg_2: Partner,
    partner_not_allowed_in_ba: Partner,
    area_in_afg_1: Area,
    area_in_afg_2: Area,
    area_not_in_afg: Area,
) -> Program:
    return ProgramFactory.create(
        status=Program.DRAFT,
        business_area=business_area,
        partner_access=Program.NONE_PARTNERS_ACCESS,
    )


def test_none_partners_access(
    program: Program,
    business_area: BusinessArea,
) -> None:
    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0
    assert (
        RoleAssignment.objects.filter(business_area=business_area, program=None).count() == 4
    )  # UNICEF HQ and UNICEF Partner for afghanistan
    assert (
        RoleAssignment.objects.filter(
            business_area=business_area,
            program=None,
            partner__name="UNICEF HQ",
        ).count()
        == 1
    )
    assert (
        RoleAssignment.objects.filter(
            business_area=business_area,
            program=None,
            partner__name=f"UNICEF Partner for {business_area.slug}",
        ).count()
        == 1
    )

    assert program.admin_area_limits.count() == 0

    program.partner_access = Program.NONE_PARTNERS_ACCESS
    program.save()

    assert program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert program.role_assignments.count() == 0
    assert (
        RoleAssignment.objects.filter(business_area=business_area, program=None).count() == 4
    )  # UNICEF HQ and UNICEF Partner for afghanistan

    assert program.admin_area_limits.count() == 0


def test_all_partners_access(
    program: Program,
    partner_with_role_in_afg_1: Partner,
    partner_with_role_in_afg_2: Partner,
) -> None:
    assert program.role_assignments.count() == 0

    program.partner_access = Program.ALL_PARTNERS_ACCESS
    program.save()

    assert program.partner_access == Program.ALL_PARTNERS_ACCESS

    assert program.role_assignments.count() == 2
    assert program.role_assignments.filter(partner=partner_with_role_in_afg_1).count() == 1
    assert program.role_assignments.filter(partner=partner_with_role_in_afg_2).count() == 1

    assert program.admin_area_limits.count() == 0


def test_selected_into_all_and_none_partners_access(
    program: Program,
    business_area: BusinessArea,
    partner_with_role_in_afg_1: Partner,
    partner_with_role_in_afg_2: Partner,
    area_in_afg_1: Area,
) -> None:
    assert program.role_assignments.count() == 0

    program.partner_access = Program.SELECTED_PARTNERS_ACCESS
    program.save()

    assert program.role_assignments.count() == 0

    RoleAssignment.objects.create(
        partner=partner_with_role_in_afg_1,
        role=RoleFactory(name="Role for Partner"),
        business_area=business_area,
        program=program,
    )
    area_limits = AdminAreaLimitedTo.objects.create(partner=partner_with_role_in_afg_1, program=program)
    area_limits.areas.set([area_in_afg_1])

    assert program.role_assignments.count() == 1
    assert program.admin_area_limits.count() == 1
    assert program.admin_area_limits.first().areas.count() == 1
    assert program.admin_area_limits.first().areas.first() == area_in_afg_1

    program.partner_access = Program.ALL_PARTNERS_ACCESS
    program.save()

    assert program.role_assignments.count() == 2

    assert program.role_assignments.filter(partner=partner_with_role_in_afg_1).count() == 1
    assert program.role_assignments.filter(partner=partner_with_role_in_afg_2).count() == 1

    assert program.admin_area_limits.count() == 0

    program.partner_access = Program.NONE_PARTNERS_ACCESS
    program.save()

    assert program.role_assignments.count() == 0
    assert (
        RoleAssignment.objects.filter(business_area=business_area, program=None).count() == 4
    )  # UNICEF HQ and UNICEF Partner for afghanistan
    assert (
        RoleAssignment.objects.filter(
            business_area=business_area,
            program=None,
            partner__name="UNICEF HQ",
        ).count()
        == 1
    )
    assert (
        RoleAssignment.objects.filter(
            business_area=business_area,
            program=None,
            partner__name=f"UNICEF Partner for {business_area.slug}",
        ).count()
        == 1
    )
