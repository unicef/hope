from typing import Any, Callable, Iterable, List, Optional

import pytest
from django.conf import settings
from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.account.models import (
    AdminAreaLimitedTo,
    Partner,
    Role,
    RoleAssignment,
    User,
)
from hope.apps.core.models import BusinessArea
from hope.apps.geo.models import Area
from hope.apps.program.models import Program


@pytest.fixture
def set_admin_area_limits_in_program() -> Callable:
    def _set_admin_area_limits_in_program(
        partner: Partner,
        program: Program,
        areas: List[Area],
    ) -> None:
        admin_area_limits, _ = AdminAreaLimitedTo.objects.get_or_create(
            program=program,
            partner=partner,
        )
        admin_area_limits.areas.set(areas)

    return _set_admin_area_limits_in_program


@pytest.fixture
def create_partner_role_with_permissions() -> Callable:
    def _create_partner_role_with_permissions(
        partner: Partner,
        permissions: Iterable,
        business_area: BusinessArea,
        program: Optional[Program] = None,
        name: Optional[str] = None,
        whole_business_area_access: Optional[bool] = False,
    ) -> None:
        permission_list = [perm.value for perm in permissions]
        name = name or f"Partner Role with Permissions {permission_list[0:3], ...}"
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        # whole_business_area is used to create a role for all programs in a business area (program=None)
        if not program and not whole_business_area_access:
            program = ProgramFactory(business_area=business_area, name="Program for Partner Role")
        partner.allowed_business_areas.add(business_area)
        RoleAssignment.objects.get_or_create(partner=partner, role=role, business_area=business_area, program=program)

    return _create_partner_role_with_permissions


@pytest.fixture
def create_user_role_with_permissions(
    set_admin_area_limits_in_program: Any,
) -> Callable:
    def _create_user_role_with_permissions(
        user: User,
        permissions: Iterable,
        business_area: BusinessArea,
        program: Optional[Program] = None,
        areas: Optional[List[Area]] = None,
        name: Optional[str] = None,
        whole_business_area_access: Optional[bool] = False,
    ) -> RoleAssignment:
        permission_list = [perm.value for perm in permissions]
        name = name or f"User Role with Permissions {permission_list[0:3], ...}"
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        # whole_business_area is used to create a role for all programs in a business area (program=None)
        if not program and not whole_business_area_access:
            program = ProgramFactory(business_area=business_area, name="Program for User Role")
        user_role, _ = RoleAssignment.objects.get_or_create(
            user=user, role=role, business_area=business_area, program=program
        )

        # set admin area limits
        if program and areas:
            set_admin_area_limits_in_program(user.partner, program, areas)
        return user_role

    return _create_user_role_with_permissions


@pytest.fixture
def partner_unicef(db: Any) -> PartnerFactory:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def partner_unicef_hq(db: Any) -> PartnerFactory:
    return PartnerFactory(name=settings.UNICEF_HQ_PARTNER, parent=PartnerFactory(name="UNICEF"))
