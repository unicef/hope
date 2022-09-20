import time

from django.contrib.auth import get_user_model

import factory

from hct_mis_api.apps.account.models import Partner, Role, UserRole
from hct_mis_api.apps.core.models import BusinessArea


class PartnerFactory(factory.DjangoModelFactory):
    name = "UNICEF"

    class Meta:
        model = Partner
        django_get_or_create = ("name",)


class BusinessAreaFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: "BusinessArea{}".format(x))

    class Meta:
        model = BusinessArea
        django_get_or_create = ("name",)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    partner = factory.SubFactory(PartnerFactory)
    email = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}_{time.time_ns()}@unicef.com")
    username = factory.LazyAttribute(lambda o: f"{o.first_name}{o.last_name}_{time.time_ns()}")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, password="password", **kwargs)


class RoleFactory(factory.DjangoModelFactory):
    subsystem = "HOPE"
    name = factory.Sequence(lambda o: f"name{o}")

    class Meta:
        model = Role
        django_get_or_create = ("name", "subsystem")


class UserRoleFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)
    business_area = factory.SubFactory(BusinessAreaFactory)

    class Meta:
        model = UserRole
        django_get_or_create = ("user", "role")
