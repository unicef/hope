import random
import time
from typing import Any

from django.contrib.auth import get_user_model

import factory
from factory.django import DjangoModelFactory

from hct_mis_api.apps.account.models import Partner, Role, User, RoleAssignment
from hct_mis_api.apps.core.models import BusinessArea


class PartnerFactory(DjangoModelFactory):
    name = "UNICEF"

    class Meta:
        model = Partner
        django_get_or_create = ("name",)


class BusinessAreaFactory(DjangoModelFactory):
    name = factory.Sequence(lambda x: "BusinessArea{}".format(x))
    code = factory.Sequence(lambda x: "BA{}".format(x))
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


class RoleAssignmentFactory(DjangoModelFactory):
    role = factory.SubFactory(RoleFactory)
    business_area = factory.SubFactory(BusinessAreaFactory)

    class Meta:
        model = RoleAssignment
        django_get_or_create = ("user", "partner", "role")

    @factory.lazy_attribute
    def partner(self):
        # Only create partner if user is not provided
        return None if self.user else PartnerFactory()

    @factory.lazy_attribute
    def user(self):
        # Only create user if partner is not provided
        return None if self.partner else UserFactory()
