from typing import Any

import pytest

from hope.apps.account.export_users_xlsx import ExportUsersXlsx
from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.models import BusinessArea, Partner, Role, User, RoleAssignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def role_create(db: Any) -> Role:
    return RoleFactory(name="Create_program", permissions=["PROGRAMME_CREATE"])


@pytest.fixture
def partner(business_area: BusinessArea) -> Partner:
    partner = PartnerFactory(name="Partner")
    partner.allowed_business_areas.add(business_area)
    return partner


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner, first_name="A_FirstU", last_name="LastN")


@pytest.fixture
def other_user(partner: Partner) -> User:
    return UserFactory(partner=None, first_name="Z_OtherU", last_name="Last")

@pytest.fixture
def user_role_assignment(business_area: BusinessArea, user: User, other_user: User, role_create: Role):
    return (RoleAssignmentFactory(
        business_area=business_area,
        user=user,
        partner=None,
        role=role_create,
        program=None,
    ), RoleAssignmentFactory(
        business_area=business_area,
        user=other_user,
        partner=None,
        role=role_create,
        program=None,
    ))


def test_get_exported_users_file_no_users(business_area: BusinessArea,) -> None:
    export = ExportUsersXlsx(business_area_slug=business_area.slug)

    result = export.get_exported_users_file()
    assert result is None


def test_get_exported_users_file_with_users(
        business_area: BusinessArea, user: User, other_user: User, user_role_assignment: RoleAssignment
) -> None:
    export = ExportUsersXlsx(business_area_slug=business_area.slug)

    result = export.get_exported_users_file()
    assert result is not None

    rows = list(export.ws.iter_rows(values_only=True))
    # headers and 2 users
    assert len(rows) == 3
    user_role = user.role_assignments.first().role
    # headers
    assert rows[0] == (
        'FIRST NAME',
        'LAST NAME',
        'E-MAIL',
        'ACCOUNT STATUS',
        'PARTNER',
        'USER ROLES',
    )
    # user fields
    assert rows[1] == (
        user.first_name,
        user.last_name,
        user.email,
        user.status,
        user.partner.name,
        f"{business_area.name}-{user_role.name}",
    )
