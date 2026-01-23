"""Account-related factories."""

from django.contrib.auth import get_user_model
import factory
from factory.django import DjangoModelFactory

from hope.models import Partner, Role, RoleAssignment

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


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Sequence(lambda n: f"Role {n}")
    subsystem = Role.HOPE


class RoleAssignmentFactory(DjangoModelFactory):
    class Meta:
        model = RoleAssignment

    @factory.lazy_attribute
    def business_area(self):
        from extras.test_utils.factories.core import BusinessAreaFactory

        return BusinessAreaFactory()

    partner = factory.SubFactory(PartnerFactory)
