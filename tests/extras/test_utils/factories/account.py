"""Account-related factories."""

from django.contrib.auth import get_user_model
import factory
from factory.django import DjangoModelFactory

from hope.models import Partner

User = get_user_model()


class PartnerFactory(DjangoModelFactory):
    class Meta:
        model = Partner
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Partner {n}")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    partner = factory.SubFactory(PartnerFactory)
