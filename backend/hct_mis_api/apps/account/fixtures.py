import time

from django.contrib.auth import get_user_model

import factory

from hct_mis_api.apps.account.models import Role


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")

    last_name = factory.Faker("last_name")

    email = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}@unicef.com")

    username = factory.LazyAttribute(lambda o: f"{o.first_name}{o.last_name}_{time.time_ns()}")


class RoleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("name",)
