from typing import Any, Callable, Iterable, List, Optional

import pytest
from factory.django import DjangoModelFactory

from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.core.models import BusinessArea, BusinessAreaPartnerThrough
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


@pytest.fixture()
def update_partner_access_to_program() -> Callable:
    def _update_partner_access_to_program(
        partner: Partner,
        program: Program,
        areas: Optional[List[Area]] = None,
        full_area_access: Optional[bool] = False,
    ) -> None:
        program_partner_through, _ = ProgramPartnerThrough.objects.get_or_create(
            program=program,
            partner=partner,
        )
        if areas:
            program_partner_through.areas.set(areas)
        if full_area_access:
            program_partner_through.full_area_access = True
            program_partner_through.save(update_fields=["full_area_access"])

    return _update_partner_access_to_program


@pytest.fixture()
def create_partner_role_with_permissions() -> Callable:
    def _create_partner_role_with_permissions(
        partner: Partner,
        permissions: Iterable,
        business_area: BusinessArea,
        name: Optional[str] = "Partner Role with Permissions",
    ) -> None:
        business_area_partner_through, _ = BusinessAreaPartnerThrough.objects.get_or_create(
            business_area=business_area,
            partner=partner,
        )
        permission_list = [perm.value for perm in permissions]
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        business_area_partner_through.roles.add(role)

    return _create_partner_role_with_permissions


@pytest.fixture()
def create_user_role_with_permissions(update_partner_access_to_program: Any) -> Callable:
    def _create_user_role_with_permissions(
        user: User,
        permissions: Iterable,
        business_area: BusinessArea,
        program: Optional[Program] = None,
        areas: Optional[List[Area]] = None,
        name: Optional[str] = "Role with Permissions",
    ) -> UserRole:
        permission_list = [perm.value for perm in permissions]
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        user_role, _ = UserRole.objects.get_or_create(user=user, role=role, business_area=business_area)

        # update Partner permissions for the program
        if program:
            update_partner_access_to_program(user.partner, program, areas)
        return user_role

    return _create_user_role_with_permissions


class PartnerFactory(DjangoModelFactory):
    name = "UNICEF"

    class Meta:
        model = Partner
        django_get_or_create = ("name",)


@pytest.fixture()
def partner_unicef(db: Any) -> PartnerFactory:
    return PartnerFactory(name="UNICEF")
