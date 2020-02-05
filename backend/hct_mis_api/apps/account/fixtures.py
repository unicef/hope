import time

import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")

    last_name = factory.Faker("last_name")

    email = factory.LazyAttribute(
        lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}@unicef.com"
    )

    username = factory.LazyAttribute(
        lambda o: f"{o.first_name}{o.last_name}{time.time()}"
    )
