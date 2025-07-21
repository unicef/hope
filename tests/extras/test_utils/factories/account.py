import random
import time

from django.contrib.auth import get_user_model

import factory
from factory.django import DjangoModelFactory


from typing import Any, Callable, Iterable, List, Optional

import pytest

from tests.extras.test_utils.factories.account import PartnerFactory
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


@pytest.fixture()
def partner_unicef(db: Any) -> PartnerFactory:
    return PartnerFactory(name="UNICEF")


class PartnerFactory(DjangoModelFactory):
    name = "UNICEF"

    class Meta:
        model = Partner
        django_get_or_create = ("name",)


class BusinessAreaFactory(DjangoModelFactory):
    name = factory.Sequence(lambda x: "BusinessArea{}".format(x))
    code = factory.Sequence(lambda x: str(x))
    active = True

    class Meta:
        model = BusinessArea
        django_get_or_create = ("name",)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username", "email")

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    partner = factory.SubFactory(PartnerFactory)
    email = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}_{time.time_ns()}@unicef.com")
    username = factory.LazyAttribute(
        lambda o: f"{o.first_name}{o.last_name}_{time.time_ns()}{str(random.randint(111, 999))}"
    )

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> User:
        user_model = get_user_model()
        manager = cls._get_manager(model_class)
        keyword_arguments = kwargs.copy()
        if "password" not in keyword_arguments:
            keyword_arguments["password"] = "password"
        username = keyword_arguments["username"]
        if user_model.objects.filter(username=username).exists():
            keyword_arguments["username"] = username + str(random.randint(111, 999))
        return manager.create_user(*args, **keyword_arguments)


class RoleFactory(DjangoModelFactory):
    subsystem = "HOPE"
    name = factory.Sequence(lambda o: f"name{o}")

    class Meta:
        model = Role
        django_get_or_create = ("name", "subsystem")


class UserRoleFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)
    business_area = factory.SubFactory(BusinessAreaFactory)

    class Meta:
        model = UserRole
        django_get_or_create = ("user", "role")
