import os
import random
import time
from typing import Any, List

from django.conf import settings
import factory
from factory.django import DjangoModelFactory

from extras.test_utils.factories.program import ProgramFactory
from hope.models.admin_area_limited_to import AdminAreaLimitedTo
from hope.models.business_area import BusinessArea
from hope.models.partner import Partner
from hope.models.role import Role
from hope.models.role_assignment import RoleAssignment
from hope.models.user import (
    User,
)


class PartnerFactory(DjangoModelFactory):
    name = settings.UNICEF_HQ_PARTNER

    class Meta:
        model = Partner
        django_get_or_create = ("name",)

    @factory.lazy_attribute
    def parent(self) -> Any:
        if self.name == settings.UNICEF_HQ_PARTNER:
            return PartnerFactory(name="UNICEF")
        return None


class BusinessAreaFactory(DjangoModelFactory):
    name = factory.Sequence(lambda x: "BusinessArea{}".format(x))
    code = factory.Sequence(lambda x: str(x))
    active = True

    class Meta:
        model = BusinessArea
        django_get_or_create = ("name",)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
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
        user_model = User
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


class RoleAssignmentFactory(DjangoModelFactory):
    role = factory.SubFactory(RoleFactory)
    business_area = factory.SubFactory(BusinessAreaFactory)
    user = None
    partner = None

    class Meta:
        model = RoleAssignment
        django_get_or_create = ("user", "partner", "role", "business_area")

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> RoleAssignment:
        partner = kwargs.get("partner")
        user = kwargs.get("user")
        if not user and not partner:
            user = UserFactory()
            kwargs["user"] = user
        if partner:
            partner.allowed_business_areas.add(kwargs["business_area"])
        return super()._create(model_class, *args, **kwargs)


class AdminAreaLimitedToFactory(DjangoModelFactory):
    partner = factory.SubFactory(PartnerFactory)
    program = factory.SubFactory(ProgramFactory)

    class Meta:
        model = AdminAreaLimitedTo

    @factory.post_generation
    def areas(self, create: bool, extracted: List[Any], **kwargs: Any) -> None:
        if not create:
            return

        if extracted:
            for area in extracted:
                self.areas.add(area)


def create_superuser(**kwargs: Any) -> User:
    password = os.environ.get("LOCAL_ROOT_PASSWORD", "root1234")
    user_data = {
        "username": kwargs.get("username") or "root",
        "email": kwargs.get("email") or "root@root.com",
        "first_name": kwargs.get("first_name") or "Root",
        "last_name": kwargs.get("last_name") or "Rootkowski",
        "partner": kwargs.get("partner") or PartnerFactory(name="UNICEF HQ"),
        "is_active": True,
        "password": password,
    }
    return User.objects.create_superuser(**user_data)


def generate_unicef_partners() -> None:
    unicef_main_partner = PartnerFactory(name="UNICEF")
    PartnerFactory(name="UNICEF HQ", parent=unicef_main_partner)
    PartnerFactory(name="UNHCR")
    PartnerFactory(name="WFP")
